#!/usr/bin/env python 
# coding: utf8


"""
groups_wells.py

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
import numpy as np
from colorama import Fore, Back, Style
from time import time
import json

class GW(object):
    '''
    '''
    def __init__(self):
        pass

    def from_well_to_group(self, well):
        '''
        Passing from well position to group and index in group
        '''
        for g in self.well_groups :
            if well in g:
                return 'grp_{0}_{1}'.format(self.well_groups.index(g)+1, g.index(well))

    def make_default_groups(self, debug=0):
        '''
        Make groups 2x2 squares in the plate.
        Result : self.well_groups
        '''
        self.plate = np.array([j+str(i+1) for i in range(self.gr_nbcol) for j in self.lalpha]) # all combinations A1, A2, etc..
        self.plate = np.reshape(self.plate,(self.gr_nbcol, self.gr_nbline)).T # Reshape
        self.well_groups = [list(self.plate[i:i + self.shape_groups[0], j:j + self.shape_groups[1]].flatten())
                            for i in range(0, self.gr_nbline, self.shape_groups[1]) for j in range(0, self.gr_nbcol, self.shape_groups[0])] # groups with wells
        if debug>0: print(self.well_groups)

    def make_groups_with_adhoc_plate(self, path_geom, debug=0):
        '''
        Make the groups from plate_grp_geom.json file
        Result : self.well_groups
        '''
        print('##### Using plate group geom !!! ')
        self.well_groups = []                              # Dictionary of groups as list of wells
        with open(path_geom, 'r') as json_data:
            dic_plate_geom = json.loads(json_data.read())  # Load the json file
        for k,v in sorted(dic_plate_geom.items()):
            if debug>0: print('###### k: {0}, v: {1} '.format(k,v))
            subgroup = []
            if debug>0: print(type(v))
            for kk, vv in v.items():
                if debug>0: print('###### kk: {0}, vv: {1} '.format(kk,vv))
                if vv != 'ref':
                    subgroup.append(kk)           # if not ref, append
                    print(subgroup)
                else:
                    ref = kk                      # if ref, append
                    print('ref is ', ref)
            subgroup.append(ref)                  # putting the ref at the end
            self.well_groups.append(subgroup)
        if debug>0: print('######### ########## self.well_groups ', self.well_groups)

    def _make_groups_wells(self, debug=0):
        '''
        Make a list of groups of wells for a unique rectangular shape of the groups in the plate.
        This step uses self.gr_nbline, self.gr_nbcol : number of lines and columns for each group. 
        The groups of wells is saved in the list self.well_groups
        If no plate_grp_geom.json, use the default 2 by 2 groups of wells
        '''
        path_geom = 'plate_grp_geom.json'
        if os.path.exists(path_geom):
            self.make_groups_with_adhoc_plate(path_geom)   # adhoc groups
        else:
            self.make_default_groups()     # 2x2 groups default

    def make_wells_molec_dic(self, debug=0):
        '''
        Make the correspondences between wells and molec.
        Information in Interf/static/dict_well_molec.csv
        '''
        self._make_groups_wells()               # Make the groups
        for w in list(self.plate.flatten()):
            self.extract_data(w)
        last_well =  list(self.dic_wells.items())[-1][0]
        with open('Interf/static/dict_well_molec.csv', 'w') as f:
            f.write('well, molec\n')
            f.write('last_well, {0}\n'.format(last_well))
            for w,m in self.dic_wells.items():
                f.write('{0}, {1}\n'.format(w,m))
        if debug>0: print('File Interf/static/dict_well_molec.csv has been done.s')


