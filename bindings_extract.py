#!/usr/bin/env python
# coding: utf8


"""
 bindings_extract.py,v 1.0 2016/05/12
 Program for extracting automatically the binding indices from Hold up like experiments.
 It performs the baseline correction, translation and dilation adjustments.

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
sys.path.append('/home/meglio/Bureau/bitbuck/')
import subprocess
import glob, json, shutil, pickle
import string  # used for ascii strings
from platform import python_version
print("python_version", python_version())

from colorama import Fore, Back, Style
from itertools import cycle
from time import localtime, strftime, time, sleep
from copy import deepcopy

### Numerical libraries
import numpy as np
from numpy.fft import rfft, irfft
print('########## Importing scipy.interpolate #########')
try:
    from scipy.interpolate import interp1d
    from scipy.optimize import fmin # fmin_powell, fmin_l_bfgs_b, golden, fminbound
except:
    print("Couldn't import scipy libraries")
### Visualization
from matplotlib import pyplot as mplt
### Reports
from modules.make_report import REPORT
### Tests
import unittest

###
from modules.plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400     # good width seems to be 400
plt.plot_height = 400    # good height seems to be 400

###
from modules.BC import correctbaseline
from modules.read_bind import READ_BIND
from modules.log import LOG
from modules.BI import BI
from modules.com import COM
from modules.plots import PLOTS
from modules.initialize import INIT
from modules.preproc import PREPROC as PREP
from modules.transformations import TRANSF
from modules.find_intervals import FIND_INTER as FIND
from modules.groups_wells import GW
from modules.util import UTIL
from modules.proc import PROC
from modules.reproc import REPROC

root = '/Users/chiron/CloudStation/encours/Casc4de/Projets/ElectrophorÃ¨seCapillaire/'
vips33_test = root+'HOLD_UP/NatureMethods15_SupplementaryFiles/suppl_data_new/Archive_S1/PDZome_16_18E6_384/VIPS_33_1_1'

class BINDINGS_EXTRACT(UTIL,INIT,GW,LOG,BI,COM,PREP,PROC,REPROC,TRANSF,PLOTS,FIND):
    '''
    Module for processing a whole plate and visualize the results as well as the intermediate processings steps.
    The program makes in order :
        * A baseline correction
        * A normalization (made by default with the highest peak (for eg Lysozym))
        * An horizontal adjustment by translation (correction over a big slipping)
        * An horizontal adjustment by dilation (more common correction for old cartridge)
        * The calculation of the Binding Index (BI) (done once all the corrections performed)
    Parameters:
        * addr : path to the folder containing the measurements
        * interv_normalize (optionnal) : interval used for intensity normalization
            It can be also the name of the interval : "lyzo", "bsa" etc..
        * interv_adjust : interval used for adjusting the spectra along the x axis.
        * interv_analysis (optionnal)  : interval for BI calculation. (analysis interval)
        * interv_noise_extract : interval used for noise calculation
        * gr_nbline : number of lines of each rectangular group of cells
        * gr_nbcol : number of columns of each rectangular group of cells
    Functionnalities:
        * baseline correction
        * normalization with reference peak (lysozym, bsa or whatever)
        * adjustment for having superimposed spectra.
        * BI (Binding Index) calculation
    Resulting attributes:
        * self.folder : folder containing the processing
    Usage eg :
        * processing with BI calculation on group num 20 in dataset vips33 :
            python bindings_extract.py BI_grp 20 vips33
    The reprocessing uses the address saved in the log file. Becareful, you need to clean Chrome history for applying the reprocessing to other dataset..
    '''
    def __init__(self, addr, interv_normalize = None, interv_adjust= [0, 100], interv_adjust_vert= [0,0],
             interv_analysis = [40, 60], interv_noise_extract = [80, 200],
              gr_nbline = 16, gr_nbcol = 24, make_folder=False, save_dilation=True,
              save_baseline=True, dic_wells=None, params=None, debug=0):
        super().__init__()
        ####
        self.coliter = cycle(['blue', 'green', 'red', 'magenta', 'orange', 'black']) # Colors for the plots
        self.preprocessed = False                        # False before preprocessing, True after
        #### baseline
        self.init_baseline()
        #### normalization
        self.init_normalization(interv_normalize)
        self.infos_group = {}
        self.round = lambda x: round(x, 2)
        #### name molecules cutting pattern
        self.cut_pattern = ['_E6', '_HPV', '_YAP', '_TAZ', '_Pepdeath', '_Biotin',
                     '_NONE', '_RSK1A', '_RSK1B', '_RSK1C', '_PTEN', '_PTEN-Acetyl', '_CBP'] # Pepdeath used in june3_2016
        #### making default groups
        self.init_groups(gr_nbline, gr_nbcol)
        #### Adjust
        self.init_adjust(interv_adjust, interv_adjust_vert)
        #### Analysis
        self.init_analysis(interv_analysis)
        #### Noise
        self.interv_noise_extract = interv_noise_extract  # Interval used for noise calculation
        #### Binding Index
        self.dic_interact_BI = {}
        #### Inferior bound for the whole processing.
        self.low_bound = 10 # Used for removing perturbating signal at low masses.
        #### Addr
        self.init_addr(root, addr)
        #### Record the timings
        self.timings = {}                              # Timing during the processing
        #### Plot
        self.init_plots(save_baseline, save_dilation)
        self.loading_parameters_and_prepare(make_folder, dic_wells, params)

def make_manyplots(list_name_jsons):
    '''
    Make the Bokeh plot with the list of plots list_name_jsons
    Parameters:
        * list_name_jsons : list of the pickle to be gathered in a unique plot for comparison
    '''
    print('######### list_name_jsons ', list_name_jsons)
    ll = json.loads(list_name_jsons)         # Loads the json names
    # print(ll)
    print('##### ll[0] ' + ll[0])
    addr = vips33_test     # Whatever address used only for creating the object b for accessing to pck2bkh_manyplots
    b = BINDINGS_EXTRACT(addr)
    b.pck2bkh_manyplots(plt, ll, 'Interf/static/superp.html')   # Make the multiplot (from pickle to Bokeh)

def calc_BI_complete(addr=None, params=None,  find_intervals=False, comparison=False, debug=1):
    '''
    Calculation of the Binding Index on all the groups

    Parameters:
        * addr :
        * params :
        * find_intervals : determines the normalization and analysis intervals
        * comparison :
        * debug :
    Processing :
        * baseline correction + normalization on biotine or lysozym.
        * adjustmement between spectra 3 (biotine) and 0
        * translation, moving zone detection
        * dilation
        * BI calculation with error
        * writing results in a file
            * suspected erroneous processings notified with an asterisk.
    Using data VIPS_33 from Nature Methods.
    Usage :
        python bindings_extract.py complete
        saving results of BI calculation in "test_BI.csv"
    Values saved :
        * pdz_pep : pair pdz-peptide
        * nbgroup : index of the group
        * BI(pos) : binding index with position method
    '''

    if not addr:
        addr = vips33_test                           # Address by default
    print('############## addr ', addr)
    jref = -1                                        # ref for the BI, if -1 the reference is the last element in the group

    # Finding the intervals : Normalization interval and Analysis interval
    # Value by default not used..

    interv_analysis=[45,75]      # interval for analysis
    interv_normalize=[8,17]      # interval for the normalization

    ### Initialization uses params

    init = BINDINGS_EXTRACT(addr, interv_analysis=interv_analysis, interv_normalize=interv_normalize,
                            make_folder=True, dic_wells=True, params=params) #
    init.pr(addr)                                   # write the address in the log file...
    init.interv_adjust = [10, 250]     #

    if find_intervals:
        init.find_intervals(jref=jref)              # Determine automatically the intervals for normalization and analysis
    if comparison:                                  # Comparison with Nature Method paper
        ###########
        rb = READ_BIND()
        rb.readresults('PDZome_16_18E6_384_stand_corr_biotin_VIPS_33_1_1.txt')   # Read results from paper for comparison
    else:
        rb = READ_BIND()

    ############# Whole processing

    lbinewproc = []                                 # list of BIs for new processing
    lbioldproc = []                                 # list of BIs for old processing
    list_noise = []                                 # list of associated noise

    with open(os.path.join(init.folder, 'BI_results.csv'), 'w') as test :
        test.write('{0}               {1}    {2} \n'.format('pdz_pep', 'BI(pos)', 'BI paper' )) # first line
        tbeg = time()
        lresults = [lbinewproc, lbioldproc, list_noise, test]
        ####
        par = json.loads(params)                                # load the parameters for processing from transmitted json data
        if debug>0: print("########### par = json.loads(params) gives par = ", par)
        try:
            if par['range_analysis']:
                interv_analysis = init.interv_analysis
        except:
            pass
        ####
        init.init_count()                                    # Storing the number of groups processed for following the processing

        # Processing all the groups

        for rg in init.groups:                                                         # going through list of range of groups
            for nbgroup in rg:                                                         # going through groups in range
                try:
                    if debug>0:
                        print("######  just before processing nbgroup is ", nbgroup)
                        print('#### interv_analysis', interv_analysis)
                    print("########    nbgroup is {0} !!!!!".format(nbgroup))
                    c = BINDINGS_EXTRACT(addr, interv_analysis=interv_analysis,\
                         interv_normalize=interv_normalize, save_baseline=True,\
                         save_dilation=True)
                    if debug>0: print("jref in calc_BI_complete is ", jref)
                    c.complete_extract(nbgroup, jref, rb, lresults, init)                      # Main processing
                    c.count_folder(init.folder, init.number_of_groups)                         # For following the processing
                except:
                    c.debug_col('####################    Bug with group num {0}  !!!!! ############ '.format(nbgroup), 'y')
                c.save_dic_wells()                                                         # Save the wells names with the corresponding molecules (not in except)
                c.save_all_processing_infos()                                              # Save all the processings infos (not in except)

        #print("### par['root'] is ", par['root'])
        c.after_reprocess(par, init)  # Reprocess a group

    c.BI_compare_with_old_data(plt, lbinewproc, lbioldproc, list_noise, tbeg)              # Comparison with results of the Nature paper..

    try:
        init.r.end() # Closing html report
    except:
        print('not finishing the html report')

def help():
    print(help_doc)

# Available processings
help_doc = '''
'complete' : calc_BI_complete,
'makemanyplt' : make the multiplots
'''

leg = { 'complete' : calc_BI_complete, 'makemanyplt' : make_manyplots, 'help': help}

if __name__=='__main__':
    '''
    Usage:
        python bindings_extract.py processing_name parameter
        Usage example:
            python bindings_extract.py BI_grp 20
    syntax :
        'complete' : calc_BI_complete, whole test of bindings_extract for comparison with Nature method paper.
        'makemanyplt' : make the multiplots
        'help' : help information
        '''
    egnb = sys.argv[1]
    print(egnb)
    print(sys.argv[2])
    leg[egnb](*sys.argv[2:])
