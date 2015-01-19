$(document).ready(function () {
$('.product_selection').each(function () {
    var product_selection = this;
    console.log( "ready!" );
    $(product_selection).on('click', '.product_selection', function () {
    	console.log("product id " + this.value + " now access the complete model");
    	console.log( "postdebug" );
    	openerp.jsonRpc("/chd_init/get_options", 'call', {
             'id': this.value,
    		  })
                console.log("json data returned from openerp");
    			console.log(data);
    			console.log(data['value']);

    });
});
});
