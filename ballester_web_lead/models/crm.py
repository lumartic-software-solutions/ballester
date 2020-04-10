#  -*- coding: utf-8 -*-
#  Odoo, Open Source Ballester Web Lead.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo import fields, models,api,_


class Lead(models.Model):
    _inherit = 'crm.lead'
    
    transfer_date = fields.Date('Transfer Date')
    request_type = fields.Selection([('sale','Venta'),('waste','Limpieza'),('purchase','Retirada')], 'Solicitud',default="sale")
    
    # set value from wesite form
    def website_form_input_filter(self, request, values):
        values.update({
                        'street' :request.params.get('street'),
                        'street2' :request.params.get('street2'),
                        'city' :request.params.get('city'),
                        'state_id' :request.params.get('state_id'),
                        'zip' :request.params.get('zip') ,
                        'partner_id' :request.params.get('partner_id'),
                        'date_deadline' :request.params.get('date_deadline') ,
                        'transfer_date' : request.params.get('transfer_date') ,})
        return values
