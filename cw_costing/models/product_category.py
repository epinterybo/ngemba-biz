from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    x_cw_costing_duty_rate = fields.Float(string="Duty rate", default=0)
    x_cw_costing_warranty_rate = fields.Float(string="Warranty rate", default=0)
    x_cw_costing_vat_rate = fields.Float(string="VAT", default=0.15)
    x_cw_costing_shipping_rate = fields.Float(string='Shipping rate', default=0)
    cw_harmonized_code_id = fields.Many2one('cw.costing.harmonized.code', string="Harmonized Code")
    
    def search_costing_duty_rate(self):
        self.ensure_one()
        if self.x_cw_costing_duty_rate and self.x_cw_costing_duty_rate > 0:
            return self.x_cw_costing_duty_rate
        elif self.parent_id:
            for category in self:
                if category.x_cw_costing_duty_rate and category.x_cw_costing_duty_rate > 0:
                    return category.x_cw_costing_duty_rate
        return 0
        
        
    
    def search_costing_warranty_rate(self):
        self.ensure_one()
        if self.x_cw_costing_warranty_rate and self.x_cw_costing_warranty_rate > 0:
            return self.x_cw_costing_warranty_rate
        elif self.parent_id:
            for category in self:
                if category.x_cw_costing_warranty_rate and category.x_cw_costing_warranty_rate > 0:
                    return category.x_cw_costing_warranty_rate
        return 0
        
    def search_costing_vat_rate(self):
        self.ensure_one()
        if self.x_cw_costing_vat_rate and self.x_cw_costing_vat_rate > 0:
            return self.x_cw_costing_vat_rate
        elif self.parent_id:
            for category in self:
                if category.x_cw_costing_vat_rate and category.x_cw_costing_vat_rate > 0:
                    return category.x_cw_costing_vat_rate
                
        return 0
        
    def search_shipping_rate(self):
        self.ensure_one()
        if self.x_cw_costing_shipping_rate and self.x_cw_costing_shipping_rate > 0:
            return self.x_cw_costing_shipping_rate
        elif self.parent_id:
            for category in self:
                if category.x_cw_costing_shipping_rate and category.x_cw_costing_shipping_rate > 0:
                    return category.x_cw_costing_shipping_rate
        
        return 0
    
    
    def cw_search_harmonized_code_id(self):
        self.ensure_one()
        if self.cw_harmonized_code_id:
            res = self.cw_harmonized_code_id
        elif self.parent_id:
            res = self.parent_id.cw_search_harmonized_code_id()
        else:
            res = self.env['cw.costing.harmonized.code']
        
        return res
    