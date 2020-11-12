#!/usr/bin/env python 
# coding: utf8


"""
 make_report.py, v 1.0 2016/07/22
 Makes a html report with straptoc.js library

 *******************************************************************
 *
 * Copyright (c) 2016
 * Casc4de
 * Le Lodge, 20 Av du neuhof , 67100 Strasbourg, FRANCE
 *
 * All Rights Reserved
 *
 *******************************************************************
"""

class REPORT(object):
    '''
    HTML report
    Parameters:
        * name : name of the report
    '''
    
    def __init__(self, name = 'report.html', toc=False):
        self.name = name
        self.toc = toc

    def begin(self, title = None):
        '''
        Opening the report
        '''
        report = '''
<!DOCTYPE html>
<html>

<meta charset="UTF-8">

<title>{0}</title>

<script  src="http://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
<script  src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.js"></script>
<script  src="https://cdnjs.cloudflare.com/ajax/libs/jquery-contextmenu/2.1.1/jquery.contextMenu.js"></script>
<script  src="https://cdnjs.cloudflare.com/ajax/libs/jquery.perfect-scrollbar/0.6.11/js/min/perfect-scrollbar.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
<!-- Straptoc -->
<script  src="https://cdn.rawgit.com/strablabla/Tinkering/9c04e55/js/straptoc/straptoc.js"></script>
<link rel="stylesheet" href="https://cdn.rawgit.com/strablabla/Tinkering/9c04e55/js/straptoc/straptoc.css"> 
<!-- CSS -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-contextmenu/2.1.1/jquery.contextMenu.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.perfect-scrollbar/0.6.11/css/perfect-scrollbar.css">
<!-- Fonts -->
<link href='https://fonts.googleapis.com/css?family=Pathway+Gothic+One' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Londrina+Solid' rel='stylesheet' type='text/css'>
<link href='https://fonts.googleapis.com/css?family=Enriqueta' rel='stylesheet' type='text/css'>
<!-- Bootstrap -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css">
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({{tex2jax: {{inlineMath: [['$','$'], ['\\(','\\)']]}}}});
</script>
<script type="text/javascript" async
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">
</script>

<xmp theme="simplex" style="display:none;">

§novideo  
{1}

§noiframe
§col_h2 #cc0099
§col_sublist0 #cc0099
§col_sublist1 #3366ff
§col_sublist2 #990033
§col_toc #ccccff  
§toggle_hide a  
§help true  
§mathsize huge

    '''.format(title, '§notoc true' if not self.toc else '')
        with open(self.name,'w') as f:
            f.write(report)
    
    
    def write(self, txt):
        '''
        Body of the report
        '''
        with open(self.name,'a') as f:
            f.write(txt)
    
    def end(self):
        '''
        Closing the report
        '''
        report = '''
</xmp>
<script src="http://strapdownjs.com/v/0.2/strapdown.js"></script>
<script> maketoc() </script>

</html>
        '''.format()
        with open(self.name,'a') as f:
            f.write(report)

if __name__ == '__main__':
    r = REPORT()
    title = 'log file for binding_extract.py'
    txt = '''
# Binding index

all the Bis are 
    
    '''
    r.begin(title)
    r.write(txt)
    r.end()