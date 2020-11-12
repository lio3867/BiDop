
import os
import pickle, json, time
import subprocess

def init_state(debug=1):
    '''
    '''
    if debug>0: print("##### Initializing the state... !!!!!")
    try:
        os.remove('Interf/static/processed.p')
    except:
        pass
    try:
        os.remove('Interf/static/take_time.p')
    except:
        pass
    try:
        os.remove('Interf/static/superp_done.p')
    except:
        pass

def read_params_proc(config, debug=1):
    '''
    Read the parameters in the file Interf/static/proc.cfg
    '''
    path_proc = os.path.join('Interf','static', 'proc.cfg')   # Path for config file
    config.read(path_proc)                                    # Read the config file

    #########   Retrieving the parameters

    range_analysis = config['Processing']['range_analysis']   # range used for performing comparisons
    range_norm = config['Processing']['range_norm']           # range ..
    range_elems = config['Processing']['range_elems']         # range ..
    range_y_adjust = config['Processing']['range_y_adjust']   # adjustement range for postprocessing
    iterations = config['Processing']['iter']                 # nb of iterations for the baseline
    chunks = config['Processing']['chunks']                   # nb of chunks for the baseline
    speed = config['Processing']['speed']                     # speed ??

    if debug>0:
        print("#### in read_params_proc ### ")
        print("range_analysis ", range_analysis)
        print("range_norm ", range_norm)
        print("range_elems ", range_elems)
        print("range_y_adjust ", range_y_adjust)
        print("iterations ", iterations)
        print("chunks ", chunks)
        print("speed ", speed)

    ######### Make the dictionary

    proc_params = {'range_analysis':range_analysis, 'range_norm':range_norm,
                         'range_elems':range_elems, 'range_y_adjust':range_y_adjust, 
                         'iter':iterations, 'chunks':chunks,
                         'speed':speed
                         }
    return proc_params

def proc_ask_params(request, config, define_ask_param, af,  debug=False):
    '''
    '''
    # print(define_ask_param().__dict__)
    proc_params  = read_params_proc(config) # read_proc_params()
    dic_ask_param = {}
    dic_ask_param.update(define_ask_param().__dict__)
    dic_ask_param.update(proc_params)    # Add param from configfile to the dictionary used by jinja
    if debug : print(dic_ask_param)
    if request.form.get('choosefolder'):
        af.search_data('folder')                            # opens PyQt interface for searching the folder.
        session['valid'] = request.form.get('valid')
    return dic_ask_param

def proc(request):
    '''
    Launch the processing
    '''

    print("## Processing")

    # Parameters for processing

    init_state()

    param_list = []
    param_list += ['groups', 'iter', 'chunks', 'speed']                 # processing parameters
    param_list += ['makebokeh', 'elems', 'verticalcorr']     
    param_list += ['range_analysis', 'range_norm', 'range_y_adjust']    # range for reprocessing and analysis
    param_list += ['pepidentif'] 
    params = {}                                                         # dictionary for gathering parameters for the processing
    for p in param_list:                                                # Principal parameters session values
        params[p] = request.form.get(p)                                 # retrieving parameters from the form
        print(request.form.get(p))
    if params['makebokeh'] :
        params['makebokeh'] = True
    if params['verticalcorr'] :
        params['verticalcorr'] = True
    with open('data_folder.p', 'r') as f:                                            
        data_folder = json.load(f)                                       # Retrieving the folder address with json
    parameters = json.dumps(params)                                      # Transmitting parameters using json
    print('##########################   using parameters {0} #######################'.format(parameters))
    print("######### launching the processing")
    
    json.dump('ok', open('Interf/static/begin_proc.p', 'w'))
    cmd = "python bindings_extract.py complete {0} '{1}'".format(data_folder, parameters) # processing command line
    subprocess.Popen(cmd, shell='True')                                                   # Popen is non-blocking

