#!/usr/bin/env python
# coding: utf8


"""
preproc.py

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
import os, glob
import numpy as np
### Spike
from modules.BC import correctbaseline
import multiprocessing as mp
from colorama import Fore, Back, Style

class PREPROC(object):
    '''

    '''
    def __init__(self):
        pass

    def extract_data(self, elem_block, debug=0):
        '''
        Extract the spectra and axes from csv files.
        Parameters:
            * elem_block : pattern in  the name of the dataset which completely identifies this dataset and placed just before csv extension.
                * eg : 'A1' in :  data_test/VIPS_33_1_1_Data_A1.csv
            * debug :  print debugging informations
        Output:
            * self.size : size abscissa axis
            * self.time : time abscissa axis
            * self.val : values
        '''
        if debug>0:
            print("######## in extract data")
        trig_data = False # switching variable. True when data are detected in readlines.
        time = []     # list of the time values
        size = []     # list of sizes in kDaltons.
        value = []    # list of the intensities
        listfiles = glob.glob(self.addr + '/*.*')
        # print("#### self.addr is ", self.addr)
        # print("#### listfiles is ", listfiles)
        for addcsv in listfiles:
            if addcsv.find(str(elem_block) + '.csv') != -1: # find pattern elem_bloc.csv
                addcsv_block = addcsv
        f = lambda x,i : float(x[i].strip() + '.' + x[i+1].strip())
        if debug>0:
            print("using file ", addcsv_block)
        with open(addcsv_block) as csvfile:
            for line in csvfile.readlines():    # Read the whole file.
                if 'SampleName' in line :       # Retrieving the interacting molecules names.
                    pos = len(line)
                    if debug>0:
                        print('# line: ', line)
                    for l in self.cut_pattern:
                        lf = line.find(l)
                        if  lf !=-1 and  lf< pos:
                            patt = l
                            pos = lf
                    if  patt in line:  # Using the pattern detected in SampleName
                        interact = line.split('=')[1].split(patt)
                        self.pdz = interact[0]               # PDZ used in the experiment
                        self.peptide = patt[1:]+interact[1][:-1].rstrip()        # peptide used in the experiment
                    try:
                        #self.dic_wells[elem_block] = self.peptide + '-' + self.pdz
                        self.dic_wells[elem_block] = self.peptide + '_' + self.pdz
                        if debug>0:
                            print("New element in the dictionary ", self.dic_wells[elem_block])
                    except:
                        print("Possibly self.dic_wells dictionary not defined")
                    if debug>0:
                        print("#### self.peptide, self.peptide[:-1]", self.peptide, self.peptide[:-1])
                if trig_data:
                    ls = line.split(',') # line of data
                    if debug>0:
                        print("ls is ", ls)
                    if not '.' in ls[0]: # written only with commas
                        time.append(f(ls,0))   # Time
                        value.append(f(ls,2))  # spectrum
                        size.append(f(ls,4))   # Size
                    else:
                        time.append(float(ls[0]))     # Time
                        value.append(float(ls[1]))    # spectrum
                        size.append(float(ls[2]))     # Size
                if line.find('Time,Value,Size')!=-1: # find the beginning of the csv dataset values
                    trig_data = True
            self.size = np.array(size)    # resulting size abscissae
            self.time = np.array(time)    # resulting time abscissae
            self.val = np.array(value)    # spectrum

    def make_BL(self, meth= 'L-BFGS-B', debug=True): # Powell, L-BFGS-B
        '''
        Make the baseline with the extracted datasets
        This makes use of the SPIKE baseline algorithm (correctbaseline.py)
        Parameters:
            * meth : method used for attracting the baseline toward low values.
                * Possible methods are : L-BFGS-B and  Powell
                * L-BFGS-B is normally faster for small secondpower
        Output:
            * self.bl : final baseline
            * self.bls : dictionary of intermediate baselines
            * self.size_trunc : x axis with truncation
            * self.val_trunc :  original truncated spectrum
            * self.val_corr : corrected baseline spectrum
        '''
        self.s = self.val.size
        self.size_index_cut = np.where(self.size > self.low_bound) # shorten size axis
        if debug:
            print('nbiter={0}, nbchunks={1}, deg={2}, secondpower={3}'.format(self.nbiter, self.nbchunks, self.deg, self.secondpower))
        self.bl, self.bls = correctbaseline(self.val[self.size_index_cut], iterations=self.nbiter, nbchunks=self.nbchunks, firstpower=0.3,
                                secondpower=self.secondpower, degree=self.deg,  chunkratio=1.0,
                                interv_ignore = None, method=meth,
                                nbcores= 10,
                                debug = True, choiceBL = 0)
        self.size_trunc = self.size[self.size_index_cut]       # x axis with truncation
        if debug: print("###################    self.size_trunc.size {0} ".format(self.size_trunc.size))
        self.val_trunc = self.val[self.size_index_cut]         # original spectrum
        if debug: print("###################    self.size_trunc[-1] {0} ".format(self.size_trunc[-1]))
        self.val_corr = self.val_trunc-self.bl                 # corrected spectrum

    def mol_norm_corr(self, val_mol_norm_ref = None, debug=False):
        '''
        Profile normalization.
        Peak used for normalization is indicated in red on the plots.
        Calculation of ratio : self.ratio for the intensity correction with the mol_norm reference.
        Resulting corrected spectrum is self.val_corr
        Parameters:
            * val_mol_norm_ref : intensity of the peak used for normalization
            * debug : if True, debug mode is activated
        '''
        if not self.interv_normalize: # interval for normalization not defined
            normalizing_peak = self.size_trunc[np.where(self.val_corr == self.val_corr.max())][0]       # Taking the maximum for normalizaton peak
            normp, deltaa = normalizing_peak, self.delta_analysis
            interv_around_norm = [normp - deltaa, normp + deltaa]
            self.interv_normalize = map(self.round, interv_around_norm)                # Evaluated on the first spectrum
            if debug:
                print("################## Evaluation of normalizing interval is {0} ########### ".format(self.interv_normalize))
                print(" normalizing peak abscissa ", normalizing_peak)
        interv = np.where((self.interv_normalize[0] < self.size_trunc) & (self.size_trunc < self.interv_normalize[1]))
        self.mol_norm_val = self.val_corr[interv]                            # mol_norm after correction
        self.mol_norm_size = self.size_trunc[interv]
        if not val_mol_norm_ref:                                             # val_mol_norm_ref not yet defined
            self.val_mol_norm_ref = self.mol_norm_val.max()                  # Taking the maximum on the interval
            self.infos_group[self.nbgroup]['norm_int'] =  round(self.val_mol_norm_ref,2)
        else:                                                                # val_mol_norm_ref yet defined
            self.val_mol_norm_ref = val_mol_norm_ref
        self.ratio = self.val_mol_norm_ref/float(self.mol_norm_val.max())    # y axis correction ratio calculated on mol_norm reference.
        self.val_corr *= self.ratio                                          # Make the correction with the reference.
        self.mol_norm_val_corr = self.mol_norm_val*self.ratio                # Correction on the region used for normalization.

    def save_infos(self, j, debug=0):
        '''
        Save the informations relative to the jth element in the group indexed nbgroup after having done the baseline and the normalization.
        Parameters:
            * j : index in the group
        Created dictionary keys after preprocessing:
            'val_corr' : : corrected spectrum after baseline and normalization
            'size_trunc' : mass size abscissa
            'bl' : baseline
            'bls' : all the baseline
            'val' : initial profile
            'mol_norm_size' : x part of the spectrum used for normalization
            'mol_norm_val_corr' : y part of the spectrum used for normalization
            'well_id' : name of the well
            'size_index_cut' :
            'ratio' : correction ratio
        '''
        elem = self.infos_group[self.nbgroup][j]
        elem_names = ['size_trunc', 'val_corr', 'bl', 'bls',
            'mol_norm_size', 'mol_norm_val_corr',
             'size_index_cut', 'ratio']
        for n in elem_names:
            elem[n] = getattr(self, n)
        elem['value'] = self.val #
        elem['x'] = self.size_trunc          #  Shorten x axis
        elem['y'] = self.val_corr            # Keep the corrected spectrum
        # elem['well_id'] = self.group[j]    # Name of the wells
        if debug>0:
            print("##### self.peptide is {0}, self.pdz is {1} ".format(self.peptide, self.pdz))
        elem['mol_interact'] = self.peptide + '-' + self.pdz  #
        ####
        indmax = elem['mol_norm_val_corr'].argmax(axis=0)
        if debug>0:
            print("########################################################## indmax is ", indmax)
            print("self.mol_norm_size[indmax] ", self.mol_norm_size[indmax])
        self.infos_group[self.nbgroup]['norm_pos'] = self.mol_norm_size[indmax]

    def preprocess_profile(self, j, nbgroup=None, debug=False):
        '''
        Prerocesses the jth spectrum. baseline (make_BL) + normalization (mol_norm_corr).
        Saves the results in self.infos_group[nbgroup][j]
        Parameters:
            * j : index of the sub-element in the group
            * nbgroup : index of the group
        '''
        if debug:
            print("nbgroup ", nbgroup)
        if nbgroup:                                        # If the index of the group is defined (permits to define reference)
            self.nbgroup = nbgroup
            print("self.nbgroup ", self.nbgroup)
            self.group = self.well_groups[nbgroup-1]       # define the group of interest
            self.jref = j
            self.infos_group[nbgroup] = {}                 # Initialize informations about the group
            self.resulting_params_adjust[nbgroup] = {}
        if debug:
            print("type(self.infos_group) ", type(self.infos_group))
            print("j is ", j)
        self.infos_group[self.nbgroup][j] = {}
        self.infos_group[self.nbgroup][j]['BI'] = {}
        self.infos_group[self.nbgroup][j]['BI']['zone'] = {}
        self.infos_group[self.nbgroup][j]['BI']['position'] = {}
        self.resulting_params_adjust[self.nbgroup][j] = {}
        print("************ self.group[j] is ", self.group[j])
        self.extract_data(self.group[j])                    # Take the jth element in the group.
        self.make_BL()                                      # Make the baseline
        if nbgroup != None: self.val_mol_norm_ref = None
        self.mol_norm_corr(self.val_mol_norm_ref)           # return ratio, val_mol_norm_ref  and make normalization
        self.save_infos(j)

    def preprocess_group(self, jref, nbgroup): #
        '''
        Preprocess the group nbgroup. Make the baseline and normalization
        Parameters:
            * jref : index of the reference
            * nbgroup : group number
        Called by "complete processing"
            which is called by "complete_extract"
                which is called by "complete_extract"
        '''
        print('####### in processing group, group number {0} '.format(nbgroup))
        print('chosen jref value ', jref)
        self.preprocess_profile(j=jref, nbgroup=nbgroup)  # enter the ref number and the group number
        self.group_size = len(self.well_groups[nbgroup-1])
        for j in range(self.group_size):                 # go through the whole group
            if j != self.jref:
                self.preprocess_profile(j)
        self.preprocessed = True
