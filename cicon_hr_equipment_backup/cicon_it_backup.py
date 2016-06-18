from openerp import models,fields,api
from datetime import datetime
from openerp.exceptions import ValidationError

_RRULE_TYPE = [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
            ]


class CiconItJobCategory(models.Model):
    _name = 'cicon.it.job.category'
    _description = " Category"

    name = fields.Char('Category', required=True)
    parent_id = fields.Many2one('cicon.it.job.category', string="Parent")

    _sql_constraints = [('uniq_categ', 'UNIQUE(name)', 'Unique Category')]

    @api.constrains('parent_id')
    def _check_recursion(self):
        """
        Verifies that there is no loop in a hierarchical structure of records,
        by following the parent relationship using the **parent** field until a loo        is detected or until a top-level record is found.

        :param cr: database cursor
        :param uid: current user id
        :param ids: list of ids of records to check
        :param parent: optional parent field name (default: ``self._parent_name = parent_id``)
        :return: **True** if the operation can proceed safely, or **False** if an infinite loop is detected.
        """
        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % ('parent_id', self._table)
        for rec in self:
            current_id = rec.id
            while current_id is not None:
                self._cr.execute(query, (current_id,))
                result = self._cr.fetchone()
                current_id = result[0] if result else None
                if current_id == rec.id:
                    raise ValidationError("Cannot create recursive Category !")


class CiconItJobType(models.Model):
    _name = 'cicon.it.job.type'
    _description = " Job Type"

    name = fields.Char('Job Type', required=True)

    _sql_constraints = [('uniq_job_type', 'UNIQUE(name)', 'Unique Job Type')]


class CiconItSupportTeam(models.Model):
    _name = 'cicon.it.support.team'
    _description = "Support Team"

    name = fields.Char('Team', required=True)
    team_lead_id = fields.Many2one('res.users', string='Team Lead', required=True)
    member_ids = fields.Many2many('res.users', 'cicon_it_team_user_rel','team_id', 'user_id', string="Members")

    _sql_constraints = [('uniq_team', 'UNIQUE(name,team_lead_id)', 'Unique Team')]


class CiconItJobProfile(models.Model):
    _name = 'cicon.it.job.profile'
    _description = "Job Profile"

    @api.model
    def _count_tasks(self):
        for rec in self:
            rec.task_count = len(rec.job_task_ids)

    name = fields.Char('Profile Name', required=True)
    user_id = fields.Many2one('res.users', required=True, string="Created", default=lambda self: self.env.user)
    category_id = fields.Many2one('cicon.it.job.category', string="Category", required=True)
    job_task_ids = fields.One2many('cicon.it.job.task', 'job_profile_id', string="Jobs")
    task_log_ids = fields.One2many('cicon.it.job.task.log', 'job_profile_id', string="Logs")
    notes = fields.Text('Notes')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Important'),
                                 ('4', 'Very Important')], string='Priority')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    task_count = fields.Integer('Task Count', compute=_count_tasks, store=False)
    delegated_user_ids = fields.Many2many('res.users', 'cicon_it_job_profile_user_rel','job_profile_id', 'user_id', string="Delegated User",
                                          help="Who all Can manage jobs in this Profile")

    _sql_constraints = [('uniq_profile', 'UNIQUE(name,company_id)', 'Unique Name per Company')]


class CiconItJobTask(models.Model):
    _name = 'cicon.it.job.task'
    _description = 'Job Task'

    @api.multi
    def _get_last_update(self):
        for rec in self:
            if rec.job_log_ids:
                _last_log = rec.job_log_ids.browse(max(rec.job_log_ids.filtered(lambda record: record.state == 'done')._ids))
                rec.last_updated = _last_log.log_datetime

    name = fields.Char('Task', required=True)
    rrule_type = fields.Selection(_RRULE_TYPE, string='Recurrency', requied=True)
    job_profile_id = fields.Many2one('cicon.it.job.profile', string="Job Profile", required=True)

    equipment_ids = fields.Many2many('hr.equipment','cicon_it_task_equip_rel', 'job_task_id', 'equipment_id', string='Related Equipments')
    source_type_ids = fields.Many2many('cicon.it.job.type', 'cicon_it_task_source_job_type_rel', 'job_task_id', 'job_type_id', string="Source")
    dest_type_ids = fields.Many2many('cicon.it.job.type','cicon_it_task_dest_job_type_rel', 'job_task_id', 'job_type_id', string="Destination")
    last_updated = fields.Datetime('Last Update', readonly=True, compute=_get_last_update, store=False)
    job_log_ids = fields.One2many('cicon.it.job.task.log', 'job_task_id', string="Logs")
    notes = fields.Text('Notes')
    assign_type = fields.Selection([('team', 'Team'), ('user', 'User')], string='Task Assign',default='user')
    assign_team_id = fields.Many2one('cicon.it.support.team', string='Assigned Team')
    assign_user_id = fields.Many2one('res.users', string="Assigned To")
    user_id = fields.Many2one('res.users', string='Created', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id)

    active = fields.Boolean('Active', default=True)

    _sql_constraints = [('uniq_job', 'UNIQUE(job_profile_id,name)', 'Unique Job')]


class CiconItJobTaskLog(models.Model):
    _name = 'cicon.it.job.task.log'
    _description = "Task Log"

    user_id = fields.Many2one('res.users', string="User", required=True, default=lambda self: self.env.user)
    state = fields.Selection([('pending', 'Pending'), ('fail', 'Failed'), ('done', 'Done')], string='Status',
                             default='done', required=True)
    job_task_id = fields.Many2one('cicon.it.job.task', string=" Job")
    job_profile_id = fields.Many2one('cicon.it.job.profile', related="job_task_id.job_profile_id", store=True, readonly=True, string="Job Profile")
    log_datetime = fields.Datetime('Log Date & Time', required=True, default=fields.Datetime.now)

    note = fields.Char('Note')

    @api.multi
    def add_log(self):
        self.ensure_one()
        return True

    @api.constrains('log_datetime')
    def _check_datetime(self):
        if self.log_datetime > datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
            raise ValidationError("Log Date cannot be a future time !")


