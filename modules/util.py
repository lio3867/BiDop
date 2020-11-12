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
from colorama import Fore, Back, Style
from time import localtime, strftime, time, sleep


class UTIL(object):
    '''
    '''
    def __init__(self):
        pass

    

    def init_count(self):
        '''
        Stores the number of groups processed in nbfolders.txt
        '''
        with open('nbfolders.txt', 'w') as nb:
            mess = "0/{0}".format(self.number_of_groups)
            nb.write(mess)
            
    def count_folder(self, path, number_of_groups):
        '''
        Counting number of folders in path
        '''
        countdir = 0
        with open('nbfolders.txt', 'w') as nb:
            for root, dirs, files in os.walk(path):
                    countdir += len(dirs)
            mess = "{0}/{1}".format(countdir, number_of_groups)
            print(mess)
            nb.write(mess)

    def pr(self, mess0, mess1=None, col=''):
        '''
        Print in sys.stdout and in the logging file.
        Parameters:
            * mess : message
            * col : color in the console
        '''
        print(col + mess0)
        try:
            self.logger.info(mess0)
        except:
            print('Possibly logger not defined')
        if not mess1:
            mess1 = mess0 # duplicate
        try:
            self.r.write(mess1 + ' \n')
        except:
            print("can't write in {0}".format(mess1))
    
    def datetime(self):    
        '''
        Time: year, month, day, hour, minute
        '''
        tag_date = strftime('%y%m%d_%H%M', localtime()).replace('.','')
        return tag_date

    def debug_col(self, mess, col):
        '''
        Show colored messages
        '''
        dic_col = {'g':Fore.GREEN, 'b':Fore.BLUE, 'r':Fore.RED, 'y':Fore.YELLOW}
        print(dic_col[col] + mess)  # 
        print(Style.RESET_ALL)

        