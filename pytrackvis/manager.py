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
import glob



from pytrackvis.appenv import *
from pytrackvis.mapper import OSMMapper
from pytrackvis.helpers import C, set_proxy,track_similarity, manhattan_point
from pytrackvis.helpers import glob_filelist
from pytrackvis.filemanager import FileManager

class Manager:
    LOG_NAME = "PyTrackVis"

    def __init__(self, config):
        self.config = config
        self.verbose = self.config.verbose
        self.db = None
        self.logger = logging.getLogger(Manager.LOG_NAME)

    def db_connect(self):
        self.db = sqlite3.connect(self.config.database["file"], check_same_thread=False)
        self.db.row_factory = sqlite3.Row

    def startup(self):
        self.configure_logger()
        self.db_connect()

    def shutdown(self):
        """ends the execution, closes the database
        """
        if self.db:
            self.db.close()
        raise SystemExit

    def configure_logger(self):

        logging.getLogger().setLevel(self.config.logs["level"])
        log_formatter = logging.Formatter(self.config.logs["format"])
        rootLogger = logging.getLogger()

        file_handler = logging.FileHandler(self.config.logs["app"])
        file_handler.setFormatter(log_formatter)
        rootLogger.addHandler(file_handler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(log_formatter)
        rootLogger.addHandler(consoleHandler)

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
                self.logger.error("Cant' load %s: %s" % (fname, e))
                continue

            self.logger.info("file loaded %s" % fname)
            track = fm.track()
            if track._optimizer:
                self.logger.info("Optimizer results (points): %s" % track._optimizer)

            track_id = self.db_track_exists(track)
            if not track_id:
                self.db_store_track(track)
            else:
                track.id = track_id
                self.logger.warning("Track %s exists on DB (id=%d)" % (track.hash, track.id))


    def check_similarity(self):
        # shows the similarity values of the tracks, and create matches.
        data = self.db_get_similarity()
        tracks = {}
        
        for d in data:
            fname = d["fname"]
            fm = FileManager([fname])
            try:
                fm.load(optimize_points=self.config.points["optimize"],
                        filter_points=self.config.points["filter"]
                        )
                
            except Exception as e:
                self.logger.error("Cant' load %s: %s" % (fname, e))
                continue

            print("loaded: %s" % fname)
            track = fm.track()
            tracks[str(track.hash)] = track
        
        print("done:",len(tracks))
        # check each track with the others. calculate the similarity values
        # then classify the things ordered by similarity.
        result = {}
        for tx_key in tracks:
            tx = tracks[tx_key]
            for ty_key in tracks:
                ty = tracks[ty_key]
                if tx.hash == ty.hash:
                    # same thing
                    continue
                key = "%s %s" % (tx.hash,ty.hash)
                key_r = "%s %s" % (ty.hash,tx.hash)
                if not key in result.keys() and not key_r in result.keys():
                    similarity = track_similarity(tx,ty)
                    result[key] = similarity

        for k in result.keys():
            h1,h2 = k.split(" ")
            f1 = tracks[h1].fname
            f2 = tracks[h2].fname
            if result[k] < 100000.0:
                print("-----")
                print("%3.3f" % result[k])
                print("%s" % f1)
                print("%s" % f2)
            


    #
    # database methods
    #
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
    
    def db_get_similarity(self):
        sql = "select id,hash,fname from tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return map(lambda x: dict(x), data)
    

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