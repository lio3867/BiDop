#!/usr/bin/env python 
# coding: utf8


"""
plot_adj.py,v 1.0 2016/05/12

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
global plt

import os
import json, pickle
import numpy as np
from colorama import Fore, Back, Style
from .plot_bokeh import BOKEH_PLOT
plt = BOKEH_PLOT()
plt.plot_width = 400 # good width seems to be 400
plt.plot_height = 400 # good height seems to be 400

try:
    from scipy.interpolate import interp1d
    from scipy.optimize import fmin # fmin_powell, fmin_l_bfgs_b, golden, fminbound
except:
    print("Couldn't import scipy libraries")

class PLOTS(object):
    '''

    '''
    def __init__(self):
        pass


    def save_png_or_html(self, plt, j2, debug_plot=0):
        '''
        save the png or html 
        '''
        plot_root = 'proc_grp_{0}_{1}_dilat'.format(self.nbgroup, j2)
        if debug_plot>0:
            print("#### plt.list_plot ", plt.list_plot)        # inspect inside object plt
            print("Ranges for plot are : plt.xr = {0} and plt.yr =  {1} ".format(plt.xr, plt.yr))          # range for x and y 
        plt.legend()
        name_plot_png = plot_root + '.png'
        name_plot_html = plot_root + '.html'
        if hasattr(plt,'path_file'):
            name_plot = name_plot_html
        else:
            name_plot = name_plot_png
        
        if self.save_dilation:
            print("### Save dilation")
            name_dilat_plot = os.path.join(self.folder, name_plot)
            plt.savefig(name_dilat_plot)                          # dilation plot
            print("### saved figure with name ", name_plot)
        else:
            plt.__init__()                                        # Reinitialize plt

    def pickle_after_dilat(self, plt, j2, debug_plot=0):
        '''
        pickle after dilation
        '''
        if debug_plot>0: print('pickleing horizontal dilation')                     
        plot_root = 'proc_grp_{0}_{1}_dilat'.format(self.nbgroup, j2)
        pickle_adjust_dilat = os.path.join(self.folder, plot_root + '.p')      # pickle all plots after dilation adjustment
        with open(pickle_adjust_dilat, "wb") as f:
            pickle.dump(plt.list_plot, f)

    def pickle_after_verticalcorr(self, plt, j2, debug_plot=0):
        '''
        pickle vertical correction
        '''
        if debug_plot>0:
            print('Making vertical transformation')
        plot_root = 'proc_grp_{0}_{1}_trsfvert'.format(self.nbgroup, j2)
        pickle_adjust_dilat = os.path.join(self.folder, plot_root + '.p')       # pickle the vertical adjustment
        with open(pickle_adjust_dilat, "wb") as f:
            pickle.dump(plt.list_plot, f)

    def debug_plot_adjust_plot(self, i, elem):
        '''
        '''
        print("index in the group is ", i)
        print("elem['spec_adj_x'].size ", elem['spec_adj_x'].size)
        print("elem['spec_adj_y'].size ", elem['spec_adj_y'].size)
        print("elem['spec_adj_x'] [min,max] :[{0},{1}] ".format(elem['spec_adj_x'].min(), elem['spec_adj_x'].max()))
        print("elem['spec_adj_y'] [min,max] :[{0},{1}] ".format(elem['spec_adj_y'].min(), elem['spec_adj_y'].max()))

    def make_plot_adjust_bokeh(self, plt):
        '''
        '''
        data = self.infos_group[self.nbgroup][0]
        plt.plot(data['mol_norm_size'], data['mol_norm_val_corr'], 'r', label='normalization peak') # plot in red the normalization
        plt.xlim(self.plot_liminf, self.plot_limsup)
        plt.legend()
        if self.save_dilation:                                 # show after dilation
            print("#### self.save_dilation is ", self.save_dilation)
            plt.show()

    def plot_adjust(self, plt, jref=None, j2=None, plot=False, show=False, title='',
                save=False, newfig=True, col='-', plot_both = True, save_pickle=False,
                label_corr=False, save_adjustment=True,  debug_plot=0):
        '''
        i in [jref,j2]
        Save adjusted spectra in self.infos_group[self.nbgroup][i]['x'] and self.infos_group[self.nbgroup][i]['y'] for other operations.
        Parameters:
            * jref : index of the reference
            * j2 : index of the target 
            * show : Necessary for having a html file.
            * title : title of the plot
            * save : save the figure with a given name
            * newfig : make a new figure
            * col : color of the plot. If there are two plots, col is entered for example with 'k-- g-' for plotting a black dotted line and a green line.
            * plot_both : If True plot ref and j2
            * save_pickle : save the plot in condensed shape
            * label_corr : if True, indicates in the legend that the plot is a correction.
            * debug : show the debugging messages
        '''
        if debug_plot>0:
            print("########################### in plot_adjust")
        # for i in range(self.size_groups):
        #     if i == j2:
        if newfig and hasattr(plt,'bk'): # case : new fig and Bokeh plot
            print('###############    making a new figure ')
            plt.figure(show=False)
        kc = {}
        if debug_plot>0:
            print("########### col ", col)
        if col != '-':
            if debug_plot>0: print("########### not -")
            if plot_both:
                kc[jref] = col.split()[0]
                kc[j2] = col.split()[1]
            else:
                kc[j2] = col
            if debug_plot>0: print("######## kc ", kc)
        for i in [jref,j2]:
            elem = self.infos_group[self.nbgroup][i]
            interi = elem['mol_interact']               # adjusted molecule
            if label_corr:
                interi += '_corr'
            if debug_plot>0:
                self.debug_plot_adjust_plot(i, elem)

            # Save adjustment
            
            if save_adjustment:
                elem['x'] = elem['spec_adj_x']
                elem['y'] = elem['spec_adj_y']

            if debug_plot>0:
                print("############# plot value is ", plot)
            if plot:
                if debug_plot>0:
                    print("######  after plot")
                plt.title(title)
                if plot_both or ((not plot_both) and i==j2) : # plot with ref or only non ref
                    if plot_both:
                        if debug_plot>0:
                            print("##### kindlinecolor is ", kc[i])
                    if self.makebokeh:
                        try:  
                            plt.plot(elem['x'], elem['y'], label=interi, kindline_and_color=kc[i])    # Bokeh plot with name of the interaction
                        except:
                            plt.plot(elem['x'], elem['y'], label=interi)         # adjustment control
                if debug_plot>0:
                    for lp in plt.list_plot:
                        print(Fore.BLUE + "lp['label'] : {}".format(lp['label']))
                        print(Fore.BLUE + "lp['x'].size : {}".format(lp['x'].size))
                        print(Style.RESET_ALL)

        if save_pickle:
            if self.kind_adjustment == 'dilation': 
                self.pickle_after_dilat(plt, j2)
            if self.kind_adjustment == 'transfvert':
                self.pickle_after_verticalcorr(plt, j2)

        if self.makebokeh:                            # Make the Bokeh plots
            if show:
                self.make_plot_adjust_bokeh(plt)
            if save: 
                self.save_png_or_html(plt, j2)

            print("######################### end plot_adjust")

    def plot_baseline_group(self, plt, mplt, nbgroup, show_baseline=False, show_with_corr=False,
                         show_both=False, show_all_bls=False, newfig=False, debug=True):
        '''
        Plot the result of processing for a given group.
        Parameters:
            * nbgroup : index of the plotted group.
            * show_with_corr : 
                - True : the spectra are shown with the baseline correction. 
                - False : show the spectra with the baseline.
            * show_all_bls : 
                - True : all the evolutions of the baseline in function of the iterations are shown. 
            * newfig : plot the elements of the group separately
        '''
        group_data_proc = self.infos_group[nbgroup] # Take the informations from group number nbgroup
        self.baseline_folder = os.path.join(self.folder,'proc_grp_{0}'.format(nbgroup))
        try:
            os.mkdir(self.baseline_folder)
        except:
            print("self.baseline_folder yet existing")
        for pos in group_data_proc:                    # pos :  position in the group
            if type(pos) == int:                       # Avoid taking general information 
                # print(pos)
                data = group_data_proc[pos]     
                if newfig:
                    if hasattr(plt,'path_file'):
                        print('####### chosing Bokeh')
                        plt.figure(show=False)
                    else:
                        print('####### chosing Mpl')
                        plt.figure()
                # print('######### DATA !!!' , data)
                # print('type(data) ' , type(data))
                absc = data['size_trunc']
                if debug: print("#### absc[-1] {0} ".format(absc[-1]))
                ###
                if show_with_corr : 
                    plt.title('Baseline corr grp_{0}'.format(nbgroup)) #             
                    plt.plot(absc, data['val_corr'], 'k-', label= data['mol_interact'] + '_corr')           # Show the profile with baseline correction
                    plot_root = 'baseline_corr_grp_' + str(nbgroup) + '_' + str(pos)
                ### 
                elif show_both:  
                    plt.title('Baseline corr nocorr grp_{0}'.format(nbgroup)) #   
                    plt.plot(absc, data['val_corr'], 'k-', label= data['mol_interact'] + '_corr')           # Show the profile with baseline correction
                    plt.plot(absc, data['value'][data['size_index_cut']], 'm--', label=data['mol_interact']) # Show the original profile
                    plot_root = 'baseline_corr_nocorr_grp_' + str(nbgroup) + '_' + str(pos)
                ###
                elif show_baseline:
                    plt.title('Baseline grp_{0}'.format(nbgroup)) # 
                    plt.plot(absc, data['value'][data['size_index_cut']], 'k-', label=data['mol_interact']) # Show the original profile
                    plt.plot(absc, data['bl'], 'g-', label='baseline')                                      # Show  baseline
                    plot_root = 'baseline_grp_' + str(nbgroup) + '_' + str(pos)
                ###
                else:
                    try:
                        plt.title('Rawdata grp_{0}'.format(nbgroup)) # 
                        plt.plot(absc, data['value'][data['size_index_cut']], 'k-', label=data['mol_interact']) #  Rawdata  
                        ref = group_data_proc[3]                                           # taking the reference (last one) 
                        plt.plot(absc, ref['value'][ref['size_index_cut']], 'g-', label='reference')            #  plot rawdata                      
                        plot_root = 'rawdata_grp_' + str(nbgroup) + '_' + str(pos)
                        #plt.legend()
                    except:
                        print("cannot plot the rawdata")
                plt.plot(absc, np.zeros(data['size_trunc'].size), 'b--')                                    # Floor y=0 axis
                for bb in data['bls']['bl']:                                                                # Show all the evolutions of the baselines.
                    if show_all_bls:
                        plt.plot(absc, bb)
                maxy = data['bl'].max()                                                                     # Val max for profile
                miny = data['bl'].min()                                                                     # Val min for profile
                plt.plot(data['mol_norm_size'], data['mol_norm_val_corr'], 'r', label='normalization peak') # Plot in red the spectrum on the range used for normalization
                plt.xlabel('size')
                plt.ylabel('value')
                plt.xlim(self.plot_liminf, self.plot_limsup)      # x plot range 
                marg = 1-0.5*np.sign(miny)              
                plt.ylim(miny*marg, maxy*3)                 #  y zoom 
                
                plt.legend()
                # if show_with_corr :
                #     plot_root = 'baseline_corr_grp_' + str(nbgroup) + '_' + str(pos)
                # elif show_both:
                #     plot_root = 'baseline_corr_nocorr_grp_' + str(nbgroup) + '_' + str(pos)
                # else:
                #     plot_root = 'baseline_grp_' + str(nbgroup) + '_' + str(pos)
                name_plot_png = plot_root + '.png'
                name_plot_html = plot_root + '.html'
                if hasattr(plt,'path_file'):
                    name_plot = name_plot_html
                else:
                    name_plot = name_plot_png
                print("### save with key ", plot_root)
                pickle_baseline = os.path.join(self.baseline_folder, plot_root+'.p')
                pickle.dump(plt.list_plot, open(pickle_baseline, "wb"))
                
                #### Save
                if debug:
                    print(Fore.BLUE + '################# len(plt.list_plot) {0} !!!!!'.format(len(plt.list_plot)))
                    print(Style.RESET_ALL)
                
                if self.save_baseline:                                           # Save the baseline
                    plt.show()
                    plt.savefig(os.path.join(self.baseline_folder, name_plot))
                    print("### saved figure with name ", name_plot)
                else:
                    plt.__init__()                                               # Reinitialize the "plt" object

                ### Western blot
                
                self.plot_gel(mplt, pos)

    def plot_all_baselines(self, plt, mplt, nbgroup, debug=0):
        '''
        Plot the different baselines
        '''
        self.plot_baseline_group(plt, mplt, nbgroup,  show_baseline = True, newfig = True)      # Profile without correction and baseline
        self.plot_baseline_group(plt, mplt, nbgroup,  show_with_corr = True, newfig = True)     # Profile with baseline correction
        self.plot_baseline_group(plt, mplt, nbgroup,  show_both = True, newfig = True)          # Profile with and without baseline correction
        self.plot_baseline_group(plt, mplt, nbgroup,  newfig = True) 

    def plot_max_line(self, plt, xxx, yyy, label=None, col='k--', debug=False):
        '''
        Vertical line centered on the max for controlling the adjustment. 
        Cubic interpolation is used for increasing the number of points and having a more precise maximum.
        Parameters:
            * xxx : 
            * yyy :
            * label :
            * col :
        '''
        if debug:
            print("###### xxx ", xxx)
            print("###### yyy ", yyy)
            print("#### self.interv_analysis in plot_max_line ", self.interv_analysis)
        ia = self.interv_analysis
        if debug: print("self.interv_analysis ", self.interv_analysis)
        interv_analysis = np.where((xxx > ia[0]) & (xxx < ia[1])) # Interval where is calculated the BI
        xan = xxx[interv_analysis]
        yan = yyy[interv_analysis]
        # try:
        xmax = xan[yan==yan.max()]
        interv_reduced = np.where((xan > xmax-1) & (xan < xmax+1))
        xx = xan[interv_reduced]
        yy = yan[interv_reduced] 
        g = interp1d(xx, yy, kind='cubic')
        x = np.linspace(xx.min(), xx.max(), xx.size*self.mult_density)
        y = g(x)
        interv = np.where((x > xmax-1) & (x < xmax+1))
        ymax = y[interv].max()
        xmax = float(x[interv][y[interv] == ymax])
        plt.plot([xmax, xmax],[0, ymax], col, label=label)
        # except:
        #     print("Issue with maximum and interval")

    def plot_ref_pdz(self, plt, elem, jref, j2, debug=0):
        '''
        Plot ref and pdz
        '''

        if debug>0: print("self.verticalcorr ", self.verticalcorr)
        self.plot_adjust(plt, jref, j2, plot=True, save=False, show=False,\
            newfig=True, save_adjustment=not(self.verticalcorr), col='k- b--')     # Plot reference and pdz
        if debug>0: print(Fore.RED+'After self.plot_adjust, elem[j2]["x"][0],\
            elem[j2]["x"][-1] just before self.plot_max_line ', elem[j2]["x"][0], elem[j2]["x"][-1])
        print(Style.RESET_ALL)

    def pck2bkh_manyplots(self, plt, listpicklefile, bokehname, debug=True):
        '''
        Producing Bokeh plots from pickle files for the superimposition tool in plate.html
        Parameters:
            * listpicklefile : input name for the list of pickles to be plotted.
            * bokehname : output name for the Bokeh file (format .html)
        d[1], d[4], plot after first correction and corrected plot
        '''
        
        plt.fig = False
        if debug: print('In pck2bkh_manyplots !!!!!!!')
        ymax = 0
        title_manyplt = 'Profiles Comparison'
        for p in listpicklefile:
            if debug: print("p is ", p)
            #try:
            d = pickle.load(open(p, "rb" ))
            #print("############# d.size in pck2bkh_manyplots is ", d.size)
            #title_manyplt += d[1]['label'] +'\n'
            if d[1]['y'].max() > ymax:
                ymax = d[1]['y'].max() 
            col = next(self.coliter)
            try:
                d[4]['color'] = col     # plot after second correction (processing)
            except:
                if debug: print("no d[4]['color']")
            d[1]['color'] = col     # plot after first correction (preprocessing)

            d[1]['label'] = None
            d[1]['kindline'] = 'solid'
            plt.list_plot.append(d[1])
            try:    
                plt.list_plot.append(d[4])
            except:
                if debug: print("no plt.list_plot.append(d[4])")
            # except:
            #     print("can't find the pickle")

        #### plot parameters

        plt.ylim(-ymax/10, ymax) # lim inf and sup
        plt.xlim(self.plot_liminf, self.plot_limsup)
        plt.xlabel('size')
        plt.ylabel('value')
        plt.title(title_manyplt)
        plt.legend()

        #####

        plt.show(hover_icon=False)
        plt.savefig(bokehname)

    def plot_gel(self, mplt, j, debug=0):
        '''
        Gels
        Makes the gels vertically
        '''
        # mplt.figure()
        elem = self.infos_group[self.nbgroup]
        y = elem[j]['y'][::-1]   #  [x>25]
        N = y.size
        mat = np.empty((N, N))
        for i in range(N):
            mat[i,:] = y[i]
        fig = mplt.imshow(mat, cmap='Greys')
        #fig = mplt.plot(np.arange(N),mat[0,:])
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        namefig = os.path.join(self.baseline_folder, 'gel_'+str(j))
        mplt.savefig(namefig, bbox_inches='tight', pad_inches=0)
        fig.remove()
        if debug>0:
            mplt.figure()
            mplt.plot(elem[j]['x'], elem[j]['y'])
            namey = os.path.join(self.baseline_folder, 'gely_'+str(j)+'.png')
            mplt.savefig(namey)
   