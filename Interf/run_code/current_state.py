import json
from flask import render_template,request,\
            redirect, url_for, session

def current_state(socketio, check_current_well, 
          save_current_well, save_wrong_wells):
    '''
    '''
    @socketio.on('askcurrwell', namespace='/plate_comm')
    def askcurrwell(currwell):
        '''
        Controlling the name of the current well from the server
        '''
        check_current_well(socketio)

    @socketio.on('namefolder', namespace='/plate_comm')
    def keep_current_dataset(namefolder, debug=False):
        '''
        Make a pickle of the current dataset visualized
        Permits to load this dataset when opening again the program or after reprocessing.
        '''
        if debug: print("namefolder ", namefolder)
        if namefolder:
            json.dump(namefolder, open('current_processing_folder.p', 'w'))
        return redirect(url_for('visu'))

    @socketio.on('infos_well', namespace='/plate_comm')
    def keep_current_well(infos_well, debug=True):
        '''
        Make a pickle of the current well visualized in the current folder.
        Permits to load this well when opening again the program or after reprocessing.
        '''
        if debug: print("##### infos_well ", infos_well)
        save_current_well(infos_well)
        return redirect(url_for('visu'))

    @socketio.on('wrong_wells', namespace='/plate_comm')
    def wrong_wells(infos_wrongwell, debug=False):
        '''

        Retrieve the infos about bad wells and add the info in 'dict_wells.csv'
        Receiving infos from plate.html

        '''
        save_wrong_wells(socketio, infos_wrongwell)

