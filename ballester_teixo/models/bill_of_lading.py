from odoo import api, fields, models, _


class BillOfLading(models.Model):
    _inherit = "bill.lading"

    driver_id = fields.Many2one('res.partner', domain=[
        ('type', '=', 'contact')], string="Driver")
    vehicle_id = fields.Many2one('fleet.vehicle', sting="Vehicle")

    @api.model
    def default_get(self, default_fields):
        res = super(BillOfLading, self).default_get(default_fields)
        ctx = dict(self._context)
        if ctx.get('active_model') == 'sale.order':
            sale = self.env['sale.order'].browse(ctx.get('active_id'))

            res.update(
                {'carrier_id': sale.carrier_sale_id and sale.carrier_sale_id.id or False,
                 'driver_id': sale.driver_id and sale.driver_id.id or False,
                 'vehicle_id': sale.transportation_name and sale.transportation_name.id or False})
        elif ctx.get('active_model') == 'purchase.order':
            purchase = self.env['purchase.order'].browse(ctx.get('active_id'))

            res.update(
                {'carrier_id': purchase.carrier_sale_id and purchase.carrier_sale_id.id or False,
                 'driver_id': purchase.driver_id and purchase.driver_id.id or False,
                 'vehicle_id': purchase.transportation_name and purchase.transportation_name.id or False})

        else:
            collection = self.env['collection.order'].browse(ctx.get('active_id'))
            res.update(
                {'carrier_id': collection.carrier_id and collection.carrier_id.id or False,
                 'driver_id': collection.driver_id and collection.driver_id.id or False,
                 'vehicle_id': collection.vehicle_id and collection.vehicle_id.id or False})
        return res
