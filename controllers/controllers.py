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
        if http.request.httprequest.method == 'POST' and selected_id:
             curr_types = chd_types.search([('product_option_ids','in',[selected_id])])
             curr_product = Conf_products.search([('id','=',selected_id)])
             # in the website module accessories will be written correctly, it's the same thing as the old accessoire typo.
             avail_accessories = accessories.search([('id','in',curr_product.chd_accessoire_ids.ids)])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': curr_product,
                 'curr_types' : curr_types,
                 'avail_accessories' : avail_accessories,
                 })
        return http.request.render('website_chd_product_configurator.conf_start',{
            'conf_products': Conf_products.search([('chd_origin_product','=',True)]),
        })


    def onchange_type(self,cr,uid,ids,context=None):
        curr_finishings = chd_finishing.search([('type_option_ids','in',curr_types.ids)])
        return curr_finishings


    @http.route('/chd_init/<id>/',website=True)
    def call_configurator(self,**form_data):
         Conf_products = http.request.env['product.template']
         all_accessories = []
         new_chd = http.request.env['chd.product_configurator'].create({
             'origin_product_id':form_data['product_id'],
             'partner_id':1,
             'state':'init',
             'width': form_data['width'],

         })
         for key in form_data:
             # get only accessories that have been checked, in future website validation will render this unnecessary.
             if  ('accessoryid_' in key) and form_data[key] == 'on':
                  # extrapolate the id encoded the name
                  accessory_id = int(key.split('_')[1])
                  # get the associated value by choosing the field with the right name
                  # accessoryid_{id}=on/off   and the associate quantity would be qtyaccessoryid_{id}=9898
                  accessory_qty = form_data['qtyaccessoryid_' + accessory_id]
                  new_accessory = http.request.env['chd.product_configurator'].create({
                     'product_id':accessory_id,
                     'configurator_id':new_chd.id,
                     'quantity':accessory_qty,
                     })
                  all_accessories.append(new_accessory)
         return http.request.render('website_chd_product_configurator.configuration_options',{
             'outputstuff': str(form_data),
             'curr_product_id': Conf_products.search([('id','=',form_data['id'])]),
             'curr_chd': new_chd,
             'all_accessories':all_accessories,
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



