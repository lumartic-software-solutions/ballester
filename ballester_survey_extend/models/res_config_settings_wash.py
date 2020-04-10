# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    container_compliance_id = fields.Many2one('survey.survey', 'Wash Container Compliance')
    drum_compliance_id = fields.Many2one('survey.survey', 'Wash Drum Compliance')
    crush_compliance_id = fields.Many2one('survey.survey', 'Crush Compliance')
    compact_compliance_id = fields.Many2one('survey.survey', 'Compact Compliance')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cp_obj = self.env['ir.config_parameter']
        container_compliance_id  = literal_eval(cp_obj.get_param('container_compliance_id', default='False'))
        drum_compliance_id  = literal_eval(cp_obj.get_param('drum_compliance_id', default='False'))
        crush_compliance_id  = literal_eval(cp_obj.get_param('crush_compliance_id', default='False'))
        compact_compliance_id  = literal_eval(cp_obj.get_param('compact_compliance_id', default='False'))
        res.update(
            container_compliance_id=container_compliance_id,
            drum_compliance_id=drum_compliance_id,
	     crush_compliance_id=crush_compliance_id,
             compact_compliance_id=compact_compliance_id
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('container_compliance_id', self.container_compliance_id.id )
        cp_obj.sudo().set_param('drum_compliance_id', self.drum_compliance_id.id )
        cp_obj.sudo().set_param('crush_compliance_id', self.crush_compliance_id.id)
        cp_obj.sudo().set_param('compact_compliance_id', self.compact_compliance_id.id)
        
