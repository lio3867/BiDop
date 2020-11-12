#!/usr/bin/env python
# encoding: utf-8
"""
initializing.py
Initialize the session.
"""
import os
import os.path as op


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

    
