#!/usr/bin/env python 
# coding: utf8


"""
read_bind.py,v 1.0 2016/05/12

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
class READ_BIND(object):
    '''
    Class for reading the Binding Index results established with the old method so as to make a comparison.
    '''
    def __init__(self, pattern_pdz='HPV'):
        self.dic_binding = {}     # Dictionary associating a peptide+PDZ name to  the corresponding binding index
        self.list_interm = []
        self.pattern_pdz = pattern_pdz # 
    
    def readresults(self, addr):
        '''
        Read the file and make the self.dic_binding dictionary 
        '''
        with open(addr) as f:
            lines = f.readlines()
            print(lines[0])
            for line in lines: # Read line by line
                linespl = line.split()
                idbind_well = linespl[0] + '-' + linespl[1] # Binding interaction with wells
                idbind_name = linespl[2] + '-' + linespl[3] # Binding interaction with names
                #print idbind_name
                if idbind_name not in self.dic_binding:
                    self.dic_binding[idbind_name] = [linespl[4]] # Binding interaction by name with value
                else:
                    self.dic_binding[idbind_name].append(linespl[4])
    
    def show_result_pattern(self, patt):
        '''
        Show the sorted results for a given pattern.
        The pattern can be a PDZ or a peptide.
        '''
        for k in self.dic_binding:
            if patt in k: 
                val = self.dic_binding[k][0]
                if not val.isalpha():
                    self.list_interm.append([k, val]) # intermediate list before sorting
        self.list_sorted = sorted(self.list_interm, key=lambda x: float(x[1]))[::-1]
        for elem in self.list_sorted:
            if self.pattern_pdz in patt:
                print(elem[0].split(patt + '-')[1] +': '+ elem[1] +'\n') # Show HPV results
            else:
                print(patt + elem[0].split('-' + patt)[1] +': '+ elem[1] +'\n') # Show peptides results
                
    def tests(self):
        '''
        Testing the construction of the dictionary
        '''
        print('BI HPV18_E6-RHPN2_A', self.dic_binding['HPV18_E6-RHPN2_A'])
        print('BI HPV16_E6-SHANK1_A', self.dic_binding['HPV16_E6-SHANK1_A'])
        #HPV18_E6-GRID2IP_1_B
        print('BI HPV18_E6-GRID2IP_1_B', self.dic_binding['HPV18_E6-GRID2IP_1_B'])
        #HPV16_E6-MAGI1_2_C
        print('BI HPV16_E6-MAGI1_2_C', self.dic_binding['HPV16_E6-MAGI1_2_C'])