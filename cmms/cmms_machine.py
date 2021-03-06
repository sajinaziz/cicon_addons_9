from openerp import models, fields, api, tools
from openerp import _, tools

#To store machine location
class CmmsMachineLocation(models.Model):
    _name = 'cmms.machine.location'
    _description = 'Machine Location'

    name = fields.Char("Location", required=True, help="Current Machine Location Ex: Factory 1,Factory 2")
    company_id = fields.Many2one('res.company', 'Company')

    _sql_constraints = [('uniq_location', 'UNIQUE(name)', "Location Must be unique")]

# To store machine type
class CmmsMachineType(models.Model):
    _name = "cmms.machine.type"
    _description = "Machine Type"
    _log_access = False

    name = fields.Char('Machine Type', size=64, help="Machine Type", required=True)

    _sql_constraint = [("unique_machine_type", "UNIQUE(name)", "Machine Type Must be Unique")]

#To store machine category
class CmmsMachineCategory(models.Model):
    _name = "cmms.machine.category"
    _description = "Machine Category"
    _log_access = False

    name = fields.Char('Machine Category', size=64, help="Machine Category", required=True)

    _sql_constraint = [("unique_machine_categ", "UNIQUE(name)", "Machine Category Must be Unique")]

#To store cmms machine group
class CmmsMachineGroup(models.Model):
    _name = "cmms.machine.group"
    _description = "CMMS Machine Group"
    _log_access = False
    _rec_name = 'code'

    code = fields.Char("Machine Group Code", size=5, help=" Group Code", required=True)
    description = fields.Char("Machine Group Description", size=64, help=" Group Description")

    _sql_constraints = [("unique_group_code", "UNIQUE(code)", "Machine Group Code Must be Unique")]


class CmmsPmScheme(models.Model):
    _name = 'cmms.pm.scheme'
    _description = "Preventive Maintenance Scheme"
    _log_access = False

    name = fields.Char('PM Scheme Name', size=50, required=True)
    pm_tasks_ids = fields.One2many('cmms.pm.task.master', 'pm_scheme_id', "PM Tasks")
    machine_ids = fields.One2many('cmms.machine','pm_scheme_id',"Machine")

    _sql_constraints = [('unique_scheme', 'unique(name)', 'Scheme Must be unique')]


class CmmsMachine(models.Model):
    _name = 'cmms.machine'
    _description = 'CMMS Machines'
    _rec_name = 'code'
    _inherit = ['mail.thread']

    @api.multi
    def _job_order_count(self):
        """" Calculate the total job order count, based on the job order type as breakdown.
        Calulate the total parts cost count."""
        for _rec in self:
            _rec.breakdown_count = 0
            _rec.parts_cost = 0
            _res = self.env['cmms.job.order'].read_group(domain=[('machine_id', '=', _rec.id)], fields=['job_order_type'], groupby='job_order_type')
            for r in _res:
                if r['job_order_type'] == 'breakdown':
                    _rec.breakdown_count = r['job_order_type_count']
            _rec.parts_cost = round(sum(self.env['cmms.store.invoice.line'].search([('machine_id','=',_rec.id)]).mapped('amount')),2)

    @api.multi
    def compute_joborder_open_count(self):
        """" Calculate the total job order pending count, based on the job order type as breakdown. """
        for _rec in self:
            _rec.job_order_open_count = self.env['cmms.job.order'].search_count([('machine_id','=',_rec.id),('job_order_type','=','breakdown'),('state','=','open')])

    #code, store the machine code
    code = fields.Char('Code', size=10, help="Machine Code", required=True, track_visibility='always')
    name = fields.Char('Name', help="Machine Name", required=True)
    #type id, relate to machine type table and store the machine type id
    type_id = fields.Many2one('cmms.machine.type',  string='Type', ondelete="restrict", required=True, track_visibility='onchange')
    #category_id, relate to machine category table and store the machine category
    category_id = fields.Many2one('cmms.machine.category',  string='Category', ondelete="restrict", required=True, track_visibility='onchange')
    #group_id, relate to machine group table and store the machine group names
    group_id = fields.Many2one('cmms.machine.group',  string='Group', ondelete="restrict", required=True, track_visibility='onchange')

    # company id, create a relation to company , store company and set the current logged user company as the default company
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict', required=True,
                                 default=lambda self: self.env.user.company_id, track_visibility='onchange')

    #model, store the machine model name
    model = fields.Char('Model', size=50, help="Machine Model", track_visibility='onchange')
    #supplier id, relate to partner table and store the supplier
    supplier_id = fields.Many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]", help="Supplier")
    mfg_year = fields.Char('MFG Year', size=50, help="Manufacturing Year")
    serial_no = fields.Char('Serial No', size=50, help="Serial No", track_visibility='onchange')
    note = fields.Text('Notes', size=50, help="Machine Note")
    set_code = fields.Char('Set Code', size=8, help="If machine is Part of  Set")
    #condition, store the machine condition like working or not working
    condition = fields.Selection([('working', 'WORKING'), ('not_working', 'NOT WORKING')], 'Condition', required=True, track_visibility='onchange')
    is_machinery = fields.Boolean('Is Machinery', help="If it is real Machine", default=True)
    #unit = fields.Selection([('ton', 'TON'), ('nos', 'Numbers')], string="Unit")
    #state, store the different states
    state = fields.Selection([('working', 'WORKING'), ('pending', 'PENDING'), ('repair', 'UNDER REPAIR'),
                              ('standby', 'STAND BY'), ('unstable', 'UNSTABLE CONDITION')], 'Status',
                             required=True, track_visibility='onchange')
    active = fields.Boolean('Active in System', default=True,   help="Is Machine Active in System")
    is_active = fields.Boolean('Is Active Machine', default=True, help="Is Machine Active or  Stand by", track_visibility='onchange')
    last_machine_code = fields.Char('Last Machine Code',  store=False, help="Show Last Machine Code Created, "
                                                                            "Please Select a group to show !.")
    #pm scheme id, relate to scheme table and store the scheme name
    pm_scheme_id = fields.Many2one('cmms.pm.scheme', string='PM Scheme', track_visibility='onchange')
    #pm task ids, relate to task view table and store the tasks
    pm_task_ids = fields.One2many('cmms.machine.task.view', 'machine_id', readonly=True)
    #spare_part_ids, relate to invoice line  table and store the spare parts
    spare_part_ids = fields.One2many('cmms.store.invoice.line', 'machine_id', readonly=True, string="Parts")
    #job_order_ids, relate to job order table and store the job orders
    job_order_ids = fields.One2many('cmms.job.order', 'machine_id', readonly=True, string="Job Orders")
    breakdown_count = fields.Integer('Breakdowns', compute=_job_order_count)
    parts_cost = fields.Float('Parts Cost', compute=_job_order_count)
    #location id, relate to machine location table and store the location
    location_id = fields.Many2one('cmms.machine.location', string="Location",  track_visibility='onchange')

    job_order_open_count = fields.Integer('Pending Job Orders', compute = compute_joborder_open_count)

    _sql_constraints = [("unique_machine_code", "UNIQUE(code)", "Machine Code Must be Unique")]

    _order = 'set_code'

    @api.onchange('group_id')
    #find out the last stored machine code
    def onchange_group_id(self):
        self.last_machine_code = ''
        if self.group_id:
            dm = [('group_id', '=', self.group_id.id)]
            _machines = self.env['cmms.machine'].search(dm, order='id DESC', limit=1)
            self.last_machine_code = _machines.code

#store pmtask master data
class CmmsPmTaskMaster(models.Model):
    _name = "cmms.pm.task.master"
    _description = "Preventive Maintenance Tasks"

    def _str_hour(self, _duration):
        duration_str ='00:00'
        if _duration > 0:
            _duration_to_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(_duration * 60, 60))
            duration_str = str(_duration_to_hour)
        return duration_str



    @api.multi
    @api.depends('duration')
    def _calc_str_duration(self):
        for rec in self:
            rec.duration_str = self._str_hour(rec.duration)

    name = fields.Char('PM Task Description', size=200, required=True)
    #pm scheme id, relate to scheme table and store the pm scheme names
    pm_scheme_id = fields.Many2one('cmms.pm.scheme', 'PM Scheme', required=True)
    #interval id, relate to pm interval table and store the interval
    interval_id = fields.Many2one('cmms.pm.interval', "Interval",required=True)
    #action by, store the action like operator or technician
    action_by = fields.Selection([('operator', 'Operator'), ('technician', 'Technician')], string='Action By', default='technician')
    active = fields.Boolean('Is Active', default=True)
    material_required = fields.Text('Materials / Tools Required')
    #approx. cost , approximate cost for performing the task.
    approx_cost = fields.Float('Approx. Cost', digits=(10, 2), help="Approx. Cost to perform this Task")
    duration = fields.Float('Duration', digits=(4, 2), help="Approx. Duration to perform Task")
    duration_str = fields.Char(string='Duration', store=False, compute=_calc_str_duration)

    _order = 'pm_scheme_id,interval_id'


class CmmsMachineTaskView(models.Model):
    _name = 'cmms.machine.task.view'
    _description = "Machine Task View"
    _auto = False
    _order = 'interval_id'

    #find out next task  run date and task completed date
    def _get_next_date(self):
        _sch_obj = self.env['cmms.pm.schedule.master']
        _task_line_obj = self.env['cmms.pm.task.job.order.line']
        for rec in self:
            _schs = _sch_obj.search([('machine_ids', 'in', rec.machine_id.id), ('interval_id', '=', rec.interval_id.id)], limit=1)
            rec.next_date = _schs.next_date
            _task_line = _task_line_obj.search([('pm_task_id', '=', rec.task_id.id), ('job_order_id.machine_id', '=', rec.machine_id.id), ('state', '=', 'done')], order='date_completed desc', limit=1)
            rec.last_date = _task_line.date_completed

    machine_id = fields.Many2one('cmms.machine', string="Machine", readonly=True)
    task_id = fields.Many2one('cmms.pm.task.master', string="Task", readonly=True)
    pm_scheme_id = fields.Many2one('cmms.pm.scheme', related="machine_id.pm_scheme_id", string="PM Scheme", readonly=True)
    interval_id = fields.Many2one('cmms.pm.interval', string="Interval", readonly=True)
    next_date = fields.Date('Next Run Date', readonly=True, compute=_get_next_date)
    last_date = fields.Date('Last Run Date', readonly=True, compute=_get_next_date)

    def _from(self):
        from_str = """
        CMMS_MACHINE M INNER JOIN cmms_pm_task_master T ON M.pm_scheme_id = T.pm_scheme_id
        """
        return from_str

    def _select(self):
        select_str = """
        SELECT (TEXT(M.id) || T.ID)::INT as id ,M.id AS machine_id , T.ID as task_id  , T.interval_id"""
        return select_str

    def _group_by(self):
        group_by_str = """ORDER BY T.interval_id """
        return group_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))













