from openerp import models, osv, fields, api
from dateutil import parser


class cicon_prod_order(models.Model):
    _name = 'cicon.prod.order'
    _inherit = ['mail.thread']
    _description = 'CICON Production Order'

    @api.depends('product_lines')
    def _get_tonnage(self):
        for rec in self:
            rec.total_tonnage = sum([r.product_qty for r in rec.product_lines if r.unit_id.name == 'TON'])
            _temp = []
            for line in rec.product_lines:
                _temp.extend(line.mapped('product_tmpl_id')._ids)
                # _temp_str.extend([x.name for x in line.product_tmpl_id])
            rec.template_ids = list(set(_temp))
            if rec.template_ids:
                rec.template_str = ','.join([x.name for x in rec.template_ids])

    name = fields.Char('Armaor Code / Internal Ref.', size=12, required=True, track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    revision_no = fields.Integer('Revision No', required=True, readonly=True, track_visibility="onchange", states={'pending': [('readonly', False)]})
    description = fields.Char('Description', track_visibility="onchange", readonly=True, states={'pending': [('readonly', False)]})
    remarks = fields.Text('Remarks')
    customer_order_id = fields.Many2one ('cicon.customer.order', "Customer Order", readonly=True, states={'pending': [('readonly', False)]})
    required_date = fields.Date('Required Date', readonly=True, states={'pending': [('readonly', False)]})
    product_lines = fields.One2many('cicon.prod.order.line', 'prod_order_id', string="Products", readonly=True, states={'pending': [('readonly', False)]})
    tag_count = fields.Integer('Tags', readonly=True, states={'pending': [('readonly', False)]})
    bar_mark_count = fields.Integer('Bar Marks', readonly=True, states={'pending': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='customer_order_id.project_id.partner_id', string='Customer', readonly=True)
    project_id = fields.Many2one('res.partner.project', related='customer_order_id.project_id', string='Project', readonly=True)
    state = fields.Selection([('pending', 'New'), ('progress', 'In Progress'), ('transit', 'Transit'),
                              ('delivered', 'Delivered'), ('cancel', 'Cancel'),
                              ('hold', 'On Hold'), ('transfer', 'Transfer')], default='pending',  string='Status', track_visibility="onchange")
    total_tonnage = fields.Float(compute=_get_tonnage, digits=(10, 3), store=True, string='Total Tonnage')
    created_user = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user.id)
    # prod_note = fields.Char(store=False, string="Warning", readonly=True)
    planned_date = fields.Date('Planned Date')
    plan_id = fields.Many2one('cicon.prod.plan', string="Production Plan")
    sequence = fields.Integer('Sequence')
    template_ids = fields.Many2many('product.template', compute=_get_tonnage, store=False, string='Products')
    template_str = fields.Char(compute=_get_tonnage,store=False, string='Products')
    load = fields.Integer("Load Priority")

    _order = "required_date desc"

    @api.multi
    def set_deliver(self):
        return self.write({'state': 'delivered'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def set_pending(self):
        return self.write({'state': 'pending'})

    #Removed for Test In Production
    # @api.multi
    # def set_transit(self):
    #     return self.write({'state': 'transit'})

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=('%s/C') % (self.name))
        default.update(state='pending')
        return super(cicon_prod_order, self).copy(default)

    @api.model
    def plan_groups(self, present_ids, domain, **kwargs):
        _plans = self.env['cicon.prod.plan'].search([('state', '!=', 'done')]).name_get()
        return _plans, None

    _group_by_full = {
        'plan_id': plan_groups,
    }

    # @api.one
    # def write(self, vals):
    #     if vals.get('planned_date:day'):
    #         _day_val = vals.pop('planned_date:day')
    #         _date_val = parser.parse(_day_val)
    #         vals.update({'planned_date': _date_val.strftime('%Y-%m-%d')})
    #     return super(cicon_prod_order, self).write(vals)

    _sql_constraints = [('unique_code', 'UNIQUE(name,revision_no)', 'Code By Revision Must be unique')]


cicon_prod_order()


class cicon_prod_order_line(models.Model):
    _name = 'cicon.prod.order.line'
    _description = "Production Order Line"

    @api.one
    @api.depends('product_id')
    def _get_dia_value(self):
        self.dia_attrib_value_id = None
        if self.product_id:
            for a in self.product_id.attribute_value_ids:
                if a.attribute_id.name == "Diameter":
                    self.dia_attrib_value_id = a.id
                    break
                elif a.attribute_id.name == "Reduce Coupler Type":
                    self.dia_attrib_value_id = a.id
                    break

    prod_order_id = fields.Many2one('cicon.prod.order', string="Production Order")
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', required=True)
    product_qty = fields.Float('Quantity', digits=(10, 3), required=True)
    unit_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit', readonly=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', readonly=True)
    dia_attrib_value_id = fields.Many2one('product.attribute.value', compute=_get_dia_value, string='Diameter', store=True)

cicon_prod_order_line()


class cicon_prod_plan(models.Model):
    _name = 'cicon.prod.plan'
    _description = "CICON Production Plan"
    _rec_name = 'display_name'

    @api.multi
    def _display_name(self):
        for rec in self:
            rec.display_name = rec.plan_date + '/' + str(rec.work_shift).upper()

    display_name = fields.Char(string="Name", compute=_display_name)
    plan_date = fields.Date('Plan Date', required=True, default=fields.Date.context_today)
    work_shift = fields.Selection([('day', 'Day'), ('night', 'Night')], required=True, string="Work Shift")
    prod_order_ids = fields.One2many('cicon.prod.order','plan_id', string="Orders")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Complete')], default="pending", string="Status" , required=True)

    _sql_constraints = [('uniq_plan', 'UNIQUE(plan_date,work_shift)', "Unique Plan !")]

cicon_prod_plan()


class cicon_customer_order(models.Model):
    _inherit = 'cicon.customer.order'

    def _get_prod_order_count(self):
        for rec in self:
            rec.prod_order_count = len(self.prod_order_ids) or 0

    prod_order_ids = fields.One2many('cicon.prod.order', 'customer_order_id', string='Production Orders', copy=False)
    prod_order_count = fields.Integer('Production Order Count', compute=_get_prod_order_count, store=False, readonly=True)

    @api.multi
    def order_cancel(self):
        self.ensure_one()
        #TODO: Check for production Orders status
        if self.prod_order_count == 0:
            self.write({'state': 'cancel'})
        else:
            raise UserWarning("Please Cancel Production Order !")


cicon_customer_order()


