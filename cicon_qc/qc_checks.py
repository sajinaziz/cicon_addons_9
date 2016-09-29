from openerp import models, fields, api



class CiconQcCheckOperation(models.Model):
    _name = 'cicon.qc.check.operation'
    _description = "QC Check operations"

    name = fields.Char('Operation', required=True)
    description = fields.Text("Description")

    _sql_constraints = [('uniq_check_op','UNIQUE(name)', ('Unique check operation name !'))]


class CiconQcCheck(models.Model):
    _name = 'cicon.qc.check'
    _description = "Quality Checks"


    name = fields.Char('QC Check Ref:')
    prod_order_ids = fields.Many2many('cic.prod.order', 'cic.prodorder.qccheck_rel',
                                      'qc_check_id', 'prod_order_id', string="Production Orders")
    date = fields.Date('Date')
    state = fields.Selection([('new','TO DO'),('pass','PASS'),('fail','FAIL')], string='Status')
    operation_id = fields.Many2one('cicon.qc.check.operation', string="Qc Check Operation", required=True)
    note = fields.Text( string='Notes')
    user_id = fields.Many2one('res.users', string="User")





