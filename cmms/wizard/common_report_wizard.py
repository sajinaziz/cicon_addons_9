from openerp import models, fields, api
from datetime import datetime,date,timedelta
import calendar


class CmmsCommonReportWizard(models.TransientModel):
    _name = 'cmms.common.report.wizard'
    _description = "CMMS Reports"


    @api.onchange('report_by')
    def _get_date(self):
        today = datetime.today() # store the current date(today's date)
        first_day = today.replace(day=1) # find the first day of the current date or current month
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]) # find the last day of the current date or current month
        week_day = (today.weekday()+1)% 7 # find the current day number: 1=monday, 6= saturday

        saturday = today - timedelta(7 + week_day - 6) #find the current day before  saturday  and convert to the date format
        this_saturday = '{:%Y-%m-%d}'.format(saturday)
        if self.report_by == "this_month":
            self.start_date = first_day # assign this month first day and last day
            self.end_date = last_day
        elif self.report_by == "last_month":
            last_day_prev_month = first_day - timedelta(days=1) # find  the last day of the previous month or last month
            first_day_prev_month = last_day_prev_month.replace(day=1) # find the first day of the previous month or last month
            self.start_date = first_day_prev_month # assign  first day and last day of the previous month
            self.end_date = last_day_prev_month
        elif self.report_by == "this_week":
            self.start_date = this_saturday # assign  the current day before  saturday and current day of this week
            self.end_date = today
        elif self.report_by == "last_week":
            sat_day = (saturday.weekday() + 1) % 7  # find the last week  saturday number
            self.start_date = saturday - timedelta(7 + sat_day - 6) # find  and assign the last saturday
            self.end_date = this_saturday #assign  the current day before  saturday


    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    report_by = fields.Selection([('this_month','This Month'),('this_week','This Week'),('last_month','Last Month'),('last_week','Last Week')],string='Report By')
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
