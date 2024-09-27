import random
from odoo import models, fields, _, api


class PosSimpleCount(models.Model):
    _name = 'ybo_pos_cash_move.pos_simple_count'
    _description = 'Simple Count'
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
    
    total_expect_f_pos = fields.Monetary(string='Total expected Fpos', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    total_amount_sold = fields.Monetary(string='Total amount sold', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    expected_cash = fields.Monetary(string='Expected bill/coin', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    total_bill_coin = fields.Monetary(string='Total bill/coin counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    total_cheque_expected = fields.Monetary(string='Expected cheque', required=True, readonly=True,
                                    currency_field='currency_id',default=0 ,compute='_compute_total_expected_cheque')
    total_cheque = fields.Monetary(string='Total cheque counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    propose_cash_out_amount = fields.Monetary(string='Propose cashout amount ', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    propose_cash_out_amount_left = fields.Monetary(string='Propose cashout amount left', readonly=True,
                                    currency_field='currency_id', compute='_compute_propose_amount_left')
    
    total_pos_eft = fields.Monetary(string='Total FPOS  counted', required=True, readonly=True,
                                    currency_field='currency_id',default=0)
    
    f_pos_list = fields.Json(string='FPOS List', readonly=True,default=[])
    f_pos_list_display = fields.Char('FPOS list display', compute='_compute_f_pos_list_display', readonly=True)
    
    f_pos_expected_list = fields.Json(string='FPOS expected List', readonly=True,default=[])
    f_pos_expected_list_display = fields.Char('FPOS expected list display', compute='_compute_f_pos_expected_list_display', readonly=True)

    reference_code = fields.Text(string='Reference', readonly=True)
    pos_id = fields.Many2one('pos.config', string='Point of Sale', required=True)
    pos_name = fields.Char(related='pos_id.name', string='POS Name', readonly=True, store=True)
    pos_session = fields.Many2one('pos.session', string='POS Session', required=True, readonly=True)
    cashier_id = fields.Many2one('res.users', string='Cashier', required=True,readonly=True)
    cashier_comment = fields.Text(string='Cashier Comment', readonly=True)
    
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
    
    
    total_5_vt_proposal = fields.Integer(string='5VT Bills Propose', default=0, readonly=True)
    total_10_vt_proposal = fields.Integer(string='10VT Bills Propose', default=0, readonly=True)
    total_20_vt_proposal = fields.Integer(string='20VT Bills Propose', default=0, readonly=True)
    total_50_vt_proposal = fields.Integer(string='50VT Bills Propose', default=0, readonly=True)
    total_100_vt_proposal = fields.Integer(string='100VT Bills Propose', default=0, readonly=True)
    total_200_vt_proposal = fields.Integer(string='200VT Bills Propose', default=0, readonly=True)
    total_500_vt_proposal = fields.Integer(string='500VT Bills Propose', default=0, readonly=True)
    total_1000_vt_proposal = fields.Integer(string='1000VT Bills Propose', default=0, readonly=True)
    total_2000_vt_proposal = fields.Integer(string='2000VT Bills Propose', default=0, readonly=True)
    total_5000_vt_proposal = fields.Integer(string='5000VT Bills Propose', default=0, readonly=True)
    total_10000_vt_proposal = fields.Integer(string='10000VT Bills Propose', default=0, readonly=True)
    
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'),('rejected', 'Rejected')],
                            string='Admin Decision', default='pending')
    
    admin_comment = fields.Text(string='Admin Comment')
    admin_id = fields.Many2one('res.users', string='Administrator')
    approval_date_time = fields.Datetime(string='Approval Date and Time', readonly=True)

    formatted_total_counted = fields.Char(string='Formatted Total Counted', compute='_compute_formatted_total_counted')
    
    cheques_id = fields.One2many("ybo_pos_cash_move.pos_simple_count_cheque","pos_cash_report_id",string="Cheques",readonly=True)
    
    expected_cheques = fields.Many2many('pos.payment', 'simple_count_payment_rel', 'simple_count_id', 'payment_id', string='Expected Cheque',readonly=True)
    
    final_count = fields.Boolean(string='Final Count',default=False)

    @api.depends('total_counted',)
    def _compute_formatted_total_counted(self):
        for record in self:
        
            record.formatted_total_counted = f"{record.total_counted:.2f}"


    @api.model_create_multi
    def create(self, vals_list):
        return super(PosSimpleCount, self).create(vals_list)
    
    @api.depends('f_pos_list')
    def _compute_f_pos_list_display(self):
        for record in self:
            if record.f_pos_list and isinstance(record.f_pos_list, list):
                record.f_pos_list_display = ' ,  '.join(map(lambda obj: str(obj['amount']), record.f_pos_list))
            else:
                record.f_pos_list_display = ''
                
    @api.depends('f_pos_list')
    def _compute_f_pos_expected_list_display(self):
        for record in self:
            if record.f_pos_expected_list and isinstance(record.f_pos_expected_list, list):
                record.f_pos_expected_list_display = ' ,  '.join(map(lambda obj: str(obj['amount']), record.f_pos_expected_list))
            else:
                record.f_pos_expected_list_display = ''
    
            
    @api.depends('total_cheque_expected','expected_cash','total_expect_f_pos')
    def _compute_expected_amount(self):
        for record in self:
            
            print(record.total_cheque_expected,record.expected_cash,record.total_expect_f_pos)
        
            record.expected_amount = record.total_cheque_expected +  record.expected_cash  + record.total_expect_f_pos
            
            
            
    @api.depends('expected_amount','total_counted')
    def _compute_amount_difference(self):
        for record in self:
        
            record.total_difference =  record.total_counted - record.expected_amount         
    
                
    @api.depends('expected_cheques')
    def _compute_total_expected_cheque(self):
        for record in self:
            value = 0
            
            for elt in record.expected_cheques :
                value = value + elt.amount       
            record.total_cheque_expected = value     
            
    @api.depends('propose_cash_out_amount','total_bill_coin')
    def _compute_propose_amount_left(self):
        for record in self:
            record.propose_cash_out_amount_left = record.total_bill_coin - record.propose_cash_out_amount
            

    def set_approved(self):
        for rec in self:
            rec.state = 'approved'
            rec.admin_id = self.env.user.id
            rec.approval_date_time = fields.Datetime.now()
            
            
            value = rec.total_bill_coin - 25000
            
            bill_totals = [
            
                ['total_10000_vt_proposal', rec.total_10000_vt,10000],
                ['total_5000_vt_proposal', rec.total_5000_vt,5000],
                ['total_2000_vt_proposal', rec.total_2000_vt,2000],
                ['total_1000_vt_proposal', rec.total_1000_vt,1000],
                ['total_500_vt_proposal', rec.total_500_vt,500],
                ['total_200_vt_proposal', rec.total_200_vt,200],
                ['total_100_vt_proposal', rec.total_100_vt,100],
                ['total_50_vt_proposal', rec.total_50_vt,50],
                ['total_20_vt_proposal', rec.total_20_vt,20],
                ['total_10_vt_proposal', rec.total_10_vt,10],
                ['total_5_vt_proposal', rec.total_5_vt,5],
            ]
            
            amount = 0
            
            for key,qty,val in bill_totals :
                if value < 5 :
                    break
                
                if qty <= 0 :
                    pass
                
                r = value // val
                count = r if qty - r >= 0 else qty
                rec[key] = count
                
                value = value - ( count * val)
                
                amount = amount + ( count * val)
                
            rec.propose_cash_out_amount = amount    
                
                
            self.env["bus.bus"]._sendone(
                rec.cashier_id.id,
                "simple_notification",
                {
                    "title" : f"The Simple Count operation of {rec.total_counted} has been  {rec.state}",
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
                    "title" : f"The Simple Count operation operation of {rec.total_counted} has been  {rec.state}",
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

    def submit_cash_count(self, pos_session_id, pos_id, amount, cashier_comment, money_details,cheques=[],f_pos=0,f_pos_list=[],final_count=False):
        bill_totals,amount_bill = self.aggregate_cash_counts(money_details)
        
        expected_amount,expected_cash,total_amount_sold = self.get_expect_amount(pos_session_id)
        total_cheque = 0
        
        latest_record = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')],order='create_date desc', limit=1)
        f_pos_expect_list = []
        if len(latest_record) > 0 :
        
            f_pos_expected = 0
            for rec in self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'ilike', "bank"),('payment_date',">",latest_record[0].create_date)]):
                f_pos_expected = f_pos_expected + rec.amount 
                f_pos_expect_list.append({"amount":rec.amount})
        else :
            f_pos_expected = 0
            for rec in self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'ilike', "bank")]):
                f_pos_expected = f_pos_expected + rec.amount 
                f_pos_expect_list.append({"amount":rec.amount})
            
        
        
        for cheque in cheques :
            
            total_cheque = total_cheque + float(cheque["amount"])

        vals = {
            'pos_id': pos_id,
            'total_counted': amount,
            "expected_cash" : expected_cash if expected_cash != None else amount ,
            'total_bill_coin' : amount_bill,
            "total_cheque" : total_cheque,
            "total_pos_eft": f_pos,
            "total_expect_f_pos" : f_pos_expected,
            "f_pos_expected_list":f_pos_expect_list,
            "f_pos_list":f_pos_list,
            'pos_session': pos_session_id,
            "total_amount_sold": total_amount_sold,
            'cashier_comment': cashier_comment,
            'money_detail': money_details,
            'cashier_id': self.env.user.id,
            "final_count" : final_count,
            'reference_code': self._generate_unique_reference(),
            **bill_totals,
        }
        
        new_record = self.create([vals])
        
        
        latest_record = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')],order='create_date desc', limit=1)
        
        if len(latest_record) > 0 :
        
            payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check']),('payment_date',">",latest_record[0].create_date)])
        else :
            payments = self.env['pos.payment'].search([("session_id.id","=",pos_session_id),("payment_method_id.name",'in', ["Cheque","cheque","cheques","Cheques",'check'])])
        if payments :
            new_record.expected_cheques = [(4, id.id) for id in payments]
            
            
        
        if new_record :
            already_use_payment = []
            
            not_use_cheque = []
        
            for cheque in cheques :
                
        
                pay = payments.search([('amount',"=",float(cheque['amount'])),('id',"not in",already_use_payment)])
                
                if len(pay) > 0 :
                    self.env['ybo_pos_cash_move.pos_simple_count_cheque'].create([
                        {
                            'pos_cash_report_id': new_record.id,
                            "drawer" : pay[0].partner_id.name,
                            "bank" : pay[0].bank_id.name,
                            "account_number" : pay[0].check_bank_account,
                            "cheque_number": pay[0].check_number,
                            'amount' : pay[0].amount
                        }
                    ])
                        
                    already_use_payment.append(pay[0].id)  
                        
                    
                else :
                    not_use_cheque.append(cheque) 
                    
    
                    
            for cheque in not_use_cheque :
                
                
                
                pay = payments.search([('amount',">=",float(cheque['amount'])- 5),('amount',"<=",float(cheque['amount'])+5),('id',"not in",already_use_payment)])
                
                if len(pay) > 0 :
                    self.env['ybo_pos_cash_move.pos_simple_count_cheque'].create([
                        {
                            'pos_cash_report_id': new_record.id,
                            "drawer" : pay[0].partner_id.name,
                            "bank" : pay[0].bank_id.name,
                            "account_number" : pay[0].check_bank_account,
                            "cheque_number": pay[0].check_number,
                            'amount' : pay[0].amount
                        }
                    ])
                        
                    already_use_payment.append(pay[0].id)     
                    
                else  :
                    
                    self.env['ybo_pos_cash_move.pos_simple_count_cheque'].create([
                        {
                            'pos_cash_report_id': new_record.id,
                            "drawer" : "XXXX",
                            "bank" : "XXXX",
                            "account_number" : "XXXX",
                            "cheque_number":"XXXX",
                            'amount' : float(cheque['amount'])
                        }
                    ])
                    
                    
                    
        admin_group = self.env.ref("point_of_sale.group_pos_manager")
        
        admin_users = self.env['res.users'].search([('groups_id', 'in', admin_group.id)])
        
        for user in admin_users :
        
            self.env["bus.bus"]._sendone(
                user.id,
                "simple_notification",
                {
                    "title" : f"A new simple count operation has been submit by {new_record.cashier_id.name}, please review it and take corresponding action",
                    "message" : f"{new_record.cashier_comment}"
                }
            )
        return new_record
    
    def total_amount_cash_in_out(self,pos_session_id):
        records = self.env['ybo_pos_cash_move.pos_cash_report'].search([('pos_session.id',"=",pos_session_id),('count_type','in',["in","out"]),('state',"=",'approved')])
        
        amount_in = 0
        amount_out = 0
        
        for record in records :
            if record.count_type == "in" :
                amount_in += record.total_counted
            else :
                amount_out += record.total_counted  
                
        return amount_in,amount_out     
    
    
    def get_expect_amount(self,pos_session_id):
        pos_session = self.env['pos.session'].browse(pos_session_id)
        
        data_val = pos_session.get_closing_control_data() 
        total_cash_in,total_cash_cash_out = self.total_amount_cash_in_out(pos_session_id)
        
        val =   data_val["orders_details"]["amount"] + data_val["default_cash_details"]["opening"] + total_cash_in - total_cash_cash_out 
        val_1 =  data_val["default_cash_details"]["amount"] 
        # for elt in data_val["other_payment_methods"] :
        #     if elt['name'] == "Customer Account" :  
            
        #         val_1 = val_1 + elt["amount"] 
            
        print(f'val from custom {val} and val from system {val_1}')  
        return val_1,data_val["default_cash_details"]["amount"],data_val["orders_details"]["amount"]
        

    def _generate_unique_reference(self):
        sequence_number = ''.join(str(random.randint(0, 9)) for _ in range(5))
        return f"CSH-Simple-Count-{sequence_number}"



class BankReport(models.AbstractModel):
    _name = 'report.ybo_pos_cash_move.report_pos_cash_move'
