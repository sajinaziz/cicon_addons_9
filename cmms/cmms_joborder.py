from openerp import models, fields, api
# from openerp.exceptions import Warning


JOB_ORDER_TYPE = [('breakdown', 'BREAKDOWN'), ('preventive', 'PREVENTIVE'), ('general', 'GENERAL')]


class CmmsJobCategory(models.Model):
    _name = "cmms.job.category"
    _description = "Job Category"
    _log_access = False

    name = fields.Char('Job Category')

    _sql_constraint = [("unique_name", "unique(name)", "Job Category must be Unique")]

CmmsJobCategory()


class CmmsJobOrder(models.Model):
    _name = "cmms.job.order"
    _description = "CMMS Job Order"
    _inherit = ['mail.thread']

    #Inverse Sample for Job Order Code
    # def _set_job_code(self):
    #     for rec in self:
    #         if rec.job_order_code_id:
    #             rec.job_order_code_id.write({'created': True, 'cancelled': False})
    @api.model
    def _get_default_status(self):
        _status = self.env['cmms.job.order.status'].search([('sequence', '>', '0')], order='sequence', limit=1)
        if _status:
            return _status

    job_order_code_id = fields.Many2one("cmms.job.order.code",
                                        domain="[('job_order_type','=',job_order_type),('printed','=',True),"
                                               "('created','=',False),('cancelled','=',False)]")
    name = fields.Char("Code", required=True, track_visibility='always')
    job_order_type = fields.Selection(JOB_ORDER_TYPE, "JobOrderType", required=True)
    machine_id = fields.Many2one('cmms.machine', 'Machine', required=True, readonly=True, states={'open': [('readonly', False)]})
    machine = fields.Char('Machine Name', related='machine_id.name', store=False, readonly=True)
    machine_type = fields.Many2one('cmms.machine.type', string='Machine Type', related='machine_id.type_id', store=False, readonly=True)
    job_order_date = fields.Date('Job Order Date', required=True, readonly=True,
                                 states={'open': [('readonly', False)]}, track_visibility='onchange')
    breakdown_datetime = fields.Datetime('Breakdown Time', readonly=True,
                                         states={'open': [('readonly', False)]})
    reported_datetime = fields.Datetime('Reported Date', readonly=True,
                                        states={'open': [('readonly', False)]})
    description = fields.Char(string='Description', size=200, readonly=True,
                              states={'open': [('readonly', False)]})
    job_category_id = fields.Many2one('cmms.job.category', 'Job Category', readonly=True,
                                      states={'open': [('readonly', False)]})
    company_id = fields.Many2one('res.company', related='machine_id.company_id', string="Company",
                                 store=True, readonly=True)
    reported_by = fields.Char("Reported/Operated By", size=50, readonly=True,
                              states={'open': [('readonly', False)]})
    foreman = fields.Char('Foreman In charge', size=50, readonly=True,
                          states={'open': [('readonly', False)]})
    technician = fields.Char('Maintenance In charge', size=50, readonly=True,
                             states={'open': [('readonly', False)]})
    reason = fields.Text('Reason', size=500, readonly=True,
                         states={'open': [('readonly', False)]})
    corrective_action = fields.Text('Action', size=500, readonly=True,
                                    states={'open': [('readonly', False)]})
    service = fields.Boolean('Service Assistance', readonly=True,
                             states={'open': [('readonly', False)]})
    priority = fields.Selection([('low', 'LOW PRIORITY'), ('normal', 'PRIORITY REPAIR'),
                                 ('high', 'PRIORITY NEXT DAY'), ('highest', 'URGENT REPAIR')], "Priority", readonly=True,
                                states={'open': [('readonly', False)]}, default='low', track_visibility='onchange')
    attended_by = fields.Char('Attended By', size=100, readonly=True,
                              states={'open': [('readonly', False)]})

    work_start_datetime = fields.Datetime('Work Started', readonly=True,
                                          states={'open': [('readonly', False)]})
    work_end_datetime = fields.Datetime('Work End', readonly=True,
                                        states={'open': [('readonly', False)]})

    status_id = fields.Many2one('cmms.job.order.status', string="Status", default=_get_default_status, track_visibility='onchange')
    state = fields.Selection(related='status_id.state_name', string="State",
                             store=True, readonly=True)

    sch_pm_task_ids = fields.One2many('cmms.pm.task.job.order.line', 'job_order_id', string="PM Tasks")
    spare_part_ids = fields.One2many('cmms.store.invoice.line', 'job_order_id', readonly=True, string="Parts")

    _order = 'job_order_date desc'

    _sql_constraints = [("unique_code", "unique(name)", "Job Order Code must be Unique")]

    #("unique_machine_job", "unique(machine_id,job_order_date,job_order_type)", "Job Order Machine/Day/Job Type")

    @api.onchange('job_order_code_id')
    def _set_code(self):
        if self.job_order_code_id:
            self.name = self.job_order_code_id.name

    @api.onchange('job_order_type')
    def _get_job_code(self):
        if self.job_order_type:
            _last_rec = self.search([], order='id desc', limit=1)
            _last_id = _last_rec.job_order_code_id.id or 0
            _latest_rec = self.env['cmms.job.order.code'].search([('printed', '=', True), ('created', '=', False), ('cancelled', '=', False), ('company_id', '=', self.env.user.company_id.id), ('job_order_type', '=',  self.job_order_type), ('id', '>', _last_id)], order='id',   limit=1)
            self.job_order_code_id = _latest_rec.id
            self.name = _latest_rec.name

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.job_order_code_id:
                rec.job_order_code_id.write({'cancelled': True, 'created': False})
        res = super(CmmsJobOrder, self).unlink()
        return res

    @api.model
    def create(self, vals):
        res = super(CmmsJobOrder, self).create(vals)
        self.job_order_code_id.write({'cancelled': False, 'created': True})
        return res

    @api.multi
    def print_job_order(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'cmms.report_job_order_cmms')

CmmsJobOrder()


class CmmsJobOrderStatus(models.Model):
    _name = "cmms.job.order.status"
    _description = "Job Order Status"

    name = fields.Char('Status', required=True)
    state_name = fields.Selection([('open', 'Pending'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Completed')], 'State', default='open', required=True)
    sequence = fields.Integer('Sequence')
    fold = fields.Boolean('Fold', default=False)

    _order = 'sequence'

    _sql_constraints = [('uniq_status', 'UNIQUE(name)', 'Status Should be Unique!')]

CmmsJobOrderStatus()


class CmmsJobOrderCode(models.Model):
    _name = "cmms.job.order.code"
    _description = "Job Order Code"

    name = fields.Char('Job Order Code', size=12, required=True)
    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type", required=True)
    created = fields.Boolean('Is Created')
    printed = fields.Boolean('Is Printed')
    cancelled = fields.Boolean('Is Cancelled')
    company_id = fields.Many2one('res.company', "Company", required=True)

    _sql_constraint = [("unique_name", "unique(name)", "Job Order Code must be Unique")]

CmmsJobOrderCode()


class CmmsPmTaskJobOrderLine(models.Model):
    _name = 'cmms.pm.task.job.order.line'
    _description = "PM Job Order Tasks"

    job_order_id = fields.Many2one('cmms.job.order', string="Job Order")
    pm_task_id = fields.Many2one('cmms.pm.task.master', string="PM Task")
    interval_id = fields.Many2one('cmms.pm.interval', related='pm_task_id.interval_id', string='Interval', store=False, readonly=True)
    machine_id = fields.Many2one('cmms.machine', ralated='job_order_id.machine_id', string="Machine", store=False)
    date_completed = fields.Date('Completed Date', required=False, readonly=True, states={'done': [('readonly', False), ('required', True)]})
    state = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ('cancel', 'Cancelled')],
                             string="State", default='pending')
    remarks = fields.Char('Remarks')

    @api.onchange('state')
    def _change_state(self):
        if self.state == 'done':
            if not self.date_completed:
                self.date_completed = fields.Date.today()

CmmsPmTaskJobOrderLine()


