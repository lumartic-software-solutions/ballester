from odoo import api, fields, models, _
import dateutil.parser
# coding=utf-8


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    carrier_invoice_id = fields.Many2one('res.partner', domain=[
                                 ('type', '=', 'center'),
                                 ('center_type', '=', 'carrier')], string="Transportista" ,related='collection_id.carrier_id')
    driver_id = fields.Many2one('res.partner', domain=[
        ('type', '=', 'contact')], string="Driver", related='collection_id.driver_id')

