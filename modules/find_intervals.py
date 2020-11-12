#!/usr/bin/env python 
# coding: utf8


"""
find_intervals.py

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
import os, sys
import numpy as np
from .plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400 # good width seems to be 400
plt.plot_height = 400 # good height seems to be 400
from colorama import Fore, Back, Style
from time import time

try:
    from scipy.interpolate import interp1d
    from scipy.optimize import fmin # fmin_powell, fmin_l_bfgs_b, golden, fminbound
except:
    print("Couldn't import scipy libraries")

class FIND_INTER(object):
    '''
    '''
    def __init__(self):
        pass


    def set_interv_analysis(self, inf, sup):
        '''
        Interval used for analysis to be set after automatic detection of moving zone.  
        '''
        self.analinf, self.analsup = inf, sup
        self.interv_analysis = [inf, sup]
    
    def mean_L1(self, l):
        '''
        Find the mean value for the L1 regression.
        Parameters:
            * l : list of the values on which we make the L1 regression
        '''
        x = np.arange(len(l))
        delta1 = lambda param : np.abs(param[0]*x + param[1]-np.array(l)).sum()
        param = [1, 1]
        param_opt = fmin(delta1, param, xtol=1e-8) # L1 minimization
        a1, b1 =  param_opt[0], param_opt[1]
        mean = (a1*x+b1).mean()                    # middle position of the interval
        return mean
    
    def estimate_analysis_interv(self, lmaxchange):
        '''
        Find statistically the "right" analysis interval using L1 norm for elminating outliers.
        Parameters :
            * lmaxchange :
        Output :
            * resulting interval : self.estimated_analysis_interv
        '''
        mean = self.mean_L1(lmaxchange)
        inf, sup = mean-self.delta_analysis, mean+self.delta_analysis
        self.set_interv_analysis(inf, sup)
        print('interval for analysis is [{0},{1}]'.format(inf, sup))
        self.interv_analysis = [inf, sup]
    
    def find_groups_out_of_estimated_interv(self, lmaxchange):
        '''
        Discriminate the groups which are inside the right analysis interval from those which are outside. 
        Parameters :
            * lmaxchange :
        '''
        loutside = []
        linside = []
        interv = [self.analinf, self.analsup]    
        for nbgroup in range(1, self.number_of_groups): # go through all the groups
            if not interv[0] < lmaxchange[nbgroup-1] < interv[1]: # keep the groups which are outside the right interval.
                loutside.append(nbgroup-1)
            else:
                linside.append(nbgroup-1) # keep the groups which are inside the right interval.
        #plt.figure()
        ll = len(lmaxchange)
        x = np.arange(ll)
        plt.plot([0,x.max()], [interv[0]]*2, 'k--')
        plt.plot([0,x.max()], [interv[1]]*2, 'k--')
        plt.plot(np.array(linside) + 1, np.array(lmaxchange)[linside], 'k*') # Good points
        plt.plot(np.array(loutside) + 1, np.array(lmaxchange)[loutside], 'r*') # Bad points
        plt.xlabel('index')
        plt.ylabel('size(kDa)')
        plt.title('confidence zone')
        plt.show()
        plt.savefig('good_analysis_interval.html')
    
    def find_normalization_interval(self, plot=True, number_of_groups=20):
        '''
        Find the interval where to select the maximum peak used for normalization.
        Makes a statistic of the highest peaks and determines by L1 norm which interval
        is the most prone to contain the peak inserted by users for the normalization of all the spectra.
        Parameters:
            * plot : plot for control
            * number_of_groups : number  of groups used for the statistic
        '''
        lmax = []
        t0 = time()
        for nbgroup in range(1, number_of_groups): #c.number_of_groups
            self.nbiter = 2                                   # iterations for the baseline
            self.nbchunks = 100                               # number of segments in the baseline
            self.deg = 1                                      # local polynomial degree 
            for j in range(self.size_groups):                 # go through the whole group
                self.group = self.well_groups[nbgroup]
                self.extract_data(self.group[j])              # Take the jth element in the group.
                self.make_BL()
                print(np.where(self.val_corr == self.val_corr.max())[0])
                posmax = self.size_trunc[np.where(self.val_corr == self.val_corr.max())[0]]
                lmax.append(posmax)                           # make the list of the max
        self.mean = self.mean_L1(lmax)                        # Determine with L1 norm the position of the peak used for normalization.
        t1 = time()
        print('time elapsed is {0} min'.format((t1-t0)/60))
        print('the peak used for normalization is very close to {0}'.format(self.mean))
        self.interv_normalize = [self.mean-5, self.mean+5] # Set the interval for normalization of the spectra.
        print("#### normalization interval is [{0},{1}] ".format(self.mean-5, self.mean+5))
    
    def find_analysis_interval(self, jref=None, number_of_groups = 20):
        '''
        Find the interval for analysis
        Parameters:
            * jref :
            * number_of_groups :
        '''
        lmaxchange = []
        for nbgroup in range(1, number_of_groups): #
            print(nbgroup)
            self.preprocess_group(jref = jref, nbgroup = nbgroup , nbiter=2, nbchunks = 50, deg=1) # Processing : baseline and normalization
            elem = self.infos_group[nbgroup]
            self.translate_and_detect_maxchange(plt, jref=jref, plot=False)      # It is assumed that the dilation is not too strong. 
            m = self.round(elem['xmaxchange'])                   # Position of the maximal change.
            lmaxchange.append(m)
        self.estimate_analysis_interv(lmaxchange)
        self.find_groups_out_of_estimated_interv(lmaxchange)
    
    def find_intervals(self, jref=None, number_of_groups=20):
        '''
        Search for the intervals for normalization and analysis. 
        Parameters:
            * number_of_groups : number of groups on which is done the statistic.
        Output:
            * self.interv_normalize : normalization interval deduced from the statistic
            * self.interv_analysis : analysis interval deduced from the statistic
        
        '''
        print('''
    
                   #######  Find interval for normalization ####### 
    
        ''')
        self.find_normalization_interval(plot=False, number_of_groups=number_of_groups) # Find the interval for normalization
        print('''
    
                   #######  Find interval for analysis ####### 
    
        ''')
        self.find_analysis_interval(jref=jref, number_of_groups= number_of_groups) # Find the interval for analysis

    def retrieve_pos_int(self, nbgroup, jref, j2):
        '''
        Retrieving the informations of positions and intensities for reference and pdz
        Parameters:
            * nbgroup : number of the group
            * jref : index of the reference
            * j2 : index of the target
        '''

        ##### Retrieve pos and int
    
        # sref = self.filter_interp(nbgroup, jref, on_adjust=True)
        # s2 = self.filter_interp(nbgroup, j2, sref['x'], on_adjust=True)
        # sref = self.filter_interp(nbgroup, jref, on_adjust=True)
        # s2 = self.filter_interp(nbgroup, j2, sref['x'], on_adjust=True)
        # ####
        # sref_min = np.where(sref['x'] == s2['x'].min())[0]
        # sref_max = np.where(sref['x'] == s2['x'].max())[0]
        # s = slice(sref_min, sref_max)
        # #sref['x'], sref['y'] = sref['x'][s], sref['y'][s]
        ####
        
        ####
        # srefmax = sref['y'].max()
        # elem['pdz_pos'] = round(s2['x'][sref['y'] == srefmax][0], 2)
        # elem['pdz_int'] = round(s2['y'][sref['y'] == srefmax][0], 0)
        # elem['ref_int'] = round(srefmax, 0)

        elem = self.infos_group[self.nbgroup]
        x = elem[jref]['x'] 
        ll = np.where((x > self.analinf) & (x < self.analsup))
        s1 = elem[jref]['y'][ll]
        s2 = elem[j2]['y'][ll]
        s2x = elem[j2]['x'][ll]
        s1x = elem[jref]['x'][ll]

        elem[j2]['pdz_pos'] = round(s2x[s1 == s1.max()][0], 2)
        elem[j2]['pdz_int'] = round(s2[s1 == s1.max()][0] , 2)
        elem[j2]['ref_int'] = s1.max()

    def check_infos_group(self):
        '''
        Check infos_group values
        '''
        try:
            elem = self.infos_group[nbgroup]
            for jj in range(0,4):
                try:
                    print('jj max_2nd_corr', elem[jj]['max_2nd_corr'])
                except: 
                    print('jj max_2nd_corr not exising')
        except:
            pass

    def take_max(self, elem, j2, debug=0):
        '''
        Take the max in the region between lysozym and BI zone.
        '''

        x = elem[j2]['x']                             # x pdz before adjustment
        iav = self.interv_adjust_vert                 # interval for adjustment
        lll = np.where((x > iav[0]) & (x < iav[1]))
        if debug>0:
            print("self.interv_adjust_vert ", self.interv_adjust_vert)
            # print('x ', x)
            # print('lll ', lll)
        max_sec = elem[j2]['y'][lll].max()
        self.infos_group[self.nbgroup][j2]['max_2nd_pos'] =\
                round(elem[j2]['x'][lll][elem[j2]['y'][lll] == max_sec][0],2)  # position of the max between lyzo and analysis
        print(Fore.RED+"##### self.infos_group[self.nbgroup][j2]['max_2nd_pos'] ", self.infos_group[self.nbgroup][j2]['max_2nd_pos'])
        print(Style.RESET_ALL)

        self.infos_group[self.nbgroup][j2]['max_2nd_corr'] = round(elem[j2]['y'][lll].max(), 0)         # Max in interval between lyso and analysis
        if debug>0: print("self.infos_group[self.nbgroup][j2].keys() ", self.infos_group[self.nbgroup][j2].keys())
        