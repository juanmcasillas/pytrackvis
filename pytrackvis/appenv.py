##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // appenv.py 
# //
# // Creates a global object with the configuration and some global elements
# // if needed, to avoid the use of globals in the configuration.
# //
# // 21/02/2024 08:31:37  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import json
import os
import os.path

class AppEnvConfig:
    "must match exactly the json file"
    def __init__(self, **kwargs):

        self.verbose = 0
        self.api_key_file = "tokens.ini"


        if kwargs:
            for key,value in kwargs.items():
                self.__dict__[key] = value

    def validate(self):
        pass




class AppEnv:
    __conf = AppEnvConfig() # default init

    @staticmethod
    def config(fname=None):
        if not fname:
            return AppEnv.__conf
        else:
            try:
                with open(fname) as json_data_file:
                    data = json.load(json_data_file)
                    #data = json.load(json_data_file, object_hook=lambda d: SimpleNamespace(**d))
                    AppEnv.__conf = AppEnvConfig(**data)
                    AppEnv.__conf.validate()
                    AppEnv.__conf.config_dir = os.path.dirname(fname)
                    AppEnv.__conf.config_file = os.path.basename(fname)
                    return AppEnv.__conf
            except Exception as e:
                raise Exception(e) from e
    
    @staticmethod
    def config_set(var, value):
        AppEnv.__conf.__dict__[var] = value
        return AppEnv.__conf
    
    @staticmethod
    def print_config():
        print("AppEnv Configuration")
        for i in AppEnv.__conf.__dict__.keys():
            print("  %s: %s" % (i, AppEnv.__conf.__dict__[i]))
    
def APPENVCONFIG():
    "syntactic sugar for the other modules"
    return AppEnv.config()


def test_config():

    APPENVCONFIG()
    AppEnv.config("config/pytrackvis.json")
    AppEnv.print_config()

if __name__ == "__main__":

    test_config()