$(document).ready(function () {

	$('.type_selection').each(function () {
	    var type_selection = this;
	    $(type_selection).on('click', '.type_selection', function ()
	    {
	    	console.log("type id " + this.value + " now access the complete model");
	    	console.log( "postdebug" );
	    	openerp.jsonRpc('/chd_init/getch/', 'call',
	    		 {
	             'type_id': this.value,
	    		  }).then(function (data) {
	    			  			var  dd_list=document.getElementById("type_select_id");
			  					document.getElementById("out_msg").innerHTML=  dd_list.options[dd_list.selectedIndex].text+".";
	    			  			console.log(data);
	    			  			var data_js = eval(data);
	    			  			$('#fini_select_id').empty();
	    			  			for (var key in data_js)
	    			  			{
	    			  			    if (data_js.hasOwnProperty(key))
	    			  			    {
	    			  			        $('#fini_select_id').append("<option value='" +data_js[key].id+ "'>"+ data_js[key].name+ "</option>");
	    			  			    }
	    			  			}

	    		  })
	    });
	});
	$("#mainf").submit( function()
		        {
		 			$('<input />').attr('type', 'hidden')
			         .attr('name', "post-addition")
			         .attr('value', "addition")
			         .appendTo('#mainf');
    	             return true;
		        });
});




