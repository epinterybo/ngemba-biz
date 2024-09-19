import logging
from pytz import timezone, UTC
from collections import defaultdict
from datetime import datetime, time, timedelta
from dateutil import relativedelta
from psycopg2 import OperationalError

from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero, frozendict, split_every

import os
import sys
import importlib.util

_logger = logging.getLogger(__name__)


class CwForecastReportCronTrack(models.Model):
    _name = 'cw.ocm.forecast.cron.track'
    _description = 'Cw Ocm Forecast Cron Track'
    
    offset_start = fields.Integer(string='Starting Number', default=0, required=False)
    last_starting_time = fields.Datetime(string='Last starting time', default=lambda self: fields.Datetime.now())

class CwOcmForecast(models.Model):
    _name = 'cw.ocm.forecast'
    _description = "CW OCM Forecast Report"
    
    x_ListID = fields.Char(string='x_ListID', required=False)
    x_FullName = fields.Char(string='x_FullName', required=False)
    x_salesdesc = fields.Text(string='x_salesdesc', required=False)
    
    product_id = fields.Many2one('product.product', string='Product')
    categ_id = fields.Many2one('product.category',  string='Category')
    #seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors', depends_context=('company',))
    #seller_ids = fields.One2many('product.supplierinfo', 'product_id', string='Vendors')
    seller_ids = fields.Many2many('res.partner', string='Vendors')
    stock_selling_status = fields.Char(string='S. status')
    should_be_ordered = fields.Boolean(string='S.B.O', default=False)
    OrderRecommend90 = fields.Integer(string='To Order', default=0)
    OrderRecommend120 = fields.Integer(string='To Order 120', default=0)
    OrderRecommend180 = fields.Integer(string='To Order 180', default=0)
    OrderRecommend365 = fields.Integer(string='To Order 365', default=0)
    x_QTYonHand = fields.Float(string='Stock', default=0)
    X_QtyonOrder = fields.Float(string='I.B.O', default=0)
    in_draft_order = fields.Float(string='I.D.O', default=0)
    X_Invoice30days = fields.Float(string='S 30', default=0)
    X_Invoice60Days = fields.Float(string='S 60', default=0)
    X_Invoice90days = fields.Float(string='S 90', default=0)
    x_invoice120days = fields.Float(string='S 120', default=0)
    x_Invoice180days = fields.Float(string='S 180', default=0)
    X_invoice365days = fields.Float(string='S 365', default=0)
    X_unique30 = fields.Integer(string='C 30', default=0)
    X_unique60 = fields.Integer(string='C 60', default=0)
    X_unique90 = fields.Integer(string='C 90', default=0)
    X_unique120 = fields.Integer(string='C 120', default=0)
    X_unique180 = fields.Integer(string='C 180', default=0)
    x_unique365 = fields.Integer(string='C 365', default=0)
    X_unique30percent = fields.Integer(string='C 30 P.', default=0)
    X_unique60percent = fields.Integer(string='C 60 P.', default=0)
    X_unique90percent = fields.Integer(string='C 90 P.', default=0)
    X_unique120percent = fields.Integer(string='C 120 P.', default=0)
    X_unique180percent = fields.Integer(string='C 180 P.', default=0)
    X_unique365percent = fields.Integer(string='C 365 P.', default=0)
    x_VendorName = fields.Char(string='x_VendorName', required=False)
    x_LastPOnum = fields.Char(string='x_LastPOnum', required=False)
    x_lastPurchaseOrderDate = fields.Datetime(string='x_lastPurchaseOrderDate', required=False)
    x_lastReceivedTime = fields.Datetime('x_lastReceivedTime', required=False)
    nb_days_last_delivery = fields.Integer(string='D.S.L.D', default=0)
    nb_days_last_po = fields.Integer(string='D.S.L PO', default=0)
    X_lastpurchaseOrderQTY = fields.Integer(string='Q.L. PO', default=0)
    X_StockTakedate = fields.Datetime(string='X_StockTakedate', required=False)
    nb_since_last_stocktake  = fields.Integer(string='D.S.L S.T', default=0)
    is_stock_take_correct = fields.Boolean(string='S.T. OK', default=True)
    X_stockTakeOffby = fields.Integer(string='S.T difference', default=0)
    X_isactive =  fields.Integer(string='Active', default=1)
    X_LastPurchasePrice = fields.Float(string='P. Amount')
    X_lastPurchaseExchange = fields.Float(string='X_lastPurchaseExchange', required=False, store=True)
    x_lastReceivedQTY = fields.Float(string='x_lastReceivedQTY', required=False)
    currency_id = fields.Many2one('res.currency', string='Currency')
    should_be_deleted = fields.Boolean(string='To deleted', default=False)
    is_dead_stock = fields.Boolean(string='Dead Stock', default=False)
    AppearsInTargetItems = fields.Boolean(string='In Target', default=False)
    #orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', string='Order Point', compute='_compute_orderpoint_id', store=True)
    combined_30_days = fields.Char(string='S30 (C)', required=False)
    combined_60_days = fields.Char(string='S60 (C)', required=False)
    combined_90_days = fields.Char(string='S90 (C)', required=False)
    combined_180_days = fields.Char(string='S180 (C)', required=False)
    combined_365_days = fields.Char(string='S365 (C)', required=False)
    product_image = fields.Binary(string='Product Image', compute='_compute_product_image')
    currency_price_id = fields.Many2one('res.currency', string='Currency V', default=lambda self: self.env.ref('base.VUV').id)
    X_SalesPrice = fields.Float(string='Price', compute='_compute_product_price', store=True)
    X_purchasecost = fields.Float(string='P.L. Cost', store=True)
    stock_and_back_order = fields.Float(string="St_I.B.O", compute='_compute_stock_and_back_order', store=True)
    copied_product_name = fields.Char(string='__', compute='_compute_copied_product_name', store=True)
    action_buttons = fields.Char(string='Action Buttons')
    record_id_value = fields.Integer(string='_', compute='_compute_record_id_value', store=True)
    
    x_timecreateditem = fields.Datetime(string='x_timecreateditem', required=False, compute='_compute_x_timecreateditem', store=True)

    SoldinBetween0n30 = fields.Integer(string='SoldinBetween0n30', required=False)
    SoldinBetween30n60 = fields.Integer(string='SoldinBetween30n60', required=False)
    SoldInBetween60n90 = fields.Integer(string='SoldInBetween60n90', required=False)
    SoldInBetween90n120 = fields.Integer(string='SoldInBetween90n120', required=False)
    SoldInBetween120n180 = fields.Integer(string='SoldInBetween120n180', required=False)
    SoldInBetween180n365 = fields.Integer(string='SoldInBetween180n365', required=False)

    NumberofQuotes0n30 = fields.Integer(string='NumberofQuotes0n30', required=False)
    NumberofQuotes30n60 = fields.Integer(string='NumberofQuotes30n60', required=False)
    NumberofQuotes60n90 = fields.Integer(string='NumberofQuotes60n90', required=False)
    NumberofQuotes90n120 = fields.Integer(string='NumberofQuotes90n120', required=False)
    NumberofQuotes120n180 = fields.Integer(string='NumberofQuotes120n180', required=False)
    NumberofQuotes180n365 = fields.Integer(string='NumberofQuotes180n365', required=False)

    NumberofRefunds0n30 = fields.Integer(string='NumberofRefunds0n30', required=False)
    NumberofRefunds30n60 = fields.Integer(string='NumberofRefunds30n60', required=False)
    NumberofRefunds60n90 = fields.Integer(string='NumberofRefunds60n90', required=False)
    NumberofRefunds90n120 = fields.Integer(string='NumberofRefunds90n120', required=False)
    NumberofRefunds120n180 = fields.Integer(string='NumberofRefunds120n180', required=False)
    NumberofRefunds180n365 = fields.Integer(string='NumberofRefunds180n365', required=False)

    x_qtyonhand30 = fields.Integer(string='x_qtyonhand30', required=False)
    x_qtyonhand60 = fields.Integer(string='x_qtyonhand60', required=False)
    x_qtyonhand90 = fields.Integer(string='x_qtyonhand90', required=False)
    x_qtyonhand120 = fields.Integer(string='x_qtyonhand120', required=False)
    X_qtyonhand180 = fields.Integer(string='X_qtyonhand180', required=False)
    x_qtyonhand365 = fields.Integer(string='x_qtyonhand365', required=False)

    x_qtyonorder30 = fields.Integer(string='x_qtyonorder30', required=False)
    x_qtyonorder60 = fields.Integer(string='x_qtyonorder60', required=False)
    x_qtyonorder90 = fields.Integer(string='x_qtyonorder90', required=False)
    x_qtyonorder120 = fields.Integer(string='x_qtyonorder120', required=False)
    x_qtyonorder180 = fields.Integer(string='x_qtyonorder180', required=False)
    x_qtyonorder365 = fields.Integer(string='x_qtyonorder365', required=False)

    NumberofPurchaseOrdersQTY = fields.Integer(string='NumberofPurchaseOrdersQTY', required=False)

    x_PurchaseOrder30 = fields.Integer(string='x_PurchaseOrder30', required=False)
    x_PurchaseOrder60 = fields.Integer(string='x_PurchaseOrder60', required=False)
    x_PurchaseOrder90 = fields.Integer(string='x_PurchaseOrder90', required=False)
    x_PurchaseOrder120 = fields.Integer(string='x_PurchaseOrder120', required=False)
    x_PurchaseOrder180 = fields.Integer(string='x_PurchaseOrder180', required=False)
    x_PurchaseOrder365 = fields.Integer(string='x_PurchaseOrder365', required=False)
    
    category_name = fields.Char(string='Category Name', required=False)
    currency_name = fields.Char(string='Currency Name', required=False)
    barcode = fields.Char(string='Barcode', required=False)
    Vendor_name = fields.Char(string='Vendor Name', required=False)
    categ_parent_id = fields.Integer(string='Categorie Parent id', default=0, required=False)
    categ_complete_name = fields.Char(string='Categorie full Name')
    categ_parent_path = fields.Char(string='Categ Parent Path')


    @api.depends('product_id')
    def _compute_product_image(self):
        for record in self:
            record.product_image = record.product_id.image_1920
            
    @api.depends('product_id')
    def _compute_x_timecreateditem(self):
        for record in self:
            if record.product_id:
                record.x_timecreateditem = record.product_id.create_date
            else:
                record.x_timecreateditem = False
    
        
    def get_currency_id_by_code(self, currency_code):
        currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
        _logger.info("currency to is %s", currency.name)
        return currency.id if currency else None
    
    
    def get_conversion_rate(self, from_currency_id, to_currency_id, date_rate: datetime,  amount=1.0):
        #_logger.info('currency_from id is %s', from_currency_id)
        #_logger.info('currency to is %s', to_currency_id)
        from_currency = self.env['res.currency'].browse(from_currency_id)
        to_currency = self.env['res.currency'].browse(to_currency_id)

        if from_currency and to_currency:
            #currency_model = self.env['res.currency']
            #rate = currency_model._get_conversion_rate(from_currency=from_currency, to_currency=to_currency, date=date_rate.date())
            #_logger.info('currency_from is %s', from_currency.name)
            #_logger.info('currency to is %s', to_currency.name)
            rate = from_currency._convert(from_amount=1.0, to_currency=to_currency, company=self.env.company, date=date_rate.date())
            return rate
        return 0.0
    
    @api.depends('product_id', 'currency_id', 'x_lastPurchaseOrderDate')
    def _compute_exchange_rate(self):
        for record in self:
            if record.product_id and record.currency_id and record.x_lastPurchaseOrderDate:
                currency_vuv_id = self.get_currency_id_by_code('VUV')
                if currency_vuv_id:
                    record.X_lastPurchaseExchange = self.get_conversion_rate(from_currency_id=record.currency_id, to_currency_id=currency_vuv_id, amount=1.0, date_rate=record.x_lastPurchaseOrderDate)
                else:
                    record.X_LastPurchasePrice = False
            else:
                record.X_LastPurchasePrice = False
    
    
    def get_po_exchange_rate(self, currency_id: int, po_date: datetime):
        currency_vuv_id = self.get_currency_id_by_code('VUV')   
        if currency_id:
            return self.get_conversion_rate(from_currency_id=currency_id, to_currency_id=currency_vuv_id, amount=1.0, date_rate=po_date)            
        else:
            return 0.0
        
    
    @api.depends('product_id')
    def _compute_product_price(self):
        for record in self:
            if record.product_id and record.product_id.product_tmpl_id and record.product_id.product_tmpl_id.list_price:
                X_SalesPrice = record.product_id.product_tmpl_id.list_price
                
                """
                pricelist = self.env['product.pricelist'].search([('company_id', '=', self.env.company.id)], limit=1)
                if pricelist:
                    price = pricelist._get_product_price(record.product_id, 1.0, self.env.user.partner_id)
                    #get_product_price(record.product_id, 1.0, self.env.user.partner_id)
                    X_SalesPrice = price
                else:
                    X_SalesPrice = 0.0
                """
            else:
                X_SalesPrice = 0.0
            
            product_template = record.product_id.product_tmpl_id
            taxes = product_template.taxes_id
            if taxes:
                record.X_SalesPrice = taxes.compute_all(X_SalesPrice, currency=None, quantity=1.0)['total_included']
            else:
                record.X_SalesPrice = X_SalesPrice
    
    @api.depends('product_id')
    def _compute_copied_product_name(self):
        for record in self:
            if record.product_id:
                record.copied_product_name = record.product_id.display_name
                """
                if record.product_id.default_code and len(record.product_id.default_code) > 0:
                    record.copied_product_name = "[" + record.product_id.default_code + "] " + record.product_id.display_name
                else:
                    record.copied_product_name = record.product_id.display_name
                """
            else:
                record.copied_product_name = ""
    
    @api.depends('product_id')
    def _compute_record_id_value(self):
        for record in self:
            if record.product_id:
                record.record_id_value = record.product_id.id
            else:
                record.record_id_value = 0
            #record.record_id_value = int(record.id) if record.id else 0
    
    
    @api.depends('x_QTYonHand')
    def _compute_stock_and_back_order(self):
        for record in self:
            stock_full = 0
            if record.x_QTYonHand:
                stock_full += record.x_QTYonHand
                
            if record.X_QtyonOrder:
                stock_full += record.X_QtyonOrder
                
            record.stock_and_back_order = stock_full
    
    
    @api.model
    def delete_all_records(self):
        # Search for all records of the model
        records = self.search([])

        # Delete All Records
        records.unlink()
    

    def is_product_favorite(self, product):
        #_logger.info("Your object: %s", product.priority)
        
        if int(product.priority) == 0:
            return False
        else:
            return True


    def _compute_quantity_sold_last_n_days(self, product, days):
        # Calculate the date N days ago
        date_n_days_ago = datetime.now() - timedelta(days=days)

        # Search for sales orders containing the product and created within the last N days
        sales_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),  # Consider only confirmed and done sales orders
            ('order_line.product_id', '=', product.id),
            ('create_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', datetime.now().strftime('%Y-%m-%d 23:59:59'))
        ])
        
        total_quantity_sold = 0
        
        """
        for order in sales_orders:
            invoices = order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            if invoices:
                for line in order.order_line:
                    product_id = line.product_id.id
                    if product_id == product.id:
                        total_quantity_sold += line.product_uom_qty
        """

        # Sum the quantities of the product sold in the matching sales orders
        #total_quantity_sold = sum(order.order_line.filtered(lambda line: line.product_id == product).mapped('product_uom_qty') for order in sales_orders)
        total_quantity_sold = sum(
            sum(line.product_uom_qty for line in order.order_line.filtered(lambda line: line.product_id == product))
            for order in sales_orders
        )
        
        # Search for POS orders containing the product and created within the last N days
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),  # Consider only paid, done, and invoiced POS orders
            ('lines.product_id', '=', product.id),
            ('date_order', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:59:59'))
        ])
        
        # Sum the quantities of the product sold in the matching POS orders
        total_quantity_sold_pos_orders = sum(
            sum(line.qty for line in order.lines.filtered(lambda line: line.product_id == product))
            for order in pos_orders
        )
        
        total_quantity_sold += total_quantity_sold_pos_orders

        
        
        
        #_logger.info("_compute_quantity_sold_last_n_days Product Name is %s", product.name)
        
        total_quantity_sold_2 = 0
        list_id = product.x_cw_list_id
        
        if list_id:
            #_logger.info("_compute_quantity_sold_last_n_days Product list_id is %s", product.x_cw_list_id)
            sales_orders_old = self.env['cw.old.order.line'].search([
                ('x_cw_product_list_id', '=', list_id),
                ('x_cw_order_line_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00'))
            ])
            #_logger.info("Sales orders Old is %s", sales_orders_old)
            total_quantity_sold_2 = sum(order.x_cw_order_line_quantity for order in sales_orders_old)
            #_logger.info("Total Quantity sold is %s", str(total_quantity_sold_2))

        full_total = total_quantity_sold + total_quantity_sold_2
            

        return full_total


    def _compute_quantity_sold_between_n_and_m_days(self, product, days_min, days_max):
        # Calculate the date N days ago
        date_n_days_ago = datetime.now() - timedelta(days=days_max)
        date_n_days_ago_min = datetime.now() - timedelta(days=days_min)

        # Search for sales orders containing the product and created within the last N days
        sales_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),  # Consider only confirmed and done sales orders
            ('order_line.product_id', '=', product.id),
            ('create_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
        ])
        
        """
        total_quantity_sold = 0
        
        for order in sales_orders:
            invoices = order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            if invoices:
                for line in order.order_line:
                    product_id = line.product_id.id
                    if product_id == product.id:
                        total_quantity_sold += line.product_uom_qty
        """
                
        
        # Sum the quantities of the product sold in the matching sales orders
        #total_quantity_sold = sum(order.order_line.filtered(lambda line: line.product_id == product).mapped('product_uom_qty') for order in sales_orders)
        total_quantity_sold = sum(
            sum(line.product_uom_qty for line in order.order_line.filtered(lambda line: line.product_id == product))
            for order in sales_orders
        )
        
        # Search for POS orders containing the product and created within the last N days
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),  # Consider only paid, done, and invoiced POS orders
            ('lines.product_id', '=', product.id),
            ('date_order', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('date_order', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
        ])
        
        # Sum the quantities of the product sold in the matching POS orders
        total_quantity_sold_pos_orders = sum(
            sum(line.qty for line in order.lines.filtered(lambda line: line.product_id == product))
            for order in pos_orders
        )
        
        total_quantity_sold += total_quantity_sold_pos_orders
        
        
        #_logger.info("_compute_quantity_sold_last_n_days Product Name is %s", product.name)
        
        total_quantity_sold_2 = 0
        list_id = product.x_cw_list_id
        
        if list_id:
            #_logger.info("_compute_quantity_sold_last_n_days Product list_id is %s", product.x_cw_list_id)
            sales_orders_old = self.env['cw.old.order.line'].search([
                ('x_cw_product_list_id', '=', list_id),
                ('x_cw_order_line_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
                ('create_date', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
            ])
            #_logger.info("Sales orders Old is %s", sales_orders_old)
            total_quantity_sold_2 = sum(order.x_cw_order_line_quantity for order in sales_orders_old)
            #_logger.info("Total Quantity sold is %s", str(total_quantity_sold_2))

        full_total = total_quantity_sold + total_quantity_sold_2
            

        return full_total



    def _compute_quantity_refund_between_n_and_m_days(self, product, days_min, days_max):
        # Calculate the date N days ago
        date_n_days_ago = datetime.now() - timedelta(days=days_max)
        date_n_days_ago_min = datetime.now() - timedelta(days=days_min)

        # Search for sales orders containing the product and created within the last N days
        sales_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),  # Consider only confirmed and done sales orders
            ('order_line.product_id', '=', product.id),
            ('create_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
        ])

        total_quantity_refund = 0

        for order in sales_orders:
            # Check if the order has been invoiced and has credit notes
            invoices = order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            credit_notes = order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_refund' and inv.state == 'posted')
            
            if invoices and credit_notes:
                for line in order.order_line:
                    product_id = line.product_id.id
                    if product_id == product.id:
                        total_quantity_refund += line.product_uom_qty
                        
        
        # Search for POS orders containing the product and created within the specified date range
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),  # Consider only paid, done, and invoiced POS orders
            ('lines.product_id', '=', product.id),
            ('date_order', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('date_order', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
        ])

        total_quantity_refund_pos_orders = 0

        for order in pos_orders:
            # Check if the order has been refunded
            for line in order.lines:
                if line.product_id.id == product.id and line.qty < 0:  # Negative quantity indicates a refund
                    total_quantity_refund_pos_orders += abs(line.qty)
                    
        total_quantity_refund += total_quantity_refund_pos_orders


        return total_quantity_refund


    def _compute_quantity_quote_between_n_and_m_days(self, product, days_min, days_max):
        # Calculate the date N days ago
        date_n_days_ago = datetime.now() - timedelta(days=days_max)
        date_n_days_ago_min = datetime.now() - timedelta(days=days_min)

        # Search for sales orders containing the product and created within the last N days
        sales_orders = self.env['sale.order'].search([
            ('order_line.product_id', '=', product.id),
            ('create_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
        ])

        # Sum the quantities of the product sold in the matching sales orders
        #total_quantity_sold = sum(order.order_line.filtered(lambda line: line.product_id == product).mapped('product_uom_qty') for order in sales_orders)
        total_quantity_sold = sum(
            sum(line.product_uom_qty for line in order.order_line.filtered(lambda line: line.product_id == product))
            for order in sales_orders
        )
        
        total_quantity_sold_2 = 0
        list_id = product.x_cw_list_id
        
        if list_id:
            #_logger.info("_compute_quantity_sold_last_n_days Product list_id is %s", product.x_cw_list_id)
            sales_orders_old = self.env['cw.old.order.line'].search([
                ('x_cw_product_list_id', '=', list_id),
                ('x_cw_order_line_date', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
                ('create_date', '<=', date_n_days_ago_min.strftime('%Y-%m-%d 23:59:59'))
            ])
            #_logger.info("Sales orders Old is %s", sales_orders_old)
            total_quantity_sold_2 = sum(order.x_cw_order_line_quantity for order in sales_orders_old)
            #_logger.info("Total Quantity sold is %s", str(total_quantity_sold_2))

        full_total = total_quantity_sold + total_quantity_sold_2
            

        return full_total

    def get_archive_n_days(self, product, days):
        date_n_days_ago = datetime.now() - timedelta(days=days)

        # Search for sales orders containing the product and created within the last N days
        return self.env['cw.product.data.daily.archive'].search([
            ('product_id', '=', product.id),
            ('zdate', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('zdate', '<=', date_n_days_ago.strftime('%Y-%m-%d 23:59:59'))
        ], limit=1)


    def _compute_qty_on_hand_day(self, archive):
        if archive and archive.QuantityOnHand:
            return archive.QuantityOnHand
        else:
            return 0

    
    def _compute_qty_on_order_day(self, archive):
        if archive and archive.QuantityOnOrder:
            return archive.QuantityOnOrder
        else:
            return 0


    def get_quantity_ordered_since_n_days(self, product, days):
        date_n_days_ago = datetime.now() - timedelta(days=days)

        """
        purchase_order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            '|',
            ('order_id.state', '=', 'purchase'),
            ('order_id.state', '=', 'done'),
            ('date_order', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:59:59'))
        ])
        """

        purchase_order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['purchase', 'done']),  # Consider only purchase orders in the purchase state
            ('date_order', '>=', date_n_days_ago.strftime('%Y-%m-%d 00:00:00')),
            ('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:59:59'))
        ])

        return sum(line.product_qty - line.qty_received for line in purchase_order_lines)



    def get_quantity_waiting_for_delivery(self, product):
        # Search for purchase order lines containing the product and waiting for delivery
        purchase_order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', '=', 'purchase'),  # Consider only purchase orders in the purchase state
        ])

        # Compute the total quantity waiting for delivery
        total_quantity_waiting = sum(line.product_qty - line.qty_received for line in purchase_order_lines)
        
        total_quantity_waiting_2 = 0
        list_id = product.x_cw_list_id
        day_limit = datetime.now() - timedelta(days=365)
        
        if list_id:
            cw_old_po_order_list = self.env['cw.old.po.order.line'].search([
                ('product_id', '=', product.id),
                ('x_cw_po_line_date', '>=', day_limit.strftime('%Y-%m-%d 00:00:00'))
            ])
            total_po_waiting = sum(po_order.x_cw_po_line_quantity for po_order in cw_old_po_order_list)
            total_po_received = 0
            
            for po_order in cw_old_po_order_list:
                list_delivery = self.env['cw.old.product.delivery'].search([
                    ('x_cw_product_list_id', '=', po_order.x_cw_product_list_id),
                    ('x_cw_po_ref_number', '=', po_order.x_cw_po_ref_number)
                ])
                total_for_po = sum(delivery.x_cw_quantity_received for delivery in list_delivery)
                total_po_received += total_for_po
                
            total_quantity_waiting_2 = total_po_waiting - total_po_received
            
            if total_quantity_waiting_2 < 0:
                total_quantity_waiting_2 = 0

        return total_quantity_waiting + total_quantity_waiting_2

    def get_quantity_in_draft(self, product):
        order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', '=', 'draft'),
        ])

        total_quantity_draft = sum(line.product_qty for line in order_lines)

        return total_quantity_draft



    def get_days_since_last_order(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            # Calculate the number of days since the purchase order was made
            days_since_last_order = (datetime.now() - recent_purchase_order_line.order_id.date_order).days
        else:
            # If no purchase order found, return None or any default value as per your requirement
            days_since_last_order = -1

        return days_since_last_order
    
    
    def get_most_recent_purchase_order_old_data(self, product):
        list_id = product.x_cw_list_id
        
        recent_purchase_order = self.env['cw.old.po.order.line'].search([
            ('x_cw_product_list_id', '=', list_id),
        ], order='x_cw_po_line_date desc', limit=1)
        
        if recent_purchase_order:
            return recent_purchase_order
        
        return
    
    
    def get_days_since_last_order_old_data(self, recent_purchase_order):
        if recent_purchase_order: 
            day_since_last_order = (datetime.now() - recent_purchase_order.x_cw_po_line_date).days
        else:
            day_since_last_order = -1
            
        return day_since_last_order



    def get_days_since_last_delivery(self, product):
        recent_delivery_order_line = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only delivery orders in the done state
            ('purchase_line_id', '!=', False),
            #('picking_id.picking_type_id.code', '=', 'outgoing'),  # Consider only outgoing deliveries
        #], order='picking_id.date_done desc', limit=1)
        ], order='date desc', limit=1)

        if recent_delivery_order_line:
            #days_since_last_delivery = (datetime.now() - recent_delivery_order_line.picking_id.date_done).days
            days_since_last_delivery = (datetime.now() - recent_delivery_order_line.date).days
        else:
            # If no delivery order found, return None or any default value as per your requirement
            days_since_last_delivery = -1
            
        list_id = product.x_cw_list_id
        days_since_last_delivery_2 = -1
        
        if list_id:
            recent_delivery_po_order_old = self.env['cw.old.product.delivery'].search([
                ('x_cw_product_list_id', '=', list_id),
            ], order="x_cw_received_date desc", limit=1)
            
            if recent_delivery_po_order_old:
                days_since_last_delivery_2 = (datetime.now() - recent_delivery_po_order_old.x_cw_received_date).days
        
        if (days_since_last_delivery_2 >= 0 and days_since_last_delivery >= 0 and days_since_last_delivery_2 < days_since_last_delivery) or (days_since_last_delivery_2 >= 0 and days_since_last_delivery == -1) :
            return days_since_last_delivery_2
            
        return days_since_last_delivery
    
    def get_last_delivery_date(self, product):
        recent_delivery_order_line = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only delivery orders in the done state
            ('purchase_line_id', '!=', False),
            #('picking_id.picking_type_id.code', '=', 'outgoing'),  # Consider only outgoing deliveries
        #], order='picking_id.date_done desc', limit=1)
        ], order='date desc', limit=1)

        if recent_delivery_order_line:
            #days_since_last_delivery = (datetime.now() - recent_delivery_order_line.picking_id.date_done).days
            days_since_last_delivery = (datetime.now() - recent_delivery_order_line.date).days
        else:
            # If no delivery order found, return None or any default value as per your requirement
            days_since_last_delivery = -1
            
        list_id = product.x_cw_list_id
        days_since_last_delivery_2 = -1
        
        if list_id:
            recent_delivery_po_order_old = self.env['cw.old.product.delivery'].search([
                ('x_cw_product_list_id', '=', list_id),
            ], order="x_cw_received_date desc", limit=1)
            
            if recent_delivery_po_order_old:
                days_since_last_delivery_2 = (datetime.now() - recent_delivery_po_order_old.x_cw_received_date).days
        
        if (days_since_last_delivery_2 >= 0 and days_since_last_delivery >= 0 and days_since_last_delivery_2 < days_since_last_delivery) or (days_since_last_delivery_2 >= 0 and days_since_last_delivery == -1) :
            return recent_delivery_po_order_old.x_cw_received_date
            
        return recent_delivery_order_line.date
    
    
    def get_last_delivery_qty(self, product):
        recent_delivery_order_line = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only delivery orders in the done state
            ('purchase_line_id', '!=', False),
        ], order='date desc', limit=1)
        
        if recent_delivery_order_line:
            return recent_delivery_order_line.product_uom_qty
        else:
            return 0

    
    def get_most_recent_purchase_order_vendor(self, product):
        order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            #('order_id.state', 'in', ['draft', 'done']),
            ('order_id.state', 'in', ['purchase', 'done']),  # Consider purchase orders in purchase or done state
        ])

        # Extract the distinct purchase orders from those lines
        purchase_orders = order_lines.mapped('order_id')

        # Sort the purchase orders by the date_order in descending order and take the first
        most_recent_purchase_order = purchase_orders.sorted(key=lambda r: r.date_order, reverse=True)[:1]

        return most_recent_purchase_order.partner_id.name
        
        

    def get_most_recent_purchase_order_line(self, product):
        order_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            #('order_id.state', 'in', ['draft', 'done']),
            ('order_id.state', 'in', ['purchase', 'done']),  # Consider purchase orders in purchase or done state
        ])

        # Extract the distinct purchase orders from those lines
        purchase_orders = order_lines.mapped('order_id')

        # Sort the purchase orders by the date_order in descending order and take the first
        most_recent_purchase_order = purchase_orders.sorted(key=lambda r: r.date_order, reverse=True)[:1]

        if most_recent_purchase_order:
            po_id = most_recent_purchase_order.id
            first_order_line2 = self.env['purchase.order.line'].search([
                ('product_id', '=', product.id),
                ('order_id', '=', po_id)
            ], limit=1)
            return first_order_line2
        else:
            return 
        

    def get_quantity_from_last_purchase_order(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            # Retrieve the quantity ordered in the purchase order line
            quantity_from_last_purchase_order = recent_purchase_order_line.product_qty
        else:
            # If no purchase order found, return None or any default value as per your requirement
            quantity_from_last_purchase_order = None

        return quantity_from_last_purchase_order
    
    
    def get_quantity_from_last_purchase_order_old_data(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            return recent_purchase_order_line.x_cw_po_line_quantity
        
        return None


    
    def get_unit_purchase_amount_from_last_purchase_order(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            # Retrieve the unit purchase amount (price) from the purchase order line
            unit_purchase_amount = recent_purchase_order_line.price_unit
        else:
            # If no purchase order found, return None or any default value as per your requirement
            unit_purchase_amount = None

        return unit_purchase_amount
    
    
    def get_unit_purchase_amount_from_last_purchase_order_old_data(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            return recent_purchase_order_line.x_cw_po_line_quantity
        
        return None

    

    def get_currency_from_last_purchase_order(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            # Retrieve the currency from the purchase order
            currency = recent_purchase_order_line.order_id.currency_id
        else:
            # If no purchase order found, return None or any default value as per your requirement
            currency = None

        return currency
    
    def get_currency_from_last_purchase_order_old_data(self, recent_purchase_order_line):
        if recent_purchase_order_line:
            return recent_purchase_order_line.x_cw_currency_id
        
        return None
            

    
    def get_days_since_last_stock_take(self, product):
        # Search for the most recent stock move related to the product
        recent_stock_move = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only stock moves in the done state
        ], order='date desc', limit=1)

        if recent_stock_move:
            # Retrieve the date of the associated stock inventory
            #last_stock_take_date = recent_stock_move.inventory_id.date
            last_stock_take_date = recent_stock_move.picking_id.date

            if recent_stock_move.picking_id.date:
                # Calculate the number of days since the stock take was done
                #days_since_last_stock_take = (fields.Date.today() - last_stock_take_date).days
                days_since_last_stock_take = (datetime.now() - last_stock_take_date).days
            else:
                days_since_last_stock_take = -1
        else:
            # If no stock move found, return None or any default value as per your requirement
            days_since_last_stock_take = -1

        return days_since_last_stock_take
    
    
    def get_last_stock_take_date(self, product):
        # Search for the most recent stock move related to the product
        recent_stock_move = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only stock moves in the done state
        ], order='date desc', limit=1)

        if recent_stock_move:
            if recent_stock_move.picking_id.date:
                return recent_stock_move.picking_id.date

        return False
    
    
    def get_days_since_last_stock_take_old_data(self, product):
        days_since_last_stock_take = -1
        list_id = product.x_cw_list_id
    
        if list_id:
            stock_take = self.env['cw.old.stock.take'].search([
                ('x_cw_product_list_id', '=', list_id)
            ], order='x_cw_stock_take_date desc', limit=1)
            
            if stock_take:
                days_since_last_stock_take = (datetime.now() - stock_take.x_cw_stock_take_date).days
                
        return days_since_last_stock_take
    
    
    def get_last_stock_take_old_data_date(self, product):
        list_id = product.x_cw_list_id
    
        if list_id:
            stock_take = self.env['cw.old.stock.take'].search([
                ('x_cw_product_list_id', '=', list_id)
            ], order='x_cw_stock_take_date desc', limit=1)
            
            if stock_take and stock_take.x_cw_stock_take_date:
                return stock_take.x_cw_stock_take_date
                
        return False
    

    def get_stock_take_discrepancy(self, product):
        # Search for the most recent stock move related to the product
        recent_stock_move = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),  # Consider only stock moves in the done state
        ], order='date desc', limit=1)

        if recent_stock_move:
            # Retrieve the associated stock inventory
            last_inventory = recent_stock_move.picking_id
            #last_inventory = recent_stock_move.inventory_id
            # Calculate the discrepancy between expected and actual quantities
            discrepancy = sum(
                line.inventory_diff_quantity
                for line in last_inventory.move_line_ids.quant_id
            )
        else:
            # If no stock move found, return None or any default value as per your requirement
            discrepancy = 0

        return discrepancy


    def get_unique_customers_last_x_days(self, product, days=30):
        # Calculate the date X days ago
        date_x_days_ago = fields.Date.today() - timedelta(days=days)

        # Search for sale orders containing the product within the past X days
        sale_orders = self.env['sale.order'].search([
            ('state', '=', 'sale'),  # Consider only confirmed sale orders
            ('order_line.product_id', '=', product.id),
            #('confirmation_date', '>=', date_x_days_ago),
            ('date_order', '>=', date_x_days_ago),
        ])

        # Get unique customers from the sale orders
        unique_customers = sale_orders.mapped('partner_id')
        #_logger.info("unique_customers len is %s", len(unique_customers))
        
        set_unique_1 = set(unique_customers)
        #_logger.info("set_unique_1 is %s", set_unique_1)
        
        #partner_ids = [partner.id for partner in set_unique_1]
        
        
        if len(set_unique_1) > 0:
            #partner_ids = list(set_unique_1)
            partner_ids = [partner.id for partner in unique_customers]  # Ensure this is a list of IDs
            #_logger.info("Partner_ids is %s", partner_ids)
            partners = self.env['res.partner'].search([
                ('id', 'in', partner_ids)
            ])
            
            unique_customers_list_id = partners.mapped('x_cw_list_id')
        
            """
            _logger.info("Unique Customers is %s", unique_customers)
            
            unique_customers_list_id = [customer.x_cw_list_id for customer in unique_customers]
            
            _logger.info("unique_customers_list_id is %s", unique_customers_list_id)

            # Count the number of unique customers
            num_unique_customers = len(unique_customers)
            
            
            _logger.info("list_id is  %s", list_id)
            
            unique_customers_for_old_data = self.env['cw.old.order.line'].search([
                ('x_cw_product_list_id', '=', list_id),
                ('x_cw_order_line_date', '>=', date_x_days_ago),
                ('x_cw_order_customer_list_id', '!=', False)
            ]).read_group(
                [],
                ['x_cw_order_customer_list_id'], # Group by the field you want to get unique values for
                ['x_cw_order_customer_list_id']  # Specify the fields you want to read
            )
            """
            list_id = product.x_cw_list_id
        
            if list_id:
                unique_customers_for_old_query = self.env['cw.old.order.line'].search([
                    ('x_cw_product_list_id', '=', list_id),
                    ('x_cw_order_line_date', '>=', date_x_days_ago),
                    ('x_cw_order_customer_list_id', '!=', False)
                ])
                
                unique_customers_for_old_data = unique_customers_for_old_query.mapped('x_cw_order_customer_list_id')
                
                # Convert arrays to sets
                set1 = set(unique_customers_list_id)
                set2 = set(unique_customers_for_old_data)
                
                shared_entries = set1.intersection(set2)
                
                nb_common = len(shared_entries)

                return len(set_unique_1) + len(set2) - nb_common
        
        return len(set_unique_1)


    @api.model
    def scheduler_job_to_run(self):
        self.delete_all_records()
        
        tracking_offset = self.env['cw.ocm.forecast.cron.track'].search([], limit=1, order='create_date desc')
        if not tracking_offset:
            tracking_offset = self.env['cw.ocm.forecast.cron.track'].create({
                        'offset_start': 0, 
                        'last_starting_time': datetime.now()
                    })
        else:
            tracking_offset.write({
                        'offset_start': 0, 
                        'last_starting_time': datetime.now()
                    })
        
        self.process_all_products()
    
    
    @api.model
    def scheduler_job_to_run_continue(self):
        self.process_all_products()

    def _get_cron_action(self, model_id:int, cron_code):
        actions = self.env['ir.actions.server'].search([
                ('model_id', '=', model_id),
                ('code', '=', cron_code)
            ])
        
        for action in actions:
            cron_job = self.env['ir.cron'].search([('ir_actions_server_id', '=', action.id)], limit=1)
            if cron_job:
                return cron_job
        
        return False
        
        
    @api.model
    def call_scheduler_job_to_run_continue(self):
        cron_model_id = self.env['ir.model'].search([('model', '=', 'cw.ocm.forecast')], limit=1).id
        cron_code = 'model.scheduler_job_to_run_continue()'
        
        #existing_cron = self.env['ir.cron'].search([('model_id', '=', cron_model_id), ('code', '=', cron_code)], limit=1)
        existing_cron = self._get_cron_action(model_id=cron_model_id, cron_code=cron_code)
        #next_call_time = datetime.now() + timedelta(seconds=10)
        next_call_time = datetime.now()
        
        if existing_cron:
            # If cron job exists, reschedule it
            existing_cron.write({'nextcall': next_call_time})
        """
        else:
            _logger.info("FALSE call_scheduler_job_to_run_continue %s et cron_code is %s and it's %s", cron_model_id, cron_code, existing_cron)
            # If cron job does not exist, create a new one
            cron = self.env['ir.cron'].create({
                'name': 'CW Forecast Running - Continuing',
                'model_id': cron_model_id,
                'state': 'code',
                'code': cron_code,
                'interval_number': 1000,
                'interval_type': 'days',
                'numbercall': 1,
                'nextcall': next_call_time,
            })
            _logger.info(f'New cron job Continue scheduled: {cron.name} to run at {next_call_time}')
        """
        
    @api.model
    def get_tag_ids_from_names(self, tag_names):
        tags = self.env['product.tag'].search([('name', 'in', tag_names)])
        return tags.ids

    @api.model
    def process_all_products(self):
        batch_size = 300
        tag_names = ['seller refurbished']
        tag_ids = self.get_tag_ids_from_names(tag_names)
        templates = self.env['product.template'].search([
            ('product_tag_ids', 'not in', tag_ids)
        ])
        
        tracking_offset = self.env['cw.ocm.forecast.cron.track'].search([], limit=1, order='create_date desc')
        if not tracking_offset:
            tracking_offset.create(
                    {
                        'offset_start': 0, 
                        'last_starting_time': datetime.now()
                    })
        
        offset = tracking_offset.offset_start
        
        if offset == 0:
            tracking_offset.write(
                    {
                        'offset_start': 0,
                        'last_starting_time': datetime.now()
                    })
        
        product_model = self.env['product.product']
        total_products = product_model.search_count([
                ('type', '=', 'product'),
                ('product_tmpl_id', 'in', templates.ids),
                '|',  # Logical OR operator
                ('active', '=', True),
                ('active', '=', False)
            ])
        
        #while offset < total_products:
        if offset < total_products:
            # Retrieve products per batch
            products = product_model.search([
                    ('type', '=', 'product'),
                    ('product_tmpl_id', 'in', templates.ids),
                    '|',  # Logical OR operator
                    ('active', '=', True),
                    ('active', '=', False)
                ], limit=batch_size, offset=offset)

            for product in products:
                self.process_product(product)
            
            self.env.cr.commit()
            _logger.info(f"Commited batch starting at offset {offset}")
            offset += batch_size
            tracking_offset.write({'offset_start': offset})
            
            cron_model_id = self.env['ir.model'].search([('model', '=', 'cw.ocm.forecast')], limit=1).id
            cron_code = 'model.call_scheduler_job_to_run_continue()'
            
            #existing_cron = self.env['ir.cron'].search([('model_id', '=', cron_model_id), ('code', '=', cron_code)], limit=1)
            existing_cron = self._get_cron_action(model_id=cron_model_id, cron_code=cron_code)
            #next_call_time = datetime.now() + timedelta(seconds=15)
            next_call_time = datetime.now()
            
            if existing_cron:
                # If cron job exists, reschedule it
                existing_cron.write({'nextcall': next_call_time})
                _logger.info(f'Existing cron job rescheduled: {existing_cron.name} to run at {next_call_time}')
                _logger.info("Forecast Report Cron Reschedules")
        else:
            tracking_offset.write({'offset_start': 0})
            _logger.info("All batches Forecast Report processed successfully")
            

    def get_category_full_name(self, categ_id, category_names):
        category_names.append(categ_id.name)
        if categ_id.parent_id:
            return self.get_category_full_name(categ_id=categ_id.parent_id, category_names=category_names)
        else:
            return ' / '.join(reversed(category_names))
        
    def get_category_parent_id(self, product):
        if product.categ_id.parent_id:
            return product.categ_id.parent_id
        else:
            return False

    
    def compute_full_name(self, product):
        category_names = []
        return self.get_category_full_name(categ_id=product.categ_id, category_names=category_names) + ' / ' + product.name
    
    
    def compute_categ_path(self, categ_id):
        category_path = []
        return self.get_category_full_name(categ_id=categ_id, category_names=category_path)
    
    
    def get_category_full_path(self, categ_id, category_path):
        category_path.append(categ_id.id)
        if categ_id.parent_id:
            return self.get_category_full_path(categ_id=categ_id.parent_id, category_names=category_path)
        else:
            return '/'.join(reversed(category_path))

    
    @api.model
    def process_product(self, product):
        X_Invoice30days = self._compute_quantity_sold_last_n_days(product, 30)
        X_Invoice60Days = self._compute_quantity_sold_last_n_days(product, 60)
        X_Invoice90days = self._compute_quantity_sold_last_n_days(product, 90)
        x_invoice120days = self._compute_quantity_sold_last_n_days(product, 120)
        x_Invoice180days = self._compute_quantity_sold_last_n_days(product, 180)
        X_invoice365days = self._compute_quantity_sold_last_n_days(product, 365)
        SoldinBetween0n30 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=0, days_max=30)
        SoldinBetween30n60 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=30, days_max=60)
        SoldInBetween60n90 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=60, days_max=90)
        SoldInBetween90n120 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=90, days_max=120)
        SoldInBetween120n180 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=120, days_max=180)
        SoldInBetween180n365 = self._compute_quantity_sold_between_n_and_m_days(product=product, days_min=180, days_max=365)

        NumberofQuotes0n30 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=0, days_max=30)
        NumberofQuotes30n60 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=30, days_max=60)
        NumberofQuotes60n90 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=60, days_max=90)
        NumberofQuotes90n120 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=90, days_max=120)
        NumberofQuotes120n180 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=120, days_max=180)
        NumberofQuotes180n365 = self._compute_quantity_quote_between_n_and_m_days(product=product, days_min=180, days_max=365)

        NumberofRefunds0n30 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=0, days_max=30)
        NumberofRefunds30n60 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=30, days_max=60)
        NumberofRefunds60n90 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=60, days_max=90)
        NumberofRefunds90n120 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=90, days_max=120)
        NumberofRefunds120n180 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=120, days_max=180)
        NumberofRefunds180n365 = self._compute_quantity_refund_between_n_and_m_days(product=product, days_min=180, days_max=365)

        if X_Invoice30days > 0:
            X_unique30 = self.get_unique_customers_last_x_days(product, 30)
            X_unique30percent = round((X_unique30 /  X_Invoice30days) * 100, 0)
        else:
            X_unique30 = 0
            X_unique30percent = 0
            
        if X_Invoice60Days > 0:
            X_unique60 = self.get_unique_customers_last_x_days(product, 60)
            X_unique60percent = round((X_unique60 /  X_Invoice60Days) * 100, 0)
        else:
            X_unique60 = 0
            X_unique60percent = 0
            
        if X_Invoice90days > 0:
            X_unique90 = self.get_unique_customers_last_x_days(product, 90)
            X_unique90percent = round((X_unique90 / X_Invoice90days) * 100, 0)
        else:
            X_unique90 = 0
            X_unique90percent = 0
            
        if x_invoice120days > 0:
            X_unique120 = self.get_unique_customers_last_x_days(product, 120)
            X_unique120percent = round((X_unique120 / x_invoice120days) * 100, 0)
        else:
            X_unique120 = 0
            X_unique120percent = 0
            
        if x_Invoice180days > 0:
            X_unique180 = self.get_unique_customers_last_x_days(product, 90)
            X_unique180percent = round((X_unique180 / x_Invoice180days) * 100, 0)
        else:
            X_unique180 = 0
            X_unique180percent = 0
            
        if X_invoice365days > 0:
            x_unique365 = self.get_unique_customers_last_x_days(product, 365)
            X_unique365percent = round((x_unique365 / X_invoice365days) * 100, 0)
        else:
            x_unique365 = 0
            X_unique365percent = 0
            
        combined_30_days = str(int(X_Invoice30days)) + " (" + str(X_unique30percent) + "%)"  
        combined_60_days = str(int(X_Invoice60Days)) + " (" + str(X_unique60percent) + "%)" 
        combined_90_days = str(int(X_Invoice90days)) + " (" + str(X_unique90percent) + "%)" 
        combined_120_days = str(int(x_invoice120days)) + " (" + str(X_unique120percent) + "%)" 
        combined_180_days = str(int(x_Invoice180days)) + " (" + str(X_unique180percent) + "%)" 
        combined_365_days = str(int(X_invoice365days)) + " (" + str(X_unique365percent) + "%)"  
        

        nb_days_last_delivery = self.get_days_since_last_delivery(product)
        x_lastReceivedTime = self.get_last_delivery_date(product)
        recent_purchase_order_line = self.get_most_recent_purchase_order_line(product)
        recent_purchase_order_line_old_data = self.get_most_recent_purchase_order_old_data(product)
        
        if recent_purchase_order_line_old_data:
            if recent_purchase_order_line and recent_purchase_order_line.order_id.date_order:
                if recent_purchase_order_line_old_data.x_cw_po_line_date > recent_purchase_order_line.order_id.date_order:
                    nb_days_last_po = self.get_days_since_last_order_old_data(recent_purchase_order_line_old_data)
                    X_lastpurchaseOrderQTY = self.get_quantity_from_last_purchase_order_old_data(recent_purchase_order_line_old_data)
                    X_LastPurchasePrice = self.get_unit_purchase_amount_from_last_purchase_order_old_data(recent_purchase_order_line_old_data)
                    x_LastPOnum = recent_purchase_order_line_old_data.x_cw_po_ref_number
                    x_VendorName = recent_purchase_order_line_old_data.x_cw_old_partner_id.name
                    x_lastPurchaseOrderDate = recent_purchase_order_line_old_data.x_cw_po_line_date
                    if recent_purchase_order_line_old_data.x_cw_currency_id:
                        currency_id = recent_purchase_order_line_old_data.x_cw_currency_id.id
                    else:
                        currency_id = None
                else:
                    nb_days_last_po = self.get_days_since_last_order(recent_purchase_order_line)
                    X_lastpurchaseOrderQTY = self.get_quantity_from_last_purchase_order(recent_purchase_order_line)
                    X_LastPurchasePrice = self.get_unit_purchase_amount_from_last_purchase_order(recent_purchase_order_line) 
                    currency_id = self.get_currency_from_last_purchase_order(recent_purchase_order_line)
                    x_LastPOnum = recent_purchase_order_line.order_id.name
                    x_VendorName = recent_purchase_order_line.order_id.partner_id.name
                    x_lastPurchaseOrderDate = recent_purchase_order_line.order_id.date_order
            else:
                nb_days_last_po = self.get_days_since_last_order_old_data(recent_purchase_order_line_old_data)
                X_lastpurchaseOrderQTY = self.get_quantity_from_last_purchase_order_old_data(recent_purchase_order_line_old_data)
                X_LastPurchasePrice = self.get_unit_purchase_amount_from_last_purchase_order_old_data(recent_purchase_order_line_old_data)
                x_LastPOnum = recent_purchase_order_line_old_data.x_cw_po_ref_number
                x_VendorName = recent_purchase_order_line_old_data.x_cw_old_partner_id.name
                x_lastPurchaseOrderDate = recent_purchase_order_line_old_data.x_cw_po_line_date
                if recent_purchase_order_line_old_data.x_cw_currency_id:
                    currency_id = recent_purchase_order_line_old_data.x_cw_currency_id.id
                else:
                    currency_id = None
        else:
            if recent_purchase_order_line:
                nb_days_last_po = self.get_days_since_last_order(recent_purchase_order_line)
                X_lastpurchaseOrderQTY = self.get_quantity_from_last_purchase_order(recent_purchase_order_line)
                X_LastPurchasePrice = self.get_unit_purchase_amount_from_last_purchase_order(recent_purchase_order_line) 
                currency_id = self.get_currency_from_last_purchase_order(recent_purchase_order_line)
                x_LastPOnum = recent_purchase_order_line.order_id.name
                x_VendorName = recent_purchase_order_line.order_id.partner_id.name
                x_lastPurchaseOrderDate = recent_purchase_order_line.order_id.date_order
            else:
                nb_days_last_po = -1
                X_lastpurchaseOrderQTY = 0
                X_LastPurchasePrice = 0
                currency_id = False
                x_LastPOnum = False
                x_VendorName = False
                x_lastPurchaseOrderDate = False
                    
                    
        nb_since_last_stocktake = self.get_days_since_last_stock_take(product)
        nb_since_last_stocktake_2 = self.get_days_since_last_stock_take_old_data(product)
        
        if (nb_since_last_stocktake_2 >= 0 and nb_since_last_stocktake >= 0 and nb_since_last_stocktake_2 < nb_since_last_stocktake) or (nb_since_last_stocktake_2 >= 0 and nb_since_last_stocktake == -1):
            nb_since_last_stocktake = nb_since_last_stocktake_2
            list_id = product.x_cw_list_id
            stock_take = self.env['cw.old.stock.take'].search([
                    ('x_cw_product_list_id', '=', list_id)
                ], order='x_cw_stock_take_date desc', limit=1)
            X_stockTakeOffby = stock_take.x_cw_stock_take_difference
            is_stock_take_correct = stock_take.x_cw_stock_take_ok
            X_StockTakedate = self.get_last_stock_take_old_data_date(product)
        else:
            X_stockTakeOffby = self.get_stock_take_discrepancy(product)
            X_StockTakedate = self.get_last_stock_take_date(product)
            if X_stockTakeOffby > 0 :
                is_stock_take_correct = False
            else:
                is_stock_take_correct = True
        
        

        X_isactive = product.sale_ok or product.purchase_ok

        categ_id = product.categ_id.id
        
        vendors = product.seller_ids.sorted('sequence')

        new_seller_ids = []
        for seller_info in vendors:
            new_seller_ids.append(seller_info.partner_id.id)


        #seller_ids = new_seller_ids
        seller_ids = [(6, 0, new_seller_ids)]

        AppearsInTargetItems = self.is_product_favorite(product)
        
        
        x_QTYonHand = product.qty_available
        X_QtyonOrder = self.get_quantity_waiting_for_delivery(product)
        in_draft_order = self.get_quantity_in_draft(product)

        qty_on_hand = x_QTYonHand + X_QtyonOrder

        OrderRecommend90 = X_Invoice90days - qty_on_hand
        OrderRecommend120 = x_invoice120days - qty_on_hand
        OrderRecommend180 = x_Invoice180days - qty_on_hand
        OrderRecommend365 = X_invoice365days - qty_on_hand

        if OrderRecommend90 > 0 : 
            should_be_ordered = True
        else :
            should_be_ordered = False
            OrderRecommend90 = 0

        sale90days_by_2 = X_Invoice90days * 2
        sale30days_by_3 = X_Invoice30days * 3

        should_be_deleted = False
        is_dead_stock = False
        stock_selling_status = 'OK'

        if qty_on_hand > 0 and (nb_days_last_delivery > 100 or nb_days_last_delivery < 0) and sale90days_by_2 >= qty_on_hand :
            stock_selling_status = 'OK'
        elif qty_on_hand > 0 and (nb_days_last_delivery > 100 or nb_days_last_delivery < 0) and sale90days_by_2 < qty_on_hand and  X_isactive :
            selling_ratio = sale90days_by_2/qty_on_hand

            if selling_ratio >= 0.75 :
                stock_selling_status = 'Slow'
            elif selling_ratio >= 0.5 :
                stock_selling_status = 'Very Slow'
            else :
                stock_selling_status = 'Very Dead'
                should_be_deleted = True
                is_dead_stock = True
        
        elif qty_on_hand > 0 and (nb_days_last_delivery > 45 or nb_days_last_delivery < 0) and sale30days_by_3 < qty_on_hand and X_isactive :
            selling_ratio_2 = sale30days_by_3/qty_on_hand

            if selling_ratio_2 >= 0.75 :
                stock_selling_status = 'Slow'
            elif selling_ratio_2 >= 0 :
                stock_selling_status = 'Very Slow'
            else :
                stock_selling_status = 'Dead'
                is_dead_stock = True
        
        x_lastReceivedQTY = self.get_last_delivery_qty(product)

        
        record_values = {}
        product_tmpl = product.product_tmpl_id
        if product.x_cw_list_id and len(product.x_cw_list_id) > 5:
            record_values['x_ListID'] = product.x_cw_list_id
        elif 'x_studio_cw_listid' in product_tmpl._fields and product_tmpl.x_studio_cw_listid and len(product_tmpl.x_studio_cw_listid) > 0:
            record_values['x_ListID'] = product_tmpl.x_studio_cw_listid
            
        record_values['x_FullName'] = self.compute_full_name(product=product)
        record_values['x_salesdesc'] = product.product_tmpl_id.description_sale
        
        if product.product_tmpl_id and product.product_tmpl_id.standard_price:
            record_values['X_purchasecost'] = product.product_tmpl_id.standard_price

        
        archive_30_days = self.get_archive_n_days(product=product, days=30)
        archive_60_days = self.get_archive_n_days(product=product, days=60)
        archive_90_days = self.get_archive_n_days(product=product, days=90)
        archive_120_days = self.get_archive_n_days(product=product, days=120)
        archive_180_days = self.get_archive_n_days(product=product, days=180)
        archive_365_days = self.get_archive_n_days(product=product, days=365)

        NumberofPurchaseOrdersQTY = self.get_quantity_ordered_since_n_days(product=product, days=60)

        x_PurchaseOrder30 = self.get_quantity_ordered_since_n_days(product=product, days=30)
        x_PurchaseOrder60 = self.get_quantity_ordered_since_n_days(product=product, days=60)
        x_PurchaseOrder90 = self.get_quantity_ordered_since_n_days(product=product, days=90)
        x_PurchaseOrder120 = self.get_quantity_ordered_since_n_days(product=product, days=120)
        x_PurchaseOrder180 = self.get_quantity_ordered_since_n_days(product=product, days=180)
        x_PurchaseOrder365 = self.get_quantity_ordered_since_n_days(product=product, days=365)
        
        
        record_values['product_id'] = product.id
        record_values['categ_id'] = categ_id
        record_values['barcode'] = product.product_tmpl_id.barcode
        
        category_names = []
        categ_full_name = self.get_category_full_name(categ_id=product.categ_id, category_names=category_names)
        record_values['category_name'] = product.categ_id.name
        record_values['categ_complete_name'] = categ_full_name
        
        categ_parent_id = self.get_category_parent_id(product=product)
        
        if categ_parent_id:
            record_values['categ_parent_id'] = categ_parent_id.id
            categ_parent_path = self.compute_categ_path(categ_id=categ_parent_id)
            record_values['categ_parent_path'] = categ_parent_path
        else:
            record_values['categ_parent_id'] = 0
            
        record_values['seller_ids'] = seller_ids
        record_values['X_Invoice30days'] = X_Invoice30days
        record_values['X_Invoice60Days'] = X_Invoice60Days
        record_values['X_Invoice90days'] = X_Invoice90days
        record_values['x_invoice120days'] = x_invoice120days
        record_values['x_Invoice180days'] = x_Invoice180days
        record_values['X_invoice365days'] = X_invoice365days

        record_values['x_qtyonhand30'] = self._compute_qty_on_hand_day(archive=archive_30_days)
        record_values['x_qtyonhand60'] = self._compute_qty_on_hand_day(archive=archive_60_days)
        record_values['x_qtyonhand90'] = self._compute_qty_on_hand_day(archive=archive_90_days)
        record_values['x_qtyonhand120'] = self._compute_qty_on_hand_day(archive=archive_120_days)
        record_values['X_qtyonhand180'] = self._compute_qty_on_hand_day(archive=archive_180_days)
        record_values['x_qtyonhand365'] = self._compute_qty_on_hand_day(archive=archive_365_days)


        record_values['x_qtyonorder30'] = self._compute_qty_on_order_day(archive=archive_30_days)
        record_values['x_qtyonorder60'] = self._compute_qty_on_order_day(archive=archive_60_days)
        record_values['x_qtyonorder90'] = self._compute_qty_on_order_day(archive=archive_90_days)
        record_values['x_qtyonorder120'] = self._compute_qty_on_order_day(archive=archive_120_days)
        record_values['x_qtyonorder180'] = self._compute_qty_on_order_day(archive=archive_180_days)
        record_values['x_qtyonorder365'] = self._compute_qty_on_order_day(archive=archive_365_days)

        record_values['NumberofPurchaseOrdersQTY'] = NumberofPurchaseOrdersQTY

        record_values['x_PurchaseOrder30'] = x_PurchaseOrder30
        record_values['x_PurchaseOrder60'] = x_PurchaseOrder60
        record_values['x_PurchaseOrder90'] = x_PurchaseOrder90
        record_values['x_PurchaseOrder120'] = x_PurchaseOrder120
        record_values['x_PurchaseOrder180'] = x_PurchaseOrder180
        record_values['x_PurchaseOrder365'] = x_PurchaseOrder365


        record_values['SoldinBetween0n30'] = SoldinBetween0n30
        record_values['SoldinBetween30n60'] = SoldinBetween30n60
        record_values['SoldInBetween60n90'] = SoldInBetween60n90
        record_values['SoldInBetween90n120'] = SoldInBetween90n120
        record_values['SoldInBetween120n180'] = SoldInBetween120n180
        record_values['SoldInBetween180n365'] = SoldInBetween180n365

        record_values['NumberofQuotes0n30'] = NumberofQuotes0n30
        record_values['NumberofQuotes30n60'] = NumberofQuotes30n60
        record_values['NumberofQuotes60n90'] = NumberofQuotes60n90
        record_values['NumberofQuotes90n120'] = NumberofQuotes90n120
        record_values['NumberofQuotes120n180'] = NumberofQuotes120n180
        record_values['NumberofQuotes180n365'] = NumberofQuotes180n365

        record_values['NumberofRefunds0n30'] = NumberofRefunds0n30
        record_values['NumberofRefunds30n60'] = NumberofRefunds30n60
        record_values['NumberofRefunds60n90'] = NumberofRefunds60n90
        record_values['NumberofRefunds90n120'] = NumberofRefunds90n120
        record_values['NumberofRefunds120n180'] = NumberofRefunds120n180
        record_values['NumberofRefunds180n365'] = NumberofRefunds180n365

        record_values['x_QTYonHand'] = x_QTYonHand
        record_values['X_QtyonOrder'] = X_QtyonOrder
        record_values['in_draft_order'] = in_draft_order
        record_values['X_unique30'] = X_unique30
        record_values['X_unique60'] = X_unique60
        record_values['X_unique90'] = X_unique90
        record_values['X_unique120'] = X_unique120
        record_values['X_unique180'] = X_unique180
        record_values['x_unique365'] = x_unique365
        record_values['X_unique30percent'] = X_unique30percent
        record_values['X_unique60percent'] = X_unique60percent
        record_values['X_unique90percent'] = X_unique90percent
        record_values['X_unique120percent'] = X_unique120percent
        record_values['X_unique180percent'] = X_unique180percent
        record_values['X_unique365percent'] = X_unique365percent
        record_values['x_VendorName'] = x_VendorName
        record_values['x_LastPOnum'] = x_LastPOnum
        record_values['x_lastPurchaseOrderDate'] = x_lastPurchaseOrderDate
        record_values['x_lastReceivedTime'] = x_lastReceivedTime
        record_values['x_lastReceivedQTY'] = x_lastReceivedQTY
        record_values['nb_days_last_delivery'] = nb_days_last_delivery
        record_values['nb_days_last_po'] = nb_days_last_po
        record_values['X_lastpurchaseOrderQTY'] = X_lastpurchaseOrderQTY
        record_values['nb_since_last_stocktake'] = nb_since_last_stocktake
        record_values['is_stock_take_correct'] = is_stock_take_correct
        record_values['X_stockTakeOffby'] = X_stockTakeOffby
        record_values['X_isactive'] = X_isactive
        record_values['X_LastPurchasePrice'] = X_LastPurchasePrice
        record_values['X_StockTakedate'] = X_StockTakedate

        if currency_id:
            record_values['currency_id'] = currency_id.id

        record_values['AppearsInTargetItems'] = AppearsInTargetItems
        record_values['should_be_ordered'] = should_be_ordered

        record_values['OrderRecommend90'] = OrderRecommend90
        record_values['OrderRecommend120'] = OrderRecommend120
        record_values['OrderRecommend180'] = OrderRecommend180
        record_values['OrderRecommend365'] = OrderRecommend365


        record_values['stock_selling_status'] = stock_selling_status
        record_values['should_be_deleted'] = should_be_deleted
        record_values['is_dead_stock'] = is_dead_stock
        
        record_values['combined_30_days'] = combined_30_days
        record_values['combined_60_days'] = combined_60_days
        record_values['combined_90_days'] = combined_90_days
        record_values['combined_180_days'] = combined_180_days
        record_values['combined_365_days'] = combined_365_days
        
        
        if currency_id and x_lastPurchaseOrderDate:
            X_lastPurchaseExchange = self.get_po_exchange_rate(currency_id=currency_id.id, po_date=x_lastPurchaseOrderDate)
            record_values['X_lastPurchaseExchange'] = X_lastPurchaseExchange
            record_values['Vendor_name'] = self.get_most_recent_purchase_order_vendor(product=product)
            
        if currency_id:
            record_values['currency_name'] = currency_id.name

        #_logger.info("data to be saved is %s", record_values)

        self.create(record_values)
        
    @api.model
    def copy_btn(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]
        self.ensure_one()
        self.copied_product_name = self.product_id.display_name
        
        return {
            'type': 'ir.actions.client',
            'tag': 'copy_product_name',
            'params': {
                'product_name': self.product_id.display_name
            }
        }
    
    @api.model
    def your_method(self, params):
        #active_id = args[0]
        _logger.info("001 - active id or parameters send was %s", params)
        #active_id = active_id[0]
        #self.ensure_one()
        
        print("Your method has been called!")
        #_logger.info("002 - active id or parameters send was %s", active_id)
        return True
        
        

    @api.model
    def create_rfq(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]

        record = self.env['cw.ocm.forecast'].browse(active_id)

        if record.OrderRecommend90 <= 0 : 
            raise UserError("The recommended quantity should be greater than 0")

        if  not record.product_id.seller_ids:
                raise UserError("The product has no vendors.")
        
        j = 0

        for vendor in record.product_id.seller_ids:
            j = j + 1
                

        try:
            # Get the vendors ordered by sequence
            vendors = record.product_id.seller_ids.sorted('sequence')

            # Ensure at least one vendor is found
            if not vendors:
                raise ValueError("No vendor found for the product")

            # Get the first vendor
            vendor = vendors[0]


            quantity_order = record.OrderRecommend90

            # Create the request for proposal
            rfq_vals = {
                'partner_id': vendor.partner_id.id,
                'user_id': self.env.user.id,
                'origin': record.product_id.name,
                'order_line': [(0, 0, {
                    'product_id': record.product_id.id,
                    'product_qty': record.OrderRecommend90,
                })]
                #'product_id': record.product_id.id,
                #'product_qty': record.OrderRecommend90,
                # Add other RFQ fields as needed
            }
            rfq = self.env['purchase.order'].create(rfq_vals)

            # Optionally, you can confirm the RFQ or leave it in draft state
            # rfq.button_confirm()

            """
            rfq = self.env['purchase.order'].create({
                #'partner_id': vendor.name.id,
                'partner_id': vendor.id,
                'order_line': [(0, 0, {
                    'product_id': record.product_id.id,
                    'product_qty': record.OrderRecommend90,
                })]
            })
            """

            qty_on_hand = record.x_QTYonHand + record.X_QtyonOrder

            in_draft_order = quantity_order

            OrderRecommend90 = record.X_Invoice90days - qty_on_hand

            if OrderRecommend90 > 0 : 
                should_be_ordered = True
            else :
                should_be_ordered = False
                OrderRecommend90 = 0

            record.write({
                'OrderRecommend90': OrderRecommend90,
                'should_be_ordered': should_be_ordered,
                'in_draft_order' : in_draft_order
            })

            
            rfq_url = f"#action={self.env.ref('purchase.purchase_rfq').id}&id={rfq.id}&model=purchase.order&view_type=form"

            # Create the notification with a link to the RFQ
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Request for Quotation Created'),
                    'message': _('Request for Quotation #%s has been successfully created.') % rfq.name,
                    'links': [{
                        'label': rfq.name,
                        'url': rfq_url
                    }],
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError("Error creating purchase order: %s" % (str(e)))


    @api.depends('product_id')
    def _compute_orderpoint_id(self):
        for record in self:
            orderpoint = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', record.product_id.id)], limit=1)
            record.orderpoint_id = orderpoint.id

    def _get_procurement_date(self):
        return timezone(self.company_id.partner_id.tz or 'UTC').localize(datetime.combine(self.lead_days_date, time(12))).astimezone(UTC).replace(tzinfo=None)


    @api.model
    def action_replenish(self, active_id):
        now = self.env.cr.now()
        active_id = self._context.get('active_id')
        record = self.env['cw.ocm.forecast'].browse(active_id)

        if record.OrderRecommend90 <= 0 : 
            raise UserError("The recommended quantity should be greater than 0")

        location_id = record.product_id.location_id.id


        if not location_id:
            location_name = "Stock"
            location = self.env['stock.location'].search([('name', '=', location_name)], limit=1)
            location_id = location.id

        if not location_id:
            default_location = self.env['stock.location'].search([('usage', '=', 'internal'), ('company_id', '=', self.env.company.id)], limit=1)
            location_id = default_location.id
        

        orderpoint = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', record.product_id.id)], limit=1)
        origin = self.env['ir.sequence'].next_by_code('stock.orderpoint')


        if orderpoint.id:
            orderpoint.write({
                'qty_to_order': record.OrderRecommend90,
            })
            record.orderpoint_id = orderpoint.id
        else :
            orderpoint = self.env['stock.warehouse.orderpoint'].create({
                'product_id': record.product_id.id,
                'product_min_qty': 0,  # Example value, adjust as needed
                'product_max_qty': 0,  # Example value, adjust as needed
                'qty_multiple': 1,  # Example value, adjust as needed
                'qty_to_order': record.OrderRecommend90,
                'product_uom': record.product_id.uom_id.id,
                'location_id': location_id,
                'company_id': self.env.company.id,
            })
            record.orderpoint_id = orderpoint.id

        
        try:
            procurements = []
            origins = orderpoint.env.context.get('origins', {}).get(orderpoint.id, False)
            if origins:
                origin = '%s - %s' % (orderpoint.display_name, ','.join(origins))
            else:
                origin = orderpoint.name
                
            if float_compare(orderpoint.qty_to_order, 0.0, precision_rounding=orderpoint.product_uom.rounding) == 1:
                date = orderpoint._get_orderpoint_procurement_date()
                global_visibility_days = self.env['ir.config_parameter'].sudo().get_param('stock.visibility_days')
                if global_visibility_days:
                    date -= relativedelta.relativedelta(days=int(global_visibility_days))
                values = orderpoint._prepare_procurement_values(date=date)
                procurements.append(self.env['procurement.group'].Procurement(
                    orderpoint.product_id, orderpoint.qty_to_order, orderpoint.product_uom,
                    orderpoint.location_id, orderpoint.name, origin,
                    orderpoint.company_id, values))
            try:
                self.env['procurement.group'].with_context(from_orderpoint=True).run(procurements, raise_user_error=True)
            except ProcurementException as errors:
                orderpoints_exceptions = []
                for procurement, error_msg in errors.procurement_exceptions:
                    orderpoints_exceptions += [(procurement.values.get('orderpoint_id'), error_msg)]
                all_orderpoints_exceptions += orderpoints_exceptions
                failed_orderpoints = self.env['stock.warehouse.orderpoint'].concat(*[o[0] for o in orderpoints_exceptions])
                if not failed_orderpoints:
                    _logger.error('Unable to process orderpoints')  

        except UserError as e:
            if len(self) != 1:
                raise e
            raise RedirectWarning(e, {
                'name': self.product_id.display_name,
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'views': [(self.env.ref('product.product_normal_form_view').id, 'form')],
            }, _('Edit Product'))
            
        notification = False
        if len(self) == 1:
            notification = self.with_context(written_after=now)._get_replenishment_order_notification()
        # Forced to call compute quantity because we don't have a link.
        #self._compute_qty()
        #self.filtered(lambda o: o.create_uid.id == SUPERUSER_ID and o.qty_to_order <= 0.0 and o.trigger == 'manual').unlink()
        return notification


    def _procure_orderpoint_confirm(self, orderpoint, company_id=None):
        self = self.with_company(company_id)
        procurements = []
        origins = orderpoint.env.context.get('origins', {}).get(orderpoint.id, False)
        if origins:
            origin = '%s - %s' % (orderpoint.display_name, ','.join(origins))
        else:
            origin = orderpoint.name
            
        if float_compare(orderpoint.qty_to_order, 0.0, precision_rounding=orderpoint.product_uom.rounding) == 1:
            date = orderpoint._get_orderpoint_procurement_date()
            global_visibility_days = self.env['ir.config_parameter'].sudo().get_param('stock.visibility_days')
            if global_visibility_days:
                date -= relativedelta.relativedelta(days=int(global_visibility_days))
            values = orderpoint._prepare_procurement_values(date=date)
            procurements.append(self.env['procurement.group'].Procurement(
                orderpoint.product_id, orderpoint.qty_to_order, orderpoint.product_uom,
                orderpoint.location_id, orderpoint.name, origin,
                orderpoint.company_id, values))
        try:
            self.env['procurement.group'].with_context(from_orderpoint=True).run(procurements, raise_user_error=True)
        except ProcurementException as errors:
            orderpoints_exceptions = []
            for procurement, error_msg in errors.procurement_exceptions:
                orderpoints_exceptions += [(procurement.values.get('orderpoint_id'), error_msg)]
            all_orderpoints_exceptions += orderpoints_exceptions
            failed_orderpoints = self.env['stock.warehouse.orderpoint'].concat(*[o[0] for o in orderpoints_exceptions])
            if not failed_orderpoints:
                _logger.error('Unable to process orderpoints')
                

        return {}



    @api.depends('product_id', 'location_id', 'product_id.stock_move_ids', 'product_id.stock_move_ids.state', 'product_id.stock_move_ids.date', 'product_id.stock_move_ids.product_uom_qty')
    def _compute_qty(self):
        orderpoints_contexts = defaultdict(lambda: self.env['stock.warehouse.orderpoint'])
        for orderpoint in self:
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.qty_on_hand = False
                orderpoint.qty_forecast = False
                continue
            orderpoint_context = orderpoint._get_product_context()
            product_context = frozendict({**orderpoint_context})
            orderpoints_contexts[product_context] |= orderpoint
        for orderpoint_context, orderpoints_by_context in orderpoints_contexts.items():
            products_qty = {
                p['id']: p for p in orderpoints_by_context.product_id.with_context(orderpoint_context).read(['qty_available', 'virtual_available'])
            }
            products_qty_in_progress = orderpoints_by_context._quantity_in_progress()
            for orderpoint in orderpoints_by_context:
                orderpoint.qty_on_hand = products_qty[orderpoint.product_id.id]['qty_available']
                orderpoint.qty_forecast = products_qty[orderpoint.product_id.id]['virtual_available'] + products_qty_in_progress[orderpoint.id]
    
    
    @api.model
    def execute_external_script(self):
        script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'external_script.py')
        spec = importlib.util.spec_from_file_location("external_script", script_path)
        external_script = importlib.util.module_from_spec(spec)
        sys.modules["external_script"] = external_script
        spec.loader.exec_module(external_script)
        external_script.run_script()



