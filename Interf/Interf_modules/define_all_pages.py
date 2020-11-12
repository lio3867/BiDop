#!/usr/bin/env python
# encoding: utf-8
"""
define_all_pages.py
Build the variables used by jinja needed for the views
"""
import os
import os.path as op
import shutil as sh
import glob
from flask import url_for, session
import json

Interface_subtitle = ""

class define_page(object):
    '''
    General template
    '''
    def __init__(self):
        self.body = {}
        self.header = {}
        self.footer = {}
        ### Body
        self.body['main_title'] = ""
        self.body['subtitle'] = ""
        self.body['explanations'] = ""
        ### Header
        self.header['main_title'] = ""
        self.header['presentation_interface'] = ""
        self.header['background'] = '/static/img/bindings_margin_pale.jpg' # '/static/img/bubbles.jpg'
   
        self.header['url_home'] = url_for('select_proc_visu')
        self.header['url_doc'] = url_for('documentation')
        ### Footer
        self.footer['background'] = '/static/img/black.jpg'
        self.footer['copyright'] = "Copyright@Casc4de 2016"

class define_firstpage(define_page):
    def __init__(self):
        '''
        Welcome page with link for login.
        '''
        define_page.__init__(self)
        self.header['main_title'] = 'BiDop'
        self.header['mess'] = 'Bind Domain Peptide'
        self.header['presentation_interface'] = 'Interface for extracting bindings index from Caliper measurements..'
        ###
        self.body['main_title'] = ""
        self.body['subtitle'] = ""
        self.body['explanations'] = " "
        self.body['begin'] = u"Begin \u2192"
        
class define_select_proc_visu(define_page):
    def __init__(self):
        '''
        Page for chosing between visualization of the datasets and entering the parameters.
        '''
        define_page.__init__(self)
        ### Header
        self.header['background'] = '/static/img/grey.png'
        self.header['main_title'] = "Processing or Visualization"
        self.header['presentation_interface'] = ''
        session['data_folder'] = None
        session['data_file'] = None

class define_ask_param(define_page):
    def __init__(self):
        '''
        Page for chosing the parameters of processing
        '''
        define_page.__init__(self)
        ### Header
        self.header['background'] = '/static/img/grey.png'
        self.header['main_title'] = "Prepare processing"
        self.header['presentation_interface'] = ''
        try:
            with open('data_folder.p', 'r') as f:
                data_folder = json.load(f)     # Retrieving the folder address with json
            print('#### data_folder is ', data_folder)
        except: 
            print('data_folder not found !!!')
            data_folder = '.'
        self.data_folder = data_folder
        # session['data_folder'] = data_folder
        # session['data_file'] = None

class define_make_plate(define_page):
    def __init__(self):
        '''
        Make the groups in the plate
        '''
        define_page.__init__(self)
        ### Header
        self.header['main_title'] = "Define the plate"
        self.header['presentation_interface'] = Interface_subtitle
    
class define_processing(define_page):
    def __init__(self):
        '''
        Page for launching the processing
        '''
        define_page.__init__(self)
        ### Header
        self.header['main_title'] = "Processing"
        self.header['presentation_interface'] = Interface_subtitle
        self.url_processing = url_for('processing')

class define_follow_processing(define_page):
    def __init__(self):
        '''
        Page for following the processing
        '''
        define_page.__init__(self)
        ### Header
        self.header['main_title'] = "Follow processing"
        self.header['presentation_interface'] = Interface_subtitle

class define_visu(define_page):
    def __init__(self):
        '''
        Page for the visualization of the results
        '''
        define_page.__init__(self)
        ### Header
        self.header['main_title'] = "Visualization"
        self.header['presentation_interface'] = Interface_subtitle
        self.addrproc = list_folder() 
        # print('#### self.addrproc {0}'.format(self.addrproc))

def list_folder():
    '''
    list of the folders
    '''
    dirs = os.listdir('Interf/static')
    patt = 'processing'
    lproc = [d for d in dirs if patt in d]  # Use the occurence 'processing' in the name of the dataset folder
    return lproc #[0]
       
def list_files(folder, listfiles):
    '''
    Makes the list of files in the folder.
    '''
    typefiles = [op.join( folder, kind) for kind in ['*.jpg', '*.png', '*.tif']]
    for t in typefiles:
        try:
            for f in glob.glob(t):
                if os.path.isfile(f):
                    listfiles.append(op.basename(f))
                    #sh.copy(f, os.path.join('Interf/static/img_analyzed', op.basename(f)))
        except:
            print(t)
    print("listfiles ", listfiles)
         
class define_documentation(define_page):
    def __init__(self):
        '''
        Page for the documentation
        '''
        define_page.__init__(self)
        ### Header
        self.header['main_title'] = "Documentation"
        self.header['presentation_interface'] = Interface_subtitle
    