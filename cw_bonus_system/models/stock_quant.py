from odoo import _, api, fields, models, SUPERUSER_ID

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.model
    def action_set_inventory_quantity(self):
        res = super().action_set_inventory_quantity()
        print("christian passe par action_set_inventory_quantity 01")
        
        return res
    
    def  action_apply_inventory(self):
        user_id = self.env.user.id
        
        # Get the inventory quantities before applying the inventory adjustment
        before_inventory_quantities = {quant.product_id: quant.quantity for quant in self}
        
        # Call super to execute the original method
        result = super().action_apply_inventory()
        
        # Get the inventory quantities after applying the inventory adjustment
        after_inventory_quantities = {quant.product_id: quant.quantity for quant in self}
        
        # Compare the inventory quantities to identify the impacted products
        products_counted = []
        for product, before_quantity in before_inventory_quantities.items():
            after_quantity = after_inventory_quantities.get(product, 0.0)
            if before_quantity != after_quantity:
                products_counted.append(product)
                product_id = product.id
                
        print("christian passe par action_apply_inventory 02")
        return result
    
    def set_counting_bonus_point(self, product_id: int):
        product = self.env['product.product'].browse(product_id)
        user_id = self.env.user.id
        
        
        employee_user = self.env['cw.bonus.employee'].search([
            ('user_id', '=', self.created_user_id)
        ], limit=1)
        
        
        if not employee_user:
            return
        
        #the logic to add Point should go here
        points = 100
        self.env['cw.bonus.points.tracking'].create_new_points_history_from_inventory(product_id=product_id, employer_id=employee_user.id, points=points)
        
        
        