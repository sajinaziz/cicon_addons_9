from openerp import models, api
from calendar import Calendar


class PmSchPlanReport(models.AbstractModel): # Report File Name
    _name = 'report.cmms.cmms_pm_plan_report_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.cmms_pm_plan_report_template')
        _docs = self._get_date_list()
        docargs = {
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
            'get_pm_detail': self._get_pm_details
        }
        return report_obj.render('cmms.cmms_pm_plan_report_template', docargs)

    def _get_date_list(self):
        _cal = Calendar()
        _date = list(_cal.itermonthdates(self._context.get('rpt_year'), self._context.get('rpt_month')))
        return _date

    def _get_pm_details(self, _pm_date):
        _pm_list = {}
        if _pm_date:
            _sch_obj = self.env['cmms.pm.schedule.master']
            _sch_recs = _sch_obj.search([('next_date', '=', _pm_date)])
            if _sch_recs:
                _interval = _sch_recs.mapped('interval_id')
                for _intv in _interval:
                    _sch_intv = _sch_recs.filtered(lambda r: r.interval_id.id == _intv.id)
                    _machines = _sch_intv.mapped('machine_ids')
                    _m_task_count = {}
                    for m in _machines:
                        _sch_intv_machine = _sch_intv.filtered(lambda r: m in r.machine_ids)
                        _m_task_count[m.code] = len(_sch_intv_machine.mapped('pm_task_ids'))
                    _pm_list[_intv.name] = _m_task_count
        return _pm_list

PmSchPlanReport()