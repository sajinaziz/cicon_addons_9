from openerp import models, fields, api


class CiconTechRfi(models.Model):
    _name = 'cicon.tech.rfi'
    _description = "RFI"

    name = fields.Char('RFI Reference', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string="Customer/Contractor", domain=[('customer', '=', True)], required=True)
    job_site_id = fields.Many2one('cic.job.site', string="Project / Job Site",
                                  domain="[('partner_id', '=', partner_id)]", required=True)
    site_contact_ids = fields.Many2many('tech.project.contact', 'cicon_tech_rfi_contact_rel',
                                        'rfi_id', 'contact_id', string="Contacts")
    element = fields.Char('Element', required=True)
    level = fields.Char('Level')
    rfi_date = fields.Date('RFI Date', default=fields.Date.context_today, required=True)
    subject = fields.Char('Subject')
    description = fields.Html('Description')
    created_by = fields.Many2one('res.users', string="Raised By", default=lambda self: self.env.user, required=True)
    attachment_count = fields.Integer('Attachment No:')
    response_last_date = fields.Date("Response Required Date")
    contractor_remarks = fields.Text('Contractor Remarks')
    contractor_subject = fields.Text('Contractor Subject')
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.user.company_id)
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Sent'), ('done', 'Replied'),
                              ('cancel', 'Cancelled')], string="Status", required=True, default='draft')

    _sql_constraints = [('unique_rfi', 'UNIQUE(name)', 'RFI Reference Must be Unique')]

CiconTechRfi()

