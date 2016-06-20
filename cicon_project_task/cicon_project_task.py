from openerp import models, fields, api


class CiconProject(models.Model):
    _inherit = 'project.project'

    parent_id = fields.Many2one('project.project', string="Parent Project", help="Parent Project")

CiconProject()
