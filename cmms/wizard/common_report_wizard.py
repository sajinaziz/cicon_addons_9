from openerp import models, fields, api


class CmmsCommonReportWizard(models.TransientModel):
    _name = 'cmms.common.report.wizard'
    _description = "CMMS Reports"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    report_list = fields.Selection([('expense_summary', 'Expense Summary'),
                                   ('expense_detailed', 'Expense Detailed')], string='Report', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def show_report(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx['from_date'] = self.start_date
        ctx['to_date'] = self.end_date
        ctx['heading'] = self.report_list
        ctx['company_id'] = self.company_id.id
        return self.with_context(ctx).env['report'].get_action(self, report_name='cmms.cmms_inventory_expense_report_summary', data={})
