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

class COM(object):
    '''

    '''
    def __init__(self):
        pass

    def format_interv(self, interv):
        '''
        Format the intervalls for "all_processing_infos"
        '''
        interv = "".join(str(interv).split(' '))
        interv = interv.replace(',', ' ')[1:-1]
        return interv

    def dic_comments(self):
        '''
        Read the comment file remarks.csv
        and fill the dictionary self.infos_group for each well
        '''
        path_comment_file = os.path.join(os.path.dirname(self.addr), 'remarks.txt')
        print("###### searching the comment file at address {0} ".format(path_comment_file))
        with open(path_comment_file, 'r') as f:
            for l in f.readlines():
                print("line is ",l)
                ls = l.split()
                w, comment  = ls[0], ' '.join(ls[1:])
                sgrp = self.from_well_to_group(w).split('_')
                numgrp = int(sgrp[1])
                numidx = int(sgrp[2])
                self.infos_group[numgrp][numidx]['comment'] = comment
            
    def save_all_processing_infos(self, debug=0):
        '''
        Dictionary for conserving in "dict_all_infos.csv" all the informations for each well processed.
        '''
        try:
            self.dic_comments()  # make the dictionary for the comments
        except:
            print('###### no comment file found !!! ')
        with open(os.path.join(self.folder,'dict_all_infos.csv'), 'w') as d:
            d.write('{0},{1},{2},{3},{4},{5},\
                        {6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},\
                        {19},{20},{21},{22},{23},{24},{25},\n'.format('well', 'molec',
                                                 'group', 'index', 'BI_position',
                                                 'BI_zone', 'BI_error', 'pdz_pos', 'pdz_int',
                                                 'ref_int', 'max_2nd_corr', 'max_2nd_pos', 'y_dilation',
                                                 'norm_pos', 'norm_int', 'range_norm',
                                                 'range_anal', 'range_2nd_corr',
                                                 'iter', 'nbchunks', 'speed',
                                                 'translX,dilatX, dilatY', 'validated', 'reprocessed', 'comments', 'additionnal_comments'))   # First line

            ## ,{25}  , 'additionnal_comments'
            print(Fore.YELLOW + '#################### resulting_params_adjust !!!!!!!!!!!!!!!!!!!!!! ', self.resulting_params_adjust)
            print(Style.RESET_ALL)
            for w in self.dic_wells:                                     # Reading all the wells
                try:
                    BIp = self.dic_wells_BIp[w]                          # Passing from well to BI position
                    BIz = self.dic_wells_BIz[w]                          # Passing from well to BI zone
                except:
                    BIp = 'not_calculated'
                    BIz = 'not_calculated'

                molec = self.dic_wells[w]                                # residue for which we calculate the BI
                sgrp = self.from_well_to_group(w).split('_')
                numgrp = int(sgrp[1])
                numidx = int(sgrp[2])
                if len(sgrp[1]) == 1:
                    sgrp[1] = '0' + sgrp[1]
                grp = sgrp[0] + '_' + sgrp[1]                            # group
                idx = sgrp[2]                                            # index in group 
         
                elem = self.infos_group[numgrp][numidx]
                if debug>0: print("elem.keys() ", elem.keys())           # print all the keys

                try:
                    dilaty = elem['dilaty']                              # Indicating if dilation in along y or not
                except:
                    dilaty = 'n'
                try:
                    pdz_pos = elem['pdz_pos']                            # pdz position
                except:
                    pdz_pos = 'None'
                try:
                    pdz_int = elem['pdz_int']                            # pdz intensity
                except:
                    pdz_int = 'None'
                try:
                    ref_int = self.infos_group[numgrp][numidx]['ref_int']        # reference intensity
                except:
                    ref_int = 'None'
                try:
                    norm_pos = self.infos_group[numgrp]['norm_pos']      # normalization peak position
                except:
                    norm_pos = 'None'
                try:
                    norm_int = self.infos_group[numgrp]['norm_int']      # normalization peak intensity
                except:
                    norm_int = 'None'

                ##### ranges

                range_norm = self.format_interv(self.interv_normalize)   # Formatting normalization interval
                range_anal = self.format_interv(self.interv_analysis)    # Formatting analysis interval

                ##### baseline

                nbchunks = self.nbchunks
                nbiter = self.nbiter
                speed = self.secondpower

                ##### secondary correction

                iav = self.interv_adjust_vert   
                range_2nd_corr = str(iav[0]) + ' ' + str(iav[1])  # Second corr range
                try:
                    max_2nd_corr = elem['max_2nd_corr']           # value max in vertical correction zone.
                except:
                    max_2nd_corr = 'None'
                try:
                    max_2nd_pos = elem['max_2nd_pos']             # position max in vertical correction zone.
                except:
                    max_2nd_pos = 'None'

                ##### flags

                validated = 'y'
                reproc_status = '_'

                ##### BI error

                try:
                    BIerr = elem['BI']['position']['error']
                except:
                    BIerr = 'None'

                ##### Comments

                try:
                    comment = elem['comment']
                except:
                    comment = '_'

                #####

                ladj = ['translat', 'dilat', 'transfvert']
                adj_params = ''
                for adj in ladj:
                    try:
                        adjust_done = self.resulting_params_adjust[numgrp][numidx][adj]
                    except:
                        adjust_done = 'None'
                    adj_params += str(adjust_done)+', '
                adj_params = adj_params[:-1]                       # adjustment coefficients

                corresp = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13},\
                       {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21} {22}, {23}, {24}  \n'.format(w, molec, grp, idx,
                                 BIp, BIz, BIerr, pdz_pos, pdz_int, ref_int, max_2nd_corr, max_2nd_pos, dilaty,
                                 norm_pos, norm_int, range_norm, range_anal, range_2nd_corr,
                                 nbiter, nbchunks, speed, adj_params, validated, reproc_status, comment )  # Building the new  line
                d.write(corresp)           # Writing a new line

    def save_dic_wells(self, defect=False):
        '''
        Dictionary for establishing the link between wells, molecular interactions names, groups and BIs
        '''
        print(self.dic_wells_BIp)
        last_well =  list(self.dic_wells.items())[-1][0]
        with open(os.path.join(self.folder,'dict_wells.csv'), 'w') as d:
            d.write('{0} , {1} , {2}, {3}\n'.format('well', 'molec', 'group_with_index', 'BI'))   # First line
            d.write('last_well, {0}\n'.format(last_well))                                         # Second line
            for w in self.dic_wells:
                try:
                    BI = self.dic_wells_BIp[w]
                except:
                    BI = 'not_calc' # 'not_calculated'
                if defect : 
                    BI = "defect"
                corresp = '{0} , {1}, {2}, {3} \n'.format(w, self.dic_wells[w], self.from_well_to_group(w), BI ) 
                d.write(corresp)           # Writing a new line

                