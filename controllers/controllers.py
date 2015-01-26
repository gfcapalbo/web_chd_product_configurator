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
        chd_price_components_at = http.request.env['price.component.attribute.template']
        chd_types = http.request.env['product.type']
        chd_finishing = http.request.env['product.finishing']
        # when posting a selected product to configure
        if http.request.httprequest.method == 'POST' and selected_id:
             curr_types = chd_types.search([('product_option_ids','in',[selected_id])])
             curr_product = Conf_products.search([('id','=',selected_id)])
             curr_chd_price_component_ats = chd_price_components_at.search(
                 [('id','in',curr_product.attribute_template_ids.ids),
                     ('active','=',True)
                     ])
             avail_accessories = accessories.search([('id','in',curr_product.chd_accessoire_ids.ids)])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': curr_product,
                 'curr_types' : curr_types,
                 'curr_chd_price_component_ats': curr_chd_price_component_ats,
                 'avail_accessories' : avail_accessories,
                 })
        # first iteration, loading the page
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
         curr_product_id = Conf_products.search([('id','=',form_data['id'])])
         chd_price_components_at = http.request.env['price.component.attribute.template']

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



         # if there aren't any errors, upload the image
         message = ''
         if Conf_products.search([('id','=',form_data['product_id'])])[0].chd_configurator_has_image:

             import werkzeug
             import base64
             try:
                 fileitem = form_data['pic']
                 # add uploaded image to configurator
                 chd_dict['image'] = base64.b64encode(fileitem.stream.read())
                 chd_dict['image_filename'] = fileitem.filename
                 message = 'image uploaded successfully'
             except:
                 message = 'there where problems uploading your image, contact us'
         if message == '': message = 'no image needed for this product'




         new_chd = http.request.env['chd.product_configurator'].create(chd_dict)
         # add accessories and price components selections to the configurator
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
             elif ('pricecomponent_' in key) :
                 # if it is of type "string" the value is the index of the selection in pricecomponent_name, the id is encoded in the key
                 if 'pricecomponent_string' in key:
                     pricecomponent_id = int(key.split('_')[3])

                 # if it is of type numerical the value is the actual value of the pricecomponent_name, the id is encoded in the key
                 if 'pricecomponent_int' in key:
                     pricecomponent_id = int(key.split('_')[3])







         # our product configurator is ready, we can now calculate options
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
             avail_accessories = accessories.search([('id','in',curr_product_id.chd_accessoire_ids.ids)])
             curr_chd_price_component_ats = chd_price_components_at.search(
                 [('id','in',curr_product_id.attribute_template_ids.ids),
                     ('active','=',True)
                     ])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': curr_product_id,
                 'curr_types' : curr_types,
                 'avail_accessories' : avail_accessories,
                 'curr_chd_price_component_ats': curr_chd_price_component_ats,
                 'errormsg': errormsg,
                 })

         return http.request.render('website_chd_product_configurator.sale_options',{
             'curr_product_id': curr_product_id,
             'curr_chd': new_chd,
             'all_accessories':all_accessories,
             'results':results,
             'configuration_form':str(form_data),
             'message':message,
             })



    @http.route('/chd_init/buy<id>/',website=True)
    def chosen_option(self,**form_data):
        result = http.request.env['chd.product_configurator.result'].search([('id','=',form_data['id'])])
        configurator = http.request.env['chd.product_configurator'].search([('id','=',result.configurator_id.id)])
        http.request.context['active_id'] = result.id
        fields = ['order_id','return_to_order','display_order_id','result_id']
        doorder_model = http.request.env['chd.product_configurator.do_order']
        # again, access 7.0 with ._model property
        a = doorder_model._model.default_get(http.request.cr,http.request.uid,fields_list=fields,context=http.request.context)

        """vals = {
            'result_id': form_data['id'],
            'order_id': get_last_open_salesorder(1),
            'return_to_order': False ,
            }
        order = http.request.env['chd.product_configurator.do_order'].create(vals)"""
        return http.request.render('website_chd_product_configurator.buy_option',{
                'allstuff':str(form_data),
                })


    # method for fetching finishing options via json
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












