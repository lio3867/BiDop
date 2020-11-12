import os, time
import json, pickle
import shutil
import subprocess

def visualisation(request, retrieve_params, debug=True):
    '''
    '''
    if debug : print("## Visualization of the processed dataset")

    ##### Reprocessing the current group 

    if request.form.get('range_analysis'):       # As the request is done from Visu it is a reprocessing                                

        list_range, list_proc_param, list_various, list_grp = retrieve_params(request)       # retrieves the params 
        range_analysis_form, range_norm_form, range_y_adjust_form = list_range               # ranges for analysis, normalization, and adjustement
        iter_form, nbchunks_form, speed_form, chck_verticalcorr = list_proc_param            # processing parameters
        addr_form, root_form = list_various                                                  # path informations
        grp_form, range_elems_form = list_grp                                                # infos about groups

        if debug:
            print("########  in Interf_modules/visualisation  !!!!!")
            print("iter_form, nbchunks_form, speed_form, chck_verticalcorr ", iter_form, nbchunks_form, speed_form, chck_verticalcorr)
            print("range_analysis_form, range_norm_form, range_y_adjust_form ", range_analysis_form, range_norm_form, range_y_adjust_form)

        ################# Fill the params dictionary to be transmitted to bindings_extract.py
        
        params = {}                                      # dictionary for gathering parameters for processing
        grp = grp_form.split('_')[1] # 
        params['groups'] = grp + '-' + grp               # groups to be processed
        params['iter'] = iter_form                       # number of iterations
        params['chunks'] = nbchunks_form                 # number of chunks for the baseline
        params['speed'] = speed_form                     # speed convergence for baseline
        params['makebokeh'] = 'True'                     # make or not the Bokeh plots
        params['range_analysis'] = range_analysis_form   # range for calculating the BI
        params['range_norm'] = range_norm_form           # range for normalization
        params['elems'] = range_elems_form #             # elements in the group to be processed
        params['root'] = root_form #                     # address of the dataset
        params['grp_elem'] = grp_form #
        params['verticalcorr'] = chck_verticalcorr       # checkbox for making or not the vertical correction
        params['range_y_adjust'] = range_y_adjust_form   # range for vertical correction
        data_folder = addr_form # 
        
        #################

        parameters = json.dumps(params)                  # Transmitting the parameters to bindings_extract.py using json format
        print("######### launching the processing")
        take_time = True
        t0 = time.time()
        cmd = "python bindings_extract.py complete {0} '{1}'".format(data_folder, parameters) # processing command line
        print("cmd is ", cmd)
        subprocess.Popen(cmd, shell='True')                                                   # Popen is non-blocking

    if request.form.get('infos_erase'):                 # Erasing the current dataset
        infos_erase = request.form.get('infos_erase')
        if debug : print('###### infos_erase is  ', infos_erase)
        json_data  = request.form.get('infos_erase')
        list_erase = json.loads(json_data)
        for erase_elem in list_erase:
            shutil.rmtree(os.path.join('Interf','static', erase_elem))  # Erase the current folder

    if request.form.get('infos_newname'):                   # Renaming the current dataset
        input_newname = request.form.get('input_newname')
        # prev_name = request.form.get('prev_name')     # Previous name
        with open('current_processing_folder.p', 'r') as f:
            prev_name = json.load(f)
        if debug :
            print('##### the previous name is {0} !!!!!!!! '.format(prev_name))
            print('##### the new name is {0} !!!!!!!! '.format(input_newname))
        oldpath = os.path.join('Interf','static', prev_name)
        newpath = os.path.join('Interf','static', input_newname)
        shutil.copytree(oldpath, newpath) # 
        shutil.rmtree(oldpath)

def superp_plots(manyplots):
    '''
    Routine for superimposing plots
    '''
    global superp_done 
    
    print("#### in superp_plots !!!!!")
    superp_done = False
    try:
        os.remove('Interf/static/superp.html')
    except:
        print('#### file not existing')
    if manyplots:
        print('############### received list of plots information : ', manyplots)
    cmd = "python bindings_extract.py makemanyplt '{0}' ".format(manyplots) 
    subprocess.Popen(cmd, shell='True') 

def check_current_well(socketio, debug=False):
    '''
    '''
    try: 
        with open('current_processing_folder.p', 'r') as f:
            currf = json.load(f)
            currw = os.path.join('Interf/static', currf, 'current_processing_well.p')
            with open(currw, 'r') as f: # sending the current well to the client
                name_current_well = json.load(f)
                socketio.emit('currwell',
                          name_current_well,
                          namespace='/plate_comm')
    except:
        print('no current_processing_well')

def save_current_well(infos_well, debug=False):
    '''
    '''
    folder, currwell = json.loads(infos_well)
    print('###### keeping the well !!!!!!!')
    if infos_well:
        if debug : print('### received message : ', infos_well)
        path_current_well = os.path.join('Interf/static', folder, 'current_processing_well.p')
        if debug : print('###### path_current_well', path_current_well)
        json.dump(currwell, open(path_current_well, 'w'))
