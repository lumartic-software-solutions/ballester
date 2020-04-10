#  -*- coding: utf-8 -*-
#  Odoo, Open Source Ballester Web Lead.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). 
from odoo import http
from odoo.http import request
from odoo.addons.website_crm.controllers.main import WebsiteForm


class ContactDetails(http.Controller):
    
    #contactus main page to set state
    @http.route('/contactus', type='http', auth='public', website=True)
    def contactus(self):
        values={}
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'states': states,
        })
        return http.request.render('website.contactus', values)



class WebsiteForm(WebsiteForm):

    # set the value in request
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        partner_obj = request.env['res.partner']
        if model_name == 'crm.lead':
            sequence = request.env['ir.sequence'].next_by_code('crm.lead') or _('New')
            if not request.params.get('name') :
                request.params['name'] = sequence
            if request.params.get('request_type') :
                request.params['request_type'] = request.params.get('request_type') 
            if request.params.get('first_name') or request.params.get('last_name') :
                name = ''
                if request.params.get('first_name') :
                    name = request.params.get('first_name') 
                if request.params.get('last_name') :
                    name += ' ' + request.params.get('last_name')    
                request.params['partner_name'] = name
            if request.params.get('customer_name'): 
                partner_id = partner_obj.search([('name','=',request.params.get('customer_name'))])
                if not partner_id :
                    create_partner_id = partner_obj.create({'name' : request.params.get('customer_name'),
                                                    'street' :request.params.get('street'),
                                                    'street2' :request.params.get('street2'),
                                                    'city' :request.params.get('city'),
                                                    'zip' :request.params.get('zip')})
                    request.params['partner_id'] = create_partner_id.id
                else:
                    request.params['partner_id'] = partner_id.id
                    request.params['street'] = partner_id.street
                    request.params['street2'] = partner_id.street2
                    request.params['city'] = partner_id.city
                    request.params['zip'] = partner_id.zip
        return super(WebsiteForm, self).website_form(model_name, **kwargs)
