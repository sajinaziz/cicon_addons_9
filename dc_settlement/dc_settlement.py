from openerp import fields, models, api


class CicDcSettlement(models.Model):
    _inherit = ['mail.thread']
    _name = 'cic.dc.settlement'
    _description = "DC Settlement"

    name = fields.Char('DC Number', required=True , help="DC Number")
    date = fields.Date('Date', help="DC Date")
    due_date = fields.Date('Due Date', help="DC Due Date")
    amount = fields.Float('Amount', digits=(15, 2), help="DC Amount")
    partner_id = fields.Many2one('res.partner', 'Beneficiary', domain="[('company_type','=','company')]", help="DC Partner")
    ac_no = fields.Char('Account No', help="DC Account#")
    sign_by = fields.Many2one('res.users', 'Signed By', help="DC Signed By")
    is_clearing_co = fields.Boolean('Clearing Co.', help="If Clearing Co.")
    is_customer = fields.Boolean('Is Customer', help="If Customer")
    ac_debited = fields.Boolean('Account Debited', help="If Account Debited")
    sign_checked = fields.Boolean('Sign Checked', help="Sign Checked")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, help="DC Date")
    interest_rate = fields.Float('Interest Rate', help="Interest Rate")


CicDcSettlement()

