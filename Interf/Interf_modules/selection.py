import os
from threading import Thread

def select_action(background_thread, debug=False):
    '''
    '''
    global thread
    try:
        os.remove('nbfolders.txt')
    except:
        print('no nbfolders.txt')
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()  