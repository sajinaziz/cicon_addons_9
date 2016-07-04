from openerp import models, fields, api


class CmmsCommonReportWizard(models.TransientModel):
    _name = 'cmms.common.report.wizard'
    _description = "CMMS Reports"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    report_list = fields.Selection([('expense_report', 'Expense Report'),
                                   ('expense_detailed', 'Expense Detailed'),('job_order_report','Job Order Report')],string='Report', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def show_report(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx['from_date'] = self.start_date
        ctx['to_date'] = self.end_date
        ctx['company_id'] = self.company_id.id
        if self.report_list == 'expense_report':
            ctx['heading'] = "Expense Report - Detailed [ " + self.start_date + '-' + self.end_date + ' ]'
            return self.with_context(ctx).env['report'].get_action(self, report_name='cmms.cmms_inventory_expense_report_summary', data={})
