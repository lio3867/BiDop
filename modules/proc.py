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
import os, sys, glob
from time import time
from copy import deepcopy
from colorama import Fore, Back, Style
sys.path.append('/home/meglio/Bureau/bitbuck/')
import numpy as np
### Plots
from .plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400                     # good width seems to be 400
plt.plot_height = 400                    # good height seems to be 400
from matplotlib import pyplot as mplt

class PROC(object):
    '''

    '''
    def __init__(self):
        pass

    def preprocess_and_adjust(self, nbgroup, jref, j2, max_line=True, debug=0):
        '''
        Making translation and dilation adjustments for a given element j2 in the group.
        First make the preprocessing f all the element of the group. Then make the translation, dilation on y, dilation on x.
        Parameters:
            * nbgroup : group targeted
            * jref : reference
            * j2 : spectrum to be corrected in the group
            * max_line : if True plot the line indicating the maximum of the ref and j2
        Calls "preprocess_group"
            which is calls "preprocess_profile"
        Called by complete_extract
            which is called by calc_BI_complete
        '''
        self.tt0 = time()
        nbgroup = int(nbgroup)

        print('in preprocess_and_adjust')
        self.check_infos_group()

        self.pr('''

                             ########### nbgroup {0}  ########

            '''.format(nbgroup), '\n## num group {0} '.format(nbgroup))

        print("jref is ", jref)
        print("j2 is ", j2)
        print("self.preprocessed ", self.preprocessed)
        #self.interv_adjust = [10, 100]                       # Avoid edges which induce a bug for translation adjustment
        if not self.preprocessed:
            print("######  preprocessing !!!!! ")
            self.preprocess_group(jref=jref, nbgroup=nbgroup)     # Preprocessing : baseline and normalization, calls preprocess_profile

            infosbaseline0 = '''Baseline parameters:
                                iterations : {0}
                                nbchunks : {1}
                                secondpower : {2}
                                polynomial degree : {3}
                    '''.format(self.nbiter, self.nbchunks, self.secondpower, self.deg)
            infosbaseline1 = '''* Baseline parameters::
        * iterations : {0}
        * nbchunks : {1}
        * secondpower : {2}
        * polynomial degree : {3} '''.format(self.nbiter, self.nbchunks, self.secondpower, self.deg)
            self.pr('''

            #### Preprocessings plots ####

            ''', '### Preprocessing'
            )
            print("in preprocess_and_adjust make the plot for preprocesing")
            if j2 == 0: #
                self.pr(infosbaseline0, infosbaseline1)                                  # Informations about the Baseline processing.
                self.pr('Steps', '* Steps ::')                                           # Informations about the Baseline processing.
            #if self.save_baseline:
            self.plot_all_baselines(plt, mplt, nbgroup)
            self.timings['preprocessing'] = round(time()-self.tt0, 4)
            ###### adjustments
            print('########### in preprocess_and_adjust  before adjustments  ')
            self.check_infos_group()
            ########## Translation adjustment
            self.make_horizontal_translation(nbgroup, jref, j2, plt, mplt)
        else:
            print("######  preprocessing yet Done   !!!!! ")

        self.infos_group[self.nbgroup][jref] = deepcopy(self.jref_full)                       # Retrieving the full reference
        if debug>0:
            print(Fore.GREEN + "###### self.jref_full['x'].size  ", self.jref_full['x'].size)     # Check size of the full ref retrieved
            print(Style.RESET_ALL)  # Remove color

        ########## Vertical adjustment

        if debug>0: print("Before performing vertical dilation examination of self.infos_group[self.nbgroup] ", self.infos_group[self.nbgroup])

        if j2 != jref:    # We don't deal with the reference

            ##########  Vertical adjustment

            if self.verticalcorr:
                self.make_vertical_adjustement(nbgroup, jref, j2, plt, mplt)    # Performing vertical adjustement.

            elem = self.infos_group[self.nbgroup]
            if debug>0: print('########### in preprocess_and_adjust   ')
            self.check_infos_group()

            if debug>0: print("Plot ref and pdz, Take the max in the region between lysozym and BI zone, Horizontal adjustment, saving positions and intensities  ")

            self.plot_ref_pdz(plt, elem, jref, j2)                                         # Plot ref and pdz
            self.take_max(elem, j2)                                                        # Take the max in the region between lysozym and BI zone.

            ######## horizontal dilation

            self.make_horizontal_dilation(elem, nbgroup, jref, j2, max_line, plt, mplt)    #  Horizontal adjustment

            ##########  saving positions and intensities

            self.retrieve_pos_int(nbgroup, jref, j2)
            ymax = elem[j2]['ref_int']*1.1            # lim sup using height of reference peak
            ymin = -elem[j2]['ref_int']*0.1           # lim inf using height of reference peak
            plt.ylim(ymin, ymax)                      # Show using lim inf lim sup

            ##########  Save and plot the Final result

            # if debug: print("##### plt.list_plot just before saving", plt.list_plot)

            self.plot_adjust(plt, jref, j2, plot=True, title='Final result grp {0} elem {1}'.format(nbgroup, j2+1),
                                save=True, show=True, newfig=False, col='g-', save_pickle=True,
                                plot_both=False, label_corr=True, debug_plot=0)

            self.timings['plot_adjust_dilation'] = round(time()-self.tt0, 4)

    def BI_comp_lists(self, elem, j2, jref, nbgroup, test, lbinewproc, lbioldproc, list_noise):
        '''
        Information for comparison with Katia results
        '''
        ##########

        molec = elem[j2]['mol_interact']                                  # residue for which we calculate the BI
        if j2 != jref :
            bipos = round(elem[j2]['BI']['position']['value'], 5)         # BI position value
            bizone = round(elem[j2]['BI']['zone']['value'], 5)            # BI zone value
        else :
            bizone = bipos = "ref"
        interv = elem[j2]['BI']['interval']                               # interval for BI calculation
        self.dic_wells_BIp[self.well_groups[nbgroup-1][j2]] = bipos
        self.dic_wells_BIz[self.well_groups[nbgroup-1][j2]] = bizone
        try:
            bipaper = round(float(rb.dic_binding[molec][0]),4)
        except:
            print("Non existing key {0}".format(molec))
            bipaper = 0
        test.write('{0}     {1}     {2} \n'.format(molec, bipos, bipaper))
        lbinewproc.append(bipos)      # List BIs with new proc method
        lbioldproc.append(bipaper)    # List BIs with old proc method (the one of the paper)
        list_noise.append(self.infos_group[nbgroup][j2]['BI']['position']['error']) # noise taken at the end of the spectra.

    def proc_a_well(self, j2, jref, logger, dic_wells,\
              dic_wells_BIp, dic_wells_BIz, infos_group, resulting_params_adjust,\
              report, lresults, nbgroup, debug=1):
        '''
        Process a given well
        '''
        print("debug is ", debug)
        print('########################## Beginning new process')
        self.group_size = len(self.well_groups[nbgroup-1])
        print('########################## size of the group to be dealt with is {0} '.format(self.group_size))
        for jj in range(0,self.group_size):
            try:
                if debug>0: print('In complete_extract, jj max_2nd_corr', elem[jj]['max_2nd_corr'])
            except:
                if debug>0: print('In complete_extract, not exising')
        if jref == -1:
            jref  = self.group_size-1             # jref taken as the last element in the group
            if debug>1: print('## ## ## ## jref for jref = -1 is ', jref)
        if j2 != jref:
            self.list_elems_in_grp.append(j2)
            if debug>1: print('########################## after self.list_elems_in_grp.append(j2)')
        self.logger = logger
        self.folder = self.logger.folder
        self.dic_wells = dic_wells                     # passing the dictionary  self.dic_wells
        self.dic_wells_BIp = dic_wells_BIp             # passing the dictionary  self.dic_wells_BIp
        self.dic_wells_BIz = dic_wells_BIz             # passing the dictionary  self.dic_wells_BIz
        self.infos_group = infos_group
        self.resulting_params_adjust = resulting_params_adjust
        self.r = report                                # passing the html report

        if debug>0: print('########################## after self.r = report # html report')

        print('#### in complete_extract')
        self.check_infos_group()

        #####

        lbinewproc, lbioldproc, list_noise, test = lresults               # lists for comparison

        ###### preprocessing and adjustments
        if debug>0:
            print("in complete extract jref is ", jref)
            print("in complete extract j2 is ", j2)
        self.preprocess_and_adjust(nbgroup, jref, j2)                     # translation + dilation, calls process group
        elem = self.infos_group[nbgroup]

        ###### # BI calculation

        self.extractBIs(plt, jref, j2)                                    # Extract the binding index for the pair j2/jref
        self.BI_comp_lists(elem, j2, jref, nbgroup, test, lbinewproc, lbioldproc, list_noise)

        #######
        self.pr('''

        ####### Cumulative Timings ######
        ''', '\n### Cumulative Timings \n')
        self.pr('* Times', '* Times ::', col=Fore.MAGENTA)
        for t in ['translation_group', 'dilation', 'noise and BI']: #
            time_message = "    * time after {0} : {1} s ".format(t, self.timings[t])
            self.pr(time_message, col=Fore.MAGENTA)
        print(Style.RESET_ALL)
        self.pr('-------------', '\n$*') # draw a line

    def complete_extract(self, nbgroup, jref, rb, lresults, init, debug=1):
        '''
        For each group, adjust the spectra and make the BI calculations
        Parameters :
            * nbgroup : number of the group
            * jref : index of the reference profile
            * rb :
            * lresults :
            * init : object containing the objects used from one group to another.
        calls "complete processing"
            which "calls preprocess_group"
                which "calls preprocess_profile"
        Called by "calc_BI_complete"
        '''
        logger, report, dic_wells,\
        dic_wells_BIp, dic_wells_BIz, infos_group, resulting_params_adjust = init.logger, init.r,  init.dic_wells,\
                        init.dic_wells_BIp, init.dic_wells_BIz, init.infos_group, init.resulting_params_adjust

        if debug>0: print("###### in complete_extract ################ ")

        ###### Baseline parameters

        self.nbchunks, self.nbiter, self.secondpower = init.nbchunks, init.nbiter, init.secondpower #   Chunks nb, iterations and secondpower

        ###### Processing intervals

        self.interv_adjust_vert = init.interv_adjust_vert                                                   #   vertical range for y adjustment
        print(Fore.RED + '########  Retrieved interv_adjust_vert is {0}'.format(self.interv_adjust_vert))
        print(Style.RESET_ALL)
        self.interv_analysis, self.interv_normalize = init.interv_analysis, init.interv_normalize           #  range analysis and normalize

        ###### Options for plot and processing

        self.makebokeh  = init.makebokeh
        self.verticalcorr  = init.verticalcorr

        ######
        if debug>0:
            print("*************** jref = ", jref)
            print("****  init.elems ", init.elems)

        self.list_elems_in_grp = []
        if init.elems !='all':
            for rg in init.elems:                           # Reading subgroup of elements in group
                for j2 in rg:                               # for each element in subgroup
                    self.proc_a_well(j2, jref, logger, dic_wells,\
                            dic_wells_BIp, dic_wells_BIz, infos_group, resulting_params_adjust,\
                            report, lresults, nbgroup)
        else:
            print("#### Processing all the elements of the group !!!!!!!")
            self.group_size = len(self.well_groups[nbgroup-1])
            print("*** self.group_size is ", self.group_size)
            for j2 in range(0, self.group_size):                               # for each element in the group
                print("dealing with j2 = ", j2)
                self.proc_a_well(j2, jref, logger, dic_wells,\
                        dic_wells_BIp, dic_wells_BIz, infos_group, resulting_params_adjust,\
                        report, lresults, nbgroup)
