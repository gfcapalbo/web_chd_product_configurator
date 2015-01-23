# -*- coding: utf-8 -*-
from openerp import http
from openerp import api
from datetime import  datetime
from openerp.osv import fields,orm
import json



class product_template(orm.Model):
    _inherit = 'product.template'
    computed_floatdate = fields.float(compute='compute_total')

    @api.multi
    @api.depends('product_template.product_option_ids')
    def compute_total(self):
        return float(datetime.now())


class Chd_init(http.Controller):
    @http.route('/chd_init/',auth='public',website=True)


    def start(self,selected_id=False,type=False):
        Conf_products = http.request.env['product.template']
        accessories = http.request.env['product.product']
        chd_types = http.request.env['product.type']
        chd_finishing = http.request.env['product.finishing']
        # when posting a selected product to configure
        if http.request.httprequest.method == 'POST' and selected_id:
             curr_types = chd_types.search([('product_option_ids','in',[selected_id])])
             curr_product = Conf_products.search([('id','=',selected_id)])
             # accessories=old accessoire typo in product configurator.
             avail_accessories = accessories.search([('id','in',curr_product.chd_accessoire_ids.ids)])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': curr_product,
                 'curr_types' : curr_types,
                 'avail_accessories' : avail_accessories,
                 })
        # first iteration ,whe loading the page
        return http.request.render('website_chd_product_configurator.conf_start',{
            'conf_products': Conf_products.search([('chd_origin_product','=',True)]),
        })


    def onchange_type(self,cr,uid,ids,context=None):
        curr_finishings = chd_finishing.search([('type_option_ids','in',curr_types.ids)])
        return curr_finishings


    @http.route('/chd_init/<id>/',website=True)
    def call_configurator(self,**form_data):
         errormsg = ""
         Conf_products = http.request.env['product.template']
         chd_results = http.request.env['chd.product_configurator.result']
         all_accessories = []
         chd_dict = {
             'origin_product_id':form_data['product_id'],
             'partner_id':1,
             'state':'config',
             'quantity': form_data['quantity']
             }
         # dynamic and fixed size types
         if form_data['product_id_chd_size_type'] == "fixed":
            chd_dict['size_id'] = form_data['size']
            chd_size = http.request.env['chd.size'].search([('id','=',form_data['size'])])
            chd_dict['width'] = chd_size.width
            chd_dict['height'] = chd_size.height
         else:
            chd_dict['width'] = form_data['width']
            chd_dict['height'] = form_data['height']

         new_chd = http.request.env['chd.product_configurator'].create(chd_dict)
         for key in form_data:
             # get only accessories that have been checked, in future website validation will render this unnecessary.
             if  ('accessoryid_' in key) and form_data[key] == 'on':
                  # extrapolate the id encoded the name
                  accessory_id = int(key.split('_')[1])
                  # get the associated value by choosing the field with the right name
                  # accessoryid_{id}=on/off   and the associate quantity would be qtyaccessoryid_{id}=9898
                  accessory_qty = form_data['qtyaccessoryid_' + str(accessory_id)]
                  if accessory_qty == 0:
                    alert_msg += "An accessory has been selected with quantity 0, please specify quantity"
                  new_accessory = http.request.env['chd.accessoire_line'].create({
                     'product_id':accessory_id,
                     'configurator_id':new_chd.id,
                     'quantity':accessory_qty,
                     })
                  all_accessories.append(new_accessory)
         # _model refers to old API model, self.pool is not available in controller context (praise the lord for Holger!)

         try:
             new_chd._model.calculate_price(http.request.cr,http.request.uid,[new_chd.id],context=http.request.context)
         except:
             errormsg = "No result found for the values that you entered. We would be happy to give you a custom quote. Please call 010-7856766"
         results = chd_results.search([('configurator_id','=',new_chd.id)])
         if errormsg != "":
             chd_types = http.request.env['product.type']
             Conf_products = http.request.env['product.template']
             accessories = http.request.env['product.product']
             curr_types = chd_types.search([('product_option_ids','in',[form_data['product_id']])])
             curr_product = Conf_products.search([('id','=',form_data['product_id'])])
             avail_accessories = accessories.search([('id','in',curr_product.chd_accessoire_ids.ids)])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': curr_product,
                 'curr_types' : curr_types,
                 'avail_accessories' : avail_accessories,
                 'errormsg': errormsg,
                 })

         import cgi,os
         import cgitb; cgitb.enable()

         try:  # Windows needs stdio set for binary mode.
             import msvcrt
             msvcrt.setmode (0,os.O_BINARY)  # stdin  = 0
             msvcrt.setmode (1,os.O_BINARY)  # stdout = 1
         except ImportError:
             pass

         form = cgi.FieldStorage()

         # A nested FieldStorage instance holds the file
         fileitem = form_data['pic']

         # Test if the file was uploaded
         if fileitem.filename:

            # strip leading path from file name to avoid directory traversal attacks
            fn = os.path.basename(fileitem.filename)
            # open('files/' + fn,'wb').write(fileitem.stream.read())
            open(fileitem.filename,'wb').write(fileitem.stream.read())
            message = 'The file "' + fn + '" was uploaded successfully'

         else:
            message = 'No file was uploaded'

         print """\
         Content-Type: text/html\n
         <html><body>
         <p>%s</p>
         </body></html>
         """ % (message,)
         return http.request.render('website_chd_product_configurator.configuration_options',{
             'curr_product_id': Conf_products.search([('id','=',form_data['id'])]),
             'curr_chd': new_chd,
             'all_accessories':all_accessories,
             'results':results,
             'allstuff':str(form_data),
             'message':message,
             })


    @http.route('/chd_init/getch/',type='json',website=True)
    def tr(self,type_id):
        curr_types = http.request.env['product.finishing'].search([('type_option_ids','in',[type_id])])
        data = json.dumps(http.request.registry['product.finishing'].search_read(
            http.request.cr,
            http.request.uid,
            fields=['id','name'],
            limit=30,
            domain=[('type_option_ids','in',[int(type_id)])],
            context=http.request.context
            ))
        return data



