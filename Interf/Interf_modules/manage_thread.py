import os, time
import json, pickle
import shutil
import subprocess
opj = os.path.join

def stopthread(message):
    '''
    Create the messages for indicating the end of the processing.. 
    '''
    print("####### {0}".format(message))
    if message == 'processed':
        json.dump('processed', open('Interf/static/processed.p', 'w'))
        print('received processed')
        json.dump('False', open('Interf/static/take_time.p', 'w'))

def bckgrd_thread(socketio, debug=False):
    '''
    Thread running in the background
    '''
    count = 0
    print("######## In bckgrd_thread !!!!   ")

    try:
        os.remove('Interf/static/superp.html')
    except:
        print('file not existing')
    t0 = 0
    current_nbfolder = 0
    current_nbfolder_old = 0
    while True:
        try:
            with open(opj(os.getcwd(),'nbfolders.txt'), 'r') as f:
                data = f.readlines() # Transmitted line
                if debug:
                    print("################################# #### found nbfolders !!!!")
                    print('##### data is ', data)
        except:
            data = 'no data yet' 
        time.sleep(0.3) # O.3 permits a good refresh for superimposed plots..
        count += 1
        
        isprocessed = os.path.exists('Interf/static/processed.p')
        finished = os.path.exists('Interf/static/take_time.p')
        begin_proc = os.path.exists('Interf/static/begin_proc.p')
        if begin_proc:
            t0 = time.time()
            os.remove('Interf/static/begin_proc.p')
            if debug: print("#### t0 = ", t0)
        if debug: print('not isprocessed and not finished and t0!=0 ', not isprocessed and not finished and t0!=0)

        if not isprocessed and not finished and t0!=0:        # if processing and measuring time
            t1 = time.time()
            time_el = round((t1-t0)/60.0, 1)
            if debug: print("time elapsed in float is ", time_el)
            time_elapsed = str(time_el)
            time_elapsed_old = time_elapsed
            # # print("### time elapsed : {0}".format(time_elapsed))
        else:
            try:
                time_elapsed = time_elapsed_old
            except:
                time_elapsed = 0
        try:
            dd = data[0].split('/')
            current_nbfolder = int(dd[0])
            if debug:
                print("dd[0] ", dd[0])
                print("dd[1] ", dd[1])
                print("time elapsed in float before ratio is ", time_el)

            ratio_elapsed = float(dd[1])/float(dd[0])
            if debug:
                print("### time_el*(ratio_elapsed-1) {0} ".format(time_el*(ratio_elapsed-1)))
                print("#### ratio_elapsed ", ratio_elapsed)
                print("#### time_el ", time_el)
            if current_nbfolder_old != current_nbfolder:
                time_left = time_el*(ratio_elapsed-1)  # time left for finishing the processing
                time_left_old = time_left
            elif current_nbfolder==0: 
                time_left = '?'
            else:
                time_left = time_left_old
            current_nbfolder_old = current_nbfolder
            
        except:
            time_left = 0
        if debug: print('############################## time_left', time_left)
        socketio.emit('follow',
                      {'data': data, 'count': count, 'time': time_elapsed, 'time_left' : time_left},
                      namespace='/follow_proc')

        ########## Name current dataset

        try: 
            with open('current_processing_folder.p', 'r') as f: # sending the current folder to the client
                name_current_dataset = json.load(f)
                socketio.emit('message',
                          name_current_dataset,
                          namespace='/plate_comm')
        except:
            print('no current_processing_folder')
            json.dump('processing_example', open('current_processing_folder.p', 'w'))

        ########## Test reprocessing

        try: 
            with open('reprocessing_done.p', 'r') as f: # sending the current folder to the client
                reproc_done = json.load(f)
                socketio.emit('reproc_ok',
                          '',
                          namespace='/plate_comm')
                os.remove('reprocessing_done.p')
                print("#### reprocessing_done.p erased !!!")
        except:
            pass 

        ########## Signal for multiplots
        sup_html = os.path.exists('Interf/static/superp.html')
        sup_done = os.path.exists('Interf/static/superp_done.p')
        if sup_html and sup_done:                             # detect that sup_html and sup_done exist..
            socketio.emit('superimp', 'done',  namespace='/plate_comm')
            os.remove('Interf/static/superp_done.p')

