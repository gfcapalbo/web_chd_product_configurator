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

	$(':input').each(function() {
			var element=this;
			console.log(element);
			$(element).on('change', function()
					{

						if (document.getElementById("div_" + element.name)) {
							var currdiv = (document.getElementById("div_" + element.name));
							currdiv.innerHTML = "";
						} else {
							var currdiv = document.createElement("div");
							currdiv.id ="div_" + element.name;
							currdiv.setAttribute('class', 'quotation');
						}
						var value = element.value;
						if (value=='on'){
							value= 'selected';
						}

						var rawname = element.name;
						var name = rawname.split("_");
						console.log(name);
						if ((name.length > 2) && ((name[0] == 'qtyaccessoryid') || (name[0] == 'accessoryid')))  {
							var newcontent = document.createTextNode(name[2] +" : " + value);
						}
						if ((name.length > 2) && (name[0] == 'pricecomponent'))  {
							var newcontent = document.createTextNode(name[3] +" : " + value);
						} else {
							var newcontent = document.createTextNode(rawname +" : " + value);
						}
						currdiv.appendChild(newcontent);
						if (name[0] == 'qtyaccessoryid') {
							var feedback_container= document.getElementById("accessory_preferences");
						} else {
							var feedback_container= document.getElementById("preferences");
						}
						feedback_container.appendChild(currdiv);
					});
			});




	//added after on submit , with the rest of the form fields.
	$("#mainf").submit( function()
		        {
		 			$('<input />').attr('type', 'hidden')
			         .attr('name', "feedback")
			         .attr('value', document.getElementById("feedback").innerHTML)
			         .appendTo('#mainf');
    	             return true;
		        });
});




