#!/usr/bin/env python
# coding: utf8


"""
proc.py

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
import os, sys, glob, json
from time import time
from copy import deepcopy
from colorama import Fore, Back, Style
sys.path.append('/home/meglio/Bureau/bitbuck/')
import numpy as np
### Plots
from .plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400                    # good width seems to be 400
plt.plot_height = 400                   # good height seems to be 400
from matplotlib import pyplot as mplt
import subprocess
import pickle

class REPROC(object):
    '''
    Reprocess the group
    '''
    def __init__(self):
        pass

    def modify_dict_well(self, grp_dic_wells_targ, grp_dic_wells_proc, debug=0):
        '''
        Modifying the dict_well.csv file
        '''

        with open(grp_dic_wells_targ, 'r') as targ:                        # File dict_wells.csv in which to make corrections
            lines = targ.readlines()
        if debug>0: print(lines)
        for i, ltarg in enumerate(lines):                                  # Replacing the BI value in the resutling processing file..
            if debug>0: print('##### ##### ', ltarg)
            with open(grp_dic_wells_proc, 'r') as src:                     # Reprocessed dict_wells.csv
                for lsrc in src.readlines():
                    if debug>0: print('##### ## ', lsrc)
                    if lsrc[:10] in ltarg:                                 # If lsrc[:10] is in the target
                        lines[i] = lsrc
        with open(grp_dic_wells_targ, 'w') as targ:                        # Rewriting dict_wells.csv with corrections
            for l in lines:
                targ.write(l)

    def modify_all_infos(self, grp_dic_all_infos_targ, grp_dic_all_infos_proc, debug=0):
        '''
        Modifying the dict_all_infos.csv file
        '''

        with open(grp_dic_all_infos_targ, 'r') as targ:                    # File dict_all_infos.csv in which to make corrections
            lines = targ.readlines()
        if debug>0: print(lines)
        for i, ltarg in enumerate(lines):                                  # Replacing the BI value in the resutling processing file..
            if debug>0: print('##### ##### ', ltarg)
            with open(grp_dic_all_infos_proc, 'r') as src:                 # Reading lines of the reprocessed csv file...
                for lsrc in src.readlines():
                    if debug>0: print('##### ## ', lsrc)
                    if lsrc[:10] in ltarg and not 'norm_pos' in ltarg :     # If lsrc[:10] is in the target, avoid the first line
                        linereproc = ' '.join(lsrc.strip().split()[:-1]) + ' y \n'
                        lines[i] = linereproc                               # Replacement and add 'y' for reprocessed

        with open(grp_dic_all_infos_targ, 'w') as targ:                     # Rewriting dict_all_infos.csv with corrections
            for l in lines:
                targ.write(l)

    def cleaning_after_reprocess(self, grp_proc_bl, grp_proc_dil, grp_proc_p, target_folder, source_folder, debug=1):
        '''
        Copying and erasing after reprocessing
        '''
        cmd = 'cp -R '+ grp_proc_bl + ' ' + grp_proc_dil + ' ' + grp_proc_p + ' ' + target_folder # + grp_copy_dil + ' '    # Copy reprocessed data
        if debug>0: print('######### Copying the reprocessed datasets ', cmd)
        subprocess.call(cmd, shell = 'True')                                     # Replacing data in the original folder
        subprocess.call('rm -R ' + source_folder, shell = 'True')              # Remove the folder containing the reprocessed data

        self.debug_col(' ############  Copy/Removed launched ', 'r')

        if debug>0:
            print("###### folder in which are the files", source_folder)
            print("###### target folder ", target_folder) #
        with open('reprocessing_done.p', "w") as f:                              #  indicates reprocessing done
            json.dump('', f)
            print("#### wrote the file tag reprocessing_done.p !!! ")

    def after_reprocess(self, par, init, debug=1):
        '''
        Reprocess the group
        '''
        try:                                                                           # Copy and erase data for the single reprocessing.
            if par['root']:                                                            # par['root'] means local Reprocessing
                reprocessed  = True

                ########  Preparing the addresses

                if debug>0:
                    print('###### in after_reprocess !!!!! ')
                    print('################# subgroup elements are : ', self.list_elems_in_grp)
                source_folder = init.folder
                if debug>0: print('######### group  is  ', par['grp_elem'])
                target_folder = os.path.join('Interf', par['root'][1:])                                                     # folder in which we want to change the processing of the group  .encode('utf-8')
                grp_elem = par['grp_elem']

                self.debug_col(' ############  Reproc working until here', 'y')

                if debug>0: print('##### group elem ', grp_elem)
                grp_spl = grp_elem.split('_')
                grp_proc_bl = os.path.join(source_folder, 'proc_grp_' + grp_spl[1])                                         # Group proc baseline
                grp_elem_base =  grp_elem.split('_')[0]+ '_' + grp_elem.split('_')[1] + '_'
                grp_proc_dil = ''
                grp_proc_p = ''

                for i in self.list_elems_in_grp:
                    grp_proc_dil +=  os.path.join(source_folder, 'proc_{0}_dilat.html '.format(grp_elem_base + str(i)))     # Group proc dilation
                    grp_proc_p +=  os.path.join(source_folder, 'proc_{0}_dilat.p '.format(grp_elem_base + str(i)))          # Group proc dilation pickle
                if debug>0:
                    print('##### grp_proc_dil ',  grp_proc_dil)
                    print('##### grp_proc_p ',  grp_proc_p)
                ##
                grp_dic_wells_targ = os.path.join(target_folder, 'dict_wells.csv')             #   dict_wells.csv with new information
                grp_dic_wells_proc = os.path.join(source_folder, 'dict_wells.csv')             #   dict_wells.csv with old information
                ##
                grp_dic_all_infos_targ = os.path.join(target_folder, 'dict_all_infos.csv')     #   dict_all_infos.csv with new information
                grp_dic_all_infos_proc = os.path.join(source_folder, 'dict_all_infos.csv')     #   dict_all_infos.csv with old information

                self.debug_col(' ############  Addresses are made ', 'g')

                ### Modify the informations

                self.modify_dict_well(grp_dic_wells_targ, grp_dic_wells_proc)
                self.modify_all_infos(grp_dic_all_infos_targ, grp_dic_all_infos_proc)
                self.cleaning_after_reprocess(grp_proc_bl, grp_proc_dil, grp_proc_p, target_folder, source_folder) # Delete the data
                print("##### Reprocessing is OK ")

        except:
            print("par['root'] not existing so no reprocessing !!!" )
