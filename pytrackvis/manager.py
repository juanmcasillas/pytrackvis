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

from pytrackvis.appenv import *
from pytrackvis.altitude import *
from pytrackvis.mapper import OSMMapper
from pytrackvis.helpers import C, set_proxy, manhattan_point, same_track
from pytrackvis.helpers import glob_filelist, add_similarity_helpers, del_similarity_helpers
from pytrackvis.helpers import CacheManager
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
        self.track_previews = CacheManager(self.config.map_preview["track_previews_dir"])
        self.sim_previews = CacheManager(self.config.sim_preview["sim_previews_dir"])

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
        # clear the directory of previews
        shutil.rmtree(self.config.map_preview["track_previews_dir"], ignore_errors=True)
        os.makedirs(self.config.map_preview["track_previews_dir"],exist_ok=True)


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
                # create track map preview
                map = self.mappreview_manager.create_map_preview(track)
                #relative route (for www)
                track.preview = "%s.png" % self.track_previews.map_object(track.hash, create_dirs=True, relative=True)
                # absolute path (for store)
                target = self.track_previews.map_object(track.hash)
                map.save("%s.png" % target, 'PNG')
                self.db_store_track(track)
                # calculate similarity
                map_sim = self.simpreview_manager.create_map_preview(track, empty_map=True, track_color=(200,200,200))
                target_sim = self.sim_previews.map_object(track.hash, create_dirs=True)
                map_sim = map_sim.convert('L').point(lambda x : 255 if x > 1 else 0, mode='1')
                map_sim.save("%s.png" % target_sim, 'png')

                # elevation profile
                png = PNGFactory( outputfname="%s_elevation.png" % target)
                png.CreatePNG(track._gpx, elevation=track.stats().uphill_climb)
                
                # metadata info for checking similarity:
                metadata = {
                    'center': { 
                        'latitude':  track.stats().middle_point.lat,
                        'longitude': track.stats().middle_point.long,
                        'elevation': track.stats().middle_point.elev,
                    },
                    'length': track.stats().length_3d
                }
                fd = open("%s.json" % target_sim,"w+")
                fd.write(json.dumps(metadata))
                fd.close()
 
            else:
                track.id = track_id
                self.logger.warning("Track %s exists on DB (id=%d)" % (track.hash, track.id))


    # def check_similarity_points(self):
    #     # shows the similarity values of the tracks, and create matches.
    #     file_data = self.db_get_similarity()
    #     tracks = {}

    #     for d in file_data:
    #         fname = d["fname"]
    #         fm = FileManager([fname])
    #         try:
    #             fm.load(optimize_points=self.config.points["optimize"],
    #                     filter_points=self.config.points["filter"],
    #                     only_load=True
    #                     )
                
    #         except Exception as e:
    #             self.logger.error("check_similarity: Can't load %s: %s" % (fname, e))
    #             continue

    #         print("loaded: %s" % fname)
    #         track = fm.track()
    #         add_similarity_helpers(track)
    #         # create the elements for fast comparation.
    #         tracks[str(track.hash)] = track
        
    #     print("done:",len(tracks))
    #     # check each track with the others. calculate the similarity values
    #     # then classify the things ordered by similarity.
    #     result = []
    #     print(len(tracks.keys()))
    
    #     for tx_key in tracks:
    #         tx = tracks[tx_key]
    #         tx.similar_tracks = [tx.hash]
    #         # create a point cache
    #         print("-> %s %s" % (tx.hash,tx.fname))
    #         for ty_key in tracks:
    #             ty = tracks[ty_key]
    #             print("\t*%s %s" % (ty.hash,ty.fname))
    #             if tx.hash == ty.hash:
    #                 # same track, skip
    #                 continue
                
    #             if not ty.hash in tx.similar_tracks:
    #                 #if same_track(tx, ty, trk1_cache=track1_cache):
    #                 if same_track(tx, ty, use_cache=True):
    #                     tx.similar_tracks.append(ty.hash)
    
    #     ## done. Check all the data.
    #     ## filter similar groups by matching then.
    #     similar_tracks = []
    #     for tx_key in tracks:
    #         tracks[tx_key].similar_tracks.sort()
    #         if tracks[tx_key].similar_tracks not in similar_tracks:
    #             similar_tracks.append(tracks[tx_key].similar_tracks)

    #     for i in similar_tracks:
    #         print(i)
    #     self.db_save_similarity(similar_tracks)

    def check_similarity(self, match_treshold=500.0):

        def is_similar(image1, image2):
            # print(image1.shape)
            # print(image2.shape)
            # print(image1)
            # print(image2)
            s = np.bitwise_xor(image1,image2).any()
            return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())
        
        def difference(image1, image2):
           
            diff = image1 - image2
            if np.all(diff == 0):
                return False
            else:
                img = Image.fromarray(np.uint8(diff)).convert('L')
                img.save("diff.png","png")
                return True

            im1 = Image.fromarray(np.uint8(image1)).convert('L')
            im2 = Image.fromarray(np.uint8(image2)).convert('L')
            diff = ImageChops.difference(im1, im2)
            diff.save("diff.png","png")
            r = diff.getbbox()
            print("getbox", r)
            if r:
                return True
            else:
                return False
        

        def mse(image1, image2):
            # the 'Mean Squared Error' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
            err /= float(image1.shape[0] * image1.shape[1])
            # return the MSE, the lower the error, the more "similar"
            # the two images are
            return err            

        # shows the similarity values of the tracks, and create matches.
        # based on sim files (similarity files using distance)
        file_data = self.db_get_similarity()
        tracks = {}

        for d in file_data:
            fname = d["fname"]
            hash = d["hash"]
            # XXX
            target_png = "%s.png" % self.sim_previews.map_object(hash)
            target_json = "%s.json" % self.sim_previews.map_object(hash)
            if not os.path.exists(target_png):
                self.logger.error("check_similarity: Can't load %s: %s" % (fname, target_png))
                continue

            #data = Image.open(target) # open colour image
            #data = data.convert('L')
            data = cv2.imread(target_png, cv2.IMREAD_GRAYSCALE) #cv2.COLOR_BGR2GRAY, ,cv2.COLOR_BGR2GRAY
            cv2.imshow("", data)
            #cv2.waitKey(100)
            points = cv2.findNonZero(data)
            
            fd = open(target_json)
            data_json =fd.read()
            fd.close()
            data_json = json.loads(data_json)
        

            #data = cv2.imread( target, cv2.IMREAD_GRAYSCALE )
            print("loaded: %s" % target_png)
            # create the elements for fast comparation.
            tracks[str(hash)] = C(similar_tracks=[], img=data, points=points, hash=hash, fname=fname, 
                                  target=target_png, json=data_json)
        
        print("done:",len(tracks))
        # check each track with the others. calculate the similarity values
        # then classify the things ordered by similarity.
        result = []
        distance_manager = cv2.createHausdorffDistanceExtractor()

        for tx_key in tracks:
            tx = tracks[tx_key]
            tx.similar_tracks = [tx.hash]
            # create a point cache
            for ty_key in tracks:
                ty = tracks[ty_key]
                if tx.hash == ty.hash:
                    # same track, skip
                    # pass for tests continue
                    continue
                
                if not ty.hash in tx.similar_tracks:
                    #mse_val = mse(tx.img, ty.img)
                    #is_sim = is_similar(tx.img, ty.img)
                    hausdor_d = distance_manager.computeDistance(tx.points, ty.points)
                    tx_center = C(latitude=tx.json['center']['latitude'],
                                  longitude=tx.json['center']['longitude'],
                                  elevation=tx.json['center']['elevation'] )

                    ty_center = C(latitude=ty.json['center']['latitude'],
                                  longitude=ty.json['center']['longitude'],
                                  elevation=ty.json['center']['elevation'] )


                    geo_d = distancePoints3D(tx_center, ty_center)
                    length_d = tx.json['length'] - ty.json['length']
                    if hausdor_d <2.0 and geo_d < 100.0 and math.fabs(length_d) <= 100:
                        tx.similar_tracks.append(ty.hash)
                        print("\t-> %s %s" % (tx.target,tx.fname))                    
                        print("\t*  %s %s" % (ty.target,ty.fname))                    
                        print("\t: hau_d %3.2f" % hausdor_d)
                        print("\t: geo_d %3.2f" % geo_d)
                        print("\t: len_d %3.2f" % length_d)
        
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

        sql = "insert into similar_tracks(id, hash_track, id_track) values (?, ?, ?)"
        sql2 = "select id from tracks where hash = ?"
    
        for i in range(len(data)):
            for j in data[i]:
                cursor2 = self.db.cursor()
                cursor2.execute(sql2,(j,))
                track_id = cursor2.fetchone()["id"]
                cursor2.close()
                cursor.execute(sql, (i, j, track_id,))  
        
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
        insert into tracks(fname, hash, preview, stamp, number_of_points, 
                           duration, length_2d, length_3d,
                           start_time,end_time,moving_time,
                           
                           stopped_time, moving_distance,
                           stopped_distance,
                           
                           max_speed_ms,max_speed_kmh,
                           avg_speed_ms,avg_speed_kmh,
                           uphill_climb,downhill_climb,
                           minimum_elevation,maximum_elevation,
                           
                           name,kind,device,equipment,
                           description,
                           is_clockwise,score,
                           
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
        values ( ?, ?, ?, ?, ?,
                 ?, ?, ?,
                 ?, ?, ?,

                 ?, ?,
                 ?,

                 ?, ?, 
                 ?, ?,
                 ?, ?,
                 ?, ?,

                 ?, ?, ?, ?, 
                 ?,  
                 ?, ?,

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