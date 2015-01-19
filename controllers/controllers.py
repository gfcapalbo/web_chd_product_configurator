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
        chd_types = http.request.env['product.type']
        chd_finishing = http.request.env['product.finishing']
        if http.request.httprequest.method == 'POST' and selected_id:
             curr_types = chd_types.search([('product_option_ids','in',[selected_id])])
             curr_finishings = chd_finishing.search([('type_option_ids','in',curr_types.ids)])
             return http.request.render('website_chd_product_configurator.configurator',{
                 'curr_product_id': Conf_products.search([('id','=',selected_id)]),
                 'curr_types' : curr_types,
                 'curr_finishings': curr_finishings,
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
         return http.request.render('website_chd_product_configurator.configuration_options',{
             'curr_product_id': Conf_products.search([('id','=',form_data['id'])])
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



