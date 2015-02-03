# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.osv import orm
import json


class Chd_website(http.Controller):

    @http.route('/chd_init/', auth='public', website=True)
    def start(self, selected_id=False, type=False):
        partner = self.get_current_partner()
        if partner is False:
            return request.render(
                'website_chd_product_configurator.no_partner', {})
        Conf_products = request.env['product.template']
        accessories = request.env['product.product']
        chd_price_components_at = request.env[
            'price.component.attribute.template']
        chd_types = request.env['product.type']
        chd_finishing = request.env['product.finishing']
        # when posting a selected product to configure
        if request.httprequest.method == 'POST' and selected_id:
            curr_types = chd_types.search([
                ('product_option_ids', 'in', [selected_id])
                ])
            curr_product = Conf_products.search([('id', '=', selected_id)])
            curr_chd_price_component_ats = chd_price_components_at.search([
                ('id', 'in', curr_product.attribute_template_ids.ids),
                ('active', '=', True)
                ])
            avail_accessories = accessories.search([
                ('id', 'in', curr_product.chd_accessoire_ids.ids)
                ])
            return request.render(
                'website_chd_product_configurator.configurator',
                {
                    'curr_product_id': curr_product,
                    'curr_types': curr_types,
                    'curr_chd_price_component_ats':
                    curr_chd_price_component_ats,
                    'avail_accessories': avail_accessories,
                    })
        # first iteration, loading the page
        return request.render('website_chd_product_configurator.conf_start', {
            'conf_products': Conf_products.search([(
                'chd_origin_product', '=', True)
                ]),
            })

    # shows the options list
    @http.route('/chd_init/<id>/', website=True)
    def call_configurator(self, **form_data):
        errormsg = ""
        Conf_products = request.env['product.template']
        chd_results = request.env['chd.product_configurator.result']
        curr_product_id = Conf_products.search([('id', '=', form_data['id'])])
        chd_price_components_at = request.env[
            'price.component.attribute.template']
        all_accessories = []
        all_attributes = {}
        chd_dict = {
            'origin_product_id': curr_product_id.ids[0],
            'partner_id': self.get_current_partner().id,
            'state': 'config',
            'quantity': form_data['quantity']
            }
        # dynamic and fixed size types
        if form_data['product_id_chd_size_type'] == "fixed":
            chd_dict['size_id'] = form_data['size']
            chd_size = request.env['chd.size'].search([
                ('id', '=', form_data['size'])
                ])
            chd_dict['width'] = chd_size.width
            chd_dict['height'] = chd_size.height
        else:
            chd_dict['width'] = form_data['width']
            chd_dict['height'] = form_data['height']
        # if there aren't any errors, upload the image
        message = ''
        has_image = Conf_products.search([
            ('id', '=', form_data['product_id'])
            ])[0].chd_configurator_has_image
        if has_image:
            try:
                import base64
                fileitem = form_data['pic']
                # add uploaded image to configurator
                chd_dict['image'] = base64.b64encode(fileitem.stream.read())
                chd_dict['image_filename'] = fileitem.filename
                message = 'image uploaded successfully'
            except:
                message = 'Problems uploading your image, please contact us'
        if message == '':
            message = 'no image needed for this product'
        for key in form_data:
            if ('pricecomponent_' in key):
                # if it is of type "string" the value is the index of the
                # selection in pricecomponent_name, the id encoded in the key
                if 'pricecomponent_string' in key:
                    pricecomponent_id = int(key.split('_')[3])
                    pricecomponent_value = form_data[key]
                # if it is of type numerical the value is the actual value of
                # the pricecomponent field, the id is encoded in the key
                if 'pricecomponent_int' in key:
                    pricecomponent_id = int(key.split('_')[3])
                    pricecomponent_value = form_data[key]
                # the configurator stores the attributes in a
                # dictionary in the "attributes" field ,
                all_attributes[
                    '_attribute_' + str(pricecomponent_id)
                    ] = int(pricecomponent_value)

        # add attributes to the configurator
        chd_dict['attributes'] = str(all_attributes)
        # dictionary is complete, create configurator
        new_chd = request.env['chd.product_configurator'].create(chd_dict)
        # add accessories and price components selections to the configurator
        for key in form_data:
            # get only accessories that have been checked
            if ('accessoryid_' in key) and form_data[key] == 'on':
                # extrapolate the id encoded the name
                accessory_id = int(key.split('_')[1])
                # get the associated value by choosing the field with the
                # right name accessoryid_{id}=on/off and the associated
                # quantity would be qtyaccessoryid_{id}=9898
                accessory_qty = form_data['qty' + key]
                new_accessory = request.env['chd.accessoire_line'].create({
                    'product_id': accessory_id,
                    'configurator_id': new_chd.id,
                    'quantity': accessory_qty,
                    })
                all_accessories.append(new_accessory)
        # our product configurator is ready, we can now calculate options
        # _model refers to old API model, self.pool
        # is not available in controller context (praise the lord for Holger!)
        try:
            res = new_chd._model.calculate_price(
                request.cr, request.uid, [new_chd.id], context=request.context)
        except orm.except_orm:
            errormsg = "No result found for the values that you entered. \
            We would be happy to give you a custom quote. \
            Please call 010-7856766"
        results = chd_results.search([('configurator_id', '=', new_chd.id)])
        if errormsg != "" and len(results.ids) == 0:
            chd_types = request.env['product.type']
            Conf_products = request.env['product.template']
            accessories = request.env['product.product']
            curr_types = chd_types.search(
                [('product_option_ids', 'in', [int(form_data['product_id'])])])
            avail_accessories = accessories.search(
                [('id', 'in', curr_product_id.chd_accessoire_ids.ids)])
            curr_chd_price_component_ats = chd_price_components_at.search(
                [
                    ('id', 'in', curr_product_id.attribute_template_ids.ids),
                    ('active', '=', True)
                    ])
            return request.render(
                'website_chd_product_configurator.configurator', {
                    'curr_product_id': curr_product_id,
                    'curr_types': curr_types,
                    'avail_accessories': avail_accessories,
                    'curr_chd_price_component_ats':
                    curr_chd_price_component_ats,
                    'errormsg': errormsg,
                    })

        return request.render(
            'website_chd_product_configurator.sale_options',
            {
                'curr_product_id': curr_product_id,
                'curr_chd': new_chd,
                'all_accessories': all_accessories,
                'results': results,
                'configuration_form': str(form_data),
                'message': message,
                'summary': form_data['summary'],
                })

    def get_current_partner(self):
        partner_model = request.env['res.partner']
        current_partner = partner_model.search(
            [('user_account_id', '=', request.uid)])
        if len(current_partner) == 0:
            return False
        else:
            return current_partner[0]

    @http.route('/chd_init/buy<id>/', website=True)
    def chosen_option(self, **form_data):
        partner = self.get_current_partner()
        if partner is False:
            return request.render(
                'website_chd_product_configurator.no_partner', {})
        result_model = request.env['chd.product_configurator.result']
        result = result_model.search([('id', '=', form_data['id'])])
        configurator = request.env['chd.product_configurator'].search(
            [('id', '=', result.configurator_id.id)])
        request.context['active_id'] = result.id
        fields = [
            'order_id',
            'return_to_order',
            'display_order_id',
            'result_id']
        if form_data['action'] == 'buy':
            doorder_model = request.env['chd.product_configurator.do_order']
            # again, access 7.0 with ._model property
            doorder_res = doorder_model._model.default_get(
                request.cr, request.uid,
                fields_list=fields, context=request.context)
            order = request.env['sale.order'].search(
                [('id', '=', doorder_res['order_id'])])
            return request.render(
                'website_chd_product_configurator.buy_option', {
                    'summary': form_data['summary'],
                    'result': result,
                    'order': order,
                    })

    # method for fetching finishing options via json
    @http.route('/chd_init/getch/', type='json')
    def tr(self, type_id):
        curr_types = request.env['product.finishing'].search(
            [('type_option_ids', 'in', [type_id])])
        data = json.dumps(request.registry['product.finishing'].search_read(
            request.cr,
            request.uid,
            fields=['id', 'name'],
            limit=30,
            domain=[('type_option_ids', 'in', [int(type_id)])],
            context=request.context
            ))
        return data
