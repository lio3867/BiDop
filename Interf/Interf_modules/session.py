#!/usr/bin/env python
# encoding: utf-8
"""
session.py
Initialize the session.
"""
import os
import os.path as op
from flask import session

basic_proc_config = '''
[DATA]
data_folder : None

'''

def make_proc_config(addr):
    '''
    Creates a default configuration file in "instance" folder if no config file exists. 
    '''
    print("Makes the default config file in 'instance' folder ")
    if not os.path.exists(addr):
        print("no config file found so make it")
        with open(addr, 'w') as f:
            f.write(basic_proc_config)
            
def init_session(app):
    '''
    Principal route
    block_proc : blocks the launching of the processors via multiprocessing
    results_folder : directory where are saved the processed datasets.
    proc_config_addr : addresse where is saved the configfile for processing "proc_config.cfg"
    '''
    session['valid'] = None

    
