import os
import json

def make_addr_dict(p, dict_name):
    return os.path.join('Interf', 'static', p, dict_name)

def modify_dict_wells(p, w, m, index_badgood = -1, debug=False):
    '''
    Modify dict_wells.csv for the plate visualisation
    index_badgood: index of the element to be changed in the line
    '''
    proc_dict_wells = make_addr_dict(p, 'dict_wells.csv') 
    with open(proc_dict_wells, 'r') as f:              # Open the original file
        with open('interm_wells.txt', 'w') as g:       # Temporary file
            for l in f.readlines():
                ll = l.split(',')
                l = l.strip()
                if w == ll[0].strip():
                    if debug : print("last element in dict_wells.csv is ", ll[index_badgood])
                    if m == 'smile' and ll[index_badgood].strip() != 'bad':
                        l += ', bad' 
                    elif m == 'sad' and ll[index_badgood].strip() == 'bad':
                        l = ",".join(ll[:index_badgood])   # Assembling the line again
                g.write(l+'\n')
    os.rename('interm_wells.txt', proc_dict_wells)

def modify_dict_all_infos(p, w, m, index_badgood = 24, debug=False):
    '''
    Modify dict_all_infos.csv which concentrates all the informations.
    index_badgood: index of the element to be changed in the line
    '''
    proc_dict_all_infos = make_addr_dict(p, 'dict_all_infos.csv')
    with open(proc_dict_all_infos, 'r') as f:          # Open the original file
        with open('interm_all_infos.txt', 'w') as g:   # Temporary file
            for l in f.readlines():
                ll = l.split(',')
                l = l.strip()
                if w == ll[0].strip():
                    good = ll[index_badgood].strip()
                    if debug : print("element in dict_all_infos.csv is ", good)
                    if m == 'smile' and  good == 'y':
                        ll[index_badgood] = 'n'
                    elif m == 'sad' and good == 'n':
                        ll[index_badgood] = 'y'
                    l = ",".join(ll)    # Assembling the line again
                    l = l.strip()
                    if debug : print('after reconstruction we have the line {0} '.format(l))
                g.write(l+'\n')
    os.rename('interm_all_infos.txt', proc_dict_all_infos)

def make_postcomments(debug=True):
    '''
    Make comments about the quality of the processing etc
    '''
    p, w, m = json.loads(message) # proc, well, comment
    print("####### comment is {0}, well is {1} ".format(m, w))
    proc_dict_all_infos = os.path.join('Interf', 'static', p, 'dict_all_infos.csv')
    with open(proc_dict_all_infos, 'r') as f:
        with open('interm_all_infos.txt', 'w') as g:   # Temporary file
            for l in f.readlines():
                ll = l.split(',') 
                ll[-1] = ll[-1][:-1]                   # removing line return after comments from file
                if w == ll[0].strip():
                    if len(ll)<28:                     # if no additionnal comment.. 
                        ll.append(' '+ m)              # adding comment
                    else:
                        ll[-1] = ' '+ m
                l = ",".join(ll)
                print("l is ", l)
                g.write(l + '\n')
    os.rename('interm_all_infos.txt', proc_dict_all_infos)

def save_wrong_wells(socketio, infos_wrongwell, debug=True):
    '''
    '''
    if debug : print(infos_wrongwell)
    p, w, m = json.loads(infos_wrongwell)   # proc, well, mood
    modify_dict_wells(p, w, m)              # dict_wells
    modify_dict_all_infos(p, w, m)          # dict_all_infos
    socketio.emit('wrong_wells', infos_wrongwell,  namespace='/plate_comm')

