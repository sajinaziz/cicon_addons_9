from openerp import models,fields,api

class CiconEmail(models.Model):
    _inherit = ['mail.thread']
    _name = 'cicon.email'
    _description = "Cicon Email"

    #keep request information

    name = fields.Char(string="ITREF No", index=True, readonly=True)
    request_date = fields.Date(string="Date",required=True,default=fields.Date.context_today)


    manager_id = fields.Many2one('hr.employee', string="Attention", required=True)
    employee_id = fields.Many2one('hr.employee', string='Name', required=True)
    department_id = fields.Many2one('hr.department', string="Department",related='employee_id.department_id',readonly=True)
    job_id = fields.Many2one('hr.job', string="Designation",related='employee_id.job_id',readonly=True)
    location = fields.Char('Location')
    email_id = fields.Char(string="Preferred E-mail ID ",required=True)
    purpose = fields.Text(string="Purpose", required=True,help="Purpose of the Email Request!")
    approved_by = fields.Many2one('hr.employee', string="Approved By", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string="Company", required=True)


   #keep configuration settings

    approved_date = fields.Date(string="Date",  default=fields.Date.context_today,track_visibility='onchange')
    approved_email_id = fields.Char(string="Approved E-mail ID")
    pop_password = fields.Char(string="POP3 Password")
    local_password = fields.Char(string="Local Password")
    technician_id =  fields.Many2one('res.users', string='Technician', track_visibility='onchange',
                                     domain="[('login','!=','admin')]",default=lambda self: self.env.user)
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'),('done','Completed')], string="Status",  required=True,
                             default='pending',track_visibility='onchange')

    sql_constraints = [('uniq_Email_Request', 'UNIQUE(name)', 'Email Request Ref Must be Unique')]

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cicon.email.request.seq') or 'New'
        return super(CiconEmail, self).create(vals)


    @api.multi
    def print_request(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'cicon_email.report_email_template')

    @api.multi
    def pending_request(self):
        self.write({'state': 'pending'})

    @api.multi
    def approve_request(self):
        self.write({'state': 'approved'})

    @api.multi
    def done_request(self):
        self.write({'state': 'done'})

    @api.multi
    def set_pending(self):
        """Change Status on button Click"""
        return self.write({'state': 'pending'})
