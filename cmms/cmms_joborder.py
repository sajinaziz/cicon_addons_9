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

    #TODO : Implement Discuss module mail.thread

    #Inverse Sample for Job Order Code
    # def _set_job_code(self):
    #     for rec in self:
    #         if rec.job_order_code_id:
    #             rec.job_order_code_id.write({'created': True, 'cancelled': False})

    job_order_code_id = fields.Many2one("cmms.job.order.code",
                                        domain="[('job_order_type','=',job_order_type),('printed','=',True),"
                                               "('created','=',False),('cancelled','=',False)]")
    name = fields.Char("Code", required=True)

    job_order_type = fields.Selection(JOB_ORDER_TYPE, "JobOrderType", required=True)

    machine_id = fields.Many2one('cmms.machine', 'Machine', required=True, readonly=True, states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    machine = fields.Char('Machine Name', related='machine_id.name', store=False, readonly=True)

    machine_type = fields.Many2one('cmms.machine.type', string='Machine Type', related='machine_id.type_id', store=False, readonly=True)

    job_order_date = fields.Date('Job Order Date', required=True, readonly=True,
                                 states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    breakdown_datetime = fields.Datetime('BreakdownTime', readonly=True,
                                         states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    reported_datetime = fields.Datetime('ReportedDate', readonly=True,
                                        states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    description = fields.Char(string='Description', size=200, readonly=True,
                              states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    job_category_id = fields.Many2one('cmms.job.category', 'JobCategory', readonly=True,
                                      states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    company_id = fields.Many2one('res.company', related='machine_id.company_id', string="Company",
                                 store=True, readonly=True)

    state = fields.Selection([('new', 'New'), ('open', 'Pending'), ('observation', 'Observation'),
                              ('waiting_info', 'Waiting For Technical Info'),
                              ('waiting_parts', 'Waiting For Spare Parts'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Completed')], 'State', readonly=False, default='new')

    reported_by = fields.Char("Reported By", size=50, readonly=True,
                              states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    foreman = fields.Char('Foreman In charge', size=50, readonly=True,
                          states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    technician = fields.Char('MaintenanceIncharge', size=50, readonly=True,
                             states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    reason = fields.Text('Reason', size=500, readonly=True,
                         states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    corrective_action = fields.Text('Action', size=500, readonly=True,
                                    states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    service = fields.Boolean('Service Assistance', readonly=True,
                             states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    priority = fields.Selection([('low', 'LOW PRIORITY'), ('normal', 'PRIORITY REPAIR'),
                                 ('high','PRIORITY NEXT DAY'), ('highest','URGENT REPAIR')], "Priority", readonly=True,
                                states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    attended_by = fields.Char('AttendedBy', size=100, readonly=True,
                              states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    work_start_datetime = fields.Datetime('WorkStartDateTime', readonly =True,
                                          states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    work_end_datetime = fields.Datetime('WorkEndDateTime', readonly=True,
                                        states={'open': [('readonly', False)], 'new': [('readonly', False)]})

    sch_pm_task_ids = fields.One2many('cmms.pm.task.job.order.line', 'job_order_id', string="PM Tasks")

    spare_parts_ids = fields.One2many('cmms.store.invoice.line', 'job_order_id', string="Spare Parts", readonly=True)

    _order = 'job_order_date desc'

    _sql_constraints = [("unique_code", "unique(name)", "Job Order Code must be Unique"),
                        ]

    #TODO: Check if it is practical
    #("unique_machine_job", "unique(machine_id,job_order_date,job_order_type)", "Job Order Machine/Day/Job Type")

    @api.onchange('job_order_code_id')
    def _set_code(self):
        if self.job_order_code_id:
            self.name = self.job_order_code_id


    @api.onchange('job_order_type')
    def _get_job_code(self):
        if self.job_order_type:
            _last_rec = self.search([], order='id desc', limit=1)
            _last_id = _last_rec.job_order_code_id.id or 0
            _latest_rec = self.env['cmms.job.order.code'].search([('printed', '=', True), ('created', '=', False), ('cancelled', '=', False), ('company_id', '=', self.env.user.company_id.id),('job_order_type', '=',  self.job_order_type), ('id', '>', _last_id)], order='id',   limit=1)
            self.job_order_code_id = _latest_rec.id

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


CmmsJobOrder()


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
    state = fields.Selection([('pending', 'Pending'), ('done', 'Done')], string="State", default='pending')

    @api.onchange('state')
    def _change_state(self):
        if self.state == 'done':
            if not self.date_completed:
                self.date_completed = fields.Date.today()

CmmsPmTaskJobOrderLine()


