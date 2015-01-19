$(document).ready(function () {
$('.type_selection').each(function () {
    var type_selection = this;
    console.log( "ready!" );
    $(type_selection).on('click', '.type_selection', function ()
    {
    	console.log("type id " + this.value + " now access the complete model");
    	console.log( "postdebug" );
    	openerp.jsonRpc('/chd_init/getch/', 'call',
    		 {
             'type_id': this.value,
    		  }).then(function (data) {
    			  			console.log(data)
    			  			var  dd_list=document.getElementById("type_select_id");
    			  			document.getElementById("out_msg").innerHTML=  dd_list.options[dd_list.selectedIndex].text+".";
    		  })



    });
});
});



