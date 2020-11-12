#!/usr/bin/env python
# encoding: utf-8
"""
ask_data.py
"""
import sys, os
import json
try:
    from PyQt4 import QtGui
    pyqt = 'pyqt4'
    QW = QtGui.QWidget
except:
    print('no PyQt4')
try:
    from PyQt5 import QtGui, QtWidgets
    pyqt = 'pyqt5'
    QW = QtWidgets.QWidget
except:
    print('no PyQt5')

from flask import url_for, session
from bindings_extract import BINDINGS_EXTRACT

class FIND_DATA(QW):
        '''
        PyQt interface for chosing the data.
        two possible session values:
            * session['data_file'] or session['data_folder']
        '''
        def __init__(self):
            super(FIND_DATA, self).__init__()
            self.curDir = os.getcwd()
        
        def browse(self, kind = 'file', debug=False):
            '''
            Finds the folder or file.
            '''
            diagdata = {'file': 'OpenFileName', 'folder': 'ExistingDirectory'}
            if pyqt == 'pyqt4':
                meth = getattr(QtGui.QFileDialog, 'get' + diagdata[kind])
            elif pyqt == 'pyqt5':
                meth = getattr(QtWidgets.QFileDialog, 'get' + diagdata[kind])
            selected_data = meth(self, "Select_" + kind,  self.curDir)
            session['data_' + kind] = str(selected_data)
            print(type(selected_data))

            ##############

            addr = str(selected_data)
            with open('data_folder.p', 'w') as f:
                json.dump(addr, f, ensure_ascii=False)
                print("save new address of the folder to be processed  {0} !!!".format(addr))
            if debug:
                print('data_' + kind)
                print("### session['data_folder'] ", session['data_folder'])
                print("session[{0}] ".format('data_' + kind), session['data_' + kind])
                print("#### selected_data is ", selected_data)
            try:
                print("Initialize BINDINGS_EXTRACT !!! ")
                init = BINDINGS_EXTRACT(addr, interv_analysis=[45,65], interv_normalize=[8,15],
                            make_folder=True, dic_wells=True) # 
                init.make_wells_molec_dic() # Make the dictionary for correspondence between molec and wells
                print("made the dictionary for the correspondences between molec and wells ")
            except: 
                print('invalid name for folder')
            
def search_data(kind):
    '''
    Opens the PyQt interface for searching the folder
    When the folder is chosen the program stops the Qt interface. 
    '''
    if pyqt == 'pyqt4':
        app = QtGui.QApplication(sys.argv)
        ff = FIND_DATA()
        ff.browse(kind) 
        app.exit()
    elif pyqt == 'pyqt5':
        app = QtWidgets.QApplication(sys.argv)
        ff = FIND_DATA()
        ff.browse(kind) 
        sys.exit(app.exec_())
        #app.exec_()
        #app.exec()
    
if __name__ == "__main__":
   print("nothing")

