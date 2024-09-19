from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    cw_reward_card_id = fields.Many2one('cw.reward.card', string='Reward Card Redeeming', required=False)
    cw_use_points = fields.Boolean(string='Use Points', default=False)
    cw_reward_card_for_allocation_id = fields.Many2one('cw.reward.card', string='Reward Card for Allocation', required=False)
    cw_reward_card_code = fields.Char('Reward Card Code for Allocation', required=False )
    cw_sale_order_id = fields.Many2one('sale.order', string='Related Sale Order')  # Link to the related Sale Order

    @api.model
    def _process_order(self, order, draft, existing_order):
        pos_order_id  = super()._process_order(order, draft, existing_order)
        """
        # Browse the pos_order record using the returned ID
        pos_order = self.browse(pos_order_id)
        _logger.info('NOW NOW NOW Processing order  %s', pos_order)
        
        
        # Now that the order is created, check if points are being used
        if pos_order.cw_sale_order_id and pos_order.cw_sale_order_id.cw_spend_points:
            pos_order.write({
                    'cw_use_points': True,
                    'cw_reward_card_id': pos_order.cw_sale_order_id.cw_reward_card_id.id
                })  # Use write to persist the change
            # Check if points have already been deducted in the related Sale Order
            if pos_order.cw_sale_order_id.points_deducted:
                # Skip point deduction since it has already been done
                return pos_order_id
            
            
            # Check if the reward card has enough points
            self._check_sufficient_points(pos_order)
            # Deduct the required points from the reward card
            self._deduct_points(pos_order)
            """

        return pos_order_id
    
    def _check_sufficient_points(self, pos_order):
        if not pos_order.cw_reward_card_id:
            raise ValidationError('No reward card linked to the order.')

        total_points_needed = sum(int(line.product_id.cw_points_cost * line.qty) for line in pos_order.lines)
        if pos_order.cw_reward_card_id.total_points < total_points_needed:
            raise ValidationError('Not enough points on the reward card.')


    def _deduct_points(self, pos_order):
        reward_card = pos_order.cw_reward_card_id
        total_points_needed = 0
        
        for line in pos_order.lines:
            product = line.product_id
            qty = line.qty
            points_for_line = product.cw_points_cost * qty
            
            total_points_needed += points_for_line
            
            # Create a reward points history entry for each product line
            self.env['cw.reward.points.history'].create({
                'reward_card_id': reward_card.id,
                'sale_order_id': pos_order.cw_sale_order_id.id if pos_order.cw_sale_order_id else False,  # Link to Sale Order if present
                'qty': qty,
                'product_id': product.id,  # Track the product
                'points': -points_for_line,  # Deduct points for this product line
                'type': 'redeem',  # Type is redeem for deductions
            })
        
        # Update the total points on the reward card
        new_total_points = reward_card.total_points - total_points_needed
        reward_card.write({'total_points': new_total_points})
        
        if pos_order.cw_sale_order_id:
            sale_oder = pos_order.cw_sale_order_id
            sale_oder.write({
                    'points_deducted': True
                })
        
        
    
    
    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        _logger.info('We are in _order_fields %s', ui_order)
        if ui_order.get('membership_card_code'):
            _logger.info('We have posted Message %s', ui_order['membership_card_code'])
            res['cw_reward_card_code'] = ui_order['membership_card_code']
            
        # Check for sale_order_id inside lines (nested data)
        if 'lines' in ui_order:
            for line in ui_order['lines']:
                line_data = line[2]  # The actual data is in the third element (index 2)
                if 'sale_order_origin_id' in line_data:
                    sale_order_id = line_data['sale_order_origin_id']['id']
                    _logger.info('Sale Order selected from POS: %s', sale_order_id)
                    res['cw_sale_order_id'] = sale_order_id
                    break  # We can stop after finding the sale order in the first line
        return res
    
    
    def action_pos_order_paid(self):
        _logger.info('ACTION ACTION ACTION ACTION POST ORDER PAID')
        
        for pos_order in self:
            # Now that the order is created, check if points are being used
            if pos_order.cw_sale_order_id and pos_order.cw_sale_order_id.cw_spend_points and not pos_order.cw_sale_order_id.points_deducted:
                pos_order.write({
                        'cw_use_points': True,
                        'cw_reward_card_id': pos_order.cw_sale_order_id.cw_reward_card_id.id
                    })  # Use write to persist the change
                # Check if points have already been deducted in the related Sale Order
                if pos_order.cw_sale_order_id.points_deducted:
                    # Skip point deduction since it has already been done
                   continue
               
                # Check if the reward card has enough points
                self._check_sufficient_points(pos_order)
                # Deduct the required points from the reward card
                self._deduct_points(pos_order)
            
        
        res = super().action_pos_order_paid()
        _logger.info('action_pos_order_paid Waiting to implement the logic behind action_pos_order_invoice with  order ')

        for order in self:
            reward_card_allocation = order.cw_reward_card_code
            use_point = order.cw_use_points
            _logger.info('Executing logic for reward allocation after payment for order %s', order.id)
            _logger.info('action_pos_order_paid Waiting to implement the logic behind action_pos_order_invoice with  order %s', order)
            
            existing_pos_order = False
            
            if order.cw_sale_order_id:
                existing_pos_order = self.env['pos.order'].search([
                    ('cw_sale_order_id', '=', order.cw_sale_order_id.id),
                    ('id', '!=', order.id)  # Exclude the current pos_order
                ], limit=1)
            
            

            if reward_card_allocation and not use_point and not existing_pos_order:
                _logger.info('Processing reward card allocation for order %s', order.id)

                # Search for the reward card by name (reward_card_allocation)
                reward_card = self.env['cw.reward.card'].search([('name', '=', reward_card_allocation)], limit=1)

                if not reward_card:
                    _logger.warning('Reward card with code %s not found', reward_card_allocation)
                    continue

                # Link the reward card to the order
                order.write({'cw_reward_card_for_allocation_id': reward_card.id})
                
                 # Ensure that the order has a partner before generating the invoice
                if not order.partner_id:
                    # Assign a default partner (you can choose a real partner or create a default one)
                    default_partner = self.env['res.partner'].search([('name', '=', 'Default POS Customer')], limit=1)
                    if not default_partner:
                        # Create a default partner if it doesn't exist
                        default_partner = self.env['res.partner'].create({'name': 'Default POS Customer'})
                    order.partner_id = default_partner
                    _logger.info('Assigned default partner to the order %s', order.id)
                 
                    
                if not order.account_move:
                    _logger.info('No account move found, generating invoice for order %s', order.id)
                    order._generate_pos_order_invoice()

                # Process each order line
                for line in order.lines:
                    product = line.product_id
                    if product.type == 'product' and line.qty >= 1 and product.standard_price:
                        _logger.info('Processing product: %s, Quantity: %s', product.name, line.qty)
                        
                        # Call the function with the parameters: account_move_id, product_id, reward_card_code
                        if order.account_move:
                            _logger.info('PROCESSING Processing product with Account Mode: %s, Quantity: %s', product.name, line.qty)
                            self._allocate_points_to_card(order.account_move.id, product.id, reward_card, line.price_unit, product.standard_price, line.qty)
                        else:
                            _logger.warning('No account move linked to the order for reward allocation: %s', order.id)

        return res
    
    
    def _generate_pos_order_invoice(self):
        _logger.info('GENERATE GENERATE Processing product with Account Mode')
        return super()._generate_pos_order_invoice()
    


    
    
    def _refund(self):
        orders = super()._refund()
        
        for order in orders:
            reward_card = order.cw_reward_card_for_allocation_id
            
            
            if reward_card:
                _logger.info('Processing points reversal for refunded order: %s', order.id)
                
                for line in order.lines:
                    product = line.product_id
                    refunded_qty = line.qty
                    
                    if product.type == 'product' and line.qty >= 1:
                        if order.account_move:
                            self._subtract_points_for_refund(order.account_move.id, product.id, reward_card, line.price_unit, product.standard_price, refunded_qty)
                        else:
                            _logger.warning('No account move linked to the order for refund: %s', order.id)
        
        return orders
    
    
    
    def _allocate_points_to_card(self, account_move_id, product_id, reward_card, unit_price, landed_price, quantity):
        _logger.info('Allocating points for Account Move ID: %s, Product ID: %s, Reward Card: %s, Unit Price: %s, Quantity: %s',
                     account_move_id, product_id, reward_card.name, unit_price, quantity)

        # Example logic: You can calculate points based on the unit price and quantity
        points_to_allocate = int((quantity * (unit_price - landed_price) * 0.03) * 3)  
        
        if points_to_allocate > 0 :
            # Add points to the reward card (modify in memory)
            new_total_points = reward_card.total_points + points_to_allocate

            # Persist the changes to the database by writing the new value to the 'total_points' field
            reward_card.write({'total_points': new_total_points})

            # Log the allocation in reward points history
            self.env['cw.reward.points.history'].create({
                'reward_card_id': reward_card.id,         # Link the reward card
                'invoice_id': account_move_id,            # Link the account move (invoice)
                'product_id': product_id,                 # Link the product
                'points': points_to_allocate,             # The number of points allocated
                'type': 'gain',                           # Type of transaction is "gain"
                'qty': quantity,                           # Type of transaction is "gain"
            })

        _logger.info('Allocated %s points to reward card %s', points_to_allocate, reward_card.name)
        
        
    
    def _subtract_points_for_refund(self, account_move_id, product_id, reward_card, unit_price, landed_price, quantity):
        _logger.info('Subtracting points for Account Move ID: %s, Product ID: %s, Reward Card: %s, Unit Price: %s, Quantity: %s',
                 account_move_id, product_id, reward_card.name, unit_price, quantity)
        
        # Find the original 'gain' entry in the reward points history
        reward_point_lines = self.env['cw.reward.points.history'].search([
            ('reward_card_id', '=', reward_card.id),
            ('product_id', '=', product_id),
            ('type', '=', 'gain'),
            ('fully_reversed', '=', False)
        ])
        
        total_quantity_to_refund = quantity
        for line in reward_point_lines:
            available_qty_to_reverse = line.qty - line.qty_reversed
            
            if available_qty_to_reverse <= 0:
                continue  # Skip if there's no available quantity to reverse
            
            if available_qty_to_reverse >= total_quantity_to_refund:
                qty_to_reverse = total_quantity_to_refund
            else :
                qty_to_reverse = available_qty_to_reverse
                
            points_per_unit = line.points / line.qty
            points_to_subtract = int(points_per_unit * qty_to_reverse) 
            
            # Subtract points from the reward card
            new_total_points = reward_card.total_points - points_to_subtract
            if new_total_points < 0:
                new_total_points = 0  # Ensure points don't go negative
                
            # Update the reward card's total points
            reward_card.write({'total_points': new_total_points})
            
            # Log the points subtraction in reward points history as a 'reverse' entry
            self.env['cw.reward.points.history'].create({
                'reward_card_id': reward_card.id,
                'invoice_id': account_move_id,
                'product_id': product_id,
                'points': -points_to_subtract,  # Subtract points (negative)
                'type': 'reverse',
                'qty_reversed': quantity,
            })
            
            new_qty_reversed = line.qty_reversed + qty_to_reverse
            line.write({
                'qty_reversed': new_qty_reversed,
                'fully_reversed': new_qty_reversed >= line.qty,  # Set fully_reversed if all items are refunded
                'has_been_reversed': True
            })
            
            _logger.info('Subtracted %s points from reward card %s for product %s', points_to_subtract, reward_card.name, product_id)
            break  # Exit loop after finding and processing one line

    
