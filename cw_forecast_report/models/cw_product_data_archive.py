import logging
from pytz import timezone, UTC
from collections import defaultdict
from datetime import datetime, time, timedelta
from dateutil import relativedelta

from odoo import _, api, fields, models
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import RedirectWarning, UserError
from odoo.tools import float_compare, frozendict

_logger = logging.getLogger(__name__)

class CwProductDataArchive(models.Model):
    _name = 'cw.product.data.daily.archive'
    _description = "CW Products Daily Data Archive"
    
    product_id = fields.Many2one('product.product', string='Product', readonly=True,)
    categ_id = fields.Many2one('product.category',  string='Category', compute='compute_categ_id', readonly=True, store=True)
    x_ListID = fields.Char(string='x_ListID', required=False, compute='compute_x_List_id', store=True)
    zdate = fields.Datetime(string='Zdate', required=False, default=lambda self: fields.Datetime.now(), readonly=True, store=True)
    # The code you provided is not valid Python code. It seems like you have written some comments and
    # a variable name "TimeCreated" without any actual code. If you have a specific question or need
    # help with Python code, please provide more context or a specific problem you are facing.
    TimeCreated = fields.Datetime(string='TimeCreated', required=False, readonly=True, compute='compute_time_created', store=True)
    TimeModified = fields.Datetime(string='TimeModified', required=False, readonly=True, store=True, compute='compute_time_modified')
    Name = fields.Char(string='Name', required=False, readonly=True, compute='compute_name', store=True)
    FullName = fields.Char(string='FullName', required=False, readonly=True, compute='compute_full_name', store=True)
    BarCodeValue = fields.Char(string='BarCodeValue', required=False, readonly=True, compute='compute_barcode', store=True)
    #AssignEvenIfUsed = fields.Boolean(string='AssignEvenIfUsed', required=False, readonly=True)
    #AllowOverride = fields.Boolean(string='AllowOverride', required=False, readonly=True)
    IsActive = fields.Boolean(string='IsActive', required=False, readonly=True, compute='compute_is_active', store=True)
    #ClassRef_ListID = fields.Char(string='ClassRef_ListID', required=False, readonly=True, compute='compute_class_ref_list_id')
    #ClassRef_FullName = fields.Char(string='ClassRef_FullName', required=False, readonly=True, compute='compute_class_ref_full_name')
    FullCategoryName = fields.Char(string='FullCategoryName', compute='compute_full_category_name', store=True)
    ParentRef_ListID = fields.Char(string='ParentRef_ListID', required=False, readonly=True, compute='compute_parent_ref_list_id', store=True)
    ParentRef_FullName = fields.Char(string='ParentRef_FullName', required=False, readonly=True, compute='compute_parent_ref_full_name', store=True)
    Sublevel = fields.Integer(string='Sublevel', required=False, readonly=True, compute='compute_sub_level', store=True)
    #ManufacturerPartNumber = fields.Char(string='ManufacturerPartNumber', required=False, readonly=True)
    #UnitOfMeasureSetRef_ListID = fields.Char(string='UnitOfMeasureSetRef_ListID', required=False, readonly=True)
    #UnitOfMeasureSetRef_FullName = fields.Char(string='UnitOfMeasureSetRef_FullName', required=False, readonly=True)
    #ForceUOMChange = fields.Boolean(string='ForceUOMChange', required=False, readonly=True)
    #IsTaxIncluded = fields.Boolean(string='IsTaxIncluded', required=False, readonly=True)
    #SalesTaxCodeRef_ListID = fields.Char(string='SalesTaxCodeRef_ListID', required=False, readonly=True)
    #SalesTaxCodeRef_FullName = fields.Char(string='SalesTaxCodeRef_FullName', required=False, readonly=True)
    SalesDesc = fields.Text(string='SalesDesc', required=False, readonly=True, compute='compute_sales_desc', store=True)
    SalesPrice = fields.Float(string='SalesPrice', required=False, readonly=True, compute='compute_sales_price', store=True)
    #IncomeAccountRef_ListID = fields.Char(string='IncomeAccountRef_ListID', required=False, readonly=True)
    #IncomeAccountRef_FullName = fields.Char(string='IncomeAccountRef_FullName', required=False, readonly=True)
    PurchaseDesc = fields.Char(string='PurchaseDesc', required=False, readonly=True, compute='compute_purchase_desc', store=True)
    PurchaseCost = fields.Float(string='PurchaseCost', required=False, readonly=True, compute='compute_purchase_cost', store=True)
    #PurchaseTaxCodeRef_ListID = fields.Char(string='PurchaseTaxCodeRef_ListID', required=False, readonly=True)
    #PurchaseTaxCodeRef_FullName = fields.Char(string='PurchaseTaxCodeRef_FullName', required=False, readonly=True)
    #COGSAccountRef_ListID = fields.Char(string='COGSAccountRef_ListID', required=False, readonly=True)
    #COGSAccountRef_FullName = fields.Char(string='COGSAccountRef_FullName', required=False, readonly=True)
    #PrefVendorRef_ListID = fields.Char(string='PrefVendorRef_ListID', required=False, readonly=True)
    #PrefVendorRef_FullName = fields.Char(string='PrefVendorRef_FullName', required=False, readonly=True)
    #AssetAccountRef_ListID = fields.Char(string='AssetAccountRef_ListID', required=False, readonly=True)
    #AssetAccountRef_FullName = fields.Char(string='AssetAccountRef_FullName', required=False, readonly=True)
    ReorderPoint = fields.Float(string='ReorderPoint', required=False, readonly=True, compute='compute_reorder_point')
    #Max = fields.Float(string='Max', required=False, readonly=True)
    QuantityOnHand = fields.Float(string='QuantityOnHand', required=False, readonly=True, compute='compute_quantity_on_hand', store=True)
    AverageCost = fields.Float(string='AverageCost', required=False, readonly=True, compute='compute_average_cost', store=True)
    QuantityOnOrder = fields.Float(string='QuantityOnOrder', required=False, readonly=True, compute='compute_quantity_on_order', store=True)
    QuantityOnSalesOrder = fields.Float(string='QuantityOnSalesOrder', required=False, readonly=True, compute='compute_quantity_on_sales_order', store=True)
    #UserData = fields.Char(string='UserData', required=False, readonly=True)
    #Operation = fields.Char(string='Operation', required=False, readonly=True)
    #LSData = fields.Char(string='LSData', required=False, readonly=True)
    
    
    @api.depends('product_id')
    def compute_categ_id(self):
        for record in self:
            if record.product_id:
                record.categ_id = record.product_id.categ_id.id
            else:
                record.categ_id = False
                
    @api.depends('product_id')
    def compute_x_List_id(self):
        for record in self:
            if record.product_id and record.product_id.x_cw_list_id:
                record.x_ListID = record.product_id.x_cw_list_id
            else:
                record.x_ListID = False
    
    @api.depends('product_id')
    def compute_name(self):
        for record in self:
            if record.product_id:
                record.Name = record.product_id.name
            else:
                record.Name = False
                
    @api.depends('product_id')
    def compute_time_created(self):
        for record in self:
            if record.product_id:
                record.TimeCreated = record.product_id.create_date
            else:
                record.TimeCreated = False
                
    @api.depends('product_id')
    def compute_time_modified(self):
        for record in self:
            if record.product_id:
                record.TimeModified = record.product_id.write_date
            else:
                record.TimeModified = False
                
    
    def get_category_full_name(self, categ_id, category_names):
        category_names.append(categ_id.name)
        if categ_id.parent_id:
            return self.get_category_full_name(categ_id=categ_id.parent_id, category_names=category_names)
        else:
            return ' / '.join(reversed(category_names))
    
                
    @api.depends('product_id')
    def compute_full_name(self):
        for record in self:
            if record.product_id:
                category_names = []
                record.FullName = self.get_category_full_name(categ_id=record.product_id.categ_id, category_names=category_names) + ' / ' + record.product_id.name
            else:
                record.FullName = False
    
    @api.depends('product_id')
    def compute_barcode(self):
        for record in self:
            if record.product_id:
                record.BarCodeValue = record.product_id.product_tmpl_id.barcode
            else:
                record.BarCodeValue = False
                
    @api.depends('product_id')
    def compute_is_active(self):
        for record in self:
            if record.product_id and (record.product_id.product_tmpl_id.sale_ok or record.product_id.product_tmpl_id.purchase_ok):
                record.IsActive = True
            else:
                record.IsActive = False
    """
    @api.depends('product_id')
    def compute_class_ref_list_id(self):
        for record in self:
            if record.product_id:
                record.ClassRef_ListID = record.product_id.categ_id.id
            else:
                record.ClassRef_ListID = False
    
    @api.depends('product_id')
    def compute_class_ref_full_name(self):
        for record in self:
            if record.product_id:
                record.ClassRef_FullName = record.product_id.categ_id.name
            else:
                record.ClassRef_FullName = False
    """
        
    @api.depends('product_id')
    def compute_full_category_name(self):
        for record in self:
            if record.product_id and record.product_id.categ_id:
                category_names = []
                record.FullCategoryName = self.get_category_full_name(categ_id=record.product_id.categ_id, category_names=category_names)
            else:
                record.FullCategoryName = False
    
                
    @api.depends('product_id')
    def compute_parent_ref_list_id(self):
        for record in self:
            if record.product_id.categ_id.parent_id:
                record.ParentRef_ListID = record.product_id.categ_id.parent_id.id
            else:
                record.ParentRef_ListID = False
                
    @api.depends('product_id')
    def compute_parent_ref_full_name(self):
        for record in self:
            if record.product_id.categ_id.parent_id:
                category_names = []
                record.ParentRef_FullName = self.get_category_full_name(categ_id=record.product_id.categ_id.parent_id, category_names=category_names)
            else:
                record.ParentRef_FullName = False
    
    def get_category_level(self, categ_id, level=0):
        if categ_id.parent_id:
            level += 1
            return self.get_category_level(categ_id=categ_id.parent_id, level=level)
        else:
            return level
    
    @api.depends('product_id')
    def compute_sub_level(self):
        for record in self:
            if record.product_id and record.product_id.categ_id:
                record.Sublevel = self.get_category_level(categ_id=record.product_id.categ_id, level=1)
            else:
                record.Sublevel = False
    
    
    @api.depends('product_id')
    def compute_sales_desc(self):
        for record in self:
            if record.product_id:
                record.SalesDesc = record.product_id.product_tmpl_id.description_sale
            else:
                record.SalesDesc = False
    
    @api.depends('product_id')
    def compute_sales_price(self):
        for record in self:
            if record.product_id:
                pricelist = self.env['product.pricelist'].search([('company_id', '=', self.env.company.id)], limit=1)
                if pricelist:
                    price = pricelist._get_product_price(record.product_id, 1.0, self.env.user.partner_id)
                    #get_product_price(record.product_id, 1.0, self.env.user.partner_id)
                    X_SalesPrice = price
                else:
                    X_SalesPrice = 0.0
                    
                product_template = record.product_id.product_tmpl_id
                taxes = product_template.taxes_id
                if taxes:
                    record.SalesPrice = taxes.compute_all(X_SalesPrice, currency=None, quantity=1.0)['total_included']
                else:
                    record.SalesPrice = X_SalesPrice
            else:
                record.SalesPrice = False
    
    
    @api.depends('product_id')
    def compute_purchase_desc(self):
        for record in self:
            if record.product_id:
                record.PurchaseDesc = record.product_id.product_tmpl_id.description_purchase
            else:
                record.PurchaseDesc = False
                
    @api.depends('product_id')
    def compute_purchase_cost(self):
        for record in self:
            if record.product_id:
                record.PurchaseCost = record.product_id.product_tmpl_id.standard_price
            else:
                record.PurchaseCost = False
    

    @api.depends('product_id')
    def compute_reorder_point(self):
        for record in self:
            if record.product_id:
                orderpoints = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', record.id)])
                if orderpoints:
                    record.ReorderPoint = max(orderpoints.mapped('product_min_qty'))
                else:
                    record.ReorderPoint = 0
            else:
                record.ReorderPoint = 0


    @api.depends('product_id')
    def compute_quantity_on_hand(self):
        for record in self:
            if record.product_id:
                record.QuantityOnHand = record.product_id.qty_available
            else:
                record.QuantityOnHand = False
                
    @api.depends('product_id')
    def compute_average_cost(self):
        for record in self:
            if record.product_id:
                purchase_order_moves = self.env['stock.move'].search([
                    ('product_id', '=', record.product_id.id),
                    ('state', '=', 'done'),
                    ('purchase_line_id', '!=', False)  # Ensures the move is linked to a purchase order line
                ])
                total_cost = sum(move.price_unit * move.product_qty for move in purchase_order_moves)
                total_qty = sum(move.product_qty for move in purchase_order_moves)
                record.AverageCost = total_cost / total_qty if total_qty else 0.0
            else:
                record.AverageCost = False
    
    
    @api.depends('product_id')
    def compute_quantity_on_order(self):
        for record in self:
            if record.product_id:
                purchase_order_lines = self.env['purchase.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id.state', '=', 'purchase'),  # Consider only purchase orders in the purchase state
                ])

                # Compute the total quantity waiting for delivery
                record.QuantityOnOrder = sum(line.product_qty - line.qty_received for line in purchase_order_lines)
            else:
                record.QuantityOnOrder = False
    
    
    @api.depends('product_id')
    def compute_quantity_on_sales_order(self):
        for record in self:
            if record.product_id:
                invoiced_qty = self.env['account.move.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('move_id.create_date', '>=', datetime.now().strftime('%Y-%m-%d 00:00:00')),
                    ('move_id.create_date', '<=', datetime.now().strftime('%Y-%m-%d 23:59:59')),
                    ('move_id.state', '=', 'posted')
                ])
                record.QuantityOnSalesOrder = sum(line.quantity for line in invoiced_qty)
            else:
                record.QuantityOnSalesOrder = False
    
    
    @api.model
    def process_all_products(self):
        batch_size = 25
        offset = 0
        
        product_model = self.env['product.product']
        total_products = product_model.search_count([
                ('type', '=', 'product'),
                '|',  # Logical OR operator
                ('active', '=', True),
                ('active', '=', False)
            ])
        
        while offset < total_products:
            # Retrieve products per batch
            products = product_model.search([
                    ('type', '=', 'product'),
                    '|',  # Logical OR operator
                    ('active', '=', True),
                    ('active', '=', False)
                ], limit=batch_size, offset=offset)

            for product in products:
                self.process_product(product)
            
            self.env.cr.commit()
            _logger.info(f"Commited batch starting at offset {offset}")
            offset += batch_size
        
        _logger.info("All batches processed successfully")        
    
    
    @api.model
    def process_product(self, product):
        record_values = {}
        record_values['product_id'] = product.id
        self.create(record_values)
        
    @api.model
    def delete_all_records(self):
        # Search for all records of the model
        records = self.search([])

        # Delete All Records
        records.unlink()
        
    
    @api.model
    def scheduler_job_to_run(self):
        #self.delete_all_records()
        self.process_all_products()