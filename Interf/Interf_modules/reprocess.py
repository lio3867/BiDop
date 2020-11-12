def retrieve_params(request, debug=False):
    '''
    '''
    
    print('##################  Reprocessing the data  !!!!! ')
    ################# Retrieving the parameters for processing

    #### Ranges

    range_analysis_form = request.form.get('range_analysis')       #  analysis range
    if debug : print('range_analysis_form', range_analysis_form) 
    range_norm_form = request.form.get('range_norm')               #  the normalization range
    if debug : print('range_norm_form', range_norm_form) 
    range_y_adjust_form = request.form.get('range_y_adjust')               #  the normalization range
    if debug : print('range_y_adjust_form', range_y_adjust_form) 

    #### Baseline

    iter_form = request.form.get('iter')               #  number iterations 
    nbchunks_form = request.form.get('nbchunks')       #  number chunks
    speed_form = request.form.get('speed')             #  speed

    #### Options

    chck_verticalcorr = request.form.get('verticalcorr')           #  checkbbox for vertical correction

    #### Various

    addr_form = request.form.get('addr_input')                     #  name of the dataset
    root_form = request.form.get('root_input')                     #  address of the folder

    #### groups

    grp_form = request.form.get('grp_input')                       #  which group is selected for reprocessing
    if debug : print('grp_form', grp_form) # 
    range_elems_form = request.form.get('range_elems')             #  elements in each group to be processed
    if debug : print('range_elems_form', range_elems_form) 
    if debug : print("## Processing")

    list_range = [range_analysis_form, range_norm_form, range_y_adjust_form]
    list_proc_param = [iter_form, nbchunks_form, speed_form, chck_verticalcorr]
    list_various = [addr_form, root_form]
    list_grp = [grp_form, range_elems_form]

    return list_range, list_proc_param, list_various, list_grp