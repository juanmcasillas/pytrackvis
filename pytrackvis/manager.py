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
import shutil
import numpy as np
from PIL import Image, ImageChops
import cv2 
import json
import math
import os.path
import datetime
import traceback

from pytrackvis.appenv import *
from pytrackvis.altitude import *
from pytrackvis.mapper import OSMMapper
from pytrackvis.helpers import C, set_proxy, manhattan_point, same_track
from pytrackvis.helpers import glob_filelist, add_similarity_helpers, del_similarity_helpers
from pytrackvis.helpers import CacheManager, distancePoints
from pytrackvis.track import Track
from pytrackvis.filemanager import FileManager
from pytrackvis.mapreview import MapPreviewManager
from pytrackvis.dbstats import GetStatsFromDB
from pytrackvis.qparser import QueryParser

class Manager:
    LOG_NAME = "PyTrackVis"

    def __init__(self, config):
        self.config = config
        self.verbose = self.config.verbose
        self.db = None
        self.logger = logging.getLogger()
        self.track_previews = CacheManager(self.config.map_preview["track_previews_dir"])
        self.sim_previews = CacheManager(self.config.sim_preview["sim_previews_dir"])
        self.geojson_previews = CacheManager(self.config.geojson_preview["geojson_previews_dir"])
        self.gpx_previews = CacheManager(self.config.gpx_preview["gpx_previews_dir"])

        #self.query_parser = QueryParser(get_attr="id", limit=10, offset=0)
        self.query_parser = QueryParser(get_attr=self.config.query_parser['attrs'],
                                        limit=self.config.query_parser['limit'],
                                        offset=self.config.query_parser['offset'])

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
        self.mappreview_manager_thumb = MapPreviewManager(self.config.map_preview_thumb, 
                                                    cachedir=self.config.osm_cache["directory"],
                                                    debug=self.config.osm_cache["debug"])
        self.simpreview_manager = MapPreviewManager(self.config.sim_preview, 
                                                    cachedir=None,
                                                    debug=False)
        

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
    def getstats_from_db(self):
        return GetStatsFromDB(self.db)
    


    def create_database(self):
        """create the database. Removes the directories in the preview
        """
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
        # clear the directory of previews
        shutil.rmtree(self.config.map_preview["track_previews_dir"], ignore_errors=True)
        os.makedirs(self.config.map_preview["track_previews_dir"],exist_ok=True)

        shutil.rmtree(self.config.sim_preview["sim_previews_dir"], ignore_errors=True)
        os.makedirs(self.config.sim_preview["sim_previews_dir"],exist_ok=True)

        shutil.rmtree(self.config.geojson_preview["geojson_previews_dir"], ignore_errors=True)
        os.makedirs(self.config.geojson_preview["geojson_previews_dir"],exist_ok=True)


    def import_files(self, files):
        """import the files into the database if they are not inserted. Use the hash value
           as discriminator (id)


        Args:
            files (array): an array with glob paths, or files. Example:
            ['.\data\Cartography\**\*.fit', '.\data\fit\*.fit', 'file.gpx'] 
        """

        #  .\app.py import_files .\data\Cartography\**\*.fit # All files
        #  .\app.py import_files .\data\fit\*.fit # ony files in this dir

        files = glob_filelist(files)
        trackids = []
        for fname in files:
            track_id = self.db_track_exists(Track.calculate_hash(fname))
  
            if not track_id:
                fm = FileManager([fname])
                try:
                
                    ret = fm.load(optimize_points=self.config.points["optimize"],
                                  filter_points=self.config.points["filter"]
                                )

                except Exception as e:
                    s = traceback.format_exc()
                    self.logger.exception(s)
                    self.logger.error("import_files: Can't load %s: %s" % (fname, e))
                    continue

                if ret is None:
                    self.logger.error("import_files: Can't load %s: no points" % fname )
                    continue

                track = fm.track()
                if track._optimizer:
                    self.logger.info("Optimizer results (points): %s" % track._optimizer)

                # create all the required images and products.
                # create track map preview
          
                self.create_image_products(track)
                track = self.db_store_track(track)
                self.logger.info("file stored in db successfully %s (%d)" % (fname, track.id))
                trackids.append(str(track.id))
   
 
            else:
                self.logger.warning("Track %s exists on DB (id=%d)" % (fname, track_id))

        if len(trackids) > 0:
            self.check_similarity(trackids=trackids)


    def fix_time(self, files):
        """fix the tracks that doesn't change the time value (stuck on the same stamp)

        Args:
            files (_type_): _description_
        """
        files = glob_filelist(files)
        for fname in files:
            fm = FileManager([fname])
            
            try:
                fm.load(optimize_points=False, filter_points=False )
            except Exception as e:
                self.logger.error("fix_time: Can't load %s: %s" % (fname, e))
                return
            
            p = os.path.dirname(fname)
            fn,ex = os.path.splitext(os.path.basename(fname))
            tgt = "%s/%s-fixed.gpx" % (p,fn)
            track = fm.track()
            time_base = track.points[0].time
            time_base_orig = track.points[0].time
            time_delta = datetime.timedelta(seconds=1)
            for p in track.points:
                p.time = time_base
                time_base = time_base + time_delta
    
            with open(tgt,"w+") as tgt_fd:
                tgt_fd.write(track.as_gpx())

            self.logger.info("fixed %s: %s -> %s " % (fname, time_base_orig, time_base))



    def create_image_products(self, track):

        # marginal gain if disable configure the thumbs.
        create_thumbs = True

        target_fname = self.track_previews.map_object(track.hash, create_dirs=True, relative=True)
        target_fname_abs = self.track_previews.map_object(track.hash)

        map = self.mappreview_manager.create_map_preview(track)
        if create_thumbs:
            map_thumb = self.mappreview_manager_thumb.create_map_preview(track)

        #relative route (for www)
        track.preview = "%s.png" % target_fname
        track.preview_elevation = "%s_elevation.png" % target_fname
        # absolute path (for store)
        
        map.save("%s.png" % target_fname_abs, 'PNG')
        if create_thumbs:
            map_thumb.save("%s_tb.png" % target_fname_abs, 'PNG')
        
        # elevation profile
        elev_profile_fname = "%s_elevation.png" % target_fname_abs
        if create_thumbs:
            elev_profile_fname_thumb = "%s_elevation_tb.png" % target_fname_abs

        png = PNGFactory(outputfname=elev_profile_fname, size=self.config.elevation_profile['size'])
        png.CreatePNG(track._gpx, 
                        elevation=track.stats().uphill_climb, 
                        draw_border=self.config.elevation_profile['border'])

        if create_thumbs:
            png = PNGFactory(outputfname=elev_profile_fname_thumb, size=self.config.elevation_profile['thumb_size'])
            png.CreatePNG(track._gpx, 
                            elevation=track.stats().uphill_climb, 
                            draw_border=self.config.elevation_profile['border'],
                            full_featured=False)

        # calculate similarity
        map_sim = self.simpreview_manager.create_map_preview(track, empty_map=True, track_color=(200,200,200))
        target_sim = self.sim_previews.map_object(track.hash, create_dirs=True)
        map_sim = map_sim.convert('L').point(lambda x : 255 if x > 1 else 0, mode='1')
        map_sim.save("%s.png" % target_sim, 'png')

        # precache geojson objects
        geojson_fname_abs = self.geojson_previews.map_object(track.hash,create_dirs=True)
        geojson_fname = "%s.geojson" % geojson_fname_abs
        with open(geojson_fname,"w+") as geojson_fd:
            geojson_fd.write(json.dumps(track.as_geojson_line()["data"]))

    def check_similarity(self, threshold={ 
                    'distance': 500.0,
                    'length': 500.0,
                    'hausdorff': 5.0 },
                    trackids = []
                ):

        

        # shows the similarity values of the tracks, and create matches.
        # based on sim files (similarity files using distance)
        file_data,groups = self.db_get_similarity(trackids)
        #print(groups)

        tracks = {}
        
        
        # testing
        limit_load = None

        for d in file_data:
            fname = d["fname"]
            hash = d["hash"]
            
            t_center = C(latitude=d['middle_lat'],longitude=d['middle_long'],elevation=d['middle_elev'])
            t_len= d['length_2d']
            metadata = C(center=t_center, length=t_len)

            # XXX
            target_png = "%s.png" % self.sim_previews.map_object(hash)
            if not os.path.exists(target_png):
                self.logger.error("check_similarity: Can't load %s: %s" % (fname, target_png))
                continue

            #data = Image.open(target) # open colour image
            #data = data.convert('L')
            data = cv2.imread(target_png, cv2.IMREAD_GRAYSCALE) #cv2.COLOR_BGR2GRAY, ,cv2.COLOR_BGR2GRAY
            #cv2.imshow("", data)
            #cv2.waitKey(100)
            points = cv2.findNonZero(data)

            #data = cv2.imread( target, cv2.IMREAD_GRAYSCALE )
            print("loaded: %s" % target_png)
            # create the elements for fast comparation.
            tracks[str(hash)] = C(similar_tracks=[],  points=points, hash=hash, fname=fname, 
                                  target=target_png, metadata=metadata, previous_checked=d['previous_checked'])
        
            if limit_load is not None:
                limit_load -= 1
                if limit_load <= 0:
                    print("limit load. breaking (debug)")
                    break

        print("done:",len(tracks))

        # check each track with the others. calculate the similarity values
        # then classify the things ordered by similarity.
        result = []
        distance_manager = cv2.createHausdorffDistanceExtractor()

        # main loop to test similarity

        modify = True
        while modify:
            print("----------------- iteration ----------------------")
            modify = False
            for tx_key in tracks:
                tx = tracks[tx_key]
                if tx.previous_checked:
                    continue

                found = False
                for group in groups:
                    if tx.hash in group and len(group) == 1:
                        # its me, skip it continue with groups
                        #print("it's me, skipping %s" % (tx.hash))
                        found = True
                        continue
                     
                    if tx.hash in group:
                        # similar to something, it's ok. break and mark as found.
                        #print("%s in group %s, skipping" % (tx.hash, group))
                        found = True
                        break
                    else:
                        # check distance with the first element
                        ty = tracks[group[0]]
                        geo_d = distancePoints(tx.metadata.center, ty.metadata.center)
                        length_d = math.fabs(tx.metadata.length - ty.metadata.length)
                        hausdor_d = 0.0

                        if geo_d < 500.0 and length_d < 500.0:
                            hausdor_d = distance_manager.computeDistance(tx.points, ty.points)
                            if hausdor_d < 5.0:
                            #if hausdor_d <2.0 and geo_d < 100.0 and math.fabs(length_d) <= 100:
                                group.append(tx.hash)
                                found = True
                                print("\t-> %s %s" % (tx.target,tx.fname))
                                print("\t*  %s %s" % (ty.target,ty.fname))
                                print("\t: hau_d %3.2f" % hausdor_d)
                                print("\t: geo_d %3.2f" % geo_d)
                                print("\t: len_d %3.2f" % length_d)
                                break
                
                # no match for this element, so add it to the groups.
                if not found:
                    groups.append( [ tx.hash ])
                    modify = True
                    # print("Created new group for %s" % tx.hash)

        for g in groups:
            print("-" * 80)
            print(g)
            for i in g:
                #t = tracks[i]
                #print(t.hash, t.fname)
                # crash because we only load the first element in the optimized (import) mode
                print(i)
        self.db_save_similarity(groups)


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
    
    def delete_track(self, track):
        target_fname = self.track_previews.map_object(track['hash'], create_dirs=True, relative=True)
        target_fname_abs = self.track_previews.map_object(track['hash'])
        target_sim = self.sim_previews.map_object(track['hash'], create_dirs=True)
        geojson_fname_abs = self.geojson_previews.map_object(track['hash'],create_dirs=True)

        track_preview_tb = "%s_tb.png" % target_fname
        
        elev_profile_fname_thumb = "%s_elevation_tb.png" % target_fname_abs
        sim_tgt = "%s.png" % target_sim
        geojson_fname = "%s.geojson" % geojson_fname_abs

        for i in [ track['preview'], 
                   track['preview_elevation'],
                   track_preview_tb, 
                   elev_profile_fname_thumb, 
                   sim_tgt, 
                   geojson_fname]:
            if os.path.exists(i):
                os.remove(i)
            
        self.db_delete_track(track['id'])



    #
    # database methods
    #
        
    def db_delete_track(self, id):

        sql1 = "delete from tracks where id = ?"
        sql2 = "delete from TRACK_IN_PLACES where id_track = ?"
        sql3 = "delete from SIMILAR_TRACKS where id_track = ?"
        cursor = self.db.cursor()
        for sql in [ sql1, sql2, sql3 ]:
            cursor.execute(sql, (id,))
        self.db.commit()
        cursor.close()
    

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
        data = dict(cursor.fetchone())
        cursor.close()
        data['similar'] = self.db_get_track_similarity(data['id'])
        return data
    
    def db_get_tracks_info(self, query=None):
        
        # this query return the IDS.
        sql = query if query else self.config.queries["default"]

        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        data = list(map(lambda x: dict(x), data))
        
        cursor.close()
        for i in data:
            i['similar'] = self.db_get_track_similarity(i['id'])
        return data

    
    def db_get_track_similarity(self, id):
        sql = """
            select * from tracks where id in (
	            select id_track from SIMILAR_TRACKS where id in (
		            select id from SIMILAR_TRACKS where id_track = ?
	            )
            );"""
        
        """
        get the groups of track similarity, but process them. If only 
        one track in the group, return an empty set (no similar, only me)
        if not, then extract my own id from the list.
        """
        cursor = self.db.cursor()
        cursor.execute(sql,(id,))
        data = cursor.fetchall()
        data = list(map(lambda x: dict(x), data))
        cursor.close()
        ret = []
        if len(data) == 1:
            return ret
        for i in data:
            if i['id'] == id:
                continue
            ret.append(i)

        return ret

    def db_track_exists_id(self, track_id):
        "check if the track is loaded in the database, using the hash"
        sql = "select id,hash from tracks where id = ?"
        cursor = self.db.cursor()
        cursor.execute(sql, (track_id,))
        data = cursor.fetchone()
        cursor.close()
        if not data:
            return False
        return data["hash"]

    def db_track_exists(self, track_hash):
        "check if the track is loaded in the database, using the hash"
        sql = "select id,hash from tracks where hash = ?"
        cursor = self.db.cursor()
        cursor.execute(sql, (track_hash,))
        data = cursor.fetchone()
        cursor.close()
        if not data:
            return False
        return data["id"]
    
    def db_save_similarity(self, groups):
        sql = "delete from similar_tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()

        sql = "insert into similar_tracks(id, hash_track, id_track) values (?, ?, ?)"
        sql2 = "select id from tracks where hash = ?"
    
        i = 0
        for g in groups:
            for h in g:
                cursor2 = self.db.cursor()
                cursor2.execute(sql2,(h,))
                track_id = cursor2.fetchone()["id"]
                cursor2.close()
                cursor.execute(sql, (i, h, track_id,))  
            i+=1
        self.db.commit()
        cursor.close()

    def db_get_similarity_groups(self):
        groups_t = {}
       
        sql = "select * from similar_tracks"
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        groups_data = map(lambda x: dict(x), data)
        cursor.close()
        
        for g in groups_data:
            if g['id'] in groups_t.keys():
                groups_t[g['id']].append(g['hash_track'])
            else:
                groups_t[g['id']] = [ g['hash_track'] ]
  
        return list(groups_t.values())


    def db_get_similarity(self, trackids = []):
        # add this attribute previous_checked to speed up the 
        # processing, so check only the tracks
        # in the array.
        sql = "select id,hash,fname,middle_lat,middle_long,middle_elev,length_2d, false as previous_checked from tracks"
        if trackids and len(trackids) > 0:
            tids = ",".join(trackids)
            sql += " where id in (%s)" % tids
        
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()

        track_data = map(lambda x: dict(x), data)
        track_data = list(track_data)
       


        groups = self.db_get_similarity_groups()
        # for elements in group, add to track data the required elements.
        for g in groups:
            key = g[0]
            found = False
            for t in track_data:
                if t["hash"] == key:
                    found = True
                    break
            if not found:
                # add this attribute previous_checked to speed up the 
                # processing, so check only the tracks
                # in the array.
                sql = "select id,hash,fname,middle_lat,middle_long,middle_elev,length_2d, true as previous_checked from tracks where hash = ?"
                cursor = self.db.cursor()
                cursor.execute(sql,(key,))
                data = cursor.fetchone()
                cursor.close()
                track_data.append(data)
                # print("*** adding %s" % key)

        return track_data, groups


    def db_update_track_field(self, field_name, track_id, field_value):
        sql = "update tracks set %s = ? where id = ?" % field_name
        cursor = self.db.cursor()
        cursor.execute(sql, (field_value,track_id))
        self.db.commit()
        cursor.close()


    def db_store_track(self, track):
        sql = """
        insert into tracks(fname, hash, preview, preview_elevation, stamp, number_of_points, 
                           duration, quality, length_2d, length_3d,
                           start_time,end_time,moving_time,
                           
                           stopped_time, moving_distance,
                           stopped_distance,
                           
                           max_speed_ms,max_speed_kmh,
                           avg_speed_ms,avg_speed_kmh,
                           uphill_climb,downhill_climb,
                           minimum_elevation,maximum_elevation,
                           
                           name,searchname,kind,device,equipment,
                           description,
                           is_clockwise,score,rating,
                           
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
        values ( ?, ?, ?, ?, ?, ?,
                 ?, ?, ?, ?,
                 ?, ?, ?,

                 ?, ?,
                 ?,

                 ?, ?, 
                 ?, ?,
                 ?, ?,
                 ?, ?,

                 ?, ?, ?, ?, ?, 
                 ?,  
                 ?, ?,?,

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