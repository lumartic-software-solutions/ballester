# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sddr_compliance_id = fields.Many2one('survey.survey', 'SDDR Compliance')
    waste_compliance_id = fields.Many2one('survey.survey', 'Waste Compliance')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cp_obj = self.env['ir.config_parameter']
        sddr_compliance_id  = literal_eval(cp_obj.get_param('sddr_compliance_id', default='False'))
        waste_compliance_id  = literal_eval(cp_obj.get_param('waste_compliance_id', default='False'))
        res.update(
            sddr_compliance_id=sddr_compliance_id,
            waste_compliance_id=waste_compliance_id 
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('sddr_compliance_id', self.sddr_compliance_id.id )
        cp_obj.sudo().set_param('waste_compliance_id', self.waste_compliance_id.id)
