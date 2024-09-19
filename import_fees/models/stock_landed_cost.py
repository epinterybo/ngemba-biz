from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from math import ceil


class ReceivedProductLine(models.Model):
    _name = 'import_fees.received.product.line'
    # ==== Business fields ====
    landed_costs_id = fields.Many2one('stock.landed.cost', 'Landed Cost')
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True)
    quantity = fields.Float(string='Quantity',
                            default=1.0, digits=(14, 4))
    price_unit = fields.Monetary(string='Unit Price', store=True, readonly=True,
                                 currency_field='currency_id')
    price_total = fields.Monetary(string='Total', store=True, readonly=True,
                                  currency_field='currency_id')
    local_price_total = fields.Monetary(string='Local Currency', store=True, readonly=True,
                                        currency_field='local_currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    local_currency_id = fields.Many2one(related='landed_costs_id.currency_id', string='Currency', readonly=True,
                                        store=True)
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', readonly=True)
    hs_code_id = fields.Many2one('import_fees.harmonized_code', string="HS Code", store=True, readonly=True,
                                 compute='_compute_hscode')

    @api.depends('product_id')
    def _compute_hscode(self):
        for elm in self:
            elm.hs_code_id = elm.product_id.search_harmonized_code_id()


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    cost_line_product_id = fields.Many2one(related='cost_line_id.product_id', string='Cost', readonly=True)


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    bill_currency_id = fields.Many2one(related='vendor_bill_id.currency_id', string='Bill currency', readonly=True,
                                       store=True,
                                       help='Bill currency')
    regime_select = fields.Selection([('1', '1')], 'Regime', default='1')
    amount_foreign_currency = fields.Monetary('Value', currency_field='bill_currency_id', default=0.0, store=True,
                                              readonly=True,
                                              compute='_compute_currency_value')
    currency_rate = fields.Float('Currency rate', readonly=True, store=True, default=0.0,
                                 compute='_compute_currency_rate')
    customs_currency_rate = fields.Float('Customs Currency rate', default=lambda x: x.currency_rate)
    amount_local_currency = fields.Monetary('Value in local currency', currency_field='currency_id', default=0.0,
                                            store=True,
                                            readonly=True,
                                            compute='_compute_local_value')
    stevedoring = fields.Monetary('Stevedoring', currency_field='currency_id', default=0.0)
    demurrage = fields.Monetary('Demurrage', currency_field='currency_id', default=0.0)
    transport = fields.Monetary('Transport', currency_field='currency_id', default=0.0)
    storage = fields.Monetary('Storage', currency_field='currency_id', default=0.0)
    bank = fields.Monetary('Bank charges', currency_field='currency_id', default=0.0)
    miscellaneous = fields.Monetary('Miscellaneous', currency_field='currency_id', default=0.0)
    royalty_fee = fields.Monetary('Royalty fee', currency_field='currency_id', default=0.0)
    freight = fields.Monetary('Freight', currency_field='currency_id', default=0.0)
    clearance = fields.Monetary('Clearance', currency_field='currency_id', default=0.0)
    transit = fields.Monetary('Transit', currency_field='currency_id', default=0.0)
    transport_cfr_foreign_currency = fields.Monetary('CFR Transport', currency_field='bill_currency_id', default=0.0)
    transport_cfr_local_currency = fields.Monetary('In local currency', currency_field='currency_id', default=0.0,
                                                   compute='_compute_transport_locale')
    insurance = fields.Monetary('Insurance', currency_field='currency_id', default=0.0)
    shipping = fields.Monetary('DHL/Fedex/UPS...', currency_field='currency_id', default=0.0)
    other = fields.Monetary('Other', currency_field='currency_id', default=0.0)
    royalty_fee_info = fields.Monetary('Royalty fee info', currency_field='currency_id', default=0.0)
    declared_value = fields.Monetary('Declared Value', currency_field='currency_id', default=0.0, readonly=True)
    customs_value = fields.Monetary('Total Duty', currency_field='currency_id', default=0.0, readonly=True)
    customs_vat_value = fields.Monetary('Customs VAT', currency_field='currency_id', default=0.0, readonly=True)
    total_customs_value = fields.Monetary('Total Customs Value', currency_field='currency_id', default=0.0,
                                          compute='_compute_customs_value')
    total_landed_cost = fields.Monetary('Total Landed Cost', currency_field='currency_id', default=0.0,
                                        compute='_compute_total_landed_cost')
    received_products_ids = fields.One2many('import_fees.received.product.line',
                                            compute='_compute_received_products_ids',
                                            inverse="_none", readonly=True, store=True, inverse_name='landed_costs_id')
    customs_fees_ids = fields.One2many('import_fees.customs_fees', inverse_name='landed_costs_id', sort="hs_code")
    create_customs_bill = fields.Boolean('Create Customs Bill', compute='_compute_create_customs_bill')
    create_shipping_bill = fields.Boolean('Create Shipping Bill', compute='_compute_create_shipping_bill')
    valuation_adjustment_lines = fields.One2many(
        'stock.valuation.adjustment.lines', 'cost_id', 'Valuation Adjustments',
        context={'group_by': ['product_id']}
    )

    def _compute_customs_bill_visible(self):
        for move in self:
            move.customs_bill_visible = self.env['ir.config_parameter'].sudo().get_param(
                'import_fees.customs_bill_visible', False)

    def _compute_shipping_bill_visible(self):
        for move in self:
            move.shipping_bill_visible = self.env['ir.config_parameter'].sudo().get_param(
                'import_fees.shipping_bill_visible', False)
    def _none(self):
        pass



    @api.depends('currency_id', 'bill_currency_id', 'vendor_bill_id', 'vendor_bill_id.invoice_date')
    def _compute_currency_rate(self):
        for elm in self:
            if elm.currency_id and elm.bill_currency_id and elm.vendor_bill_id and elm.vendor_bill_id.invoice_date:
                elm.currency_rate = elm.bill_currency_id._get_conversion_rate(elm.bill_currency_id, elm.currency_id,
                                                                              elm.company_id,
                                                                              elm.vendor_bill_id.invoice_date)
            else:
                elm.currency_rate = 0.0

    @api.depends('cost_lines')
    def _compute_create_shipping_bill(self):
        for elm in self:
            elm.create_shipping_bill = len(elm.cost_lines) > 0 and self.env['ir.config_parameter'].sudo().get_param(
                'import_fees.shipping_bill_visible', False)

    @api.depends('customs_fees_ids')
    def _compute_create_customs_bill(self):
        for elm in self:
            elm.create_customs_bill = len(elm.customs_fees_ids) > 0 and self.env['ir.config_parameter'].sudo().get_param(
                'import_fees.customs_bill_visible', False)

    def calc_customs_fees_and_open(self):
        if not self.vendor_bill_id:
            raise UserError(_("Please select a vendor bill"))
        if not self.picking_ids:
            raise UserError(_("Please select at least one picking"))
        if self.insurance == 0.0:
            cif_value = self.amount_local_currency + self.freight
            self.insurance = cif_value * 0.015
        self._compute_customs_fees_ids()
        self._compute_customs_duties()
        return self.open_customs_fees_popup()

    def open_customs_fees_popup(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Tariffs"),
            "res_model": "import_fees.customs_fees",
            "views": [[self.env.ref('import_fees.customs_fees_tree').id, "tree"]],
            "view_mode": "tree",
            "domain": [('landed_costs_id', '=', self.id)],
            "target": "new",
        }

    @api.depends('customs_value', 'customs_vat_value')
    def _compute_customs_value(self):
        for record in self:
            record.total_customs_value = record.customs_value + record.customs_vat_value

    @api.depends('stevedoring', 'demurrage', 'transport', 'storage', 'bank', 'miscellaneous', 'royalty_fee',
                 'freight', 'clearance', 'transit', 'insurance', 'shipping', 'other', 'royalty_fee_info',
                 'customs_value', 'customs_vat_value', 'amount_local_currency')
    def _compute_total_landed_cost(self):
        for record in self:
            record.total_landed_cost = ceil(record.stevedoring + record.demurrage + record.transport + record.storage +
                                            record.bank + record.miscellaneous + record.royalty_fee + record.freight +
                                            record.clearance + record.transit + record.insurance + record.shipping +
                                            record.transport_cfr_local_currency +
                                            record.other + record.royalty_fee_info + record.customs_value +
                                            record.customs_vat_value + record.amount_local_currency)

    @api.depends('transport_cfr_foreign_currency', 'currency_rate')
    def _compute_transport_locale(self):
        for elm in self:
            elm.transport_cfr_local_currency = elm.transport_cfr_foreign_currency * elm.currency_rate

    @api.depends('currency_rate', 'amount_foreign_currency')
    def _compute_local_value(self):
        for elm in self:
            elm.amount_local_currency = elm.amount_foreign_currency * elm.currency_rate
            elm.update_transport_cfr_devise()

    @api.onchange('picking_ids', 'vendor_bill_id')
    @api.depends('picking_ids', 'vendor_bill_id')
    def _compute_received_products_ids(self):
        if self.picking_ids and self.vendor_bill_id:
            stock_move_ids = self.env['stock.move'].search(
                [('picking_id', 'in', self.picking_ids.ids)])
            act_move_line_ids = self.env['account.move.line'].search([('move_id', '=', self.vendor_bill_id.id)])
            records = []
            for item in stock_move_ids:
                act_move_line_id = next(iter([elm for elm in act_move_line_ids if elm.product_id == item.product_id]),
                                        False)
                if act_move_line_id:
                    records.append((0, 0, {
                        'move_id': item.id,
                        'product_id': item.product_id.id,
                        'currency_id': self.bill_currency_id.id,
                        'quantity': item.quantity,
                        'price_unit': act_move_line_id.price_unit,
                        'price_total': item.quantity * act_move_line_id.price_unit,
                        'local_price_total': item.quantity * act_move_line_id.price_unit * self.currency_rate,
                    }))
            self.received_products_ids = [(5,)]
            self.received_products_ids = records
        else:
            self.received_products_ids = [(5,)]

    def _compute_create(self):
        pass

    def _compute_customs_fees_ids(self):
        if self.received_products_ids:
            # create a list of all hs codes in the received products
            hs_codes = set([it.hs_code_id for it in self.received_products_ids])
            for harmonized_code_id in hs_codes:
                customs_fees = self.env['import_fees.customs_fees']
                existing = customs_fees.search(
                    [('landed_costs_id', '=', self.id), ('harmonized_code_id', '=', harmonized_code_id.id)])

                data = self.calculate_tariffs(harmonized_code_id)
                if existing:
                    existing.update(data)
                else:
                    data['landed_costs_id'] = self.id
                    data['harmonized_code_id'] = harmonized_code_id.id
                    customs_fees.create(data)
            self.customs_vat_value = sum([it.vat_value for it in self.customs_fees_ids])

    def calculate_tariffs(self, hs, use_cif_value=False):
        exchange_rate = self.customs_currency_rate or self.currency_rate
        declared_value_local = sum([it.price_total for it in self.received_products_ids if
                                    it.hs_code_id.id == hs.id]) * exchange_rate
        proportion = declared_value_local / (self.amount_local_currency * (exchange_rate / self.currency_rate))
        com_value = ceil(hs.com_value)
        exm_value = ceil(hs.exm_value)
        cif_value = ceil(
            declared_value_local + proportion * (self.insurance + self.freight)) if not use_cif_value else use_cif_value
        cid_value = ceil(cif_value * hs.cid_rate)
        surcharge_value = ceil(cid_value * hs.surcharge_rate)
        pal_value = ceil(cif_value * hs.pal_rate)
        eic_value = ceil(cif_value * hs.eic_rate)
        cess_levy_value = ceil((cif_value + (cif_value * 0.1)) * hs.cess_levy_rate)
        excise_duty_value = ceil(cif_value * hs.excise_duty_rate)
        vat_value = ceil(((cif_value * 1.1) + (
                cid_value + pal_value + eic_value + cess_levy_value + excise_duty_value)) * hs.vat_rate)
        srl_value = ceil((cid_value + surcharge_value + excise_duty_value) * hs.srl_rate)
        ridl_value = ceil((cid_value + cif_value + surcharge_value + pal_value + cess_levy_value +
                           vat_value + excise_duty_value + srl_value) * hs.ridl_rate)
        sscl_value = ceil((cif_value + 0.1 * cif_value + cid_value + pal_value + cess_levy_value +
                           excise_duty_value) * hs.sscl_rate)
        customs_amount = ceil((cid_value + surcharge_value + pal_value + eic_value + cess_levy_value +
                               excise_duty_value + ridl_value + srl_value + sscl_value + com_value + exm_value))
        return {
            'rate': customs_amount / declared_value_local,
            'value': declared_value_local,
            'com_value': com_value,
            'exm_value': exm_value,
            'amount': customs_amount,
            'cif_value': cif_value,
            'cid_value': cid_value,
            'surcharge_value': surcharge_value,
            'pal_value': pal_value,
            'eic_value': eic_value,
            'cess_levy_value': cess_levy_value,
            'excise_duty_value': excise_duty_value,
            'vat_value': vat_value,
            'srl_value': srl_value,
            'ridl_value': ridl_value,
            'sscl_value': sscl_value,
        }


    @api.depends('customs_fees_ids.amount', 'customs_fees_ids.value')
    def _compute_customs_duties(self):
        for record in self:
            fees_ids = record.customs_fees_ids
            if fees_ids:
                record.customs_value = sum(it.amount for it in fees_ids)
                record.declared_value = sum(it.value for it in fees_ids)
                record.update_landed_cost_line('customs', record.customs_value, 'by_hscode')

    @api.depends('vendor_bill_id', 'picking_ids', 'received_products_ids', 'currency_rate')
    def _compute_currency_value(self):
        self.amount_foreign_currency = sum(
            item.price_total
            for item in self.received_products_ids)
        self._compute_local_value()

    # Retrieve or create tax rates
    def get_or_create_tax(self, amount):
        tax = self.env['account.tax'].search([('amount', '=', amount), ('type_tax_use', '=', 'purchase')], limit=1)
        if not tax:
            tax = self.env['account.tax'].create({
                'name': f'Tax {amount}%',
                'amount': amount,
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'display_name': f'{amount}%',
                # Assuming these are purchase taxes
                # Add other necessary fields according to your tax configuration
            })
        else:
            tax = tax[0]
        return tax
    def button_create_shipping_bill(self):
        #Search for all shipping bills with the same vendor bill by invoice origin
        shipping_bills = self.env['account.move'].search([('invoice_origin', '=', self.name), ('is_shipping_bill', '=', True)])
        if shipping_bills:
            return {
                'type': 'ir.actions.act_window',
                'name': _("Shipping Bill"),
                'res_model': 'account.move',
                'res_id': shipping_bills[0]['id'],
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
        else:
            account_inv_line = self.env['account.account'].search([
                ('company_id', '=', self.env.company.id),
                ('account_type', '=', 'asset_current'),
                ('id', '!=', self.env.company.account_journal_early_pay_discount_gain_account_id.id)
            ], limit=1)
            # Creates a new shipping bill for stevedoring, demurrage, transport, storage, bank, miscellaneous, royalty fee, freight, clearance, transit, insurance, shipping, other, royalty fee info
            items = []
            customs_id = self.env.ref('import_fees.customs')
            for item in self.cost_lines:
                if item.product_id.id != customs_id.id:
                    items.append((0, 0, {
                        'product_id': item.product_id.id,
                        'quantity': 1,
                        'price_unit': item.price_unit,
                        'account_id': account_inv_line.id,
                        'name': item.name,
                    }))
            result = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.vendor_bill_id.partner_id.id,
                'invoice_line_ids': items,
                'invoice_date': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                'invoice_origin': self.name,
                'is_shipping_bill': True,
            })
            return  {
                'type': 'ir.actions.act_window',
                'name': _("Shipping Bill"),
                'res_model': 'account.move',
                'res_id': result['id'],
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
    def button_create_customs_bill(self):
        # Search for all customs bills with the same vendor bill by invoice origin
        customs_bills = self.env['account.move'].search([('invoice_origin', '=', self.name), ('is_customs_bill', '=', True)])
        if customs_bills:
            return {
                'type': 'ir.actions.act_window',
                'name': _("Customs Bill"),
                'res_model': 'account.move',
                'res_id': customs_bills[0]['id'],
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
        else:
            # Creates a new customs bill for each product
            account_inv_line = self.env['account.account'].search([
                ('company_id', '=', self.env.company.id),
                ('account_type', '=', 'asset_current'),
                ('id', '!=', self.env.company.account_journal_early_pay_discount_gain_account_id.id)
            ], limit=1)
            # Creates a new customs bill for each product
            items = []
            for item in self.vendor_bill_id.invoice_line_ids:
                matching_customs_fees_item = next(iter([it for it in self.customs_fees_ids if
                                                        it.harmonized_code_id.id ==
                                                        item.product_id.search_harmonized_code_id().id]),
                                                  False)
                price_subtotal_local_currency = item.price_subtotal * self.currency_rate
                proportion = price_subtotal_local_currency / sum(
                    [it.value for it in self.customs_fees_ids if
                                                        it.harmonized_code_id.id ==
                                                        item.product_id.search_harmonized_code_id().id])
                product_id = self.env.ref('import_fees.customs')
                items.append((0, 0, {
                    'product_id': product_id.id,
                    'quantity': 1,
                    'price_unit': matching_customs_fees_item.amount * proportion,
                    'account_id': account_inv_line.id,
                    'name': "Customs / %s" % (item.product_id.name),
                }))
                items.append((0, 0, {
                    'product_id': product_id.id,
                    'quantity': 1,
                    'price_unit': matching_customs_fees_item.vat_value * proportion,
                    'account_id': account_inv_line.id,
                    'name': "VAT / %s" % (item.product_id.name),
                }))
            result = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.env.ref('import_fees.customs_partner').id,
                'invoice_line_ids': items,
                'invoice_date': datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                'invoice_origin': self.name,
                'is_customs_bill': True,
            })
            return  {
                'type': 'ir.actions.act_window',
                'name': _("Customs Bill"),
                'res_model': 'account.move',
                'res_id': result['id'],
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }

    def compute_landed_cost(self):
        adjustment_lines = self.env['stock.valuation.adjustment.lines']
        adjustment_lines.search([('cost_id', 'in', self.ids)]).unlink()

        towrite_dict = {}
        for cost in self.filtered(lambda c: c._get_targeted_move_ids()):
            rounding = cost.currency_id.rounding
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            all_customs_costs = []
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                hs_code = self.env['product.product'].search([('id', '=', val_line_values.get('product_id'))],
                                                             limit=1).search_harmonized_code_id() or False
                if hs_code:
                    customs_cost = val_line_values.copy()
                    customs_cost.update({
                        'hs_code': hs_code.id,

                    })
                    all_customs_costs.append(customs_cost)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += cost.currency_id.round(former_cost)

                total_line += 1

            qty_by_hscode = dict()
            hscodes = set([it['hs_code'] for it in all_customs_costs])
            for elm in hscodes:
                qty_by_hscode[elm] = sum([it['quantity'] for it in all_customs_costs if it['hs_code'] == elm])
            for item in all_customs_costs:
                item['customs_cost'] = item['quantity'] * sum(
                    x.amount
                    for x in
                    self.customs_fees_ids.filtered(
                        lambda it: it.harmonized_code_id.id == item['hs_code']
                    )) / qty_by_hscode[item['hs_code']]
            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        elif line.split_method == 'by_hscode' and total_qty:
                            value = next(iter(
                                [it['customs_cost'] for it in all_customs_costs if
                                 it['product_id'] == valuation.product_id.id and it[
                                     'move_id'] == valuation.move_id.id]), 0.0)
                        else:
                            value = (line.price_unit / total_line)

                        if rounding:
                            value = tools.float_round(value, precision_rounding=rounding, rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            adjustment_lines.browse(key).write({'additional_landed_cost': value})
        return True

    @api.onchange('stevedoring')
    def update_stevedoring(self):
        self.update_landed_cost_line('stevedoring', self.stevedoring, 'by_current_cost_price')

    @api.onchange('demurrage')
    def update_demurrage(self):
        self.update_landed_cost_line('demurrage', self.demurrage, 'by_current_cost_price')

    @api.onchange('transport')
    def update_transport(self):
        self.update_landed_cost_line('transport', self.transport, 'by_current_cost_price')

    @api.onchange('storage')
    def update_storage(self):
        self.update_landed_cost_line('storage', self.storage, 'by_current_cost_price')

    @api.onchange('bank')
    def update_bank(self):
        self.update_landed_cost_line('bank', self.bank, 'by_current_cost_price')

    @api.onchange('miscellaneous')
    def update_miscellaneous(self):
        self.update_landed_cost_line('miscellaneous', self.miscellaneous, 'by_current_cost_price')

    @api.onchange('royalty_fee')
    def update_royalty_fee(self):
        self.update_landed_cost_line('royalty_fee', self.royalty_fee, 'by_current_cost_price')

    @api.onchange('freight')
    def update_freight(self):
        self.update_landed_cost_line('freight', self.freight, 'by_current_cost_price')

    @api.onchange('clearance')
    def update_clearance(self):
        self.update_landed_cost_line('clearance', self.clearance, 'by_current_cost_price')

    @api.onchange('transit', 'currency_rate')
    @api.depends('transit', 'currency_rate')
    def update_transit(self):
        self.update_landed_cost_line('transit', self.transit, 'by_current_cost_price')

    @api.onchange('transport_cfr_foreign_currency', 'currency_rate')
    @api.depends('transport_cfr_foreign_currency', 'currency_rate')
    def update_transport_cfr_devise(self):
        tcfc = (self.transport_cfr_foreign_currency or 0.0)
        rate = (self.currency_rate or 0.0)
        self.update_landed_cost_line('transport_cfr', tcfc * rate, 'by_quantity')

    @api.onchange('insurance')
    def update_assurance(self):
        self.update_landed_cost_line('insurance', self.insurance, 'by_current_cost_price')

    @api.onchange('shipping')
    def update_dhl_fedex_ups(self):
        self.update_landed_cost_line('shipping', self.shipping, 'by_current_cost_price')

    @api.onchange('other')
    def update_others(self):
        self.update_landed_cost_line('other', self.other, 'by_current_cost_price')

    @api.onchange('royalty_fee_info')
    def update_royalty_fee_info(self):
        self.update_landed_cost_line('royalty_fee_info', self.royalty_fee_info, 'by_current_cost_price')

    def update_landed_cost_line(self, name, amount, split_method):
        if name:
            cost_line = False
            for it in self.cost_lines:
                if it.product_id.get_external_id()[it.product_id.id] == ("import_fees.%s" % name):
                    cost_line = it
                    break
            if amount:
                if cost_line:
                    self.cost_lines = [(1, cost_line.id, {'price_unit': amount,
                                                          })]
                else:
                    self.cost_lines = [(0, 0, {
                        'cost_id': self.id,
                        'price_unit': amount,
                        'product_id': self.env.ref('import_fees.%s' % name).id,
                        'split_method': split_method,
                    })]
            else:
                if cost_line:
                    self.cost_lines = [(2, cost_line.id)]


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'
    split_method = fields.Selection(selection_add=[('by_hscode', 'By HS Code'), ],
                                    ondelete={'by_hscode': "cascade"},
                                    string='Split Method',
                                    required=True,
                                    help="Equal : Cost will be equally divided.\n"
                                         "By Quantity : Cost will be divided according to product's quantity.\n"
                                         "By Current cost : Cost will be divided according to product's current cost.\n"
                                         "By Weight : Cost will be divided depending on its weight.\n"
                                         "By Volume : Cost will be divided depending on its volume.\n"
                                         "By HS Code : Cost will be divided depending on its Harmonized System Code.")
