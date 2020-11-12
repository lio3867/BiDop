#!/usr/bin/env python 
# encoding: utf-8

"""
 plot_bokeh.py,v 1.0 july 2016
 Library for replacing transparently Matplotlib by Bokeh

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
from time import time

### Numerical libraries

import numpy as np

### Visualization

import bokeh.plotting as bk
from bokeh.models import Range1d, ColumnDataSource, OpenURL, TapTool, HoverTool
from bokeh.plotting import output_file
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from itertools import cycle

class BOKEH_PLOT(object):
    '''
    Mimicking Matplotlib library with Bokeh
    Usage eg: 
        plt = BOKEH_PLOT()
        x = np.arange(120)
        plt.plot(x, x**2, 'r', label='simple square')
        plt.title("first")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.savefig('first_fig.html')
    Data for tests :
        /encours/Casc4de/Projets/ElectrophorèseCapillaire/Test_384_3juin16
        /encours/Casc4de/Projets/ElectrophorèseCapillaire/HOLD_UP/NatureMethods15_SupplementaryFiles/suppl_data_new/Archive_S1/PDZome_16_18E6_384/VIPS_33_1_1
        
    '''
    def __init__(self, zoom = None, color = 'olive', bokeh_range = None,
            path_file = "bk.html", plot_width = 500, plot_height = 500,
            bkfig = None, debug=False):
        self.debug = debug
        self.zoom = zoom
        self.color = color
        self.bokeh_range = bokeh_range
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.bkfig = bkfig
        self.xlab = None             # xlabel
        self.ylab = None             # ylabel
        self.tit = None              # Title
        self.path_file = path_file   # Path for storing the html file
        self.index_path_file = 1
        self.figure(show=False)
        self.list_plot = []          # list for recording plots informations.
        
    def plot(self, x, y, kindline_and_color='-', label=None, tap=False, size_val = 3, static_label=None ):
        '''
        Record plot coordinates and label
        Parameters:
            * x: x axis, list or numpy array
            * y: y axis, list or numpy array
            * kindline_and_color: example : "r--"
            * label: label for the given curve
        '''
        self.static_label = static_label
        size = [size_val]*len(x)
        diccol = {'r':'red', 'b':'blue', 'g':'green', 'o':'orange', 'k':'black', 'm':'magenta'}
        first = kindline_and_color[0]
        if first.isalpha():
            col = first
            if kindline_and_color[1:] != '':
                kindline = kindline_and_color[1:]
            else:
                kindline ='-'
        else:
            #col = self.coliter.next() # old syntax
            col = next(self.coliter)  # renewed at each figure call
            kindline = kindline_and_color
        ###  transform to np.array
        if type(x) == list: x = np.array(x) # 
        if type(y) == list: y = np.array(y) # 
        dic_kindline = {'-':'solid', '--':'dashed', '*':'dotted'}
        self.list_plot.append({'x': x,'y': y, 'label': label, 'color': diccol[col],
                            'kindline': dic_kindline[kindline], 'tap': tap, 'size':size}) #
        self.showed = False
        self.fig = False
                                                       
    def xlabel(self, xlabel):
        '''
        xlabel for the plot
        '''
        self.xlab = xlabel
        
    def ylabel(self, ylabel):
        '''
        ylabel for the plot
        '''
        self.ylab = ylabel
    
    def title(self, title):
        '''
        Title for the plot
        '''
        self.tit = title
    
    def figure(self, show = True):
        '''
        Create a new figure
        Called with show=False at beginning 
        '''
        if self.debug:
            print("###########   new figure  !!! ")
        self.coliter = cycle(['b', 'g', 'r', 'm', 'o', 'k']) # Colors for the plots
        if show:
            if self.debug:
                print("make show")
            self.show()
        self.namefig = self.path_file[:-5] + str(self.index_path_file) +'.html'
        output_file(self.namefig)
        if self.debug:
            print("making figure : ", self.namefig)
        self.index_path_file += 1
        self.TOOLS="crosshair, pan, wheel_zoom, box_zoom, reset,  save"    # Tools for Bokeh,  resize, , undo, redo

        # tap, box_select,

        #### Reinitialize
        
        self.xr = None
        self.yr = None
        if self.debug:
            print("self.xr ", self.xr)
            print("self.yr ", self.yr)

    def legend(self):
        pass

    def find_range(self):
        '''
        Find Range for calculating self.xr and self.yr
        '''
        xmin = self.list_plot[0]['x'][0]
        xmax = self.list_plot[0]['x'][-1]
        ymin = self.list_plot[0]['y'][0]
        ymax = self.list_plot[0]['y'][-1]
        for l in self.list_plot:
            if l['x'][0] < xmin : xmin = l['x'][0]
            if l['x'][-1] > xmax : xmax = l['x'][-1]
            if l['y'].min() < ymin : ymin = l['y'].min()
            if l['y'].max() > ymax : ymax = l['y'].max()
        if self.debug:
            print("xmin, xmax, ymin, ymax ", xmin, xmax, ymin, ymax)
        if self.bokeh_range:
            self.xr, self.yr = self.bokeh_range
        else:  
            if not self.xr:
                if self.debug:
                    print("### range x not yet defined !!! ")
                self.xr = Range1d(start = xmin, end = xmax)   # x range for Bokeh
            if not self.yr:
                if self.debug:
                    print("### range y not yet defined !!! ")
                self.yr = Range1d(start = ymin, end = ymax)   # y range for Bokeh

    def hoverlegend(self, l, genhover, hover_icon=True, debug=False):
        '''

        Legend compacified with hover tool

        '''
        if l['label']:                             # Make the label only if there is a label registered.
            infohover = next(genhover)             # syntax for Python3.

            #deltay = self.ymax
            if debug: print('########## making hover legend, current plot for {0} !!!!!!!!'.format(l['label']))
            source = ColumnDataSource(
            data=dict(
                x=[infohover['x']],
                y=[infohover['y']],
                desc=[l['label']],
                col=[l['color']],
                )
            )
            hover = HoverTool(
                tooltips="""
            <div > 
                <div>
                    <span style="font-size: 15px; ">@desc</span>
                    <span style="font-size: 15px; color: #696;">    </span>
                </div>
            </div>
            """, names=[infohover['id']]
            )
            # print('######### the associated label is {0} '.format(l['label']))
            self.bkf.square('x', 'y', size=10, name=infohover['id'], color= l['color'], source=source)
            if hover_icon:
                self.bkf.add_tools(hover)               # Add tool to the figure

    def show(self, show_logo=False, hover_icon=True, save=True):
        '''
        Parameters:
            * show_logo : if True show Bokeh logo
            * save : if True don't show figure and just save.
        '''
        if self.debug:
            print("make show")
        self.find_range()
        if self.debug:
            print(" 'x_range': {0}, 'y_range': {1}".format(self.xr, self.yr))
        dbk = {'tools': self.TOOLS,'x_range': self.xr, 'y_range': self.yr,
                       'title': self.tit, 'x_axis_label': self.xlab, 'y_axis_label': self.ylab,
                       'plot_width' : self.plot_width, 'plot_height' : self.plot_height}              # Parameters for the plot
        if self.bkfig:
            self.bkf =  self.bkfig    # Take the existing figure
        else:
            if self.debug:
                print("# create new figure")
            self.bkf = bk.figure(**dbk)                          # Creates a new figure for original spectrum
            if self.debug:
                print(" dir(self.bkf) ", dir(self.bkf))
                                 # Make the tooltip legend
         # Find position near corner upper right
        try:
            genhover = infos_hover(self.list_plot, self.ymax).gen()             # Generate information for hover legend
        except:
            genhover = infos_hover(self.list_plot).gen()             # Generate information for hover legend
        for i, l in enumerate(self.list_plot):
            self.hoverlegend(l, genhover, hover_icon=hover_icon)
            if self.debug:
                print("l['kindline'] ", l['kindline'])
            if l['kindline'] != 'dotted':
                if self.debug:
                    print("######### using lines")
                try :
                    if self.static_label:
                        legend = l['label']
                    else:
                        legend = None
                except:
                    legend = None
                self.bkf.line(l['x'], l['y'], line_color = l['color'], legend=legend, line_dash=l['kindline'])      # Plot
            else:
                if self.debug:
                    print("l['tap']: ", l['tap'])
                source = ColumnDataSource(data=dict( x=list(l['x']), y=list(l['y']), tap=l['tap'], size=l['size'] ))
                url = "@tap"
                if l['tap']:
                    if self.debug:
                        print("############# making the callback  ")
                    self.bkf.circle('x', 'y', line_color = l['color'], fill_color = l['color'], legend=l['label'], size = 'size', source=source)
                    taptool = self.bkf.select(type=TapTool)
                    taptool.callback = OpenURL(url=url )#l['tap']
                else:
                    self.bkf.circle(l['x'], l['y'], line_color = l['color'], fill_color = l['color'], legend=l['label'], size=l['size'])
        self.bkf.title.align  = 'center'  # Center the title (by default on the left) ## title_text_align Plot.title.align
        if not show_logo:
            self.bkf.toolbar.logo = None # Hide the Bokeh logo
        if save :
            bk.save(self.bkf)  # save the plot without showing it.
        else:
            bk.show(self.bkf) # show the plot in the browser
        self.list_plot = []
        self.showed = True
        if self.debug:
            print("##### showed")
        if self.fig:
            os.rename(self.namefig, self.namehtml)
        self.fig = False
        #self.figure(show=False)

    def xlim(self, xmin, xmax):  # x limits for the plot
        if self.debug:
            print("defining xmin: {0} and xmax:{1} ".format(xmin, xmax))
        self.xr = Range1d(start = xmin, end = xmax)

    def ylim(self, ymin, ymax):  # y limits for the plot
        if self.debug:
            print("defining ymin: {0} and ymax:{1} ".format(ymin, ymax))
        self.ymax = ymax
        self.yr = Range1d(start = ymin, end = ymax) 
    
    def savefig(self, namehtml):
        '''
        Rename figure
        Parameters:
            * namehtml : name of the html bokeh file.
        '''
        if self.debug:
            print("### savefig as {0} ".format(namehtml))
        if self.showed:
            if self.debug:
                print("######", self.namefig)
            os.rename(self.namefig, namehtml)
        else:
            self.fig = True
            self.namehtml = namehtml

class infos_hover():
    '''
    Find corner and increment position down in y direction.
    '''
    def __init__(self, list_plot, ylim_max=None):
        self.xmax = 0
        self.ymax = 0
        for l in list_plot:                # Find the maximum in x,y in all the plots for a single figure.
            if self.xmax < max(l['x']): 
                self.xmax = max(l['x'])*0.9
            if self.ymax < max(l['y']): 
                self.ymax = max(l['y'])*0.9
            if ylim_max:
                self.ymax = ylim_max*0.9
        self.index = -1

    def gen(self):  # Generator for producing informations for the hover square tool. 
        while 1:
            self.index += 1
            yield {'x': self.xmax, 'y': self.ymax*(1-0.05*self.index), 'id': str(self.index)}

if __name__=='__main__':

    plt = BOKEH_PLOT(debug=False) # instantiate Bokeh in replacement to Matplotlib
    print(dir(plt))
    #####
    print("############## example 1 ###############")
    x = np.arange(120)
    plt.plot(x, x**2, 'r--', label='simple square')
    plt.title("fig 1")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.savefig('fig1.html')
    plt.figure()
    #################
    print("############## example 2 ###############")
    plt.plot(x, -x**3-2*x**2+4, 'g-', label='curve')
    plt.title("fig 2")
    plt.xlabel("xsec")
    plt.ylabel("ysec")
    plt.ylim(-2e6, -5e5)
    plt.savefig('fig2.html')
    plt.figure()
    #################
    print("############## example 3 ###############")
    ll = ["http://www.colors.commutercreative.com/orange/"]*x.size
    path = 'file://' + os.getcwd()
    #ll = [os.path.join(path,"processing_nbgroup_{0}_.html".format(i+1)) for i in range(4)]
    plt.plot(x, -x**2*2+4, 'k*', label='curve dot')
    plt.title("fig 3")
    plt.plot(x, x**3+4*x, 'r*', label='sec curv dotted') # , tap=ll
    plt.xlabel("xx")
    plt.ylabel("yy")
    plt.xlim(20,60)
    plt.ylim(-1e5, 7e5)
    plt.savefig('fig3.html')
    plt.figure()
    #################
    print("############## example 4 ###############")
    plt.plot([0,20], [0,20], 'r-', label='curve')
    x = np.arange(120)
    plt.plot(x, x**2, 'g', label='sec curve') #, label='simple square'
    plt.title("fig 4")
    plt.xlabel("x")
    plt.ylabel("y")
    
    plt.show()
    plt.savefig('fig4.html')
