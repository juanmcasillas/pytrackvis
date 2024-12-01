##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // manager.py
# //
# // Manages the trackvis application (backend and frontend)
# // at high level
# //
# // 26/11/2024 11:38:36
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import logging
import logging.handlers
import sqlite3
import configparser
import sys

from pytrackvis.appenv import *
from pytrackvis.mapper import OSMMapper
from pytrackvis.helpers import C, set_proxy, manhattan_point, same_track
from pytrackvis.helpers import glob_filelist, add_similarity_helpers, del_similarity_helpers
from pytrackvis.track import Track
from pytrackvis.filemanager import FileManager
from pytrackvis.mapreview import MapPreviewManager

class Manager:
    LOG_NAME = "PyTrackVis"

    def __init__(self, config):
        self.config = config
        self.verbose = self.config.verbose
        self.db = None
        self.logger = logging.getLogger()

    def db_connect(self):
        self.db = sqlite3.connect(self.config.database["file"], check_same_thread=False)
        self.db.row_factory = sqlite3.Row

    def startup(self):
        self.configure_logger()
        self.configure_proxy()
        self.db_connect()
        self.mappreview_manager = MapPreviewManager(self.config.map_preview, 
                                                    cachedir=self.config.osm_cache["directory"],
                                                    debug=self.config.osm_cache["debug"])
        

    def shutdown(self):
        """ends the execution, closes the database
        """
        if self.db:
            self.db.close()
        raise SystemExit

    def load_tokens(self, put_env=False):
        tokens = configparser.ConfigParser()
        tokens.read(self.config.api_key_file)
        if not 'TOKENS' in tokens.keys() or not 'MAPTILER_KEY' in tokens["TOKENS"]:
            self.logger.error("can't get maptiler token")
            sys.exit(0)
        if put_env:
            os.environ["MAPTILER_KEY"] = tokens["TOKENS"]["MAPTILER_KEY"]
        
        AppEnv.config_set(self.config.tokens["MAPTILER_KEY"],tokens["TOKENS"]["MAPTILER_KEY"])
        self.config.tokens["MAPTILER_KEY"] = tokens["TOKENS"]["MAPTILER_KEY"]
        
        self.logger.info("MAPTILER_KEY token loaded")


    def configure_proxy(self):
        if self.config.proxy["enabled"]:
            set_proxy(self.config.proxy["url"])
            self.logger.info("proxy enabled: %s" % self.config.proxy["url"])
        else:
            self.logger.info("proxy disabled, direct connection")

    def configure_logger(self):

        self.logger.setLevel(self.config.logs["level"])
        log_formatter = logging.Formatter(self.config.logs["format"])
        # rootLogger = logging.getLogger()
        
        if not os.path.exists(self.config.logs["app"]):
            logpath = os.path.dirname(self.config.logs["app"])
            os.makedirs(logpath, exist_ok=True)

        file_handler = logging.FileHandler(self.config.logs["app"])
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        #consoleHandler = logging.StreamHandler()
        #consoleHandler.setFormatter(log_formatter)
        #self.logger.addHandler(consoleHandler)

    ## some commands

    def create_database(self):
        if self.db:
            self.db.close()

        with open(self.config.database['script'], 'r') as sql_file:
            sql_script = sql_file.read()

        db = sqlite3.connect(self.config.database['file'])
        cursor = db.cursor()
        try:
            cursor.executescript(sql_script)
            self.logger.info("database %s created succesfully from %s" % (
                self.config.database['file'],
                self.config.database['script'],
            ))

        except Exception as e:
            self.logger.error("error while creating %s from %s: %s" % (
                    self.config.database['file'],
                    self.config.database['script'],
                    e)
            )

        db.commit()
        db.close()

    def import_files(self, files):
        "load files from directory, or one by one. Check if track exists."
        #  .\app.py import_files .\data\Cartography\**\*.fit # All files
        #  .\app.py import_files .\data\fit\*.fit # ony files in this dir

        files = glob_filelist(files)
        for fname in files:
            fm = FileManager([fname])
            try:
                fm.load(optimize_points=self.config.points["optimize"],
                        filter_points=self.config.points["filter"]
                        )
                
            except Exception as e:
                self.logger.error("import_files: Can't load %s: %s" % (fname, e))
                continue

            self.logger.info("file loaded %s" % fname)
            track = fm.track()
            if track._optimizer:
                self.logger.info("Optimizer results (points): %s" % track._optimizer)

            track_id = self.db_track_exists(track)
            if not track_id:
                map = self.mappreview_manager.create_map_preview(track)
                map.save("map.png", 'PNG')
                #self.db_1_track(track)
                # calculate similarity
                # create map preview
            else:
                track.id = track_id
                self.logger.warning("Track %s exists on DB (id=%d)" % (track.hash, track.id))


    def check_similarity(self):
        # shows the similarity values of the tracks, and create matches.
        file_data = self.db_get_similarity()
        tracks = {}

        for d in file_data:
            fname = d["fname"]
            fm = FileManager([fname])
            try:
                fm.load(optimize_points=self.config.points["optimize"],
                        filter_points=self.config.points["filter"],
                        only_load=True
                        )
                
            except Exception as e:
                self.logger.error("check_similarity: Can't load %s: %s" % (fname, e))
                continue

            print("loaded: %s" % fname)
            track = fm.track()
            add_similarity_helpers(track)
            # create the elements for fast comparation.
            tracks[str(track.hash)] = track
        
        print("done:",len(tracks))
        # check each track with the others. calculate the similarity values
        # then classify the things ordered by similarity.
        result = []
        print(len(tracks.keys()))
    
        for tx_key in tracks:
            tx = tracks[tx_key]
            tx.similar_tracks = [tx.hash]
            # create a point cache
            print("-> %s %s" % (tx.hash,tx.fname))
            for ty_key in tracks:
                ty = tracks[ty_key]
                print("\t*%s %s" % (ty.hash,ty.fname))
                if tx.hash == ty.hash:
                    # same track, skip
                    continue
                
                if not ty.hash in tx.similar_tracks:
                    #if same_track(tx, ty, trk1_cache=track1_cache):
                    if same_track(tx, ty, use_cache=True):
                        tx.similar_tracks.append(ty.hash)
    
        ## done. Check all the data.
        ## filter similar groups by matching then.
        similar_tracks = []
        for tx_key in tracks:
            tracks[tx_key].similar_tracks.sort()
            if tracks[tx_key].similar_tracks not in similar_tracks:
                similar_tracks.append(tracks[tx_key].similar_tracks)

        for i in similar_tracks:
            print(i)
        self.db_save_similarity(similar_tracks)


    def list_tracks(self):
        tracks = self.db_get_tracks()
        for track in tracks:
            print("id:%s hash:[%s] fname:%s" % (track['id'], track['hash'], track['fname']))
        print("%d tracks loaded" % len(tracks))

    def get_track(self, id):
        trk_data = self.db_get_track(id)
        fm = FileManager([trk_data['fname']])
        
        try:
            fm.load(optimize_points=self.config.points["optimize"],
                    filter_points=self.config.points["filter"]
                    )
        except Exception as e:
            self.logger.error("get_track: Can't load %s: %s" % (trk_data['fname'], e))
            return None

        self.logger.info("file loaded %s" % trk_data['fname'])
        return fm.track()
    
    #ca
    # database methods
    #
    def db_get_tracks(self):
        sql = "select * from tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        data = map(lambda x: dict(x), data)
        cursor.close()
        return list(data)
    
    def db_get_track(self, id):
        sql = "select * from tracks where id = ?"
        cursor = self.db.cursor()
        cursor.execute(sql, (id,))
        data = cursor.fetchone()
        cursor.close()
        return dict(data)
    
    def db_get_tracks_info(self):
        sql = "select * from tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        data = map(lambda x: dict(x), data)
        cursor.close()
        return list(data)
    

    def db_track_exists(self, track):
        "check if the track is loaded in the database, using the hash"
        sql = "select id,hash from tracks where hash = ?"
        cursor = self.db.cursor()
        cursor.execute(sql, (track.hash,))
        data = cursor.fetchone()
        cursor.close()
        if not data:
            return False
        return data["id"]
    
    def db_save_similarity(self, data):
        sql = "delete from similar_tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()

        sql = "insert into similar_tracks(id, hash_track) values (?, ?)"
        for i in range(len(data)):
            for j in data[i]:
                cursor.execute(sql, (i, j,))  
        
        self.db.commit()
        cursor.close()

    def db_get_similarity(self):
        sql = "select id,hash,fname from tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        track_data = map(lambda x: dict(x), data)
        cursor.close()
        return list(track_data)
    
        # sql = "select id,hash_track from similar_tracks"
        # cursor.execute(sql)
        # data = cursor.fetchall()
        # cursor.close()
        # # build the array
        # data = map(lambda x: dict(x), data)
        
        # similar_data = {}
        # for d in data:
        #     if d['id'] not in similar_data.keys():
        #         similar_data[d['id']] = [ d['hash_track'] ]
        #     else:
        #         similar_data[d['id']].append(d['hash_track'])

        # # [
        # #     [-4733961121561410647, 2604169270486981572]
        # #     [-7144163367426839845]
        # #     [-1444645076578622331]
        # # ]
        # return track_data, list(similar_data.values())


    
   

    def db_store_track(self, track):
        sql = """
        insert into tracks(fname, hash, number_of_points, 
                           duration, length_2d, length_3d,
                           start_time,end_time,moving_time,
                           
                           stopped_time, moving_distance,
                           stopped_distance,
                           
                           max_speed_ms,max_speed_kmh,
                           avg_speed_ms,avg_speed_kmh,
                           uphill_climb,downhill_climb,
                           minimum_elevation,maximum_elevation,
                           
                           name,kind,device,equipment,
                           description,rating,
                           is_circular,quality,
                           is_clockwise,score,
                           is_cloned,
                           
                           min_lat,min_long,max_lat,max_long,
                           
                           middle_lat,middle_long,middle_elev,
                           begin_lat,begin_long,begin_elev,
                           end_lat,end_long,end_elev,
                           
                           uphill_distance,level_distance,downhill_distance,
                           
                           uphill_elevation,level_elevation,downhill_elevation,
                           
                           uphill_avg_slope,level_avg_slope,downhill_avg_slope,
                           
                           uphill_p_distance,level_p_distance,downhill_p_distance,
                           
                           uphill_speed,level_speed,downhill_speed,
                           
                           uphill_time,level_time,downhill_time,
                           
                           uphill_p_time,level_p_time,downhill_p_time,

                           uphill_slope_range_distance_0,
                           uphill_slope_range_distance_1,
                           uphill_slope_range_distance_2,
                           uphill_slope_range_distance_3,
                           uphill_slope_range_distance_4,
                           uphill_slope_range_distance_5,
                           uphill_slope_range_distance_6,

                           downhill_slope_range_distance_0,
                           downhill_slope_range_distance_1,
                           downhill_slope_range_distance_2,
                           downhill_slope_range_distance_3,
                           downhill_slope_range_distance_4,
                           downhill_slope_range_distance_5,
                           downhill_slope_range_distance_6,

                           uphill_slope_range_time_0,
                           uphill_slope_range_time_1,
                           uphill_slope_range_time_2,
                           uphill_slope_range_time_3,
                           uphill_slope_range_time_4,
                           uphill_slope_range_time_5,
                           uphill_slope_range_time_6,

                           downhill_slope_range_time_0,
                           downhill_slope_range_time_1,
                           downhill_slope_range_time_2,
                           downhill_slope_range_time_3,
                           downhill_slope_range_time_4,
                           downhill_slope_range_time_5,
                           downhill_slope_range_time_6,

                           max_heart_rate,min_heart_rate,avg_heart_rate,
                           max_power,min_power,avg_power,
                           max_cadence,min_cadence,avg_cadence,
                           max_temperature,min_temperature,avg_temperature)
        values ( ?, ?, ?, 
                 ?, ?, ?,
                 ?, ?, ?,

                 ?, ?,
                 ?,

                 ?, ?, 
                 ?, ?,
                 ?, ?,
                 ?, ?,

                 ?, ?, ?, ?, 
                 ?, ?, 
                 ?, ?,
                 ?, ?,
                 ?, 

                 ?, ?, ?, ?,    

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?,                     

                 ?, ?, ?, ?, ?, ?, ?,
                 
                 ?, ?, ?, ?, ?, ?, ?,

                 ?, ?, ?, ?, ?, ?, ?,

                 ?, ?, ?, ?, ?, ?, ?,
                 
                 ?, ?, ?,
                 ?, ?, ?,
                 ?, ?, ?,
                 ?, ?, ?
        );
        """

        cursor = self.db.cursor()
        cursor.execute(sql, track.as_tuple(db=True))
        track.id = cursor.lastrowid
        self.db.commit()
        cursor.close()
        return track