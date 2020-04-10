# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    repair_compliance_id = fields.Many2one('survey.survey', 'Repair Compliance')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cp_obj = self.env['ir.config_parameter']
        repair_compliance_id  = literal_eval(cp_obj.get_param('repair_compliance_id', default='False'))
        res.update(
            repair_compliance_id=repair_compliance_id,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('repair_compliance_id', self.repair_compliance_id.id )
        
