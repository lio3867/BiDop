/*
Main code for visualizing the datasets.
*/

var visualize = function(proc_folder){

    // alert("visualize")

    $('#current_proc').attr('value', proc_folder)                             // Stock the name of the current folder..

    //------------- Plate definitions 

    size_rect = 10
    plate = {'96':{'m': 8,'n': 12, 'spacing': 40, 'w': 500 , 'h': 300},
                   '384':{'m':16,'n':24, 'spacing':25, 'w': 600 , 'h': 360}}   // Plate dimensions and spacings

    //-------------- Color definition

    col_biotine = 'yellow'
    col_peptide = '#00ff99';
    col_neutral = '#afa2dc'

    //---------------  Interaction with plate

    extent = null;   // Brush extent
    show_coord = false  // Show cell coordinates
    root = '/static/' + proc_folder
    if (proc_folder == 'processing_example'){
        $('#processing_example').css({'color':'green'}) // coloring at initialization
    }

    statekey = -1

    //==================================== Simple markdown 

        /*
        Simple markdown used for providing informations to the user. 
        It handles classical markdown list syntax.
        */
    
        simple_md = function(text){ // mini markdown for the help
            var all_text = text.split('\n')
            var htm = $('<div/>')
            var ul = $('<ul/>').css({'text-align':'left'})
            for (i in all_text){  
                var text_insert = all_text[i].trim().slice(1) // prepare text
                if (all_text[i].match(/^\s{4}\*/)){    // detect list first level
                    ul.append($('<li/>').text(text_insert))
                    } // end if
                if (all_text[i].match(/^\s{8}\*/)){  // detect list second level
                        var interm1 = $('<ul/>').append($('<li/>').text(text_insert))
                        ul.append(interm1)
                        } // end if
                if (all_text[i].match(/^\s{12}\*/)){  // detect list third level
                        var interm2 = $('<ul/>').append($('<li/>').text(text_insert))
                        interm1.append(interm2)
                        } // end if
                if (all_text[i].match(/\s*\#/)){ // detect #
                    htm.append($('<h1/>').text(text_insert))
                    } // end if
            } // end for
            htm.append(ul);
            return htm.html()
        } // end function

    //---------------------- Shortcut keys for the interface.

    var keys = function(){/*
    # Keys: 
        * k : toggle keys
        * c : toggle spectrum panel
        * Esc : trigger the cases interactions
            * e : push e after selection for having a red rectangle around brushed area.
            * b : color the biotines
            * p : color the peptides
            * d : neutral color 
            * a : show selected wells

    */}.toString().slice(14,-3)


    //---------------------- Plate

    var div_plate = $('<div/>').addClass('div_plate') //.draggable()
    $('body').append(div_plate)

    //----------------------  plate selection

    var opt = function(val){
        return $('<option/>').text(val).attr('value',val)
        }
    var col1 = $('<div/>').attr('class',"col-sm-8")
    var col2 = $('<div/>').attr('class',"col-sm-4")

    var div_type_plate = $('<div/>').attr('class','type_plate')
                                    .hide() // Element for modifying the plate.
    var type_plate = $('<h3/>').css({'text-align':'left'})
                               .text('type plate')
    var sel_plate = $('<select/>').attr('id','select_plate')
                  .attr('class','selectpicker')
                  .attr('data-width','70px')
                  .append(opt('384'))
                  .append(opt('96'))
    var type_usage = $('<h3/>').css({'text-align':'left'})
                             .text('Usage')
    var plate_usage = $('<select/>').attr('id','select_plate_usage')
                .attr('class','selectpicker')
                .attr('data-width','140px')
                .append(opt('Plate designer'))
                .append(opt('Analysis'))

    var command =  div_type_plate 
                     .append(type_plate) // kind of plate 96 or 384
                     .append(sel_plate)
                        
    //----------------------Adding elements

    $('body').append(command)

    //----------------------  Wells with molecules

    $('body').append($('<div/>').attr('class','wellsmolec').attr('id','wellsmolec'))

     var infos_plots =  $('<input/>').attr('id', "infos_plots").hide() // keeping infos about mutiple plots
     $('body').append(infos_plots)


    $('#wellsmolec').draggable()
    // $('#wellsmolec').addClass("context-menu-well")

    //----------------------  Control panel

    // alert('making control panel')

    $('body').append($('<div/>').attr('class','controls').attr('id','ctrl'))
    $('body').append($('<div/>').attr('class','controls_switch_listmolec').attr('id','ctrl_sw_lm'))

    /*
    Switching between Control panel and list_wellmolec
    */

    // $('#ctrl_sw_lm').click(function(){  
    $('#ctrl').click(function(){                 // make listmolec appear and disappear
          if ($('#ctrl').css('z-index') == 5){
                $('#ctrl').css({'z-index': '10'})
                $('#ctrl_sw_lm').css({'z-index': '11'})
                $('#wellsmolec').css({'z-index': '5'})
              }
          else{
                $('#ctrl').css({'z-index': '5'})
                $('#ctrl_sw_lm').css({'z-index': '6'})
                $('#wellsmolec').css({'z-index': '15'})
             }
      }) // end click

    //--------------

    // $('#ctrl').draggable()
    if (! $('#ctrl').attr('class').match(/context-menu-well/)){
        $('#ctrl').addClass("context-menu-well")
    }
    
    $('body').append($('<div/>').attr('class','controls_addons').attr('id','ctrl_addons'))
   
    //----------------------  Indicates if interaction with plate is on or off

    $('body').append($('<div/>').attr('class','interact').attr('id','interact'))
    $('#interact').hide()

    //----------------------  Shortcuts

    $('body').append($('<div/>').attr('class','shortcuts').attr('id','shortcuts'))
    $('#shortcuts').html(simple_md(keys)).toggle()
    $('#shortcuts').draggable()

    //----------------------  # Buttons for choosing the kind of plot

    //---------------------- Baseline

    var button_baseline = $('<input/>').attr('type', 'button')
                                .addClass('btn btn-default ') // baseline
                                .attr('id', "show_baseline")
                                .val('preprocess')
                                //.css({'margin-left':'40px'})

    //---------------------- Diff Baselines

    var ctrl_BL = $('<div/>').attr('class','controls_baseline')
               .attr('id','ctrl_BL')
               .draggable()
    var bsp  = "10px"  // button space
    var button_BL = $('<input/>').attr('type', 'button')
                            .addClass('btn btn-default ')              // Button for baseline and original profile
                            .attr('id', "BL")
                            .val('bl')
                            .css({'margin-left':bsp})
    var button_BL_corr = $('<input/>').attr('type', 'button')          // Button for baseline substracted from profile
                        .addClass('btn btn-default ') // baseline
                        .attr('id', "BL_corr")
                        .val('--')
                        .css({'margin-left':bsp})
    var button_BL_corr_nocorr = $('<input/>').attr('type', 'button')   // Button for original profile with profile corrected
                        .addClass('btn btn-default ') // baseline
                        .attr('id', "BL_corr_nocorr")
                        .val('vs')
                        .css({'margin-left':bsp})
    ctrl_BL.append(button_BL)
           .append(button_BL_corr)
           .append(button_BL_corr_nocorr)
           .hide()

    $('body').append(ctrl_BL)

    //---------------------- Dilation
                                   
    var button_dilation = $('<input/>').attr('type', 'button') // dilation
                                .addClass('btn btn-default ') 
                                .attr('id', "show_dilation")
                                .val('Final result')
                                //.css({'margin-left':'20px'})

    //---------------------- Raw data with reference
                                   
    var button_rawdata = $('<input/>').attr('type', 'button')  // raw data
                                .addClass('btn btn-default ') 
                                .attr('id', "show_rawdata")
                                .val('rawdata')
                                //.css({'margin-left':'20px'})

    //-----------------------------------  Reprocess

    $('body').append($('<div/>').addClass('reproc').attr('id','reproc').hide())
    dic_css_reproc = {'width': '40', 'height': '25', 'margin-left': '30px'}

    //------------- Range Analysis

    var input_range_analysis = $('<input/>').attr('type', 'input')               // range input for Analysis
                                //.attr('value','30-90')
                                .attr('id', 'range_analysis')
                                .attr('name', 'range_analysis')
                                .css(dic_css_reproc)

    var reproc_range_analysis = $('<label/>').text('Analysis range :').append(input_range_analysis)   // size range 

    //------------- Range normalization

    var input_range_normal = $('<input/>').attr('type', 'input')               // range input for reprocessing
                                //.attr('value','8-17')
                                .attr('id', 'range_norm')
                                .attr('name', 'range_norm')
                                .css(dic_css_reproc)

    var reproc_range_normal = $('<label/>').text('Normalization range :')
                                           .append(input_range_normal)   // size range 

    //------------- iter

    var input_iter = $('<input/>').attr('type', 'input')                               // nb iterations for baseline
                                .attr('id', 'iter')
                                .attr('name', 'iter')
                                .css(dic_css_reproc)
                                // .append($('<span/>').text('reprocess'))
    var reproc_iter = $('<label/>').text('iter :').append(input_iter)                  

    //------------- nb Chunks

    var input_nbchunks = $('<input/>').attr('type', 'input')                           // nb chunks for baseline
                                      .attr('id', 'nbchunks')
                                      .attr('name', 'nbchunks')
                                      .css(dic_css_reproc)
    var reproc_nbchunks = $('<label/>').text('nb chunks :').append(input_nbchunks)   

    //------------- speed

    var input_speed = $('<input/>').attr('type', 'input')                             // speed for baseline
                                   .attr('id', 'speed')
                                   .attr('name', 'speed')
                                   .css(dic_css_reproc)
    var reproc_speed = $('<label/>').text('speed :').append(input_speed)           

    //---------  Elements in the group to reprocess

    var input_range_elems = $('<input/>').attr('type', 'input')                       // range group elements input for reprocessing
                                         .attr('id', 'range_elems')
                                         .attr('name', 'range_elems')
                                         .css(dic_css_reproc)

    var reproc_range_elems = $('<label/>').text(' elems in group :').append(input_range_elems)

    //---------  Range vertical correction

    var input_range_vertical_adjust = $('<input/>').attr('type', 'input')               // range for vertical adjustment
                                                   .attr('id', 'range_y_adjust')
                                                   .attr('name', 'range_y_adjust')
                                                   .css(dic_css_reproc)

    //---------  Checkbox for vertical correction

    var chckverticorr = $('<span/>').addClass("checkbox col-xs-6").css({"margin-left": "20px", "padding-bottom": "10px"})
    var nameverticorr = $('<p/>').css({"margin": "0", "padding": "0", "height": "13px", "width": "130px", "font-weight": "bold"}).text('secondary correction :')
    var inputverticorr = $('<input/>').css({"margin-left": "40px" })
                                      .attr('name', 'verticalcorr')
                                      .attr('type', "checkbox")
    nameverticorr.append(inputverticorr)
    chckverticorr.append(nameverticorr)

    var reproc_range_vertical_adjust = $('<label/>').text('range for vertical adjust :').append(input_range_vertical_adjust)

    //---------  button reprocess

    // var show_opt = $('<div/>').html("<i class='fa fa-bars fa-2x' id='proc_options' style='padding-left:215px' aria-hidden='true'></i>")
    var show_opt = $('<span/>').html('<i class="fa fa-gear fa-2x" id="proc_options" style="padding-left:20px" aria-hidden="true"></i>')
    var submit_range = $('<input/>').attr('type', 'input')            // button for triggering the reprocessing
                                    .addClass('btn btn-default')
                                    .attr('value', 'reprocess')
                                    .attr('id', 'submit_range')
                                    .attr('name', 'submit_range')
                                    .css({'font-weight':'bold', 'font-size': '14px', 'width':'120px'})

    $('#ctrl').append($('<br/>'))
    $('#ctrl').append($('<br/>'))

    //-----------------  Form for the reprocessing

    var form_params = $('<form/>').attr('id', 'form_params')
                                  .attr('action', '/visu')
                                  .attr('method', 'POST') 

    // --------------- Reprocessing parameters 

    /*
    Panel for reprocessing
    */  

    $('#reproc').html(  '<i class="fa fa-gear fa-2x" id="proc_options" style="padding-left:20px" aria-hidden="true"></i> <h3> Reprocessing <h3/>')
                .append('<br/>')
                .append(reproc_range_analysis).append('<br/>')         // range for reprocessing
                .append(reproc_range_normal).append('<br/>')           // range for normalizaton
                .append(reproc_iter).append('<br/>')                   // number of iterations
                .append(reproc_nbchunks).append('<br/>')               // number of chunks
                .append(reproc_speed).append('<br/>')                  // speed
                .append(reproc_range_elems).append('<br/>')            // range of elements in the group
                .append(chckverticorr).append('<br/>')                 // checkbox for vertical adjustment
                .append(reproc_range_vertical_adjust)                  // range for reprocessing
                .append('<br/>') 
                .append('<br/>')
                .append('<br/>')
                .append(submit_range)
    form_params.append($('#reproc'))

    $('body').append(form_params)

    // ------------------------- Reproc alert
    
    var reproc_ok = $('<div/>').addClass('reproc_ok').attr('id','reproc_ok').hide()
    var button_reproc_ok = $('<input/>')  
                        .attr('type', 'button').addClass('btn btn-default')
                        .attr('value','OK')
                        .attr('id', "butt_reproc_ok")
    button_reproc_ok.click(function(){
        reproc_ok.hide()
       })
    var reproc_mess = $('<h5/>').text('Reprocessing done !!!')
    reproc_ok.append(reproc_mess)
             .append(button_reproc_ok)

    $('body').append(reproc_ok)

    //--------------------------- Bar :  Title, well, name molec, BI
    
    var title_ctrl = $('<p/>').text('Processings Controls').css({'text-align': 'center', 'font-size':'200%'}) 
    var dic_iframe = {'frameborder': '0', 'src': '', 'width': '100%', 'height':'75%' }    

    //------------------------ bar functions

    //------- tag for good and bad wells
    var smilebars = $('<span/>').html("<i class='fa fa-smile-o fa-2x'  id='smile' style='padding-left:20px' aria-hidden='true'></i>").attr('id', 'spansmile')
    //------- List wells and molecules
    var sortbars = $('<span/>').html("<i class='fa fa-sort-amount-asc fa-2x'  id='list_sort_molec' style='padding-left:280px' aria-hidden='true'></i>")
    //------- Baseline dilation
    var icbars = $('<span/>').html("<i class='fa fa-stethoscope fa-2x' id='list_options' style='padding-left:20px'  aria-hidden='true'></i>") // fa-bars fa-image
    // var show_opt = $('<span/>').html("<i class='fa fa-gear fa-2x'  id='open_reproc' style='padding-left:20px' aria-hidden='true'></i>") // reprocbars

    $('#ctrl_sw_lm').append(smilebars)     //  bars for showing the menu
                    .append(show_opt)      //  show the panel reprocessing
                    .append(sortbars)      //  show the list of wells and molecs for sorting
                    .append(icbars)        //  show the panel for accessing to dilation, baseline etc.. 
    /*
    set the icon sad or smile
    keywords: smiley
    */

    var set_sad = function(currw){   

          /*
          sad icon and set mood to sad
          */

          $('#spansmile').html("<i class='fa fa-frown-o fa-2x'  id='smile' style='padding-left:20px' aria-hidden='true'></i>")
          $('#'+currw).attr('mood', 'sad')
          // colwell(currw)

        }
    //-----

    var set_smile = function(currw){   

          /*
          smile icon and set mood to smile
          */

          $('#spansmile').html("<i class='fa fa-smile-o fa-2x'  id='smile' style='padding-left:20px' aria-hidden='true'></i>")
          $('#'+currw).attr('mood', 'smile')
          // colwell(currw)
        }

    var smileclick = function(){           // change smiley with click

        /*
        Smile click
        keywords : click smile, smile click
        */

        $('#smile').click(function(){      // putting a mark on the deficient wells
           var currw = $('#current_well').attr('value')
           var attr = $('#'+currw).attr('mood')

            if ($('#'+currw).attr('mood') == 'smile'){
                set_sad(currw)                                 // if smile, set the sad face
                $('#'+currw).css({'fill':'grey'})              // color in grey
                } // end if
            else{
                set_smile(currw)                                                // else, set the smile
                $('#'+currw).css({'fill':$('#'+currw).attr('original_color')})  // restitute original color
                } // end else
        }) // end click $('#smile')
    }

    smileclick()

    //-------
                    
    $('#list_options').click(function(){        // Toggling list_options
          $('#ctrl_addons').toggle()            // Toggling the baseline
          $('#ctrl_BL').toggle()                // Toggling the choice of the baseline
    })

    $('#list_sort_molec').click(function(){      // Toggling wellsmolec
          $('#wellsmolec').toggle()
        }) // end click $('#list_sort_molec')

    $('#ctrl').append(title_ctrl) //
              .append($('<br/>'))  
              .append($('<p/>').attr('id', 'namewell_ctrl'))
              .append($('<p/>').attr('id', 'namemolec_ctrl'))
              .append($('<p/>').attr('id', 'BI_ctrl'))
              .append($('<br/>')) 
              .append($('<br/>'))
              .append($('<br/>'))
              .append($('<iframe/>', dic_iframe))
    
    //---------- Function for reprocessing and plot analysis

    $('#ctrl_addons').append(button_baseline)
                     .append(button_dilation)
                     .append(button_rawdata)
                     .hide().draggable()

    //------

    show_opt.click(function(){     // show options
        $('#reproc').toggle()      // show-hide reprocessing panel
       }) // end click

    /*
    Reprocess a group on click
    */

    $("#submit_range").click(function() {
        // alert('$( "#submit_range").click')
        var saved_addr = 'addr'
        d3.text(root + "/processing.log", function(data) {
            var parsedCSV = d3.csv.parseRows(data, function(d, i){
               if (i==0){                             // take the first line
                    //-------                         transmiting the name of the folder                              
                    saved_addr = d[1].split(/(\s+)/)[4]
                    // alert('###### saved_addr ' +  saved_addr)
                    var input_addr = $('<input/>').attr('type', 'input')
                                    .attr('value', saved_addr)
                                    .attr('id', 'addr_input')
                                    .attr('name', 'addr_input').hide()
                    //-------                          transmiting the root of the folder
                    // alert('###### root ' +  root)
                    var input_root = $('<input/>').attr('type', 'input')
                                    .attr('value', root)
                                    .attr('id', 'root_input')
                                    .attr('name', 'root_input').hide()
                    //-------                         transmiting the group information
                    // alert('###### selected_grp ' +  selected_grp)
                    var input_grp = $('<input/>').attr('type', 'input')
                                    .attr('value', selected_grp)
                                    .attr('id', 'grp_input')
                                    .attr('name', 'grp_input').hide()
                    //-------
                    form_params.append(input_addr)           // address of the folder to be processed
                               .append(input_root)           // address of the folder where to put the processed files
                               .append(input_grp)            // number of the group to process
                    $("#form_params").submit()
                } // end if first line 
             }); // parseRows
         }); // end d3.text
    });

    /*
    Superimposing plots
    */

    //----------------------  superimpose

    var superimpose = $('<div/>').addClass('superimpose')
                                 .attr('id','superimpose')
                                 .hide()
                                 .draggable()
    var dic_iframe = {'frameborder': '0', 'src': '', 'width': '100%', 'height':'75%' }
    var lplots = $('<span/>').attr('id', 'list_molec_manyplt')      // names of the molecules interactions
    
    var close_superimp = $('<input/>').attr('type', 'button')      // Select molecules with pattern  
                            .addClass('btn btn-default')
                            .attr('value','close')
                            .attr('id', 'close_superimp')
    var orig_superimp = $('<input/>').attr('type', 'button')      // Select molecules with pattern  
                        .addClass('btn btn-default')
                        .attr('value','original')
                        .attr('id', 'orig_superimp')

    superimpose.append($('<h4/>').text('Superimposing'))
               .append($('<iframe/>', dic_iframe))
               // .append($('<br/>'))
               // .append($('<br/>'))
               .append(lplots)
               // .append($('<br/>'))
               // .append(close_superimp)

    $('body').append(superimpose)

    //--------  Close superimpose

    $('#close_superimp').click(function(){   // closing superimpose
        $('#superimpose').hide()
      })

    //---------------  Click well and show Bokeh

    /*
    Click on well and show the dilation Bokeh plot.
    In the same time it plugs buttons for passing from baseline to dilation and inversely.
    keywords : click well, well click
    */
    
    var selected_grp = '1' // group for beginning visualization

    var show_bokeh = function(d){
        /*
        d : information containing the cell on the plate, the name, the group number etc..
        */

        selected_grp = d[2].trim()
        var txtBI = 'BI : '+ d[3]
        var css_title = {'text-align' : 'center', 'font-size': '150%', 'color':'#004466'}
        $('#BI_ctrl').text(txtBI)
                     .css(css_title)   // BI value
        var namemol = d[1]
        $('#namemolec_ctrl').text(namemol)
                            .css(css_title)  // molecular name for the interaction
        sgrp = d[2].split('_')
        var namewell = d[0]+'('+sgrp[0]+sgrp[1]+')'
        $('#namewell_ctrl').text(namewell)
                           .css(css_title) // Well name

        //--------  purple line around current selected well

        var col_select = "#8600b3"      //  purple color for the current selected well
        var col_grp = "#00cc44"         //  green color for the group

        $('.well.processed').each(function(){ 
            $(this).css({'fill': $(this).attr('color'), "outline-style": "solid", "outline-color": "#ffffff", "outline-width": "1px" }) // reinitialize color and dotted line
            if ($(this).attr('mood') == 'sad'){$(this).css({'fill':'grey'})}
            else{$(this).css({'fill':$(this).attr('original_color')})}
            })  // initialize color plate

        $('[grp]').each(function(){
             if ($(this).attr('grp')==$('#' + d[0]).attr('grp')){
                 $(this).css({"outline-style": 'solid', "outline-color": col_grp, "outline-width": "2px" }) // make a dotted line   "dotted"  "#009999" "#000000"
             } // end if
        $('#' + d[0]).css({"outline-style": "solid", "outline-color": col_select, "outline-width": "2px"}) // make a dotted line #ff4d4d
          
        })

        //--------

        $('.namemolec').css({'color': 'black'})                                   // color all molec names in black

        $('[idgrp]').each(function(){
             if ($(this).attr('idgrp')== 'grp'+ $('#' + d[0]).attr('grp')){
                 $(this).find('.namemolec').css({'color': col_grp})               // color group molecule names the elements in green
             } // end if
        })
   
        $('#' + d[1].trim()).css({'color': col_select})                           // color the molecule name in purple

        //-------- Show dilation as first view
        //----------- Show baseline and dilation

        var childifr = $('#ctrl').children('iframe') //

        //----------- Prepare address for preproc/proc visualization

        var dil = root +  '/proc_' + d[2].trim() + '_dilat.html?random='+new Date().getTime() // Bokeh dilation plot random id for refreshing

        // -----------------

        var grpspl = d[2].trim().split('_')  //
        var rootbl = root + '/proc_' + grpspl[0] + '_' + grpspl[1]
        var basel = rootbl + '/baseline_' + d[2].trim() + '.html'
        var basel_corr = rootbl + '/baseline_corr_' + d[2].trim() + '.html'
        var basel_corr_nocorr = rootbl + '/baseline_corr_nocorr_' + d[2].trim() + '.html'
        var rawdata = rootbl + '/rawdata_' + d[2].trim() + '.html'

        if (state_ctrl_proc == 'proc'){
             childifr.attr('src', dil)           // Changing source of iframe to proc
            }
        else if (state_ctrl_proc == 'preproc'){
             childifr.attr('src', basel)         //  Changing source of iframe to preproc
            }

        //----------- Show dilation
        
        var showdl = document.getElementById("show_dilation")
        showdl.onclick = function() {              // Show dilation
               childifr.attr('src', dil)           // dilation
               state_ctrl_proc = "proc"
               } // end showdl.onclick

        //----------- Show rawdata
        
        var showraw = document.getElementById("show_rawdata")
        showraw.onclick = function() {              // Show raw data
               childifr.attr('src', rawdata)           // rawdata
               state_ctrl_proc = "proc"
               } // end showdl.onclick

        //----------- Show baseline

        var showbl = document.getElementById("show_baseline");
        showbl.onclick = function() {             // Show baseline
               childifr.attr('src', basel)        //  baseline
               state_ctrl_proc = "preproc"
               $('#ctrl_BL').show()
               }                                  // showbl.onclick

        //--- BL + orig

        var bl = document.getElementById("BL");
        bl.onclick = function() {                 // Show BL
               childifr.attr('src', basel)        //  baseline
               }                                  // showbl.onclick
        
        //--- profile with substracted BL

        var bl_corr = document.getElementById("BL_corr");
        bl_corr.onclick = function() {                       // Show BL_corr
               childifr.attr('src', basel_corr)              //  Baseline
               }                                             // showbl.onclick
        
        //--- profile with substracted BL vs profile

        var bl_corr_nocorr = document.getElementById("BL_corr_nocorr");
        bl_corr_nocorr.onclick = function() {                                  // Show BL_corr_nocorr
               childifr.attr('src', basel_corr_nocorr)                         //  Baseline
               }                                                               // showbl.onclick

        /*
        Western blot
        */

        $('#divgel').empty()

        // title divgel

        txtdivgel = ''
        $('[grp]').each(function(){
             if ($(this).attr('grp')==$('#' + d[0]).attr('grp')){
                    txtdivgel += $(this).attr('id') + ' '
             } // end if
        })

        $('.title_gel_text').text(txtdivgel)   // loading the title

        // Adding the pictures

        for (i=3; i>-1; i--){      // from last to first
            var imgwb = $('<img/>').attr('src', rootbl +'/gel_'+ i + '.png')
                                .attr('width','20px')
                                .attr('height','350px')
                                .css({'z-index':'60'})
            $('#divgel').append(imgwb)

          } // end for

      } // end show_bokeh

      //--------------- Different baselines

      //------------- Defining Context Menu actions

      //$('#ctrl').addClass('context-menu-well')

      $(function() { // function for Context-Menu
        //alert('making context menu')
        $('iframe').load( function() {
          $('iframe').contents().find(".bk-canvas-events").addClass('context-menu-well')
          //.append($("<style type='text/css'>  .my-class{display:none;}  </style>"));
          });
    
        $.contextMenu({
            selector: '.context-menu-well', 
            items: {
                "dilation": {name: "dilation", disabled: false, icon: 'context-menu-icon context-menu-icon-dilation', callback: function(key, opt){ // Set dilation
                    // alert('dilation')
                        // var d = [$(this).attr('id'), well2molec[$(this).attr('id')]]
                        // onclick_elem(d)
                        // if (list_grp[$(this).attr('id')] == 'ref'){   // change only if ref
                        //     $('#grp_' + $(this).attr('id')).click()
                        //     list_grp[$(this).attr('id')] = 'molec'
                        //}
                      } // end item
                  },  // end callback
                "baseline": {name: "baseline", disabled: false, icon: 'context-menu-icon context-menu-icon-baseline', callback: function(key, opt){  // Set baseline
                    // alert('helllooo')
                      // var dicw = root + "/dict_wells.csv" +'?random='+new Date().getTime() ; // address of the file containing the correspondencies. 
                      // alert(dicw)
                      // d3.text(dicw, function(data) {
                      //     var parsedctx = d3.csv.parseRows(data, function(d, i){
                      //         var newval = ' value is '+d[2]
                      //         alert(newval)
                      //     })
                      // })
                      //----------- Show baseline
                      // var childifr = $('#ctrl').children('iframe')

                      // var grpspl = d[2].trim().split('_')  //
                      // var basel = root + '/proc_' + grpspl[0] + '_' + grpspl[1] + '/baseline_' + d[2].trim() + '.html'
                      // alert(basel)
                      
                      // childifr.attr('src', basel) //  baseline                
                    } // end item
                  }  // end callback
            } // end items
        }); // end contextMenu
    }); // end function for ContextMenu

    //----------------------  #  list of molecules

    //---------------------- Enter the theme
   
    var input_theme = $('<input/>').attr('type', 'input')
                                .attr('value','')
                                .attr('id', 'pattern_molec_input')
                                .attr('name', 'pattern_molec_input') // necessary for .val()
                                .attr('ttname', 'sorting tool') // necessary for .val()
                                .css({'width':'120'}) // , 'margin-left':'30px'
  
    var span_txt_input_theme = $('<span/>').text('filter: ')
                                           .append(input_theme) // filter for names
                                           .append($('<br/>'))
    span_txt_input_theme.addClass('ttip')


    //---------------------- Enter Comments
   
    var input_comments = $('<input/>').attr('type', 'input')
                                .attr('value','')
                                .attr('id', 'input_comments')
                                .attr('name', 'comments')               // necessary for .val()
                                .attr('ttname', 'input for comments')   // necessary for .val()
                                .css({'width':'250'})                   // , 'margin-left':'30px'
    
    // ----------------------- Select options for Comments

    var select_comment = $('<select/>').attr('id', 'select_comments')
                                       .attr('name', 'sel_comments')
                                       .addClass("selectpicker")
    list_comments = ['no PDZ signal', 'unable to dicriminate PDZ', 'Messy signal', 'Data recovered but still bad']
    var options_comments = ''
    for (i=0; i<4; i++){
        options_comments += '<option value='+ i + '>'+ list_comments[i] + '</option>'
    }
    select_comment.html(options_comments)

    // ----------------------- Span for Comments

    var span_txt_input_comments = $('<span/>').text('Comments: ')
                                              .append(input_comments) // filter for names
                                              .append(select_comment)
    span_txt_input_comments.addClass('ttip')

  
    //-------------- Submit the theme

    /*
    List of the molecules
    Plot are linked to click events on molecules names
    */

    var well2molec = {}; // dictionary for passing from well to molecule
    var molec2well = {}; // dictionary for passing from molecule to well
    var well2d = {}  // associating d to the well
    
    var sort_list_well_molec = 'desc'  // by default list oriented down
    // --- hover wells
    var divhov = $('<div/>').addClass('divhov').hide() // Tooltip with molec name when hovering the wells
    $('body').append(divhov)
    
    /*
    Tooltip
    */

    var ttip = $('<div/>').addClass('divttip')
                          .attr('id', 'ttip')
                          .text('ttip')      // Tooltip
    $('body').append(ttip)
    $('#ttip').hide() // Tooltip for explanations

    var make_list_molec = function(){

        /*
        Reads the csv file  /dict_wells.csv, and show the BIs
        */
   
        $('.molec').remove()
        // $('.divhov').remove()
        var dicw = root + "/dict_wells.csv" + '?random=' + new Date().getTime() ; // address of the file containing the correspondencies. 
        // alert(dicw)
            // --- list of molecules
        // alert('cleaning ordered_list_molec..')
        
        var ol = $('<ul/>').addClass('ordered_list_molec')  // begin list_molec
        $('.ordered_list_molec').remove()
        patt = $('#pattern_molec_input').val()
        
        //------- Pass here the first time

        var make_dic_well = function(dicw){
              d3.text(dicw, function(data) {
              var parsedCSV = d3.csv.parseRows(data, function(d, i){
                    //----- make the dictionaries
                    well2molec[d[0].trim()] = d[1].trim()          // correspondence well-->molec
                    molec2well[d[1].trim()] = d[0].trim()          // correspondence molec-->well
                    well2d[d[0].trim()] = d                        // correspondence well-->data
                    if(d[0].trim() == well2molec['last_well']){    // using last well information for triggering "make_all_elems_plate"
                          make_all_elems_plate()
                    }
                  });                                         // end parsedCSV
                });                                           // end text
              }                                               // end make_dic_well

        var colwell = function(d){       // Define the colors
            /*
            Color the wells
            */
            // alert("######### In colwell !!!!!")
            //------
            var BI_col = d[3] || -2                                // BI for color intensity
            // alert(BI_col)
            var mood = d[4] || 'smile';

            // if (mood.trim() != 'bad'){                          // BI color for valid data
            if (BI_col.trim() != "ref"){                           // valid well, BI defines the color
                var col = BIcolor(1-parseFloat(BI_col))  
               }
            else if (BI_col.trim() == "defect"){                   // defective well, green
                var col = '#00ff00' 
                // alert("Defective well")
               }
            else {                                                  // reference
                var col = '#ffffcc' // #999966  #ffffcc #33cc33 #d6f5d6
                sgrp = d[2].trim().split('_')
                $('#' + d[0]).attr('reference', sgrp[1])     // reference well
               }  
            $('#' + d[0]).attr('original_color', col)
            
            if (mood.trim() == 'bad'){
                var col = 'grey'
                $('#' + d[0]).attr('mood', 'sad')                 // Black color for invalid data
            }
            // wells color
            $('#' + d[0]).attr('color', col)                      // coloring the well with BI
            $('#' + d[0]).css({'fill': col})  
            return col
        }   

        // Make a single element

        var make_elem_plate =  function(d){
            // alert('in make_elem_plate')
            // alert(d[0])
            // search pattern in the input
            if ((d[1].search(patt)!=-1) & (d[0].trim() != 'well') & (d[0].trim() != 'last_well')){  
                // alert('after d[1].search(patt)!=-1')
                $('#' + d[0]).attr('class', 'well processed')     // add class processed 
                var BI = d[3] || 'no value'
                $('#' + d[0]).attr('BI', BI) 

                // //-----------  Dealing with colors and BI

                col = colwell(d)
                // alert(col)
                // alert('make col')

                // -------

                sgrp = d[2].trim().split('_')
                $('#' + d[0]).attr('grp', sgrp[1])                                 // keeping the group

                //----------- hover wells
                
                /*
                keywords hover well, well hover, hover
                */

                $('#' + d[0]).hover(function(){
                    var molname = $('<p/>').text(d[1].trim())                       // molecular name
                    var bindindex = $('<p/>').text('BI : ' + BI)                    // Binding INdex
                    var wellname = $('<p/>').text('well : ' + d[0])                 // Binding INdex
                    
                    divhov.empty()
                    divhov.append(molname)
                    divhov.append(bindindex)
                    divhov.append(wellname)
                    divhov.css('left', 40 + parseInt($('#' + d[0]).attr('x')))       // tooltip position in x
                    divhov.css('top', parseInt($('#' + d[0]).attr('y'))+10)          // tooltip position in y -85
                            if (!divhov.is(':visible')){
                                  divhov.toggle()
                            }  
                }) // end hover

                //-------  line molec for list wellsmolec

                var chckbox_listmolec = $('<input/>').attr('name', 'chckbx' + d[0].trim())
                         .attr('id', 'chckbx' + d[0].trim())
                         .attr('class', 'chckbx_sort')
                         .attr('type', "checkbox")
                         .css({'left':'280px', 'top':'-30px'}) //.
                var spanchckbx = $('<span/>').append(chckbox_listmolec)        // checkbox for multiple plots
                var spancell = $('<span/>').text(' ' + d[0].trim() + ' ')
                                           .css({'color': 'grey'})             // well name
                var spanmolec = $('<span/>').attr('id', d[1].trim())
                                            .addClass('namemolec')
                                            .text(d[1] + ' ')                  // molec name 
                                            .css({'color': 'black'})                  
                var spanBI = $('<span/>').text(BI).css({'color': col})         // coloring the molec name according to BI
                var line_molec = $('<p/>').addClass('molec')                   // line in wells_molec list
                                          .attr('idrefresh', 'name')
                                          .html($('<p/>').append(spanchckbx)   // checkbox
                                                         .append(spancell)     // well name
                                                         .append(spanmolec)    // molec name
                                                         .append("..")         // binding index
                                                         .append(spanBI)       // binding index
                                                         )    
                                          .click(function(){
                                                   show_bokeh(d)               // show a new plot
                                              }) // end click
                var li = $('<li/>').append(line_molec)
                sgrp = d[2].trim().split('_')
                li.attr('idwell', d[0].trim())
                  .attr('idmolec', d[1].trim())
                  .attr('idgrp', sgrp[0] + sgrp[1])                           // adding classes idwell, idmolec and idgrp for sorting on list 
                  .attr('grppos', sgrp[2])                                    // adding classes idwell, idmolec and idgrp for sorting on list molec_wells
                ol.append(li)
                $('#wellsmolec').append(ol)  // adding the built list to the div..
                } // end if  d[1].search(patt)!=-1 etc..
            else{
                $('#' + d[0]).attr('class', 'well' ) // 
                }
        } // end make_elem_plate
        
        // Make all the elements

        var make_all_elems_plate = function(){
              for (w in well2molec){
                    var d =  well2d[w] // transmit the whole  information
                    // alert(d)
                    make_elem_plate(d) // make a single element
                    if(d[0].trim() == well2molec['last_well']){
                      tinysort('ul.ordered_list_molec>li', {order : 'asc', attr : 'idwell'});   // 
                      } // end if
                    } //end for
                    // alert('numb_elem is ' + numb_elem)
                } // end make_all_elems_plate

        //-----------

        if (well2molec['well'] != 'molec'){     // If the dictionary not yet done
            patt = '' // initial pattern
            make_dic_well(dicw);
            }
        else{
            make_all_elems_plate()
            }
      } // end make_list_molec

    var refresh_list_molec = function(){
            // alert('refresh_list_molec')
          patt = $('#pattern_molec_input').val()
          // alert('pattern is ' + patt)
          make_list_molec()
    }

    var sort_active = {'background-color':'#ff9999'}
    var sort_inactive = {'background-color':'#ffffff'}

    // ------------- Submit comment

    var butt_comments = $('<input/>').attr('type', 'button')   // Select molecules with pattern  
                                .addClass('btn btn-default')
                                .attr('value','submit')
                                .attr('id', 'make_comment')
                                .attr('ttname', 'Valid comments')
                                // .click(function(){
                                //     alert("Validating comment !!!!")
                                //     socket.emit('message', 'Sending comments !!!!')
                                // })  // end click
    var submit_comment = $('<span/>').append(butt_comments)
    submit_comment.addClass('ttip')

    // ------------- Sort by group

    var butt_grp_tsort= $('<input/>').attr('type', 'button')   // Select molecules with pattern  
                                .addClass('btn btn-default')
                                .attr('value','groups')
                                .attr('id', 'sort_grp')
                                .attr('ttname', 'Sort by group name')
                                //.css({'margin-left':'100px'})
                                .click(function(){
                                    $(this).css(sort_active)             // change color of button to active state
                                    $('#sort_molec').css(sort_inactive)  // inactive state
                                    $('#span_molec_sort').html('')
                                    $('#sort_well').css(sort_inactive)  // inactive state
                                    $('#span_well_sort').html('')
                                    refresh_list_molec()                  // refresh list and plate
                                    //-------
                                    tinysort('ul.ordered_list_molec>li', {order : sort_list_well_molec, attr : 'idgrp'});   // sorting with tinysort
                                    if (sort_list_well_molec == 'desc'){   // sorting in ascending mode
                                        sort_list_well_molec = 'asc'
                                        $('#span_grp_sort').html('<i class="fa fa-arrow-up" aria-hidden="true"></i>')  // arrow up
                                        }
                                    else{                                 // sorting in descending mode
                                        sort_list_well_molec = 'desc'
                                        $('#span_grp_sort').html('<i class="fa fa-arrow-down" aria-hidden="true"></i>')  // arrow down
                                       }
                                })  // end click
    var submit_grp_tsort = $('<span/>').append(butt_grp_tsort)
    submit_grp_tsort.addClass('ttip')

    var span_grp_sort = $('<span/>').attr('id','span_grp_sort') // span for arrow up and down

    // ------------- Sort by well

    var butt_well_tsort= $('<input/>').attr('type', 'button')   // Select molecules with pattern  
                                .addClass('btn btn-default')
                                .attr('value','well')
                                .attr('id', 'sort_well')
                                .attr('ttname', 'Sort by well name')
                                //.css({'margin-left':'100px'})
                                .click(function(){
                                                    // alert('in sort_list_well_molec  !!!!!!!!!!')
                                      $(this).css(sort_active)             // change color of button to active state
                                      $('#sort_molec').css(sort_inactive)  // inactive state
                                      $('#span_molec_sort').html('')
                                    $('#sort_grp').css(sort_inactive)  // inactive state
                                    $('#span_grp_sort').html('')
                                      refresh_list_molec()                  // refresh list and plate
                                    //-------
                                      tinysort('ul.ordered_list_molec>li', {order : sort_list_well_molec, attr : 'idwell'});   // sorting with tinysort
                                                      // alert('sort_list_well_molec ' + sort_list_well_molec)
                                      if (sort_list_well_molec == 'desc'){   // sorting in ascending mode
                                            sort_list_well_molec = 'asc'
                                            $('#span_well_sort').html('<i class="fa fa-arrow-up" aria-hidden="true"></i>')  // arrow up
                                          }
                                      else{                                 // sorting in descending mode
                                            sort_list_well_molec = 'desc'
                                            $('#span_well_sort').html('<i class="fa fa-arrow-down" aria-hidden="true"></i>')  // arrow down
                                         }
                                })  // end click
    var submit_well_tsort = $('<span/>').append(butt_well_tsort)
    submit_well_tsort.addClass('ttip')

    var span_well_sort = $('<span/>').attr('id','span_well_sort') // span for arrow up and down

    // ------------- Sort by molec

    var butt_molec_tsort =$('<input/>').attr('type', 'button')   // Select molecules with pattern  
                            .addClass('btn btn-default')
                            .attr('value','molec')
                            .attr('id', 'sort_molec')
                            .attr('ttname', 'Sort by molecular name')
                            //.css({'margin-left':'100px'})
                            .click(function(){
                                  $(this).css(sort_active)  // change color of button to active state
                                  $('#sort_well').css(sort_inactive)  // inactive state
                                  $('#span_well_sort').html('')
                                $('#sort_grp').css(sort_inactive)  // inactive state
                                $('#span_grp_sort').html('')
                                  refresh_list_molec()       // refresh list and plate
                                  tinysort('ul.ordered_list_molec>li', {order: sort_list_well_molec, attr:'idmolec'});  // jQuery tinysort
                                  if (sort_list_well_molec == 'desc'){      // sorting in ascending mode
                                        sort_list_well_molec = 'asc'
                                        $('#span_molec_sort').html('<i class="fa fa-arrow-up" aria-hidden="true"></i>')  // arrow up
                                        }
                                  else{                                     // sorting in descending mode
                                        sort_list_well_molec = 'desc'
                                        $('#span_molec_sort').html('<i class="fa fa-arrow-down" aria-hidden="true"></i>')  // arrow down
                                        }
                             }) // end click

    var submit_molec_tsort = $('<span/>').append(butt_molec_tsort)
    submit_molec_tsort.addClass('ttip')

    var span_molec_sort = $('<span/>').attr('id','span_molec_sort') // span for arrow up and down

    //------------  Adding the buttons to wellsmolec

    //---------------------- multiple plots
    
    //--------- Make the plots

    var input_button_manyplots = $('<input/>').attr('type', 'button')  // when clicked, triggers the plot
                                .attr('value', 'plot')
                                .addClass('btn btn-default')
                                .attr('ttname', 'plot the selected profiles')
                                .attr('id', "manyplots")
                                .css({'margin-left':'20px'})
                                .attr('name', 'plot')

    //---- Make the plots tooltip

    var button_manyplots = $('<span/>').append(input_button_manyplots).addClass('ttip')
    $('<div/>').attr('id', 'tt_plot')
               .text('Show all the selected plots together')
               .hide()

    //--------- Show the plots

    var input_show_manyplots = $('<input/>').attr('type', 'button')
                            .attr('value', 'show')
                            .attr('name', 'show')
                            .addClass('btn btn-default')
                            .attr('ttname', 'show the plots planel')
                            .attr('id', "showplots")
                            .css({'margin-left':'2px'})
                            .click(function(){   
                                 $('#superimpose').toggle()  
                              }) // end click

    var  chckbox_origplt = $('<input/>').attr('class', 'chckorigplt')
                                .attr('name', 'chckorigplt')
                                .attr('id', 'box_origplt')
                                .attr('type', "checkbox") 

    //---- Show the plots tooltip

    var show_manyplots = $('<span/>').append(input_show_manyplots).addClass('ttip')
    $('<div/>').attr('id', 'tt_show')
               .text('Show all the selected plots together')
               .hide()

    var show_origplots = $('<span/>').text('raw_data ').append(chckbox_origplt)     // select the raw dataset for plotting

    //------------  Adding comments

    $('#wellsmolec').append(span_txt_input_comments) // btn btn-default
    $('#wellsmolec').append(submit_comment).append($('<br/>'))                     // button for validating comments

    //------------  Adding the Sorting buttons to wellsmolec


    $('#wellsmolec').append(span_txt_input_theme) // btn btn-default
                    .append($('<br/>'))
    // Sort by well
    $('#wellsmolec').append(submit_well_tsort)  // button sort well
                    .append(span_well_sort)     // arrow
                    
    // Sort by molec
    $('#wellsmolec').append(submit_molec_tsort) // button sort molec
                    .append(span_molec_sort)    // arrow

    // Sort by group
    $('#wellsmolec').append(submit_grp_tsort) // button sort groups
                    .append(span_grp_sort)    // arrow
    
    // Make multiple plots
    $('#wellsmolec').append(button_manyplots)
                    .append(show_manyplots)
                    .append(show_origplots)
                    .append($('<br/>'))
                    .append($('<br/>'))
                    .append($('<br/>'))

    //-------- Initialization with right sorting order

    var nbclick = 0

    $('#sort_well').click(function(){

       setTimeout(function() {
              nbclick += 1
              if (nbclick < 2){
                  $('#sort_well').click()
              }
         }, 100); // end setTimeout
      }); // end first click
    $('#sort_well').click()

    //----------------------

    var tr = function(w, h, ang){      // Translation and Rotation
       ang = ang || 0
       return "translate(" + w + ","+ h + ") rotate(" + ang + ")"
        }

    var add_html = function(node, htm, w, h, ang){ // adding html in the plot
        var htmnode = node.append('foreignObject')
            .attr("transform", tr(w-100, h, ang))
            .attr('width', 50)
            .attr('height', 50)
            .append("xhtml:body")
            .html(htm)
        return htmnode
        }

    /*

    Method for drawing the Plate
    Parameters:
        * m : number of rows
        * n : number of columns
        * spacing : spacing between the squares

    */

    var make_plate = function(m, n, spacing){
        // make a plate

        well_col = '#afa2dc';
        offsety = 0.75                   // offset for last blocks not touching the bottom edge in y
        offsetx = 0.25                   // offset for the blocks on the left not touching the edges in x
        var data = [];                   // list containing the coordinates of the wells. 
        for (var i = 0; i <= m*n-1 ; i++) { // make the position of the wells
            data.push({xcoord: i%n+offsetx, ycoord: Math.floor(i/n)+offsety});
            }// end for
        // var shift_left = 25

        //--------------------- Brush

        var margin = {top: 40, right: 20, bottom: 60, left: 40},
            width = n*spacing - margin.left - margin.right,
            height =  m*spacing - margin.top - margin.bottom;

        var x = d3.scale.linear()
            .range([0, width])
            .domain([0, n]);

        var y = d3.scale.linear()
            .range([height, 0])
            .domain([0, m]); 

        var brush = d3.svg.brush()
            .x(x)
            .y(y)
            .on("brush", brushmove)
            .on("brushend", brushend);

        var svg = d3.select(".div_plate").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr('class','plate')
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        // Rows and columns numbering
        //shift_left

        for(i=0; i<m; i++){                // lines numbering
          var letter = String.fromCharCode(65+i)
          add_html(svg,'<p>'+letter+'</p>', margin.left + 40, (i+1-offsety)*height/m)
        }
        for(i=0; i<n; i++){               // columns numbering
          var j= i+1
          add_html(svg,'<p>'+j+'</p>',(i+offsetx)*width/n+margin.left + 60, margin.top-55)
        }
        /*
        Dictionary making the correspondence between index and well
        */

        dic_index_well = {}
        dic_well_index = {}

        index_well = 0
        for(i=0; i<m; i++){                               // lines numbering
            var letter = String.fromCharCode(65+i)
            for(j=1; j<n+1; j++){                         // columns numbering
                index_well += 1
                dic_index_well[index_well] = letter+j     // dictionary from index to well 
                dic_well_index[letter+j] = index_well     // dictionary from well to index 
            }
        }
        
        //---------------

        svg.append("g")
            .attr("class", "brush")
            .call(brush)
          .selectAll('rect')
            .attr('height', height);

        svg.append("defs").append("clipPath")
            .attr("id", "clip")
          .append("rect")
            .attr("width", width)
            .attr("height", height + 20);

        wells = svg.selectAll(".well")
            .data(data)
            .enter().append("rect")
            .attr("class", "well")
            .attr("clip-path", "url(#clip)")
            .attr("height", size_rect)
            .attr("width", size_rect)
            .attr("x", function(d) { return x(d.xcoord); })
            .attr("y", function(d) { return y(d.ycoord); })
            .attr("id", function(d){
                  var xcorr = d.xcoord+1-offsetx;
                  var ycorr = m-d.ycoord-1+offsety;
                  return String.fromCharCode(65+ycorr)+ xcorr
            })
            //.call(d3.well_select.tooltip());
        
        /*
               Interaction with wells
        */

        //----------------------  click on well and show spectrum

        // $('.well').click(function(){
        //     if (show_coord){
        //         var id = $(this).attr("id");
        //             if (typeof(id)=='string'){
        //                 //alert(id)  // show coordinate of the well clicked.
        //                 $('#ctrl').children('iframe').attr('src', 'data/'+id + '.html')
        //                 //$('#ctrl').toggle()
        //               } // end if
        //        } // end if show_coord

        /*
        keywords: well click, click well
        */
    
       $('.well').click(function(){
           var id = $(this).attr("id");
           $('#current_well').attr('value', id)
                             .attr('mood', $(this).attr("mood"))

           var dicw = root + "/dict_wells.csv" + '?random=' + new Date().getTime() ; // address of the file containing the correspondencies. 

           var treat_smile = function(d){
                  var mood = d[4] || 'smile';
                        // alert('mood is '+ mood)
                        if (mood.trim() == 'smile'){
                            set_smile(d[0])
                            // smileclick() 
                        }
                        else if (mood.trim() == 'bad') {
                            set_sad(d[0])
                            // smileclick()
                        } 
                }

           d3.text(dicw, function(data) {
               var parsedCSV = d3.csv.parseRows(data, function(d, i){
                   // alert(d[0].trim())
                   if (id == d[0].trim()){                // reading all wells
                        // ---------  Dealing with smile
                        // alert('dealing with smile')
                        treat_smile(d)
                        smileclick()
                        show_bokeh(d)
                        // keep_bad()

                        if ($('#wellsmolec').css('z-index') == 10){
                           $('#ctrl_sw_lm').click()
                          }
                      } // end if id == d[0].trim()
                 }); // parseRows
             }); // end d3.text
         
           // if (show_coord){
           //     var id = $(this).attr("id");
           //         if (typeof(id)=='string'){
           //             //alert(id)  // show coordinate of the well clicked.
           //             $('#ctrl').children('iframe').attr('src', 'data/'+id + '.html')
           //             //$('#ctrl').toggle()
           //           } // end if
           //    } // end if show_coord
    
            /*

            Change well color for wells out of processed area

            */
            if($(this).attr("class") == "well selected"){
                $('.selected').css({'fill': well_col}) // Color well
               }
            else{
                $(this).css({'fill': well_col})
               }
        }) // end click well
    
        //---------------------- Brush

        function brushmove() {
          extent = brush.extent();
          wells.classed("selected", function(d) {
            is_brushedx = extent[0][0]-0.5 <= d.xcoord && d.xcoord <= extent[1][0];
            is_brushedy = extent[0][1]+0.5 <= d.ycoord && d.ycoord <= extent[1][1];
            is_brushed = is_brushedx && is_brushedy;
            return is_brushed;
          });
        }
        //---------------------- Brush end

        function brushend() {
          reset_axis();
          wells.classed("selected", false);
          d3.select(".brush").call(brush.clear()); 
        }

        //----------------------

        function reset_axis() {
          svg.transition().duration(500)
           .select(".x.axis")
           .call(xAxis);
        }
        //---------------------- Brush selected area
   
        function domext_int(x, y, extent) {
            x1 = Math.round(x(extent[0][0])); x2 = Math.round(x(extent[1][0])) // x1, x2
            y1 = Math.round(y(extent[0][1])); y2 = Math.round(y(extent[1][1]))  // y1, y2
            return [x1,x2,y1,y2]
        }

    /*

    Keys events

    functionnalities:
        * k: show the keys for interaction with the page.
        * c: toggle control panel contianing the processing plots
        * t: toggle interaction with the Plate
        * e: rectangle around the selected wells
        * b: if toggled permits to color cases in yellow
        * p: if toggled permits to color cases in green
        * d: deactivate color for peptides and biotine
        * a: make an alert on the selected wells

    */

        var keyev = function(key, event){
            return (event.keyCode == key.charCodeAt(0)-32 )
          }
      
          $(document).keydown(function(event){   

             //---------------------- Toggle Control plots
          
             if(event.keyCode == 27){ // Trigger statekeys with Escape
                   statekey *= -1
                   $('.interact').toggle()
                 } // end if

            //---------------------- Toggle type of plate
          
              if(keyev('t', event)){    //
                  $('.type_plate').toggle()
                } // end if key code
          
             //---------------------- Toggle Shortcuts
          
              if(keyev('k', event)){    //
                  $('#shortcuts').toggle()
                } // end if key code
            
             //---------------------- Toggle Control plots
          
              if(keyev('c', event) && statekey == 1){    //
                  $('#ctrl').toggle()
                } // end if key code

            //---------------------- red rectangle around selected wells

              if(keyev('e', event) && statekey == 1){    //
                  //alert(extent);
                  listcoord = domext_int(x,y, extent)
                  x1 = listcoord[0]; x2 = listcoord[1];
                  y1 = listcoord[2]; y2 = listcoord[3];

                  svg.append("rect")
                     .attr("x", function(){return x1})
                     .attr("y", function(){return y2})
                     .attr("width", function(){return Math.abs(x1-x2)})
                     .attr("height", function(){return Math.abs(y1-y2)})
                     .style("stroke","red")
                     .style("fill","red")
                     .style('opacity', .15)
                } // end if key code 

             //---------------------- Color wells for biotine

              if(keyev('b', event) && statekey == 1){    // color for biotine
                    well_col = col_biotine
                } // end if key code 

            //---------------------- Color wells for peptide

              if(keyev('p', event) && statekey == 1){    // color for peptide
                    well_col = col_peptide
                } // end if key code   

             //---------------------- Basic color

              if(keyev('d', event) && statekey == 1){    // deactivate biotine and peptide.
                    well_col = col_domain
                } // end if key code  

             //---------------------- show all brush selected wells 

              if(keyev('a', event) && statekey == 1){    // show selected wells
                  $('.selected').each(function(){
                      var id = $(this).attr("id");
                      if (typeof(id)=='string'){
                          //alert(id)
                        } // end if
                    })// end each            
                } // end if key code 

              //---------------------- show the plots one after another.. 

              var make_dic_scroll = function(){
                  ind_scr = 1            // index scroll
                  dic_scroll = {}                                           // Dictionary for navigating with the cursor
                  var sindex = 0                                            // scroll index of the current selected well,  initialized to 0
                  $('ul.ordered_list_molec>li').each(function(){            // read all elements in the oredered list
                         var idw = $(this).attr('idwell')                   // current examinated well
                         if ($('#current_well').attr('value') == idw){      // detect the current selected well
                             sindex = ind_scr                               // Keep in sindex the index of the well that is selected on the plate
                         } // end if
                         if ($('#'+idw).attr('class') == 'well processed'){               // if processed
                              if ($('#'+idw).attr('bi').trim() != 'not_calculated'){      // if calculated
                                  dic_scroll[ind_scr] =  idw                              // taking id of the well, fill the whole dictionary
                                  ind_scr += 1
                              }  // end if 
                         } // end if
                  })  // end each

                  //----------

                  // left right

                  wl = dic_scroll[sindex-1] // well left
                  wr = dic_scroll[sindex+1] // well right
                  list_wells_leftright = [wl, dic_scroll[sindex] , wr]     // 3 wells for going left or right

                  // up down

                  currwidx = parseInt(dic_well_index[dic_scroll[sindex]])
          
                  var wup = dic_index_well[currwidx-24] || dic_scroll[sindex]  // well up
                  var wdwn = dic_index_well[currwidx+24] || dic_scroll[sindex] // well down
                
                  list_wells_updown = [wup, dic_scroll[sindex] , wdwn]      // 3 wells for going up or down

                  //----------

                  dic_move = {'horiz':list_wells_leftright, 'vertic':list_wells_updown}       // Dictionary containing the list horiz and vertic for moves.

                  return dic_move
              }

              //---------------  Plate navigation

              //------ Horizontal

              if (event.keyCode == 37){                  // LEFT arrow for moving back on the wells
                    
                    dic_move = make_dic_scroll()         // list of 3 wells with the current one in the middle.
                    left_well = dic_move['horiz'][0]
                    if (exec_half%2 ==0){                // Correction for the issue of double execution of click
                       $('#' + left_well).click()
                    }
                    exec_half +=1                        // trick due to wellsmolec double refreshment
                    // alert('left')
                } // end if key code 

              if (event.keyCode == 39){                  // RIGHT arrow for moving forward on the wells
                    
                    dic_move = make_dic_scroll()         // list of 3 wells with the current one in the middle.
                    right_well = dic_move['horiz'][2]
                    if (exec_half%2 ==0){                // Correction for the issue of double execution of click
                       $('#' + right_well).click()
                    }
                    exec_half +=1                        // trick due to wellsmolec double refreshment
                } // end if key code 

              //------ Vertical

              if (event.keyCode == 40){                  // DOWN 

                    dic_move = make_dic_scroll()         // list of 3 wells with the current one in the middle.
                    down_well = dic_move['vertic'][2]
                    // alert("down_well " + down_well)
                    if (exec_half%2 ==0){                // Correction for the issue of double execution of click
                       $('#' + down_well).click()
                    }
                    exec_half +=1                        // trick due to wellsmolec double refreshment
                    // alert('left')
                } // end if key code 

               if (event.keyCode == 38){                 // UP

                    dic_move = make_dic_scroll()         // list of 3 wells with the current one in the middle.
                    up_well = dic_move['vertic'][0]
                    // alert("up_well " + up_well)
                    if (exec_half%2 ==0){                // Correction for the issue of double execution of click
                       $('#' + up_well).click()
                    }
                    exec_half +=1                        // trick due to wellsmolec double refreshment
                    // alert('left')
                } // end if key code 

          }) // end keydown
      
          var dim = {}
          dim['width'] = width
          dim['height'] = height
          return dim

    } // end make_plate

    //----------------------  Initialization of the plate

    var m = plate['384']['m'];
    var n = plate['384']['n'];
    var spacing = plate['384']['spacing'];
    make_plate(m, n, spacing) // initialization of the plate inside visualize

    $('#select_plate_usage').change(function() { // select between analysis and designer
        $('#plate_usage').text($(this).val())
    })// end change

    /*
    Panel for selecting the type of plate.
    */

    $('#select_plate').change(function() {                                                // select a plate 96 or 384
              d3.selectAll('.plate').remove()
              pl = $(this).val()
              var m = plate[pl]['m'];                                                     // number of lines
              var n = plate[pl]['n'];                                                     // number of columns
              var spacing = plate[pl]['spacing'];                                         // spacing between wells
              var dim = make_plate(m, n, spacing)                                         // draw the plate
              $('.div_plate').css({'width': plate[pl]['w'],'height': plate[pl]['h']})
              var width_plate = $('.div_plate').width()
              var height_plate = $('.div_plate').height()
              //alert(width_plate)
              var shift0 = width_plate + 40 + 'px'                                         // left shift for ctrl and change plate
              var shift1 = width_plate + 530 + 'px'                                        // for dicwells
              var shift2 = height_plate + 110 + 'px'                                       // vertical shift
              //alert(shift2)
              //divonside.css({'left': shift0})

              $('#ctrl').css({'left': shift0})                                             // Position of the control plot
              $('#wellsmolec').css({'left': shift1})                                       // Position of dic wells
              $('#shortcuts').css({'top': shift2})                                         // Position of shortcuts
              $('.list_proc').css({'top': shift2, 'width':width_plate*0.75})               // width(width_plate*0.75)
              
              // alert(plate[pl]['w'])
              // $('.div_plate').css({'width': 100,'height': 50})
              if (!$('#ctrl').is(":visible")){
                  $('#ctrl').toggle()
              }
        })// end change $('#select_plate')

        /*

        Tooltip hoover

        */

        make_ttip() // Make the tooltips

} // end visualize