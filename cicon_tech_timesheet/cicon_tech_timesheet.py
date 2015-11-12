from openerp import models, fields, api


class CicTechSubmittalRevision(models.Model):
    _inherit = 'tech.submittal.revision'

    task_project_id = fields.Many2one('project.project', readonly=True, related='job_site_id.project_id', store=False)
    task_id = fields.Many2one('project.task', string="Task")

CicTechSubmittalRevision()


class SubmittalDocumentRevision(models.Model):
    _inherit = 'tech.submittal.document.revision'

    task_id = fields.Many2one('project.task', readonly=True, related='revision_id.task_id', store=False)
    analytic_account_id = fields.Many2one('account.analytic.account', related='task_id.project_id.analytic_account_id', store=False, readonly=True)
    task_time_sheet_id = fields.Many2one('account.analytic.line',  string="Time Sheet")


SubmittalDocumentRevision()


