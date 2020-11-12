function shadeColor2(color, ratio_col) {   // Color Shading (used first for visu of the Binding Indices)
    /*
    Return a color according to a basic color and a ratio
    */
    var f=parseInt(color.slice(1),16),t=ratio_col<0?0:255,p=ratio_col<0?ratio_col*-1:ratio_col,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
    return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
 
} // end shadeColor2

var BIcolor = function(ratio_col){
    /*
    Return a color according to the Binding Index
    */

    if (ratio_col<1){
        return shadeColor2('#ff0000', ratio_col)
    }
    else if ((ratio_col>1)&(ratio_col<2)){
        return shadeColor2('#0033ff', 2-ratio_col) //
    }
    else {
        return "#ffffff"
    }
} // end BIcolor

