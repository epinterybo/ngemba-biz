from odoo import models, fields

class RewardPointsHistory(models.Model):
    _name = 'cw.reward.points.history'
    _description = 'CW Reward Points History'

    reward_card_id = fields.Many2one('cw.reward.card', string='Reward Card', required=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', required=False)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=False)  
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Integer(string='Quantity', default=0)
    points = fields.Integer(string='Points')
    type = fields.Selection([('gain', 'Gain'), ('redeem', 'Redeem'), ('reverse', 'Reverse')], string='Type', required=True)
    has_been_reversed = fields.Boolean(string='Has been reversed', default=False)
    qty_reversed = fields.Integer(string='Qty reversed', default=0)
    fully_reversed = fields.Boolean(string='Fully Reversed', default=False)
