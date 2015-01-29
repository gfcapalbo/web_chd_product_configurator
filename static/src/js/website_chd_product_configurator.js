$(document).ready(function () {

	$('.type_selection').each(function () {
	    var type_selection = this;
	    $(type_selection).on('click', '.type_selection', function ()
	    {
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
			$(element).on('change', function(){
				$(':input').each(function() {
						if (document.getElementById("error_msg")){
							document.getElementById("error_msg").innerHTML="";
						}
						var rawname = element.name;
						var name = rawname.split("_");
						if (document.getElementById("div_" + rawname)) {
							var currdiv = (document.getElementById("div_" + rawname));
							currdiv.innerHTML = "";
						} else {
							var currdiv = document.createElement("div");
							currdiv.id = "div_" + rawname;
							currdiv.setAttribute('class', 'quotation');
						}
						var value = element.value;
						if (element.nodeName=="SELECT") {
								value=element[element.selectedIndex].label;
						}
						if (name.length > 2){
							if (name[0] == 'qtyaccessoryid') {
								if (value > 0){
									var newcontent = document.createTextNode(name[2] +" : " + value);
								}
							}else if (name[0] == 'pricecomponent') {
								var newcontent = document.createTextNode(name[4] +" : " + value);}
						} else {
							var newcontent = document.createTextNode(rawname +" : " + value);
							}
						if (newcontent){
							currdiv.appendChild(newcontent);
							if (name[0] == 'qtyaccessoryid') {
								var feedback_container= document.getElementById("accessory_preferences");

							}else
							{
								var feedback_container= document.getElementById("preferences");
							}
							feedback_container.appendChild(currdiv);
						}

					});
				});
			});


	//added after on submit , with the rest of the form fields.
	$("#mainf").submit( function()
		        {
		 			var elements = document.querySelectorAll( 'feedback *' );
		 			$('<input />').attr('type', 'hidden')
			         .attr('name', "summary")
			         .attr('value', document.getElementById("feedback").innerHTML)
			         .appendTo('#mainf');
    	             return true;
		        });

	$('.result_option').submit( function(){
				chosenform=this;
				debugger;
	 			var elements = document.querySelectorAll( 'feedback *' );
	 			$('<input />').attr('type', 'hidden')
		         .attr('name', "summary")
		         .attr('value', document.getElementById("feedback").innerHTML)
		         .appendTo(chosenform);
	             return true;
	        });
});




