#!/usr/bin/env python
# encoding: utf-8

"""
 run.py,v 1.0 july 2016
 Flask interface for launching a processing with "bindings_extract.py" and visualize the results and processing steps.
 When launched, the program automatically opens a Chrome navigator. 

 *******************************************************************
 *
 * Copyright (c) 2016
 * Casc4de
 * Le Lodge, 20 Av du neuhof , 67100 Strasbourg, FRANCE
 *
 * All Rights Reserved
 *
 *******************************************************************
"""

import sys, os, shutil, time, json, pickle
import os.path as op
import subprocess
from time import sleep
from colorama import Fore, Back, Style
sys.path.append('Interf')

#########

from threading import Thread
import configparser

####

Debug = True

config = configparser.ConfigParser()  # Used for the default parameters

######### Eventlet for websocket

import eventlet
eventlet.monkey_patch()   

######### Flask

from flask import Flask, render_template,request,\
			redirect, url_for, session
## Flask Socket io
from flask_socketio import SocketIO, send, emit
### 
from .Interf_modules import ask_data as af 
from .Interf_modules.processing import proc, proc_ask_params, read_params_proc
from .Interf_modules import reprocess 
from .Interf_modules.postcomments import  modify_dict_wells, modify_dict_all_infos, make_postcomments, save_wrong_wells
from .Interf_modules.visualisation import visualisation, superp_plots, check_current_well, save_current_well
from .Interf_modules.manage_thread import bckgrd_thread, stopthread
from .Interf_modules.selection import select_action
from .Interf_modules.server import shutdown_server
from .Interf_modules.session import init_session
from .Interf_modules.initializing import init_state
from .Interf_modules.define_all_pages import *

from run_code.handle_processing import handle_processing
from run_code.current_state import current_state
from run_code.visu import visu

### Instantiate and configure Flask
app = Flask(__name__, static_url_path='/static')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'F34TF$($e34D';
socketio = SocketIO(app)                    # Flask websocket, used for following the processings etc..

def background_thread():
    '''
    Background task for following the processing
    It reads information about processing in nbfolders.txt
    Called by index()
    '''
    bckgrd_thread(socketio)

@socketio.on('message', namespace='/follow_proc')
def stopThread(message):
    '''
    Called at the end of the processing
    '''
    stopthread(message)

@socketio.on('comment', namespace='/plate_comm')
def make_comments(message):
    '''
    Retrieving comment from client.
    '''
    make_postcomments()

### Initialization of the Interface
@app.route('/')
def index():
    '''
    Interface first page.
    '''
    init_state()
    init_session(app)                         # Load all the basic parameters for the session
    dfp = define_firstpage()
    return render_template('firstpage.html', **dfp.__dict__)  

handle_processing(app, define_follow_processing, proc, 
         select_action, background_thread, define_select_proc_visu, 
         af, proc_ask_params, config, define_ask_param, socketio,
         read_params_proc )

current_state(socketio, check_current_well, 
          save_current_well, save_wrong_wells)

visu(app, socketio, define_make_plate, define_visu,
                 visualisation, reprocess, superp_plots)
    
@app.route('/documentation')
def documentation():
    '''
    Documentation about bindings_extract.py
    '''
    dd = define_documentation()
    return render_template('documentation.html', **dd.__dict__)
  
@app.route('/shutdown', methods = ['POST'])
def shutdown():
    '''
    Shutting down the server.
    '''
    shutdown_server(request)
    return 'Server shutting down...'

if __name__ == '__main__':
    import threading, webbrowser
    b = webbrowser.get("open -a /Applications/Google\ Chrome.app %s")  # Using Google Chrome browser
    port = 5012 
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: b.open_new(url)).start() # open a page in the browser. , new=1
    app.run(port = port, debug = Debug, use_reloader = False)
    socketio.run(app)
