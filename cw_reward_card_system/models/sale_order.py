from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    cw_spend_points = fields.Boolean(string='Spend Points')
    cw_reward_card_id = fields.Many2one('cw.reward.card', string='Reward Card')
    cw_card_total_points = fields.Integer(string='Card Total Points', related='cw_reward_card_id.total_points', readonly=True)
    points_deducted = fields.Boolean(string='Points Deducted', default=False)  # Field to track if points have been deducted
    
    @api.onchange('cw_spend_points')
    def _onchange_spend_points(self):
        if self.cw_spend_points:
            self.order_line = [(5, 0, 0)]  # Remove all lines
            
    @api.onchange('order_line')
    def _onchange_order_line(self):
        if self.cw_spend_points and self.cw_reward_card_id:
            total_points_needed = sum(line.product_id.cw_points_cost * line.product_uom_qty for line in self.order_line)
            if total_points_needed > self.cw_reward_card_id.total_points:
                raise ValidationError('Not enough points on the reward card.')
            for line in self.order_line:
                line.price_unit = 1
                line.name = '{} ({} points)'.format(line.product_id.name, line.product_id.cw_points_cost * line.product_uom_qty) 
                
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        _logger.info('GOING through action_confirm')
        _logger.info('GOING through action_confirm 002')
        if self.cw_spend_points and self.cw_reward_card_id and not self.points_deducted:
            reward_card = self.cw_reward_card_id
            total_points_needed = 0
            
            # Loop through each order line to calculate points for each product
            for line in self.order_line:
                product = line.product_id
                qty = line.product_uom_qty
                points_for_line = product.cw_points_cost * qty  # Calculate points for this line
                
                total_points_needed += points_for_line  # Accumulate total points

                # Create reward points history for each line
                self.env['cw.reward.points.history'].create({
                    'reward_card_id': reward_card.id,
                    'sale_order_id': self.id,  # Link to the current sale order
                    'product_id': product.id,  # Track the product
                    'qty': qty,
                    'points': -points_for_line,  # Deduct points for this product line
                    'type': 'redeem',  # Type is redeem for deductions
                })
            
            
            new_total_point = self.cw_reward_card_id.total_points - total_points_needed
            self.cw_reward_card_id.total_points = new_total_point
            reward_card.write({
                'total_points': new_total_point
            })
            
            self.points_deducted = True  # Mark points as deducted
            self.write({
                    'points_deducted': True
                })
        return res