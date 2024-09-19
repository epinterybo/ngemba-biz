import random
from odoo import models, fields, _, api


class PosCashReport(models.Model):
    _name = 'ybo_pos_cash_move.pos_cash_report'
    _description = 'POS Cash In/Out Report'
    _rec_name = "reference_code"
    _inherit = ['mail.thread']
    _sql_constraints = [
        ('reference_code_uniq', 'unique(reference_code)', 'Reference number must be unique!')
    ]

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                default=lambda self: self.env.company.currency_id)
    
    total_counted = fields.Monetary(string='Total amount counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    expected_amount = fields.Monetary(string='Expected amount', required=True, readonly=True,
                                    currency_field='currency_id',default=0 ,compute='_compute_expected_amount')
    total_difference = fields.Monetary(string='Difference', required=True, readonly=True,
                                    currency_field='currency_id',default=0,compute='_compute_amount_difference')
    
    total_amount_sold = fields.Monetary(string='Total amount sold', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    expected_cash = fields.Monetary(string='Expected cash', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    total_bill_coin = fields.Monetary(string='Total bill/coin counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    total_cheque = fields.Monetary(string='Total cheque amount counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    total_cheque_expected = fields.Monetary(string='Expected cheque', required=True, readonly=True,
                                    currency_field='currency_id',default=0 ,compute='_compute_total_expected_cheque')
    
    
    reference_code = fields.Text(string='Reference', readonly=True)
    pos_id = fields.Many2one('pos.config', string='Point of Sale', required=True)
    pos_name = fields.Char(related='pos_id.name', string='POS Name', readonly=True, store=True)
    pos_session = fields.Many2one('pos.session', string='POS Session', required=True, readonly=True)
    cashier_id = fields.Many2one('res.users', string='Cashier', required=True,readonly=True)
    cashier_comment = fields.Text(string='Cashier Comment', readonly=True)
    count_type = fields.Selection([('in', 'Cash In'), ('out', 'Cash Out')], string='Count Type',
                                required=True, readonly=True)
    
    money_detail = fields.Json(string='Money Detail', required=True, readonly=True)
    total_5_vt = fields.Integer(string='5VT Bills', default=0, readonly=True)
    total_10_vt = fields.Integer(string='10VT Bills', default=0, readonly=True)
    total_20_vt = fields.Integer(string='20VT Bills', default=0, readonly=True)
    total_50_vt = fields.Integer(string='50VT Bills', default=0, readonly=True)
    total_100_vt = fields.Integer(string='100VT Bills', default=0, readonly=True)
    total_200_vt = fields.Integer(string='200VT Bills', default=0, readonly=True)
    total_500_vt = fields.Integer(string='500VT Bills', default=0, readonly=True)
    total_1000_vt = fields.Integer(string='1000VT Bills', default=0, readonly=True)
    total_2000_vt = fields.Integer(string='2000VT Bills', default=0, readonly=True)
    total_5000_vt = fields.Integer(string='5000VT Bills', default=0, readonly=True)
    total_10000_vt = fields.Integer(string='10000VT Bills', default=0, readonly=True)
    
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'),('rejected', 'Rejected')],
                            string='Admin Decision', default='pending')
    
    admin_comment = fields.Text(string='Admin Comment')
    admin_id = fields.Many2one('res.users', string='Administrator')
    approval_date_time = fields.Datetime(string='Approval Date and Time', readonly=True)

    formatted_total_counted = fields.Char(string='Formatted Total Counted', compute='_compute_formatted_total_counted')
    
    cheques_id = fields.One2many("ybo_pos_cash_move.pos_cash_cheque","pos_cash_report_id",string="Cheques",readonly=True)
    
    expected_cheques = fields.Many2many('pos.payment', 'pos_cash_report_payment_rel', 'pos_cash_report_id', 'payment_id', string='Expected Cheques',readonly=True)


    @api.depends('total_counted', 'count_type')
    def _compute_formatted_total_counted(self):
        for record in self:
            sign = '-' if record.count_type == 'out' else '+'
            record.formatted_total_counted = f"{sign} {record.total_counted:.2f}"
            
    @api.depends('expected_cheques')
    def _compute_total_expected_cheque(self):
        for record in self:
            value = 0
            
            for elt in record.expected_cheques :
                value = value + elt.amount       
            record.total_cheque_expected = value    
            
    @api.depends('total_cheque_expected','total_bill_coin')
    def _compute_expected_amount(self):
        for record in self:
        
            record.expected_amount = record.total_cheque_expected +  record.total_bill_coin 
            
    @api.depends('expected_amount','total_counted')
    def _compute_amount_difference(self):
        for record in self:
        
            record.total_difference =  record.total_counted - record.expected_amount         
                    

    @api.model_create_multi
    def create(self, vals_list):
        return super(PosCashReport, self).create(vals_list)

    def set_approved(self):
        for rec in self:
            rec.state = 'approved'
            rec.admin_id = self.env.user.id
            rec.approval_date_time = fields.Datetime.now()
            
            if rec.count_type == "out" :
                
                extras = { "formattedAmount" : self.env.company.currency_id.format(rec.total_counted), "translatedType" : _(rec.count_type) }
                
                rec.pos_session.try_cash_in_out(rec.count_type,rec.total_bill_coin,rec.cashier_comment,extras)
                
            self.env["bus.bus"]._sendone(
                rec.cashier_id.id,
                "simple_notification",
                {
                    "title" : f"The {rec.count_type} operation of {rec.total_counted} has been  {rec.state}",
                    "message" : f"{rec.admin_comment}"
                }
            )    
            
    def set_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.admin_id = self.env.user.id
            rec.approval_date_time = fields.Datetime.now()
            
            self.env["bus.bus"]._sendone(
                rec.cashier_id.id,
                "simple_notification",
                {
                    "title" : f"The {rec.count_type} operation of {rec.total_counted} has been  {rec.state}",
                    "message" : f"{rec.admin_comment}"
                }
            )    

    def aggregate_cash_counts(self, money_detail):
        """Aggregate total cash-in and cash-out amounts, and bill counts."""
        bill_totals = {
            'total_5_vt': 0,
            'total_10_vt': 0,
            'total_20_vt': 0,
            'total_50_vt': 0,
            'total_100_vt': 0,
            'total_200_vt': 0,
            'total_500_vt': 0,
            'total_1000_vt': 0,
            'total_2000_vt': 0,
            'total_5000_vt': 0,
            'total_10000_vt': 0,
        }
        
        amount = 0

        if money_detail:
            for bill, qty in money_detail.items():
                field_name = f'total_{bill}_vt'
                if field_name in bill_totals:
                    bill_totals[field_name] += qty
                    
                    amount = amount + (qty * float(bill))
                    

        return bill_totals , amount

    def submit_cash_count(self, pos_session_id, pos_id, count_type, amount, cashier_comment, money_details,cheques=[]):
        bill_totals,amount_bill = self.aggregate_cash_counts(money_details)
        
        expected_cash,total_amount_sold = self.get_expect_amount(pos_session_id,count_type)
        total_cheque = 0
    
        for cheque in cheques :
            
            total_cheque = total_cheque + float(cheque["amount"])

        vals = {
            'count_type': count_type,
            'pos_id': pos_id,
            'total_counted': amount,
            "expected_cash" : expected_cash if expected_cash != None else amount ,
            'total_bill_coin' : amount_bill,
            "total_cheque" : total_cheque,
            'pos_session': pos_session_id,
            "total_amount_sold": total_amount_sold,
            'cashier_comment': cashier_comment,
            'money_detail': money_details,
            'cashier_id': self.env.user.id,
            "state" : "approved" if count_type =="in" else "pending" ,
            'reference_code': self._generate_unique_reference(count_type.upper()),
            **bill_totals,
        }
        
        
        
    
        new_record = self.create([vals])
        
        if count_type == "out" :
            latest_record = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')],order='create_date desc', limit=1)
            
            if len(latest_record) > 0 :
            
                payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check']),('payment_date',">",latest_record[0].create_date)])
            else :
                payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check'])])
                
            if payments :
                new_record.expected_cheques = [(4, id.id) for id in payments]
                
            
        
            if new_record :
            
                for cheque in cheques :
                    self.env['ybo_pos_cash_move.pos_cash_cheque'].create([
                        {
                            'pos_cash_report_id': new_record.id,
                            **cheque
                        }
                    ])
                
        
        admin_group = self.env.ref("point_of_sale.group_pos_manager")
        
        admin_users = self.env['res.users'].search([('groups_id', 'in', admin_group.id)])
        
        for user in admin_users :
        
            self.env["bus.bus"]._sendone(
                user.id,
                "simple_notification",
                {
                    "title" : f"A new {new_record.count_type} operation has been submit by {new_record.cashier_id.name}, please review it and take corresponding action",
                    "message" : f"{new_record.cashier_comment}"
                }
            )

    
    
        return new_record
    
    def total_amount_cash_in_out(self,pos_session_id):
        records = self.search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')])
        
        amount_in = 0
        amount_out = 0
        
        for record in records :
            if record.count_type == "in" :
                amount_in += record.total_counted
            else :
                amount_out += record.total_counted  
                
        return amount_in,amount_out     
    
    def enter_cheques(self,pos_session_id):
        latest_record = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')],order='create_date desc', limit=1)
            
        if len(latest_record) > 0 :
            
            payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check']),('payment_date',">",latest_record[0].create_date)])
        else :
            payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check'])])
                
        return [
            {
                "id": payment.id,
                "drawer": payment.partner_id.name,
                "bank" : payment.bank_id.name,
                "cheque_number" : payment.check_number,
                "account_number" : payment.check_bank_account
            } 
            for payment in payments
        ]
    
    def last_counted_cheques(self,pos_session_id):
        
        
        latest_record = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')],order='create_date desc', limit=1)
        
        

        if len(latest_record) > 0 :
            last_simple_count = self.env['ybo_pos_cash_move.pos_simple_count'].search([('pos_session.id',"=",pos_session_id),('state',"=",'approved'),('create_date',">",latest_record[0].create_date)],order='create_date desc', limit=1)
        else :
            last_simple_count = self.env['ybo_pos_cash_move.pos_simple_count'].search([('pos_session.id',"=",pos_session_id),('state',"=",'approved'),],order='create_date desc', limit=1)

        if len(last_simple_count) > 0: 
                return  [
                    {
                        "id": payment.id,
                        "drawer": payment.drawer,
                        "bank" : payment.bank,
                        "amount" : payment.amount,
                        "cheque_number" : payment.cheque_number,
                        "account_number" : payment.account_number
                    } 
                    for payment in last_simple_count[0].cheques_id
                ]
    
            
        return []
    
    
    
    def get_expect_amount(self,pos_session_id,count_type):
        pos_session = self.env['pos.session'].browse(pos_session_id)
        
        data_val = pos_session.get_closing_control_data() 

        
        if count_type == "out" :
            
            val = data_val["default_cash_details"]["amount"] - 25000
        
            val = val if val > 0 else 0
        
            return  val ,data_val["orders_details"]["amount"]
        
        else :
            return None , data_val["orders_details"]["amount"]
        

    def _generate_unique_reference(self, count_type):
        sequence_number = ''.join(str(random.randint(0, 9)) for _ in range(5))
        return f"CSH-{count_type.upper()}-{sequence_number}"
