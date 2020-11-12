#!/usr/bin/env python 
# coding: utf8


"""
initialize.py,v 1.0 2016/05/12

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
import string  # used for ascii strings
### Reports
from .make_report import REPORT
import json

root = '/Users/chiron/CloudStation/encours/Casc4de/Projets/ElectrophorÃ¨seCapillaire/'
vips33_test = root+'HOLD_UP/NatureMethods15_SupplementaryFiles/suppl_data_new/Archive_S1/PDZome_16_18E6_384/VIPS_33_1_1'

class INIT(object):
    '''

    '''
    def __init__(self):
        pass

    def init_baseline(self):
        '''
        Initialization of the baseline with default parameters
        '''
        self.nbiter = 2                                  # number of iterations for the baseline
        self.nbchunks = 50                               # number of chunks for the baseline
        self.firstpower = 0.3                            # power for sparsity
        self.secondpower = 2                             # power for dragging down the baseline
        self.deg = 1

    def init_normalization(self, interv_normalize):
        '''
        Initialization for spectrum normalization
        '''
        self.var_mol_norm_ref = 0                        # defines which mol_norm is the reference.
        self.dic_interv_normalize = {'lyzo' : [10, 20], 'bsa' : [70, 80]}
        if interv_normalize in ['lyzo', 'bsa']:
            self.interv_normalize = self.dic_interv_normalize[interv_normalize]
        else : 
            self.interv_normalize = interv_normalize     # interval entered by the user

    def init_groups(self, gr_nbline, gr_nbcol):
        '''
        Initialize all the parameters for making groups and make the groups
        '''
        self.gr_nbline = gr_nbline                       # number of lines in the group
        self.gr_nbcol = gr_nbcol                         # number of columns in the group
        self.lalpha = string.ascii_uppercase[:self.gr_nbline] # list of lines
        self.shape_groups = [2,2]                        # self.shape_groups[0] is the width of the group, self.shape_groups[1] is the height of the group
        self.size_groups = self.shape_groups[0]*self.shape_groups[1]
        self.number_of_groups = int(self.gr_nbline*self.gr_nbcol/self.size_groups)
        self._make_groups_wells()                        # Make the packet of 4 cells by default

    def init_adjust(self, interv_adjust, interv_adjust_vert, debug=1):
        '''
        Initialization for curves adjustement
        '''
        self.interp_kind = "linear"                      # quadratic, linear, slinear
        self.coeff_mult_size = 2                         # Sampling coefficient
        self.list_dilat = []                             # list of the different dilation coeffs used in adjust.
        self.list_translat = []                          # list of the different translation used in adjust.
        self.mult_density = 8                            # increase points density for having a correct maximum position on the peaks
        self.resulting_params_adjust = {}                # Collecting adjustment results
        #### Interval on which are done dilation and/or translation
        self.interv_adjust  = interv_adjust              # set to full for translation and reduced around zone of interest for dilation.
        self.interv_adjust_vert  = interv_adjust_vert    # interval for vertical adjustement (translation + dilation)
        if debug>0:
            print("self.interv_adjust ", self.interv_adjust)
            print("self.interv_adjust_vert ", self.interv_adjust_vert)

    def init_analysis(self, interv_analysis, debug=1):
        '''
        Initialization for result analysis
        '''
        self.interv_analysis = interv_analysis
        self.analinf = interv_analysis[0]                 # inferior bound for analysis
        self.analsup = interv_analysis[1]                 # superior bound for analysis
        self.delta_analysis = 10                          # defines the half the width of the interval of analysis
        if debug>0:
            print("##### self.analinf, self.analsup ", self.analinf, self.analsup)

    def init_plots(self, save_baseline, save_dilation, debug=1):
        '''
        Initialization for plots of the results and intermediate plots
        '''
        self.plot_liminf = 5                              # inferior limit for plot
        self.plot_limsup = self.interv_adjust[1] #100     # superior limit for plot
        if debug: print("### Using range {0}-{1} for plot ".format(self.plot_liminf,self.plot_limsup))
        self.save_baseline = save_baseline                # Makes directly the Bokeh plots for the baseline
        self.save_dilation = save_dilation                # Makes directly the Bokeh plots for the dilation step
        if debug>0:
            print("### self.plot_liminf ", self.plot_liminf)
            print("### self.plot_limsup ", self.plot_limsup)

    def init_addr(self, root, addr):
        '''
        Default dataset address or given address
        '''
        self.june_3_2016 = root + 'Test_384_3juin16'
        dic_addr = {'vips33': vips33_test, 'june16': self.june_3_2016}
        try:
            self.addr = dic_addr[addr]                 # address in dic
        except:
            self.addr = addr                           # direct address 

    def prepare_analysis(self, par, debug=0):
        '''
        Prepare range for analysis
        '''
        try:
            self.analinf = int(par['range_analysis'].split('-')[0])    # inferior bound for the analysis
            self.analsup = int(par['range_analysis'].split('-')[1])    # superior bound for the analysis
            self.interv_analysis = [self.analinf, self.analsup]        # Intervall up down for the analysis     
            if debug>0:
                print('###', self.analinf) 
                print('###', self.analsup)
        except:
            print('using the default range analysis')

    def prepare_normalization(self, par, debug=0):
        '''
        Prepare range for normalization
        '''
        try:
            self.norminf = int(par['range_norm'].split('-')[0])         # inferior bound for the normalization
            self.normsup = int(par['range_norm'].split('-')[1])         # superior bound for the normalization
            self.interv_normalize = [self.norminf, self.normsup]        # Intervall up down for the normalization 
            if debug>0:
                print('###', self.norminf) 
                print('###', self.normsup)
        except:
            print('using the default range normalize')

    def prepare_vertical_adjust(self, par, debug=0):
        '''
        Prepare range for vertical adjustment
        '''
        try:
            self.y_adjust_inf = int(par['range_y_adjust'].split('-')[0])         # inferior bound for the vertical adjustment
            self.y_adjust_sup = int(par['range_y_adjust'].split('-')[1])         # superior bound for the vertical adjustment
            self.interv_adjust_vert = [self.y_adjust_inf, self.y_adjust_sup]     # Intervall up down for the vertical adjustment
            if debug>0:
                print('###', self.y_adjust_inf) 
                print('###', self.y_adjust_sup)
        except:
            print('using the default range interv_adjust_vert')

    def prepare_groups(self, groups_string, debug=0):
        '''
        Tanslate interface information about groups
        '''
        if  groups_string == 'all':
            self.groups = [range(1, self.number_of_groups+1)]            # list of range
            print("##########  Processing all the groups")
            print("self.groups = ", self.groups)
        else:
            self.groups = []
            subgroups = groups_string.split(';')                         # parsing for having the subgroups
            if debug>0:
                print("subgroups ", subgroups)
            self.number_of_groups = 0
            for g in subgroups:                                          # Going through the subgroups in the subgroups list.
                gs = g.split('-')
                self.groups.append(range(int(gs[0]), int(gs[1])+1))      # list of ranges
                self.number_of_groups += int(gs[1])-int(gs[0])+1         # 

    def prepare_elements_in_groups(self, elems, debug=0):
        '''
        Prepare element selection in each groups from interface information 
        '''
        print("***** in prepare_elements_in_groups, elems is {0} ".format(elems))
        if  elems == 'all':
            self.elems = elems  # [range(0, self.group_size)]
            print("***###***###***in prepare_elements_in_groups, self.elems is ", self.elems)
            #deb_elem, end_elem = map(int, [elems.split('-')[0], elems.split('-')[1]])
            #self.elems = [range(deb_elem-1, end_elem)] 
        else:
            self.elems = []
            subelems = elems.split(';')             # parsing for having the subgroups
            if debug>0: print("subelems ", subelems)
            self.number_of_elems = 0
            for e in subelems:                      # Going through the subgroups in the subgroups list.
                es = e.split('-')
                self.elems.append(range(int(es[0]), int(es[1])+1)) # list of ranges
                self.number_of_elems += int(es[1])-int(es[0])+1

    def prepare_peptides_identifiers(self, par):
        '''
        '''
        print("#######  retrieving new peptides identifiers !!!!")
        try:
            list_identif = par['pepidentif'].split(',')    # 
            self.pepidentif =  ['_' +  identif for identif in list_identif]
            print('############  self.pepidentif {0} '.format(self.pepidentif))
            self.cut_pattern += self.pepidentif
            print('############  self.cut_pattern {0} '.format(self.cut_pattern))
        except:
            print('using the default Peptides separators')

    def prepare_baseline(self, par):
        '''
        '''
        self.nbiter = int(par['iter'])              # number of iterations for the baseline
        self.nbchunks = int(par['chunks'])          # number of chunks for the baseline
        self.secondpower = int(par['speed'])        # second power parameter for the baseline

    def prepare_dic_wells(self):
        '''
        '''
        self.dic_wells = {}
        self.dic_wells_BIp = {}
        self.dic_wells_BIz = {}

    def prepare_folder(self):
        '''
        '''
        date = self.datetime()
        basename = os.path.basename(self.addr)
        self.folder = 'Interf/static/processing_{0}_{1}'.format(basename, date) # folder containing the processing with data name and date.
        try:
            os.mkdir(self.folder)
        except:
            print("Directory yet exists")
        self.logging()
        self.r = REPORT(name= os.path.join(self.folder, 'html_report.html'), toc=True) # Html report with Table of Contents
        self.r.begin('HoldUp Processing Report')   # Set title's report
        self.r.write('\n# html log file')

    def loading_parameters_and_prepare(self, make_folder, dic_wells, params, debug=0):
        '''
        Prepare the foldders, the dictionaries and load the processing parameters
        '''
        #### Folders
        if make_folder:                                # If true makes the processing folder with data name and date.
            self.prepare_folder()
        #### Correspondencies
        if dic_wells:
            self.prepare_dic_wells()
        #### Parameters
        if params:    
            if debug>0: print('###############  params passed !!!!!! ')             # Parameters for reprocessing
            self.params = params
            if debug>0: print("params = ", params)
            par = json.loads(params)                    # load the parameters from transmitted json data
            if debug>0: print("par is ", par)
            self.prepare_baseline(par)
            groups_string = par['groups'].strip()       # retrieving groups information from interface
            elems = par['elems'].strip()                # elems in group to process
            
            #### Booleans

            self.makebokeh = bool(par['makebokeh'])                       # Make Bokeh plot output boolean
            self.verticalcorr = bool(par['verticalcorr'])                 # Vertical correction boolean

            ### Define ranges normalization, analysis and vertical adjustment
            
            self.prepare_analysis(par)             # Analysis
            self.prepare_normalization(par)        # Normalization
            self.prepare_vertical_adjust(par)      # Vertical adjustment
            self.prepare_groups(groups_string)     # Select the groups
            self.prepare_elements_in_groups(elems) # Select elements in the groups
            self.prepare_peptides_identifiers(par) # Peptide identifiers


            