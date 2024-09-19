from odoo import models, fields, api
from datetime import datetime

class WarrantyProduct(models.Model):
    _name = 'ybo.warranty.product'
    _description = 'Warranty Product Information'

    name = fields.Char(string='Warranty Reference', required=False, copy=False, readonly=True, default='New')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    start_date = fields.Date(string='Warranty Start Date', required=True)
    end_date = fields.Date(string='Warranty End Date', required=True)
    duration = fields.Integer(string='Warranty Duration(months)', required=True, default=0)
    quantity_delivered = fields.Float(string='Quantity Delivered', required=True, default=0)
    remaining_duration = fields.Integer(string='Remaining Warranty (days)', compute='_compute_remaining_duration')
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ], string='Status', compute='_compute_state', store=True)

    @api.depends('end_date')
    def _compute_remaining_duration(self):
        today = fields.Date.today()
        for record in self:
            if record.end_date:
                if record.end_date > today:
                    delta = record.end_date - today
                    record.remaining_duration = delta.days
                else:
                    record.remaining_duration = 0

    @api.depends('end_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if record.end_date:
                record.state = 'active' if record.end_date >= today else 'expired'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('product.warranty') or 'New'
        return super(WarrantyProduct, self).create(vals)

    def update_remaining_duration(self):
        self._compute_remaining_duration()
        self._compute_state()
