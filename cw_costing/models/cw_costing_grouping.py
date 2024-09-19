from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CwCostingGrouping(models.Model):
    _name = 'cw.costing.grouping.po'
    _description = 'CW Costing Grouping PO'
    
    
    name = fields.Char(string='Grouping Ref', compute='_compute_name_from_shipment', store=True)
    x_shipment_id = fields.Many2one('x_shipment', string="Shipment Id", required=False)
    purchase_order_ids = fields.One2many('purchase.order', 'x_cw_costing_grouping_id', string='PO(s)', required=False, compute='_compute_purchases_orders', store=True)
    cw_costing_grouping_po_line_ids = fields.One2many('cw.costing.grouping.po.line', 'cw_costing_grouping_po_id', string='Costing Lines', store=True)
    freight_cost_amount = fields.Float(string='Freight Cost')
    freight_cost_currency_id = fields.Many2one('res.currency', string='Freight cost currency', default=lambda self: self.env.ref('base.VUV'))
    tracking_grouping_order = fields.Char(string='Grouping Tracking Order', required=False)
    updated_tracking_date = fields.Datetime(string='Updated tracking Grouping Order Date')
    modified_by_id = fields.Many2one('res.users', string='Created/Modified by', readonly=True)
    is_costing_completed = fields.Boolean(string='Is Costing Completed', default=False)
    created_at = fields.Datetime(string='Created at', default=lambda self: fields.Datetime.now(), readonly=True)
    modified_at = fields.Datetime(string='Modified at', readonly=True)
    can_activate_is_completed = fields.Boolean(string='Can activate Is Completed', default=False, store=True, compute='_compute_can_activate_is_completed')
    state = fields.Selection(
        [
            ('draft', 'Draff'),
            ('in_progress', 'In Progress'),
            ('done', 'Done')
        ],
        default='draft',
        string="Status"
    )
    
    
    @api.depends('x_shipment_id')
    def _compute_name_from_shipment(self):
        for record in self:
            if record.x_shipment_id:
                record.name = record.x_shipment_id.x_name
            else:
                record.name = ""
    
    @api.depends('x_shipment_id')
    def _compute_purchases_orders(self):
        for record in self:
            if record.x_shipment_id and record.x_shipment_id.x_shipment_line_ids_cf925:
                purchase_orders = []
                for line_x_shipment in record.x_shipment_id.x_shipment_line_ids_cf925:
                    purchase_orders.append((4, line_x_shipment.x_studio_purchase_order.id))
                record.purchase_order_ids = purchase_orders
            else:
                record.purchase_order_ids = [(5, 0, 0)] # Clear the one2many field if no shipment is selected
                    
    
    """
    @api.depends('purchase_order_ids')
    def _compute_name_field(self):
        temp_name = ''
        for record in self:
            for line in record.purchase_order_ids:
                if len(temp_name) > 1:
                    temp_name = temp_name + ' - ' + line.name 
                else:
                    temp_name = line.name
                    
            record.name = temp_name
    """
            
    @api.depends('cw_costing_grouping_po_line_ids', 'freight_cost_amount')
    def _compute_can_activate_is_completed(self):
        for record in self:
            if not record.freight_cost_amount or record.freight_cost_amount <= 0:
                record.can_activate_is_completed = False
            elif not record.cw_costing_grouping_po_line_ids:
                record.can_activate_is_completed = False
            else:
                total_sub_freight_amount = sum(group_line.freight_share_amount for group_line in record.cw_costing_grouping_po_line_ids)
                difference_freight = total_sub_freight_amount - record.freight_cost_amount
                abs_difference_freight = abs(difference_freight)
                if abs_difference_freight >= 0.001:
                    record.can_activate_is_completed = False
                else:
                    record.can_activate_is_completed = True
    
    def _computer_button_text(self):
        for record in self:
            if isinstance(record.id, int):
                record.button_text = "Create & Import PO Lines"
            else:
                record.button_text = "Update & Estimate"
                
    
    def action_done(self):
        for record in self:
            if record.state != 'in_progress':
                raise UserError("Only confirmed orders can be marked as done.")
            
            if not record.can_activate_is_completed:
                raise UserError("Please save your changes before proceeding")
            
            record.state = 'done'
            record.is_costing_completed = True
            record.can_activate_is_completed = False
            
            record.write({
                'state': 'done',
                'is_costing_completed': True,
                'can_activate_is_completed': False
            })
            
            for group_line in record.cw_costing_grouping_po_line_ids:
                group_line.write({
                    'is_costing_completed': True
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # This will reload the current view
        }
    
    
    def action_cancel(self):
        for record in self:
            if record.state != 'done':
                raise UserError("We can only cancelled Costing which is in Done state")
            
            record.state = 'in_progress'
            record.is_costing_completed = False
            record.can_activate_is_completed = True
            
            record.write({
                'state': 'in_progress',
                'is_costing_completed': False,
                'can_activate_is_completed': True
            })
            
            for group_line in record.cw_costing_grouping_po_line_ids:
                group_line.write({
                    'is_costing_completed': False
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # This will reload the current view
        }
            
            
            
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['modified_by_id'] = self.env.user.id
            vals['modified_at'] = fields.Datetime.now()
            
            updated_tracking_order = vals.get('tracking_grouping_order', False)
            if updated_tracking_order:
                vals['updated_tracking_date'] = fields.Datetime.now()
                
            vals['state'] = 'in_progress'
                
            freight_amount_posted = vals.get('freight_cost_amount', 0)
    
        res = super().create(vals_list)
        self.computer_field_cw_costing_po_line_ids(res.id, freight_amount_posted=freight_amount_posted)
        
        """
        if res.freight_cost_amount:
            self.define_freight_shares_for_group(self.id)
            self.set_freight_share_amount(self.id)
        """
        
        return res
    
    
    @api.model
    def write(self, vals):
        vals['modified_by_id'] = self.env.user.id
        vals['modified_at'] = fields.Datetime.now()
        
        state = vals.get('state', 'draft')
        if state == 'draft':
            vals['state'] = 'in_progress'
        
        updated_tracking_order = vals.get('tracking_grouping_order', False)
        if updated_tracking_order:
            vals['updated_tracking_date'] = fields.Datetime.now()
            
            
        previous_elmts = []
        for line in self.purchase_order_ids:
            previous_elmts.append(line.id)
        
        res = super().write(vals)
        
        after_elmts = []
        for line in self.purchase_order_ids:
            after_elmts.append(line.id)
            
        
        if previous_elmts and after_elmts:
            if set(previous_elmts) != set(after_elmts):
                self.computer_field_cw_costing_po_line_ids(self.id)
                
        
        if self.freight_cost_amount:
            self.define_freight_shares_for_group(self.id)
            self.set_freight_share_amount(self.id)
        
        return res
    
    
    
    def unlink(self):
        for record in self:
            cw_costing_groupings_to_remove = self.env['cw.costing.grouping.po.line'].search([
                ('cw_costing_grouping_po_id', '=', record.id),
            ])
            
            for line in cw_costing_groupings_to_remove:
                line.unlink()
                
        return super().unlink()
    
    @api.model
    def create_from_view(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]
        print("active id is from create " + str(active_id))
        
    
    @api.model
    def update_from_view(self, *args, **kwargs):
        active_id = args[0]
        active_id = active_id[0]
        print("active id is from update" + str(active_id))
        
    def delete_records_for_po(self, po_id: int):
        _logger.info("Je passe par delete_records_for_po 001")
        purchase_order = self.env['purchase.order'].browse(po_id)
        purchase_order.ensure_one()
        _logger.info("Je passe par delete_records_for_po 002")
        if purchase_order:
            _logger.info("Je passe par delete_records_for_po 003")
            cw_costing_groupings_to_remove = self.env['cw.costing.grouping.po.line'].search([
                ('cw_costing_grouping_po_id', '=', self.id),
                ('purchase_order_id', '=', purchase_order.id)
            ])
            
            _logger.info("Je passe par delete_records_for_po 004")
            for line in cw_costing_groupings_to_remove:
                line.unlink()
        _logger.info("Je passe par delete_records_for_po 005")
            
    
    
    """
    @api.onchange('purchase_order_ids')
    @api.depends('purchase_order_ids')  
    """  
    def computer_field_cw_costing_po_line_ids(self, grouping_id: int = 0, freight_amount_posted: float = 0):
        if grouping_id:
            record = self.browse(grouping_id)
        else:
            record = self
        
            
        #lets start by removing entities not supposed to be there anymore
        cw_costing_groupings_to_remove = self.env['cw.costing.grouping.po.line'].search([
            ('cw_costing_grouping_po_id', '=', record.id),
            ('purchase_order_id', 'not in', record.purchase_order_ids.ids)
        ])
        
        for line in cw_costing_groupings_to_remove:
            line.unlink()
        
        #lets now save the field 
        po_lines = record.cw_costing_grouping_po_line_ids
        
        if not po_lines:
            po_lines = self.env['cw.costing.grouping.po.line']
            
            
        if self.id:
            pass
        else:
            print("je passe par isintance est 0")
            total_price_start = 0
            for purchase_order in record.purchase_order_ids:
                for order_line in purchase_order.order_line:
                    total_price_start += (order_line.product_qty * order_line.price_unit)
                    
            
        for purchase_order in record.purchase_order_ids:
            for order_line in purchase_order.order_line:
                existing_line = po_lines.filtered(lambda line: line.purchase_order_id == purchase_order and line.name == order_line.name)
                if not existing_line:
                    record_values = {}
                    record_values['purchase_order_id'] = purchase_order.id
                    record_values['cw_costing_grouping_po_id'] = record.id
                    record_values['name'] = order_line.name
                    record_values['product_id'] = order_line.product_id.id
                    record_values['quantity'] = order_line.product_qty
                    record_values['unit_price'] = order_line.price_unit
                    record_values['total_price'] = order_line.product_qty * order_line.price_unit
                    record_values['currency_id'] = purchase_order.currency_id.id
                    product_template = order_line.product_id.product_tmpl_id
                    record_values['price_excluded_vat'] = product_template.list_price
                    
                    taxes = product_template.taxes_id
                    if taxes:
                        record_values['price_include_vat'] = taxes.compute_all(product_template.list_price, currency=None, quantity=1.0)['total_included']
                    else:
                        record_values['price_include_vat'] = record_values['price_excluded_vat']
                        
                    record_values['conversion_rate'] = self.get_convert_rate_for_po(purchase_order_id=purchase_order.id)
                    
                    categ_id = order_line.product_id.categ_id
                    duty_rate = categ_id.search_costing_duty_rate()
                    warranty_rate = categ_id.search_costing_warranty_rate()
                    vat_rate = categ_id.search_costing_vat_rate()
                    
                    if not duty_rate and not warranty_rate:
                        harmonized_code = order_line.product_id.cw_search_harmonized_code_id()
                        record_values['harmonized_code_id'] = harmonized_code.id
                        record_values['duty'] = harmonized_code.cid_rate
                        record_values['warranty'] = harmonized_code.warranty_rate
                        record_values['hs_vat'] = harmonized_code.vat_rate
                    else:
                        record_values['duty'] = duty_rate
                        record_values['warranty'] = warranty_rate
                        record_values['hs_vat'] = vat_rate
                        
                    if self.id:
                        pass
                    else:
                        if total_price_start:
                            record_values['percentage_freight_share'] = record_values['total_price']/total_price_start
                            if freight_amount_posted > 0:
                                record_values['freight_share_amount'] = freight_amount_posted * record_values['percentage_freight_share']
                    
                    new_line = self.env['cw.costing.grouping.po.line'].create(record_values)
                    
                    if not self.id and total_price_start and freight_amount_posted > 0:
                        new_line.set_landed_cost_product()
                    
                    po_lines += new_line
                    
        self.define_freight_shares_for_group(grouping_id=self.id)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # This will reload the current view
        }
            
                
    
    
    def get_convert_rate_for_po(self, purchase_order_id:int):
        purchase_order = self.env['purchase.order'].browse(purchase_order_id)
        vuv_currency = self.env['res.currency'].search([('name', '=', 'VUV')], limit=1)
        po_currency = purchase_order.currency_id
        
        if po_currency.id == vuv_currency.id:
            return 1
        
        return self.get_conversion_rate(source_currency_code_id=po_currency.id, target_currency_code_id=vuv_currency.id)
    
        
    
    def get_conversion_rate(self, source_currency_code_id: int, target_currency_code_id: int):
        # Get source and target currencies
        from_currency = self.env['res.currency'].browse(source_currency_code_id)
        to_currency = self.env['res.currency'].browse(target_currency_code_id)
        
        if from_currency and to_currency:
            rate = from_currency._convert(from_amount=1.0, to_currency=to_currency, company=self.env.company, date=datetime.now().date())
            return rate
        return 0.0

        """
        if not source_currency or not target_currency:
            #raise ValueError("Source or Target currency not found")
            return 0

        # Get the most recent rate for the source currency
        latest_rate = source_currency.rate_ids.filtered(
            lambda r: r.currency_id == source_currency and r.company_id == self.env.company
        ).sorted(key=lambda r: r.create_date, reverse=True)[:1]

        if not latest_rate:
            #raise ValueError(f"No exchange rate found for {source_currency.name} to {target_currency.name}")
            return 0

        # Convert the rate
        conversion_rate = latest_rate.inverse_company_rate
        return conversion_rate
        """
        
        
    def define_freight_shares_for_group(self, grouping_id: int):
        if grouping_id:
            grouping = self.browse(grouping_id)
        else:
            grouping = self
        
        #get the list of items where amount isn't setup manually
        grouping_lines_ids = self.cw_costing_grouping_po_line_ids.filtered(lambda line: line.is_freight_cost_adjusted==False)
        
        """
        grouping_lines_ids = self.env['cw.costing.grouping.po.line'].search([
            ('cw_costing_grouping_po_id', '=', grouping.id),
            ('is_freight_cost_adjusted', '=', False)
        ])
        """
        
        total_cost = sum(group_line.total_price for group_line in grouping_lines_ids)
        total_rows = len(grouping_lines_ids)
        
        
        if total_cost and total_cost > 0:
            for group_line in grouping_lines_ids:
                freight_share = group_line.total_price / total_cost
                group_line.write({
                    'percentage_freight_share': freight_share
                })
        elif total_rows and total_rows > 0:
            for group_line in grouping_lines_ids:
                freight_share = 1 / total_rows
                group_line.write({
                    'percentage_freight_share': freight_share
                })
            
    
    @api.onchange('freight_cost_amount')
    @api.depends('freight_cost_amount', 'cw_costing_grouping_po_line_ids')
    def set_freight_share_amount(self, grouping_id: int = 0):
        if grouping_id:
            grouping = self.browse(grouping_id)
        else:
            grouping = self
            
        """
        if not grouping  not grouping.freight_cost_amount or grouping.freight_cost_amount < 0:
            raise UserError("Make sure the grouping and the freight cost are properly setup")
        """
        
        if self.freight_cost_amount and self.freight_cost_amount < 0:
            raise UserError("Make sure the grouping and the freight cost are properly setup")
        
        
        grouping_fixed_amount_line_ids = self.cw_costing_grouping_po_line_ids.filtered(lambda line: line.is_freight_cost_adjusted==True)
        
        """
        grouping_fixed_amount_line_ids = self.env['cw.costing.grouping.po.line'].search([
            ('cw_costing_grouping_po_id', '=', grouping.id),
            ('is_freight_cost_adjusted', '=', True)
        ])
        """
        
        total_fixed_amount = sum(group_line.freight_share_amount for group_line in grouping_fixed_amount_line_ids)
        
        if total_fixed_amount > grouping.freight_cost_amount:
            raise UserError("The total amount (%s) manually fixed can't be superior to the Total freight cost (%s)" % (str(total_fixed_amount), str(grouping.freight_cost_amount)))
        
        amount_to_share =  grouping.freight_cost_amount - total_fixed_amount
        
        grouping_sharing_amount_ids = self.cw_costing_grouping_po_line_ids.filtered(lambda line: line.is_freight_cost_adjusted==False)
        
        """
        grouping_sharing_amount_ids = self.env['cw.costing.grouping.po.line'].search([
            ('cw_costing_grouping_po_id', '=', grouping.id),
            ('is_freight_cost_adjusted', '=', False)
        ])
        """
        
        if len(grouping_sharing_amount_ids):
            _logger.info("Grouping  share amount lines are %s", grouping_sharing_amount_ids)
            
            for grouping_line in grouping_sharing_amount_ids:
                if grouping_line.percentage_freight_share:
                    freight_amount = amount_to_share * grouping_line.percentage_freight_share
                    grouping_line.write({
                        'freight_share_amount': freight_amount
                    })
                    grouping_line.set_landed_cost_product()
        
        
                
    @api.model
    def reload_view(self, grouping_id: int):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cw.costing.grouping.po',
            'view_mode': 'form',
            'res_id': grouping_id,  # Reloads the current record
            'target': 'current',  # Ensures it's reloaded in the current window
        }
                
        