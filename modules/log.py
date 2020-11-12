#!/usr/bin/env python 
# coding: utf8


"""
logger.py,v 1.0 2016/05/12

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
import os
import logging

class LOG(object):
    '''
    Called in "complete_extract"
    It produces a logfile 'processing.log'.
    The logfile contains all the steps of the consecutive processings
    Parameters : 
        * asctime : 
        * name : 
        * levelname : 
        * message : 
    '''
    def __init__(self):
        pass
    def logging(self, asctime=True, name=False, levelname=False, message=True):
        '''
        '''
        logfile = os.path.join(self.folder,'processing.log')
        print("path for logfile is ", logfile)
        if os.path.exists(logfile):
            os.remove(logfile)
        # http://stackoverflow.com/questions/18786912/get-output-from-the-logging-module-in-ipython-notebook
        # https://docs.python.org/2/howto/logging.html
        self.logger = logging.getLogger()
        fhandler = logging.FileHandler(filename=logfile, mode='a')
        dicmess = {'asctime' : asctime, 'name' : name, 'levelname' : levelname, 'message': message}
        logmess = ''
        for step in [ 'asctime', 'name', 'levelname', 'message']:
            if dicmess[step]:
                logmess += ' %('+step+')s - '
        logmess = logmess[:-3]
        formatter = logging.Formatter(logmess)
        fhandler.setFormatter(formatter)
        self.logger.addHandler(fhandler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.folder = self.folder

