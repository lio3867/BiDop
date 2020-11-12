var navbar = function(){   // Navbar containing link to Home, Processing, Slack.com etc..

    $('body').html(function(){/*
    <nav class="navbar navbar-light bg-faded " >
       <ul class="nav navbar-nav">

       <!-- style="background-color: white; box-shadow: 0.5em 0.5em 0.7em" -->

       <!-- Go home -->

       <li class="nav-item active">
         <a class="nav-link  " href="../select_proc_visu">  
         <i class="fa fa-home fa-2x" aria-hidden="true"></i>
           <span>Home</span>
         </a>
       </li>

       <!-- Go to Processing -->

       <li class="nav-item">
         <a class="nav-link " href="../ask_param?choosefolder=1.+Processing">
         <i class="fa fa-gear fa-2x" aria-hidden="true"></i>
           <span>Processing</span>
         </a>
       </li>


       <!-- Go to Report -->

       <li class="nav-item">
         <a class="nav-link " href="../report">
         <i class="fa fa-file-text fa-2x" aria-hidden="true"></i>
           <span>Report</span>
         </a>
       </li>


       <!-- Go to Slack -->

       <li class="nav-item">
         <a target="_blank" class="nav-link slack"  style="top:10px; left:600px" href="https://holdupmsp.slack.com/messages/general/">
            <span >  &nbsp &nbsp &nbsp Slack</span>
         </a>
       </li>


       <!-- Tooltips -->

       <li class="nav-item">
         <a class="nav-link"  id='trig_ttip' style=" left:400px" >
         <i class="fa fa-comment fa-2x" aria-hidden="true"></i>
            <span id='text_tolltips'> Tooltips </span>
         </a>
       </li>



     </ul>
    </nav>
    
    */}.toString().slice(14,-3))
}