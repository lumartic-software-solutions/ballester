# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    complex_purchase_id = fields.Many2one('survey.survey', 'Complex Purchase')
    minor_purchase_id = fields.Many2one('survey.survey', 'Minor Purchase')
    sddr_compliance_id = fields.Many2one('survey.survey', 'SDDR Compliance')
    waste_compliance_id = fields.Many2one('survey.survey', 'Waste Compliance')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cp_obj = self.env['ir.config_parameter']
        complex_purchase_id = literal_eval(cp_obj.get_param('complex_purchase_id', default='False'))
        minor_purchase_id = literal_eval(cp_obj.get_param('minor_purchase_id', default='False'))
        res.update(
            complex_purchase_id=complex_purchase_id,
		minor_purchase_id=minor_purchase_id,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('complex_purchase_id', self.complex_purchase_id.id)
        cp_obj.sudo().set_param('minor_purchase_id', self.minor_purchase_id.id)
