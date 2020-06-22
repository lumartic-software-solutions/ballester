from odoo import api, models, _
from odoo.exceptions import UserError


#  merge invoice wizard methods
class PurchaseMerge(models.TransientModel):
    _name = "purchase.merge"
    
    
    #  create merge invoices
    @api.multi
    def create_invoices(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        invoice_id = purchase_orders.action_invoice_create()
        if self._context.get('open_invoices', False):
            action = self.env.ref('account.action_invoice_tree2').read()[0]
            # action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            # action['res_id'] = invoice_id
            action['domain'] = [('id', 'in', invoice_id)]
            return action
        return {'type': 'ir.actions.act_window_close'}
    

    #  conditions for merge invoice  
    @api.model
    def _dirty_check(self):
        if self._context.get('active_model', '') == 'purchase.order':
            ids = self._context.get('active_ids', [])
            if len(ids) == 1:
                order = self.env['purchase.order'].browse(ids)
                if order['invoice_status'] != ['to invoice','no']:
                    raise UserError(_('Billing status is not match with  Waiting Bills'))
            if len(ids) > 1:
                order = self.env['purchase.order'].browse(ids)
                for d in  order:
                    if d['invoice_status'] not in ['to invoice','no']:
                        raise UserError(_('Billing status is not match with  Waiting Bills'))
                    if d['company_id'] != order[0]['company_id']:
                        raise UserError(_('companies are not same.'))
                    # if d['partner_id'] != order[0]['partner_id']:
                    #     raise UserError(_('vendors are not same.'))
            return {}
     
    #  get fields or values for merge invoice  
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(PurchaseMerge, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=False)
        self._dirty_check()
        return res

