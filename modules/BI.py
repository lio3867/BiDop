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
import numpy as np
from .plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400 # good width seems to be 400
plt.plot_height = 400 # good height seems to be 400
from colorama import Fore, Back, Style
from time import time
import os, sys
sys.path.append('/home/meglio/Bureau/bitbuck/')
from modules.BC import correctbaseline

class BI(object):
    '''
    '''
    def __init__(self):
        pass


    def BI_compare_with_old_data(self, plt, lbinewproc, lbioldproc, list_noise, tbeg, debug=0):
        '''
        Comparison of the BIs with data from Nature paper.
        '''
        tend = time()
        if debug>0:
            print("lbinewproc ", lbinewproc)
            print("lbioldproc ", lbioldproc)
        lbinewproc = np.array(lbinewproc)     # list BI new processing
        lbioldproc = np.array(lbioldproc)     # list BI old processing
        self.pr('''

                ####  Full Processing time : {0} s ####

                '''.format((round(tend-tbeg,2))))
        ####### Plots ####
        try:
            if comparison :
                self.plotBI(plt, list_noise, lbioldproc, lbinewproc)        # Plot comparison old new with indices
                self.plotBIcorrelations(plt, lbioldproc, lbinewproc)        # Plot correlation between old method and new method
        except:
            print("can't make comparison")


    def BI_message(self, jref, j2):
        '''
        Binding Index printed with interacting molecules names
        '''
        inter1 = self.infos_group[self.nbgroup][jref]['mol_interact']
        inter2 = self.infos_group[self.nbgroup][j2]['mol_interact']
        print('''

### BI calculated with reference {0} and PDZ {1}

             '''.format(inter1, inter2))

    def BI(self, plt, jref, j2,  kind="zone", plot=False, debug=0):
        '''
        Binding Index calculation
        jref : index of the reference
        j2 : index of the target
        Parameters :
            * jref : reference profile
            * j2 : profile to be processed
            * kind :
                - zone, BI calculation by taking the max on a given zone [self.analinf, self.analsup]
                - position, BI calculation by taking the max on a big peak of reference, then searching for value of the second peak at the same position in mass.
            * plot :
            debug : activate debug mode if True
        '''
        elem = self.infos_group[self.nbgroup]
        inter1 = elem[jref]['mol_interact']
        inter2 = elem[j2]['mol_interact']
        x = elem[jref]['x']

        if debug>0:
            print("analysis interval ", self.analinf, self.analsup)
            print("elem[jref]['y'].size", elem[jref]['y'].size)
            print("elem[j2]['y'].size", elem[j2]['y'].size)
        if plot:
            plt.plot(x, elem[jref]['y'], 'k-')
            plt.plot(x, elem[j2]['y'], 'r-')
            plt.show()
        ll = np.where((x > self.analinf) & (x < self.analsup))
        s1 = elem[jref]['y'][ll]
        s2 = elem[j2]['y'][ll]
        s2x = elem[j2]['x'][ll]
        s1x = elem[jref]['x'][ll]
        if debug>0:
            print("noise is ", elem['noise'])
        try:
            dI = self.infos_group[self.nbgroup]['noise']
        except:
            dI = None
        elem[j2]['BI']['interval'] = [self.analinf, self.analsup]
        if kind == 'zone':
            if debug>0:
                print("s1.max(), s2.max() ", s1.max(), s2.max())
            BI = round((s1.max()-s2.max())/s1.max(), 4)                    # BI calculation zone method
            if j2 == jref:
                BI = "ref"
            if debug>0:
                print(Fore.RED + "BI_zone : {}".format(BI))
                print(Style.RESET_ALL)
            if dI : dBI = round(((s2.max()+s1.max())/s1.max()**2)*dI, 3)              # Error propagation (BI zone)
            elem[j2]['BI']['zone'] = {'value': BI, 'error': dBI, 'compared_with': inter1}
        elif kind == 'position':
            if debug>0:
                print("s1.max(), s2[s1 == s1.max()]", s1.max(), s2[s1 == s1.max()])
            BI = round(((s1.max()-s2[s1 == s1.max()])/s1.max())[0], 4)          # BI calculation position method
            if j2 == jref:
                BI = "ref"
            # self.refmax = s1.max()
            # self.molecmax = s2.max()
            if debug>0:
                print(Fore.RED + "BI_position : {}".format(BI))
                print(Style.RESET_ALL)
            if dI : dBI = round((((s2.max()+s1[s1 == s1.max()])/s1.max()**2)*dI)[0], 3)     # Error propagation (BI position)
            elem[j2]['BI']['position'] = {'value': BI, 'error': dBI, 'compared_with': inter1}
            # print("##### elem[j2] before", elem[j2])

            # print("##### elem[j2] after ", elem[j2])
            print("elem[j2].keys() ", elem[j2].keys())

        if dI: elem[self.j2]['dBI'] = dBI #
        if debug>0:
            print('dBI is ', dBI)


        ####

        # elem['pdz_pos'] = s2x[s1 == s1.max()]
        # elem['pdz_int'] = s2[s1 == s1.max()]
        # elem['ref_int'] = s1.max()

    def extractBIs(self, plt, jref, j2):
        '''
        Calculation of BI position and BI zone.
        Parameters:
            * jref: index of the reference
            * j2 index of the target
        '''
        #t0 = time()
        self.noise_estimate(plt, j = jref)                   # Noise estimation for BI calculation
        self.BI_message(jref, j2)
        self.BI(plt, jref, j2, kind = 'zone')                # caculate the BI with zone method
        self.BI(plt, jref, j2, kind = 'position')            # caculate the BI with position method
        elem = self.infos_group[self.nbgroup]
        valpos = elem[j2]['BI']['position']['value']
        valzone = elem[j2]['BI']['zone']['value']
        # self.logger.info('''
        #
        # #### Binding index ####
        # ''')
        self.pr('''

        ### Binding index ###

        ''', '\n### Binding index \n')
        messpos =  "    * BI (position) : {0} ".format(valpos)
        messzone =  "    * BI (zone) : {0} ".format(valzone)
        self.pr( 'BIs', '* BIs ::', col=Fore.RED)
        self.pr( messpos, col=Fore.RED)
        self.pr( messzone, col=Fore.RED)
        print(Style.RESET_ALL) # Resetting colors
        t1 = time()
        self.timings['noise and BI'] = round(t1-self.tt0, 4)

    def plotBI(self, plt, list_noise, lbioldproc, lbinewproc):
        '''
        Plot the bonding indices from Nature method and new method
        Parameters:
            * list_noise : list of the noise rms from the tail of the spectra
            * lbioldproc : list of the BIs obtained with the old processing
            * lbinewproc : list of the BIs obtained with the new processing (the herein program).
        '''
        #### BIs comparisons
        path = 'file://' + os.getcwd()
        ll = [os.path.join(path, self.folder,"processing_nbgroup_{0}.html".format(i+1)) for i in range(lbinewproc.size)]
        plt.figure(show=False)
        ####
        plt.plot_width = 1000
        plt.plot_height = 300
        ####
        self.plot_noise_error(plt, list_noise, lbioldproc, lbinewproc) # Plot error bars, begins at 1
        plt.plot(1+np.arange(lbinewproc.size), lbinewproc, 'r*', label='new processing', tap=None) # BI new processing, tap = ll if interactions required
        if lbioldproc.size > 0:
            plt.plot(1+np.arange(lbioldproc.size), lbioldproc, 'k*', label='old processing') # BI old processing
            plt.title('New vs old processing')
        #########
        plt.xlabel('group index')
        plt.ylabel('Binding Index')
        plt.xlim(-1,lbinewproc.size+1)
        plt.ylim(-0.3,1)
        plt.show()
        plt.savefig(os.path.join(self.folder, 'BI_comparison.html'))

    def plotBIcorrelations(self, plt, lbioldproc, lbinewproc):
        '''
        Correlations  between old and new method on data for Nature Method.
        Parameters:
            * lbioldproc : list of the BIs obtained with the old processing
            * lbinewproc : list of the BIs obtained with the new processing (the herein program).
        '''
        #### BI correlations
        plt.figure(show=False)
        plt.plot(lbioldproc, lbinewproc, 'b*', label='correlation') # BI new processing
        maxpt = lbinewproc.max()
        plt.plot([0,maxpt], [0, maxpt], 'k--') # perfect correlation
        plt.title('Correlation between new vs old processing')
        plt.xlabel('old')
        plt.ylabel('new')
        plt.xlim(0,1)
        plt.ylim(0,1)
        plt.show()
        plt.savefig(os.path.join(self.folder,'BI_correlation_old_new.html'))

    def plot_noise_error(self, plt, list_noise, old_processing, new_processing, debug=False):
        '''
        Plot error bars for old_processing and new_processing
        Parameters:
            * list_noise : list of the noise rms from the tail of the spectra
            * lbioldproc : list of the BIs obtained with the old processing
            * lbinewproc : list of the BIs obtained with the new processing (the herein program).
        '''
        lnoisex_old, lnoisey_old = [], []
        lnoisex_new, lnoisey_new = [], []
        for i, n in enumerate(list_noise):
            val_old = old_processing[i]
            val_new = new_processing[i]
            plt.plot([i+1,i+1], [val_old-n,val_old+n], 'k-')
            plt.plot([i+1,i+1], [val_new-n,val_new+n], 'r-')
        if debug:
            print("list_noise ", list_noise)

    def noise_estimate(self, plt, j, plot = False, debug=False):
        '''
        White noise power is estimated with que queue of the signal after flattening it with the baseline tool.
        Parameters:
            * j : index of the spectrum used for estimation of the noise.
            * debug : used for following the convergence of the baseline.
        '''
        ninf, nsup = self.interv_noise_extract[0], self.interv_noise_extract[1]
        x = self.infos_group[self.nbgroup][j]['size_trunc']
        y = self.infos_group[self.nbgroup][j]['val_corr']
        ll = np.where((x > ninf) & (x < nsup))
        xnoisy  = x[ll]
        val_noisy  = y[ll]
        if debug:
            print("val_noisy.size ", val_noisy.size)
        blnoise, blsnoise = correctbaseline(val_noisy, iterations=5, nbchunks=val_noisy.size/5, firstpower=0.3,
                                secondpower=7, degree=1,  chunkratio=1.0,
                                interv_ignore = None, method="Powell",
                                nbcores= 10,
                                debug = True, choiceBL = 0)
        if debug:
            print("val_noisy.size, blnoise.size ", val_noisy.size, blnoise.size)
        val_noisy_corr = val_noisy-blnoise     # corrected spectrum
        self.infos_group[self.nbgroup]['noise'] = val_noisy_corr.std()
        if plot:
            plt.plot(xnoisy, val_noisy_corr)
            plt.plot(x, y)
            if debug:
                print(val_noisy_corr.std())
            plt.show()
