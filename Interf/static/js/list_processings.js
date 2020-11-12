var list_processings = function(ol){

    //-------  activate deactivate tooltips

    
    $('#trig_ttip').click(function(){
       
        if (show_tooltips){
            $('.ttip').hover(function(){
              $('#ttip').hide()
            })
            show_tooltips = false
        }
        else{

            $('.ttip').hover(function(){
              $('#ttip').show()
              })
            show_tooltips = true
        }
    })

    //-----------------

    $('body').append($('<div/>')
             .attr('class','list_proc') // Main panel for the processed datasets
             .attr('id','list_proc')
             )
    $('body').append($('<div/>')
         .attr('class','show_list_proc')  // Bar for showing hiding
         // .attr('id','list_proc')
         )
    var currproc = $('<div/>').attr('id','current_proc') // object to stock value of current dataset
                                .attr('value', '')
                                .hide()
    $('body').append(currproc)
    var currwell = $('<div/>').attr('id','current_well') // object to stock value of current well
                                .attr('value', '')
                                .hide()
    $('body').append(currwell)
                
    $('#list_proc').append($('<h2/>').text("Processings list").css({'text-align': 'center'})) 
    $('#list_proc').append($('<br/>'))

    //------------- Make list_proc go down and up

    $('.show_list_proc').click(function(){
        
        if ($('#wellsmolec').css('left') == '620px'){
                $('#list_proc').css({'top': '100px'})   // list_proc hidden
                $('#wellsmolec').css({'left':'120px', 'top':'470px', 'z-index':'5'})        //  wellsmolec on the left
            }
        else if ($('#wellsmolec').css('left') == '120px'){
                $('#list_proc').css({'top': '440px'})   // list_proc visible
                        // $('#wellsmolec').css({'left':'1110px', 'top':'70px'})           //  wellsmolec on the right
                $('#wellsmolec').css({'left':'620px', 'top':'70px', 'z-index':'15'})       //  wellsmolec on the right
            }  // , 'opacity':'0.7' 
        })

    //------------- add list to list_proc

    

    // Jinja Loop on the name of the folders containing the processings.

    //------------- begin loop for datasets names


    //------------- end for loop

    $('#list_proc').append(ol)                // Adding name of the folder with processing results

    //------------- Begin erasing datasets


    var form_erase_proc = $('<form/>').attr('id', 'form_erase_proc')  // Button for erasing folders with results
                                      .attr('action', '/visu')
                                      .attr('method', 'post')
    var button_erase_proc = $('<input/>').css({'margin-left':'25px', 'background-color':'#ffaa80'})
                            .attr('type', 'button').addClass('btn btn-default')
                            .attr('value','erase dataset')
                            .attr('id', "erase_proc")

        // var button_test = $('<input/>').css({'margin-left':'150px', 'background-color':'#ffaa80'})
        //                     .attr('type', 'button').addClass('btn btn-default')
        //                     .attr('value','test')
        //                     .attr('id', "testbutt")

    var infos_erase =  $('<input/>').css({'margin-left':'150px', 'background-color':'#ffaa80'})
                            .attr('type', 'input')
                            .attr('id', "infos_erase")
                            .attr('name', "infos_erase") // name used for server detection
    var alert_erase = $('<div/>').addClass('alert_erase').attr('id','alert_erase').hide().text('are you sure to delete those datasets?  ') //.css({'vertical-align':'true'})
    var button_erase_OK= $('<input/>')  
                            .attr('type', 'button').addClass('btn btn-default')
                            .attr('value','OK')
                            .attr('id', "erase_OK")
    var button_erase_cancel= $('<input/>')  
                        .attr('type', 'button').addClass('btn btn-default')
                        .attr('value','Cancel')
                        .attr('id', "erase_cancel")
    alert_erase.append($('<br/>'))
               .append(button_erase_OK)
               .append(button_erase_cancel)
    form_erase_proc.append(alert_erase)                  // adding alert for erasing
                   .append(button_erase_proc)            // adding the button for erasing
    // form_erase_proc.append(button_test)               // adding the button for erasing
    $('#list_proc').append($('<div/>').css({'text-align':'center'}).append(form_erase_proc))              // adding form to list_proc
    list_erase = []                                      // list of dataset to erase
    $("#erase_proc").click(function(){                   // Click erase button
         // curr_scroll = $('.list_proc').scrollTop()
         $('.chckgrp').each(function(){
            if ($(this).is(':checked')) {
              list_erase.push($(this).attr('id').slice(4))             // Retrieving checked element and putting in a list
            }
         }) // end each chckgrp
         infos_erase .attr('value', JSON.stringify(list_erase)).hide() // Using json for transmitting
         form_erase_proc.append(infos_erase)      
         $('#alert_erase').toggle()                   // asking confirmaton for erasing
         $("#erase_OK").click(function(){             // erasing when clicking OK
                  form_erase_proc.submit()            // sending the infos for erasing the datasets.
            })
         $("#erase_cancel").click(function(){             // Close erase confirmation window
                 $('#alert_erase').hide()
            })
        // $('.list_proc').scrollTop(curr_scroll)

    })

    chckbox_grp = $('<input/>').attr('name', 'checkgrp')
                                 .attr('id', 'chckgrp')
                                 .attr('checked','true')
                                 .attr('type', "checkbox").css({'left':'100px', 'top':'-10px'}) 

    //------------- end erasing

    /*
    Select the processing folder
    */

    $('.name_proc').click(function(){             // click on a processed dataset in panel list_proc
            
            var curr_scroll = $('.list_proc').scrollTop()
            proc_folder = $(this).attr('id')          // Retrieving the name of the folder to be analyzed.
            $('.name_proc').css({'color': 'black'})
            //-----
            $('body').empty()               // cleaning the page when changing of processing folder.
            navbar()                        // rebuild the navbar
            list_processings(ol)              // rebuild the processing list
            //-----
            visualize(proc_folder)          // launch all the other parts of the interface
            $('#' + proc_folder).css({'color': 'green'}) // color the folder in green
            $('.show_list_proc').text($('#' + proc_folder).text())
                                .css({'font-weight': 'bold'})  //, 'font-style': 'italic'})
            $('.list_proc').scrollTop(curr_scroll)
        }) // end click .name_proc
    

    //------------- Change the name of the processing folder

    var infos_newname =  $('<input/>')
                        .attr('type', 'input')
                        .attr('id', "infos_newname")
                        .attr('name', "infos_newname") // name used for server detection
                        .attr('value', 'sending_newname')
                        .hide()
    //------- OK

    var button_newname_OK= $('<input/>')  
                        .attr('type', 'button').addClass('btn btn-default')
                        .attr('value','OK')
                        .attr('id', "newname_OK")
    //------- cancel

    var button_newname_cancel= $('<input/>')  
                    .attr('type', 'button').addClass('btn btn-default')
                    .attr('value','Cancel')
                    .attr('id', "newname_cancel")
    
    //------- input for the dataset name

    var input_newname = $('<input/>').attr('type', 'input')               // name for processing datasets
                            .attr('id', 'input_newname')
                            .attr('name', 'input_newname')
                            .css({'width': '300', 'height': '30', 'margin-left': '5px'})
    
    //-------    Alert panel ".newname"

    var alert_newname = $('<div/>').addClass('newname').hide()
    alert_newname.append($('<br/>'))
                 .append(input_newname)
                 .append(button_newname_OK)
                 .append(button_newname_cancel)
    
    //-------   Making the Form for new name

    var form_newname_proc = $('<form/>').attr('id', 'form_newname_proc')  //  Form for changing the dataset name
                                  .attr('action', '/visu')
                                  .attr('method', 'post')
    var button_newname_proc = $('<input/>').css({'margin-left':'50px', 'background-color': '#33cc33' })  // #e6e600  #00b300 
                            .attr('type', 'button').addClass('btn btn-default')
                            .attr('value','change name proc')
                            .attr('id', "newname")
    form_newname_proc.append(button_newname_proc)
                     .append(infos_newname)
                     .append(alert_newname)
    //-------

    $('#list_proc').append(form_newname_proc)                  // adding form to list_proc
    
    //---------- Click OK and Cancel

    $('#newname').click(function(){                            // asking a new  name
          $('.newname').toggle()
          $('#input_newname').attr('value', proc_folder)       // insert name of current dataset in the input field.
          $("#newname_OK").click(function(){                   // sending the new name when clicking OK
                   form_newname_proc.submit()                  // sending the infos for the new name
              }) // end click
          $("#newname_cancel").click(function(){               // sending the new name when clicking OK
                   $('.newname').hide()
              }) // end click
    }) // end click newname

    // ------------------------- Gels

    /*
    Gels
    */

    var left_value = function(elem){
      return parseInt(elem.css('left').slice(0,-2))+10+'px'
     }
    var top_value = function(elem){
      return parseInt(elem.css('top').slice(0,-2))+50+'px'
     }
    var place_txt = function(elem){
         var left_tt = left_value(elem)
         var top_tt = top_value(elem)
         $('#textgel').css({'top': top_tt, 'left': left_tt })
     }
                    
    var title_gel = $('<h6/>').text('A1  A2  A3  A4').addClass('title_gel_text')
    var txt_gel = $('<div/>').html($('<h1/>').html(title_gel))
                              .addClass('title_gel')
                              .attr('id','textgel')
                              // .draggable()
  

    var wb =  $('<div/>').addClass('gel')
                           .attr('id', 'divgel')
                           .draggable( {

                            drag: function(){
                              place_txt($(this))
                             
                            }
                          }
                        )
      txt_gel.click(function(){
          $('#divgel').toggle()
      })

    $('body').append(wb)
    $('body').append(txt_gel)


} // end list_processings