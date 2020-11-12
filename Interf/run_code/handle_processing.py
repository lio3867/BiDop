import json
from flask import render_template,request,\
            redirect, url_for, session

def handle_processing(app, define_follow_processing, proc, 
         select_action, background_thread, define_select_proc_visu, 
         af, proc_ask_params, config, define_ask_param, socketio,
         read_params_proc ):
    '''
    '''
    @app.route('/select_proc_visu', methods = ['GET']) #, 
    def select_proc_visu():
        '''
        Page for selecting the folder containing the dataset.
        '''      
        select_action(background_thread)
        return render_template('select_proc_visu.html', **define_select_proc_visu().__dict__)

    @app.route('/ask_data', methods = ['POST'])
    def ask_data():
        '''
        Select the folder containing the data and redirect toward ask_param
        '''
        if request.form.get('choosefolder'):
            af.search_data('folder')           # opens PyQt interface for searching the folder.
        print("helllo")
        return redirect(url_for('ask_param'))

    @app.route('/ask_param', methods = ['GET', 'POST']) #
    def ask_param(debug=False):
        '''
        Select the parameters and redirect toward processing page.
        '''
        dic_ask_param = proc_ask_params(request, config, define_ask_param, af)
        return render_template('ask_param.html', **dic_ask_param)

    @app.route('/processing', methods = ['GET', 'POST'])
    def processing():
        '''
        Process the data and redirect toward follow_processing page.
        '''
        proc(request)
        return redirect(url_for('follow_processing'))

    @app.route('/follow_processing', methods = ['GET', 'POST'])
    def follow_processing(debug=False):
        '''
        Follow the processing
        '''
        if debug : print("## Following the processing")
        return render_template('follow_processing.html', **define_follow_processing().__dict__)

    @socketio.on('retrieve_dataset', namespace='/plate_comm')
    def ask_reproc(retrieve_dataset, debug=False):
        '''
        Controlling the name of the current dataset from the server
        '''
        if debug : print(retrieve_dataset)
        if retrieve_dataset:
            with open('current_processing_folder.p', 'r') as f:
                name_current_dataset = json.load(f)
            if debug : print('################## received ack message: ', name_current_dataset)

    @socketio.on('proc_params', namespace='/plate_comm')
    def proc_params(msg, debug=False):
        '''
        Loading processing parameters
        '''
        if debug: print('Here is the message received !!! {0}'.format(msg))
        proc_params  = read_params_proc(config)
        if debug: print("proc_params are ", proc_params)
        json_params = json.dumps(proc_params)
        socketio.emit('params_proc', json_params,  namespace='/plate_comm')

