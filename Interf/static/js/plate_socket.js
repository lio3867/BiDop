

// var name_proc = ''
$(document).ready(function(){

    // current_proc_folder = null;
    
    // io.set('log level', 1);
    namespace = '/plate_comm';        // 
    // var cwell = null ;  // current well 
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    //io.set('log level', 1);
    // Receiving 
    var lem0 = 0
    var lem1 = 0
    var lem2 = 0
    var lem3 = 0
    var lem4 = 0

    var lem00 = 0
    
    socket.on('message', function(msg) {
          if ($('#current_proc').attr('value') != msg){
            $('#'+ msg).click()                                     // Click on the right dataset name
            socket.emit('askcurrwell', 'askcurrwell');              // asking for current well
          }

          // ------------- 

          socket.emit('message', 'correctly received the time')

          /*
          Save the current folder
          */

          if (lem0 == 1){
                $('.name_proc').click(function(){
                    var name_proc = $(this).attr('id')
                    socket.emit('namefolder', name_proc);  //  sending the current folder
                    lem0 = 0
                  }) // end click

              } // end if

          /*
          Message for having the name of the current dataset
          */

          if (lem1 == 1){
                $("#submit_range").click(function(){
                    socket.emit('retrieve_dataset','message for retrieving name dataset')
                  }) // end click
              } // end if 

          /*
          Sending the signal for making the multiplot
          */

          if (lem2 == 1){
                
                $("#manyplots").click(function(){                              // click for making superimpositon of plots
                     list_plots = []                                           // list of plots to superimpose
                     $('#list_molec_manyplt').empty()                          // cleaning the window
                     var list_colors_manyplots = ['blue', 'green', 'red', '#ff66b3', '#ff8533', 'black'] // color for plots
                     var index_col = 0
                     var list_proc_checked = []                                // initializing the list of the dataset selected
                     list_proc_checked.push(proc_folder)                       // putting the current folder in the list of the dataset selected
                     $('.chckgrp').each(function(){
                        if ($(this).is(':checked')) {
                            list_proc_checked.push($(this).attr('id').slice(4))  // putting the checked dataset in the list
                          }
                        })

                     //------ list of plots for manyplots (plot superposition)

                     $('ul.ordered_list_molec>li').each(function(){
                          var many_col = list_colors_manyplots[index_col]
                          var namewell = $(this).attr('idwell')
                          var namemolec = $(this).attr('idmolec')
                          if ($('#chckbx' + namewell).is(':checked')) {         // Check the checkboxes in the list wellsmolec
                                var linewell = $('<span/>').text(namewell + ' : ').addClass('listwellplot') //.css({'color': many_col})
                                var linemolec = $('<span/>').text(namemolec).addClass('listmolplot').css({'color': many_col})
                                $('#list_molec_manyplt').append(linewell)       // adding name of the well in many plot window
                                                        .append(linemolec)      // adding name of the molec in many plot window
                                                        .append($('<br/>'))
                                // ---- plot name
                                var numgrp = $(this).attr('idgrp').slice(3)
                                var posgrp = $(this).attr('grppos')
                                for (i in list_proc_checked){

                                    // Plot the original dataset

                                    var root_pickles = 'Interf/static/' + list_proc_checked[i] + '/'
                                    if ($('#box_origplt').is(':checked')){       // original plots
                                        var elem_list_plots =  root_pickles + 'proc_grp_' + numgrp + '/' + 'baseline_corr_nocorr_grp_' + numgrp + '_' + posgrp + '.p'
                                    }

                                    // Plot the processed dataset

                                    else{               // processed plots
                                        var elem_list_plots =  root_pickles + 'proc_grp_' + numgrp + '_' + posgrp + '_dilat.p'
                                    }
                                    // alert(elem_list_plots)
                                    list_plots.push(elem_list_plots)   // Adding element to list
                                }
                                // alert(elem_list_plots) 
                                index_col += 1
                          } // end if checked
                     }) // end each 'ul.ordered_list_molec>li'
                     // alert(list_plots)
                     $('#infos_plots').attr('value', JSON.stringify(list_plots)) // Using json for transmitting
                    socket.emit('manyplots', $('#infos_plots').attr('value') )   // 
                  }) // end click "#manyplots"

              } // end if  lem2

          if (lem3 == 1){
                $('#proc_options').click(function(){ // show options
                    // alert('show opt !!!')
                    socket.emit('proc_params', 'give me the params !!! please' )   // 
                }) // end click
              }

              /*
              Sending to the server the informations about the smiley
              Sending in the same time : the current folder, the current well and the current mood
              */

              $('#smile').click(function(){ 
                    var currp = $('#current_proc').attr('value')
                    var currw =  $('#current_well').attr('value')
                    var currm =  $('#current_well').attr('mood') || 'smile'
                    smile_infos = JSON.stringify([currp, currw, currm])
                    socket.emit('wrong_wells', smile_infos)
                }) // end click

          /*
          Save the current well
          */

          if (lem00 == 1){
              $('.well').click(function(){
                // alert('hello')
                var currp = $('#current_proc').attr('value')
                var currw =  $('#current_well').attr('value')
                // alert('sending new well ' + currw)
                var infos_well = JSON.stringify([currp, currw])
                socket.emit('infos_well', infos_well);              // sending the current well name
                lem00 = 0
                }) // end click
            } // end if

          if (lem00 == 1){
              $('#make_comment').click(function(){
                // alert("Validating the comment !!!!! websocket !!!")
                var currp = $('#current_proc').attr('value')
                var currw =  $('#current_well').attr('value')
                var valcomm = $('#input_comments').val()
                if (valcomm.length != 0){
                    // alert("using input comment")
                    var current_comment = valcomm
                }
                else {
                    // alert('using selected comment ')
                    var current_comment = $("#select_comments option:selected").text()
                }
                // alert(current_comment)
                comment_infos = JSON.stringify([currp, currw, current_comment])
                socket.emit('comment', comment_infos);              // sending the current well name
                lem00 = 0
                }) // end click
            } // end if

          lem0 += 1
          lem00 += 1
          lem1 += 1
          lem2 += 1
          lem3 += 1
          lem4 += 1

        }     // end on message, function
      );    // end socket on message
      
    // ----------  Deals with current well

    socket.on('currwell', function(msg) { 
        if ($('#current_well').attr('value') != msg){         // Comparing current well with well registered.
            $('#' + msg).click()
           } // end if
        }) // end socket on currwell

      // ----------  Superimpose graphs

      socket.on('superimp', function(msg) {   
          if (msg == 'done'){       // profiles superimposition is OK    
                // alert("new superimposed plots...")                                     
                var childsuperimp = $('#superimpose').children('iframe')
                var graphsuperimp = '/static/superp.html?random=' + new Date().getTime() // Bokeh dilation plot random id for refreshing
                childsuperimp.attr('src', graphsuperimp)                               // Changing source of iframe
                // $('#showplots').click()
                if (! $('#superimpose').is(':visible')){
                    $('#superimpose').toggle()  //.append($('#list_molec_manyplt'))
                  }
          } //end if
       }) // end socket on superimp

       // ----------  Proc params

       /*
       Reads all parameters transmitted with json 
       */

       socket.on('params_proc', function(msg) {   
              // alert(msg)
              var process = JSON.parse(msg)  //  Reads the json for the reprocessing parameters
              $('#range_analysis').val(process['range_analysis'])
              $('#range_norm').val(process['range_norm'])
              $('#iter').val(process['iter'])
              $('#nbchunks').val(process['chunks'])
              $('#speed').val(process['speed'])
              $('#range_elems').val(process['range_elems'])
              $('#range_y_adjust').val(process['range_y_adjust'])

          }) //   retrieving params for processing or reprocessing

       /*
       Detect reprocessing
       */

       socket.on('reproc_ok', function() {   
            // alert('Reprocessing is effective !!!!!!!!')
            $('#reproc_ok').show()
          }) //   retrieving params for processing or reprocessing


});// end document ready

