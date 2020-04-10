from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError


class GenerateWaybillWizard(models.TransientModel):
    _name = 'waybill.wizard'

    origin_id = fields.Many2one('res.partner', "Origin")
    effecitivec_id = fields.Many2one('res.partner', "Carrier Effective")
    desination_id = fields.Many2one('res.partner', "Destination")
    note = fields.Text('Observations')
    loading_date = fields.Date("Loading Date")
    download_date = fields.Date("Download Date")
    origin_tags = 

    def generate_waybill(self):
        return {'type': 'ir.actions.act_window_close'}


class WaybillTags(models.Model):
    _name = 'waybill.tags'

    name = fields.Char("name")
