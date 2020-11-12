#!/usr/bin/env python 
# coding: utf8


"""
transformations.py

Module for transformations.. dilation (horizontal, vertical), translation (horizontal, vertical)

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
try:
    from scipy.interpolate import interp1d
    from scipy.optimize import fmin # fmin_powell, fmin_l_bfgs_b, golden, fminbound
except:
    print("Couldn't import scipy libraries")
from functools import partial
from time import time
from copy import deepcopy
import matplotlib.animation as manimation

class TRANSF(object):
    '''
    Class for performing all the transformations : horizontal and vertical translations and dilations
    '''
    def __init__(self):
        pass
    
    def adjust(self, nbgroup, j1, j2, op, plt, mplt, video=None, plot=False, kind_adjustment = '', xtol=1e-8, debug=0):
        '''
        Adjust the spectrum j2 on j1(ref). Used in preprocess_and_adjust()
        Minimize the distance for dilation or translation operation.
        At the end spectra registered in self.spec1 and self.spec2
        Becareful !!! The reference spectrum x axis(['spec_adj_x']) is changed at each adjustment
        Parameters:
            * nbgroup : index of the group
            * j1 : index of the reference spectrum in the group
            * j2 : index of the moving spectrum in the group
            * op : kind of operation i.e : dilat, translat etc..
            * video : plot a video control of the adjustment, video is the name of the video
            * plot : plot before and after the adjustment
            * kind_adjustment : translat or dilat
        '''
        self.distance = partial(self.distance_with_video, plt=plt, mplt=mplt)
        self.kind_adjustment = kind_adjustment                                   # kind of adjustment : dilat, translat, transfvert
        self.video = video
        print("######### ratio j1, j2 before adjustment ")
        self.select_pair(nbgroup, j1, j2)
        self.op = op
        self.current_j1 = j1
        self.current_j2 = j2
        if op == 'dilat':                                                        # Dilation on X axis
            param = [1] #[1] #[1] # Initialization
            self.pr( "    * performing dilation", col=Fore.GREEN)
        elif op == 'translat':                                                   # Translation on X axis
            param = [0] # Initialization
            self.pr( "    * performing translation ", col=Fore.GREEN)
        elif op == 'transfvert':                                                 # Vertical correction with y translation and y dilation
            param = [1,0] # Initialization
            self.pr( "    * performing vertical correction ", col=Fore.GREEN)
        print(Style.RESET_ALL)
        if debug>0:
            print('######################################### Making    "interm_before_adjust.html"   ')
            print("self.spec1['x'] is ", self.spec1['x'])
            plt.plot(self.spec1['x'], self.spec1['y'], 'k-')                     # spec1 before processing
            plt.show()
            addr_interm = os.path.join(self.folder, 'interm_before_adjust_{0}.html'.format(j2))
            plt.savefig(addr_interm)
        self.start_opt = False                                                   # 
        if video:
            self.init_ffmpeg(plt)
            with self.writer.saving(self.fig, self.video + ".mp4", 100):
                xopt = fmin(self.distance, param)        #                       # Optimization and video
        else: 
            self.step_dist = 0
            xopt = fmin(self.distance, param)                                    # Optimization
            print("self.dilat ", self.dilat)
            print("self.translat ", self.translat)
        if op == 'transfvert':
            self.dilaty, self.transy = xopt[0], xopt[1]                        # Dilation and Translation on Y axis. 
            mess_vert_corr = " self.dilaty: {0} , self.transy : {1} ".format(self.dilaty, self.transy)
            self.pr( "    * Vertical correction is {0} ".format(mess_vert_corr), col=Fore.GREEN)
        if debug>0:
            print('#### xopt ', xopt)
            print('#### type(xopt) ', type(xopt))
            print('#### xopt[0] ', xopt[0])
        self.resulting_params_adjust[self.nbgroup][j2][op] = round(xopt[0], 3)  # Save the adjustment parameters

        #######
        print("##### moved by {0} {1} ".format(kind_adjustment, self.infos_group[self.nbgroup][self.j2]['mol_interact']))
        # print('xopt', xopt)
        if debug>0:
            plt.plot(self.spec1['xx'], self.spec1['yy'], 'r-')
            plt.show()
            addr_interm = os.path.join(self.folder, 'interm_after_adjust_{0}.html'.format(j2))
            plt.savefig(addr_interm)
        for j in [self.jref, self.j2] :                   # Save the adjusted curves
            elem = self.infos_group[self.nbgroup][j]
            if j == self.jref  :                          # Save the curve on which are fitted the other ones. 
                elem['spec_adj_x'] = self.spec1['xx']     # Save x reference  
                elem['spec_adj_y'] = self.spec1['yy']     # Save y reference
            elif j == self.j2 :
                elem['spec_adj_x'] = self.spec2['xx']     # Save x axis for fitted  curve
                elem['spec_adj_y'] = self.spec2['yy']     # Save y values of the fitted  curve
        if debug>0:
            pass # print("self.list_dilat, self.list_translat ", self.list_dilat, self.list_translat)
        if plot:
            self.plot_adjust(plt, kind_adjustment)
        print(xopt)                                     # optimal adjustment parameter.

    def distance_with_video(self, param, plt, mplt, debug=False): # , plt, mplt, 
        '''
        Distance between profile 1 and 2 after transformation.
        Parameters:
            * param: dilation, translation or translation with dilation for vertical correction.
        The transformation is made in self.make_transf(param) 
        '''
        self.step_dist += 1
        self.make_transf(param, plt, mplt)                                                                # Make the translation, dilation or vertical correction, make self.spec1['yy'] and self.spec2['yy']
        if self.op != 'transfvert':
            self.diffsq = ((self.spec1['yy']-self.spec2['yy'])**2).sum()                       # square of the difference for fitting
        elif self.op == 'transfvert':
            self.diffsq = abs(np.abs(self.spec1['yy']).sum()-np.abs(self.spec2['yy']).sum())   # using the difference of the integrals for vertical dilation.. 

        if debug: self.debug_col('current distance is {0} '.format(self.diffsq), 'r')
        
        ### Video of the adjustment

        if self.video : # Video for controlling the fit
            plt.title(param)
            s1 = self.infos_group[self.nbgroup][self.jref]['mol_interact']
            s2 = self.infos_group[self.nbgroup][self.j2]['mol_interact']
            plt.plot(self.spec1['xx'], self.spec1['yy'], label=s1)             # reference spectrum. 
            plt.plot(self.spec2['xx'], self.spec2['yy'], label=s2+'(moved)')   # Adjusted spectrum
            plt.legend()
            self.writer.grab_frame()
            plt.clf() # Clear figure
        return self.diffsq

    def make_transf(self, param, plt, mplt):
        '''
        Transformation made on the spectrum j2.
        Parameters:
            * param: dilation or translation coefficient
        Actions:
            * Horizontal adjustment :
                - Homothetic horizontal dilation around 0 (value*self.dilat)
                - Horizontal translation.
            * Vertical adjustment: 
                - Homothetic vertical dilation around 0 
        Result :
            (self.spec1['xx'], self.spec1['yy']) and (self.spec2['xx'], self.spec2['yy'])
        '''
        if len(param) == 1 :                         # Case of horizontal adjustment
            self.size = self.spec1['x'].size
            self.make_axis(param)                    # Axis calculation taking into account the transformation
            self.interp(self.spec1)                  # fixed spectrum
            self.interp(self.spec2, make_op=True)    # Horizontal dilation or translation only on S2.
        else:
            print('#### Performing vertical adjustment !!! ')
            self.make_vertical_transf(plt, mplt, param)         # Vertical dilation or translation only on S2.

    def in_adjust_vert(self, mplt, debug=1):
        '''
        Called by make_vertical_transf
        Select Interval for vertical adjustment.
        Parameters:
            * spec :
            * debug : 
        adjvert
        '''
        print('in interv_adjust_vert, debug is ', debug)

        print("### self.dilat {0} self.translat {1} ".format(self.dilat,self.translat))
        if debug>0: print("####### self.interv_adjust_vert[0], self.interv_adjust_vert[1] ",self.interv_adjust_vert[0], self.interv_adjust_vert[1])
        
        self.spec2['spec_adj_x'] = self.spec2['x']# +xtransl  #*xdil+xtransl
        infsup1 = np.where((self.spec1['x'] > self.interv_adjust_vert[0]) & (self.spec1['x'] < self.interv_adjust_vert[1]))    # 
        infsup2 = np.where((self.spec2['spec_adj_x'] > self.interv_adjust_vert[0]) & (self.spec2['spec_adj_x'] < self.interv_adjust_vert[1]))    # 
        if debug>0: 
            print("### self.spec1['x']  ", self.spec1['x'] )
            print("### self.spec2['spec_adj_x'] ", self.spec2['spec_adj_x'])
            print("### infsup1 ", infsup1)
            print("### infsup2 ", infsup2)
        min1, min2 = self.spec1['x'][infsup1[0]].min(), self.spec2['spec_adj_x'][infsup2[0]].min()
        if debug>0: 
            print("### min1 ", min1)
            print("### min2 ", min2)
        minax = max(min1, min2)
        ###
        max1, max2 = self.spec1['x'][infsup1[0]].max(), self.spec2['spec_adj_x'][infsup2[0]].max()
        if debug>0: 
            print("### max1 ", max1)
            print("### max2 ", max2)
        maxax = min(max1, max2)
       
        self.xvert = np.linspace(minax, maxax, 50) # Same for both
        if debug>2:
            print("self.xvert.size ", self.xvert.size)
            print("#### minax {0}, maxax {1}".format(minax, maxax))

        #######  Interpolation

        spec_interp1 = interp1d(self.spec1['x'][infsup1[0]], self.spec1['y'][infsup1[0]], kind=self.interp_kind)
        spec_interp2 = interp1d(self.spec2['spec_adj_x'][infsup2[0]], self.spec2['y'][infsup2[0]], kind=self.interp_kind)
        if debug>0: 
            print("### spec_interp1 ", spec_interp1)
            print("### spec_interp2 ", spec_interp2)
 
        ####### interpolated new curves

        specxcomp, specycomp = self.xvert, spec_interp1(self.xvert)
        specxxcomp, specyycomp = self.xvert, spec_interp2(self.xvert)
        if debug>0:
            print("specxcomp.size {0}, specycomp.size {1} ".format(specxcomp.size, specycomp.size))
            print("specxxcomp.size {0}, specyycomp.size {1} ".format(specxxcomp.size, specyycomp.size))
            print("specycomp.max() {0}, specyycomp.max() {1} ".format(specycomp.max(), specyycomp.max()))
        if not self.start_opt:
            if debug>2:
                mplt.figure()
                mplt.title("j1 is "+str(self.current_j1)+" j2 is "+str(self.current_j2))
                mplt.plot(self.spec1['x'], self.spec1['y'], label='spec1')
                mplt.plot(self.spec2['x'], self.spec2['y'], label='spec2')
                #mplt.title('future correction is xdil {0}, xtransl {1} '.format(xdil, xtransl))
                
                # mplt.figure()
                mplt.legend()
                mplt.show()
                mplt.plot(specxxcomp , specyycomp, label='j2')
                mplt.plot(specxcomp , specycomp, label='ref')
                mplt.plot(specxxcomp , specyycomp, label='j2')
                mplt.title("j1 is "+str(self.current_j1)+" j2 is "+str(self.current_j2))
                mplt.legend()
                mplt.show()
                self.start_opt = True

        return specxcomp, specycomp, specxxcomp, specyycomp

    def make_vertical_transf(self, plt, mplt, param, debug=0):
        '''
        Called in make_transf
        Vertical correction (translation and dilation) on the interval "self.interv_adjust_vert"
        Parameters:
            * param : contains the informations for the vertical transform
        modifies self.spec1['xx'], self.spec2['xx'], self.spec1['yy'], self.spec2['yy']
        '''
        
        dil, transy = param  
        if debug>0:
            print("########### make_vertical_transf ")
            print("### dil {0} , transy  {1}".format(dil, transy))

        specxcomp, specycomp, specxxcomp, specyycomp = self.in_adjust_vert(mplt)
        
        #####################
        try:
            self.spec2['yy'] = specyycomp*dil[0] # + transy             # Perform y dilation
        except:
            self.spec2['yy'] = specyycomp*dil # + transy             # Perform y dilation
        self.spec1['yy'] = specycomp # 

        if debug>0:
            print("self.spec2['yy'].size ", self.spec2['yy'].size)
            print("self.spec1['yy'].size ", self.spec1['yy'].size)

        ##### x axis

        self.spec2['xx'] = specxxcomp
        self.spec1['xx'] = specxcomp
        if self.step_dist%10 == 0 and debug>1:                     # Plot every 10 steps and if debug mode is OK. 
            print("Plot self.spec2['xx'], self.spec2['yy'] ")
            plt.plot(self.spec2['xx'], self.spec2['yy'], label=self.diffsq)   # adjustment control   

    def make_vertical_adjustement(self, nbgroup, jref, j2, plt, mplt, debug = True):
        '''
        Vertical adjustment by dilation and translation
        '''
        elem = self.infos_group[self.nbgroup]
        if debug:
            print(Fore.YELLOW + "###### Before Vertical adjustment !!!!!  ")                # Check size of the full ref retrieved
            print("element in group is element ", j2)
            print('elem[j2]["y"].size before Vertical adjustment ', elem[j2]['y'].size)
            print('elem[j2]["y"].max() before Vertical adjustment ', elem[j2]['y'].max())
            print('elem[j2]["x"][0], elem[j2]["x"][-1] before Vertical adjustment ', elem[j2]["x"][0], elem[j2]["x"][-1])
            print(Style.RESET_ALL)  # Remove color
        if debug: print('making vertical adjustment between {0} and {1} '.format(jref, j2))
        self.adjust(nbgroup, jref, j2, 'transfvert', plt, mplt, plot=False, kind_adjustment='transfvert')          # adjust with vertical dilation and translation
        elem = self.infos_group[self.nbgroup]
        #if debug: print(Style.RESET_ALL)  # Remove color
        self.pr( '#######  just before plotting k-- #######  self.dilaty {0},\
                     self.transy {1}'.format(self.dilaty, self.transy), col=Fore.GREEN)
        plt.plot(elem[j2]['x'], self.dilaty*elem[j2]['y'], 'k--')                           # adjustment control
        print('####### self.dilaty before is  ', self.dilaty)
        self.dilaty = max(0.01, min(2, self.dilaty), self.dilaty)                           # self.dilaty between min and max
        print('####### self.dilaty = ', self.dilaty)
        self.infos_group[self.nbgroup][j2]['y'] *= self.dilaty                              # modifying elem['y']
        self.infos_group[self.nbgroup][j2]['dilaty'] = 'y'
        if debug:
            print(Fore.YELLOW + "###### After Vertical adjustment !!!!!  ")                 # Check size of the full ref retrieved
            print('elem[j2]["y"].size after Vertical adjustment ', elem[j2]['y'].size)
            print('elem[j2]["x"][0], elem[j2]["x"][-1] after Vertical adjustment ', elem[j2]["x"][0], elem[j2]["x"][-1])
            print('elem[j2]["y"].max() before Vertical adjustment ', elem[j2]['y'].max())
            print(Style.RESET_ALL)  # Remove color

    def make_horizontal_translation(self, nbgroup, jref, j2, plt, mplt, debug=1):
        '''
        Horizontal translation adjustment
        '''
        if debug>0: print("in make_horizontal_translation, self.group_size is ", self.group_size)
        for i in range(0, self.group_size-1): # go through the whole group
            if debug>0:
                print("index in the group is ",i)
            self.adjust(nbgroup, jref, i, 'translat', plt, mplt, plot = False, kind_adjustment='translation')     # Adjust with translation all the element of the group on element 0
        self.timings['translation_group'] = round(time()-self.tt0, 4)
        self.jref_full = deepcopy(self.infos_group[self.nbgroup][jref])
        if debug>0: print(Fore.RED + "###### self.jref_full['x'].size  ", self.jref_full['x'].size)  # Check size of the full ref saved

    def make_horizontal_dilation(self, elem, nbgroup, jref, j2, max_line, plt, mplt, debug=0):
        '''
        Horizontal adjustment by dilation
        Plot the vertical dotted lines at the maxima positions.
        '''
        if debug>0:
            print('elem[j2]["x"][0], elem[j2]["x"][-1] just before self.plot_max_line ', elem[j2]["x"][0], elem[j2]["x"][-1])
        if max_line:                      # line for max of pdz before correction
            self.plot_max_line(plt, elem[j2]['x'], elem[j2]['y'], col='b--')   # vertical line at j2 max (dotted blue)
        print("########### in make_horizontal_dilation, self.interv_analysis ", self.interv_analysis)
        #self.interv_adjust = self.interv_analysis !!!! big errrooorrr
        interm_adjust = self.interv_adjust.copy()
        self.interv_adjust = self.interv_analysis 
        self.adjust(nbgroup, jref, j2, 'dilat', plt, mplt, plot=False, kind_adjustment='dilation', debug=False)    # adjust horizontally position of j2 
        self.timings['dilation'] = round(time()-self.tt0, 4)
        if max_line:
            self.plot_max_line(plt, self.spec1['x'], self.spec1['y'], col='k--')  # line for max ref    # vertical line at jref max (dotted black)
        self.interv_adjust = interm_adjust

    def select_pair(self, nbgroup, jref, j2):
        '''
        Select spectra self.spec1 : S1 and self.spec2 : S2
        S2 will be adjusted on S1
        Parameters:
            * nbgroup : index of the group
            * jref : index of the reference
            * j2 : index of the target
        '''
        self.jref, self.j2 = jref, j2
        self.spec1 = self.filter(nbgroup, jref)    # Makes self.spec1['x'] and self.spec1['y']
        self.spec2 = self.filter(nbgroup, j2)      # Makes self.spec2['x'] and self.spec2['y']

    def filter(self, nbgroup, j, debug=1):
        '''
        Take the corrected profile and cut on the bounds [liminf, limsup] for the adjustment.
        Parameters:
            * nbgroup : index of the group
            * j: index in the group
        '''
        if debug>0: print("#### self.infos_group    ", self.infos_group)
        elem = self.infos_group[nbgroup][j]
        x, y = elem['x'], elem['y']
        sl = np.where((x > self.interv_adjust[0]) & (x < self.interv_adjust[1]))    # liminf, limsup
        spec = {'x': x[sl],'y': y[sl]}    # spectrum with bounds
        if debug>0: 
              print("#### self.interv_adjust[0], self.interv_adjust[1] ", self.interv_adjust[0], self.interv_adjust[1])                                        
        return  spec

    def filter_interp(self, nbgroup, j, xsl=None, nbpts=100, on_adjust=False, debug=False):
        '''
        Cuts the profile j and permits comparison between two profiles.
        Parameters:
            * nbgroup : index of the group
            * j : index of the profile in the group
            * xsl : x range for making two corresponding spectra
            * nbpts : number of points for the interpolation
            * debug : if True, debug mode is activated
        '''
        elem = self.infos_group[nbgroup][j]
        if on_adjust:
            x, y = elem['spec_adj_x'], elem['spec_adj_y']  # taking values after adjustment. 
        else:
            x, y = elem['x'], elem['y']
        sl = np.where((x > self.interv_adjust[0]) & (x < self.interv_adjust[1]))    # liminf, limsup
        g = interp1d(x[sl], y[sl], kind='cubic')            # interpolation
        xmin, xmax = x[sl].min(), x[sl].max()
        if debug : print("##### entering xsl is ", xsl)
        if xsl == None:
            if debug : print("Decision that xsl == None ")
            xsl = np.linspace(xmin, xmax, nbpts)  # Create  xsl
        else:
            if debug : print("xsl != None ")
            sll = np.where((xsl > xmin) & (xsl < xmax))     # liminf, limsup
            xsl = xsl[sll]
            if debug : print("##### new xsl is ", xsl)
        ysl = g(xsl)                                        # new spectrum
        spec = {'x': xsl,'y': ysl}                          # x and y on regular sampling
        return  spec

    def make_axis(self, param):
        '''
        New axis self.x for coping with changing axis bounds with dilation.
        Same axis self.x used for S1 and S2 handling.
        Parameters:
            * param : param for the current operation, i.e dilation or translation
        '''
        self.dilat, self.translat = 1, 0 # Initialize
        if self.op == 'dilat':
            self.dilat = param
        elif self.op == 'translat':
            self.translat = param
        minax = max(self.spec1['x'].min(), self.spec2['x'].min()*self.dilat+self.translat)
        maxax = min(self.spec1['x'].max(), self.spec2['x'].max())
        self.x = np.linspace(minax, min(maxax , self.interv_adjust[1]), self.size*self.coeff_mult_size) # Same for both
        
    def interp(self, spec, make_op=False, debug=False):
        '''
        Interpolations for comparing S1 and S2 for horizontal adjustment.
        Takes into account the dilation for values > 1 and < 1
        Parameters:
            * spec : spectrum used for adjustment.
            * make_op : if False there is no adjustment. 
            * debug : print debug informations
        Results : 
            * 
        '''
        if not make_op :
            dilat, translat = 1,0
        else:
            dilat, translat = self.dilat, self.translat
        t0 = time()
        if debug:
            print("kind of interpolation is ", self.interp_kind)
        spec['interp'] = interp1d(spec['x']*dilat + translat, spec['y'], kind=self.interp_kind)
        if debug:
            print("make_op", make_op)
            print("interpolation range is [{0},{1}] ".format((spec['x']*dilat+ translat).min(), (spec['x']*dilat+ translat).max())) # 
        t1  = time() 
        adjust_time = t1-t0 # Processing time for adjustment
        if debug:
            print('time elapsed is {0} '.format(adjust_time))
        if  self.translat <= 0 : #self.dilat <= 1
            ll = np.where(self.x < self.x.max()*self.dilat+self.translat)
        elif self.translat > 0 : #self.dilat > 1
            ll = np.where(self.x > self.x.min()*self.dilat+self.translat)
        spec['xx'] = self.x[ll]
        spec['yy'] = spec['interp'](spec['xx'])
        self.list_dilat.append(self.dilat)        # List of values taken by dilation parameter.
        self.list_translat.append(self.translat)  # List of values taken by translation parameter.
        
    def init_ffmpeg(self, plt):
        '''
        Initialize video tool for following adjustment convergence.
        '''
        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie', artist='Matplotlib',
                        comment='')
        self.writer = FFMpegWriter(fps=15, metadata=metadata)
        self.fig = plt.figure()

    def translate_and_detect_maxchange(self, plt, jref=None, plot=False, debug=False):
        '''
        Make translation and find automatically the zone (analysis interval) for calculating the Binding Index.
        The analysis interval is found by comparing in a given group the spectra and finding where they change the more.
        It is assumed that the dilation is not too strong. Only the translation correction is performed.
        For each group is recorded the value 'xmaxchange'
        Parameters:
            * plot :
            * debug : 
        '''
        if debug:
            print("###### in translate_and_detect_maxchange ")
        dic_diff_max = {} # Dictionary keeping maximal changes with position.
        for i in range(0, self.size_groups-1): # go through the whole group
            if debug:
                print("index in the group is ",i)
            self.adjust(self.nbgroup, jref, i, 'translat', plt, mplt, plot = plot, kind_adjustment='translation') # Adjust with translation all the group
            y0 = self.infos_group[self.nbgroup][0]['spec_adj_y']
            yi = self.infos_group[self.nbgroup][i]['spec_adj_y']
            diff = np.abs(y0-yi)  
            if debug:
                print("max diff is ", diff.max())  # Maximal displacement
            dic_diff_max[diff.max()] = np.where(diff == diff.max()) # list of all the positions with maximal difference.
        x = self.infos_group[self.nbgroup][0]['spec_adj_x']
        self.infos_group[self.nbgroup]['xmaxchange'] = x[dic_diff_max[max(dic_diff_max)]][0] # position of the maximal change over all the wells
        if debug:
            print('################ xmaxchange', self.infos_group[self.nbgroup]['xmaxchange'])
        if plot:
            plt.show()
