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

    def to_JSON(self):
        return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True,indent=4)

    @http.route('/chd_init/get_options',type='http',auth="public",methods=['GET'],website=True)
    def tr(self,id):
        curr_types = http.request.env['product.type'].search([('product_option_ids','in',[id])])
        data = http.request.registry['product.type'].search_read(
            http.request.cr,
            http.request.uid,
            fields=['id','name'],
            limit=30,
            domain=[('product_option_ids','in',[int(id)])],
            context=http.request.context
            )
        return json.dumps(data)

    """form = PostsNewForm(request.httprequest.form)
    if request.httprequest.method == 'POST' and form.validate():
        posts = request.env['blog.post']
        posts.create({
            'title': form_data.get('title', ''),
            'content': form_data.get('content', ''),
        })
        return redirect("/posts/")
    return request.render('odoo_blog.posts_new', {'form': form})"""
