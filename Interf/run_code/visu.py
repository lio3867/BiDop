import json
from flask import render_template,request,\
            redirect, url_for, session

def visu(app, socketio, define_make_plate, define_visu,
                 visualisation, reprocess, superp_plots):
    '''
    '''
    @app.route('/make_plate', methods = ['GET', 'POST']) #
    def make_plate():
        '''
        Define the groups in the plate
        '''
        return render_template('make_plate.html', **define_make_plate().__dict__)

    @app.route('/geom', methods = ['GET', 'POST']) #
    def geom():
        '''
        
        '''
        info_geom = request.form.get('info_geom')
        print('############### the dic is  ', info_geom)
        with open('plate_grp_geom.json', 'w') as f:
            f.write(info_geom)
        return redirect(url_for('make_plate'))


    @app.route('/visu', methods = ['GET','POST']) #  
    def visu(debug=True):
        '''
        Visualization of the dataset after the processing. 
        This page permits also to reprocess a selected group with new parameters.
        '''
        visualisation(request, reprocess.retrieve_params) # (request)
        return render_template('plate.html', **define_visu().__dict__)
        

    @socketio.on('manyplots', namespace='/plate_comm')
    def make_plot(manyplots):
        '''
        Make a plot or plots superposition from pickles files.
        This routine plots the curves with correction or native.
        '''
        print("######## Performing plots superimposition !!!!!")
        superp_plots(manyplots)

        json.dump('done', open('Interf/static/superp_done.p', 'w'))