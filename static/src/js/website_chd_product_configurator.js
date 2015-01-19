$(document).ready(function () {
$('.product_selection').each(function () {
    var product_selection = this;
    console.log( "ready!" );
    $(product_selection).on('click', '.product_selection', function ()
    {
    	console.log("product id " + this.value + " now access the complete model");
    	console.log( "postdebug" );
    	openerp.jsonRpc('/chd_init/getch/', 'call',
    		 {
             'id': this.value,
    		  }).then(function (data) {
    			  			console.log(data)
    			  			var  mylist=document.getElementById("prod_sel");
    			  			document.getElementById("out_msg").innerHTML=  mylist.options[mylist.selectedIndex].text+".";
    		  })



    });
});
});



