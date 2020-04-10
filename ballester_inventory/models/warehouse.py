# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Inventory.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api,_
from datetime import datetime
from odoo.tools.float_utils import float_compare


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    
    def _get_sequence_values(self):
        return {
            'in_type_id': {'name': self.name + ' ' + _('Sequence in'), 'prefix': self.code + 'IN'+ '%y(s)', 'padding': 5},
            'out_type_id': {'name': self.name + ' ' + _('Sequence out'), 'prefix': self.code + 'OUT'+ '%y(s)', 'padding': 5},
            'pack_type_id': {'name': self.name + ' ' + _('Sequence packing'), 'prefix': self.code + 'PACK'+ '%y(s)', 'padding': 5},
            'pick_type_id': {'name': self.name + ' ' + _('Sequence picking'), 'prefix': self.code + 'PICK'+ '%y(s)', 'padding': 5},
            'int_type_id': {'name': self.name + ' ' + _('Sequence internal'), 'prefix': self.code + 'INT'+ '%y(s)', 'padding': 5},
        } 