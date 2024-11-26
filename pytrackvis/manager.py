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
        files = glob_filelist(files)
        for fname in files:
            fm = FileManager([fname])
            fm.load(optimize_points=self.config.points["optimize"],
                    filter_points=self.config.points["filter"]
                    )
            self.logger.info("file loaded %s" % fname)
            track = fm.track()
            if track._optimizer:
                self.logger.info("Optimizer results (points): %s" % track._optimizer)