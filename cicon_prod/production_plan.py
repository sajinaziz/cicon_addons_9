from openerp import models, osv, fields, api
from openerp.exceptions import UserError


class cicon_prod_plan(models.Model):
    _name = 'cicon.prod.plan'
    _description = "CICON Production Plan"
    _rec_name = 'display_name'

    @api.multi
    def _display_name(self):
        for rec in self:
            rec.display_name = rec.plan_date + '/' + str(rec.work_shift).upper()
            rec.order_count_not_planned  =  self.env['cicon.prod.order'].search_count([('plan_load_id', '=', False),
                                                                                       ('state', 'not in', ['delivered', 'cancel', 'transfer', 'hold'])])

    @api.multi
    @api.depends('plan_load_ids')
    def _get_prd_orders_load(self):
        for rec in self:
            if rec.plan_load_ids:
                rec.prod_order_ids = rec.plan_load_ids.mapped('prod_order_ids')

    @api.one
    def arrange_seq(self):
        if self.plan_load_ids:
            _loads = self.plan_load_ids.mapped('load')
            if _loads:
                _range = list(range(1, max(_loads) + 1, 1))
                _miss = list(set(_range).difference(_loads))
                if _miss:
                    _recs_next = self.plan_load_ids.filtered(lambda a: a.load > min(_miss)).sorted(key= lambda x:x.load)
                    _val_min = min(_miss)
                    for _rec in _recs_next:
                        _rec.load = _val_min
                        _val_min += 1

    display_name = fields.Char(string="Name", compute=_display_name)
    plan_date = fields.Date('Plan Date', required=True, default=fields.Date.context_today)
    work_shift = fields.Selection([('day', 'Day'), ('night', 'Night')], required=True, string="Work Shift")
    plan_load_ids = fields.One2many('cicon.prod.plan.load', 'prod_plan_id', string="Loading")
    prod_order_ids = fields.Many2many('cicon.prod.order', compute=_get_prd_orders_load, store=False, readonly=True)
    note = fields.Char(string="Notes")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Complete')], default="pending", string="Status" , required=True)
    order_count_not_planned = fields.Integer(store=False ,compute=_display_name)

    _sql_constraints = [('uniq_plan', 'UNIQUE(plan_date,work_shift)', "Unique Plan !")]


class cicon_prod_plan_load(models.Model):
    _name = 'cicon.prod.plan.load'
    _description = "Load Priority"
    _rec_name = 'display_name'

    @api.multi
    @api.depends('load')
    def _display_name(self):
        for rec in self:
            rec.display_name = 'T' + str(rec.load)

    def _calc_load(self):
        _plan_id = self.env.context.get('default_prod_plan_id')
        _loads = self.env['cicon.prod.plan'].browse(_plan_id).plan_load_ids.mapped('load')
        if _loads:
            _range = list(range(1, max(_loads) + 1, 1))
            _miss = list(set(_range).difference(_loads))
            if _miss:
                return min(_miss)
            else:
                return max(_loads) + 1
        else:
            return 1

    @api.multi
    def _get_order_code(self):
        for rec in self:
            if rec.prod_order_ids:
                _codes = ', '.join(rec.prod_order_ids.mapped('name'))
                _tons = sum(rec.prod_order_ids.mapped('total_tonnage'))
                rec.prod_order_codes = _codes
                rec.prod_order_tonnage = _tons

    @api.depends('search_prod_order_ids')
    def _get_customer(self):
        self.ensure_one()
        if self.search_prod_order_ids:
            _partner = self.search_prod_order_ids.mapped('partner_id')
            self.search_partner_id = _partner

    display_name = fields.Char("Load #", compute=_display_name, store=True)
    load = fields.Integer('Load Priority', required=True, default=_calc_load)
    note = fields.Char(string="Notes")

    search_prod_order_ids = fields.Many2many('cicon.prod.order',  string="Code Search",
                                           domain="[('plan_load_id','=',False),('state','not in',['delivered','cancel','transfer','hold'])]")
    search_partner_id = fields.Many2one('res.partner', compute=_get_customer, string="Customer Search", domain="[('customer','=',True)]")

    prod_order_ids = fields.One2many('cicon.prod.order', 'plan_load_id',
                                      string='Production Orders')
    prod_order_codes = fields.Char(compute=_get_order_code, string="Codes",  store=False)
    prod_order_tonnage = fields.Float(compute=_get_order_code, string="Tonnage", digits=(10, 3), store=False)

    prod_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="Production Plan", ondelete='restrict')

    _sql_constraints = [('uniq_plan_load', 'UNIQUE(load,prod_plan_id)', "Unique Plan Load !")]

    _order = 'load'

    @api.onchange('search_prod_order_ids')
    def change_search_code(self):
        if self.search_prod_order_ids:
            _ids = [(4, o.id) for o in self.search_prod_order_ids]
            self.prod_order_ids = _ids
        else:
            self.prod_order_ids =[]

            # _customer = self.search_prod_order_ids.mapped('partner_id')
            # if len(_customer) == 1:
            #     self.search_partner_id = _customer

    @api.onchange('search_partner_id')
    def change_partner(self):
        _res = {}
        if self.search_partner_id:
            _res = {
                'domain': {'search_prod_order_ids': [('partner_id', '=', self.search_partner_id.id),
                                                     ('plan_load_id', '=', False), ('state', 'not in', ['delivered', 'cancel', 'transfer','hold'])]}}
        else:
            _res = {
                'domain': {'search_prod_order_ids': [('plan_load_id', '=', False),
                                                     ('state', 'not in', ['delivered', 'cancel', 'transfer', 'hold'])]}}
        return _res

    @api.onchange('prod_order_ids')
    def change_prod_order(self):
        if self.prod_order_ids:
            _res = {}
            _customers = self.prod_order_ids.mapped('partner_id')
            if len(_customers) == 1:
                self.search_partner_id = _customers
            if len(_customers) > 1:
                _res = {'warning': {'title': 'Error', 'message': "Different Customers in same load !"}}
            return _res

    @api.one
    def add_load(self):
        return True

    @api.multi
    def _check_customer(self):
        for rec in self:
            _customers = rec.prod_order_ids.mapped('partner_id')
            if len(_customers) > 1:
                return False
            else:
                return True

    _constraints = [
        (_check_customer, 'Different Customers found !', ['prod_order_ids']),
    ]


class cicon_prod_order(models.Model):
    _inherit = 'cicon.prod.order'

    plan_load_id = fields.Many2one('cicon.prod.plan.load', string="Plan Load", ondetele='set null', track_visibility='onchange')
    prod_plan_id = fields.Many2one('cicon.prod.plan', related='plan_load_id.prod_plan_id', store=True,
                                   string="Plan", ondetele='set null', track_visibility='onchange')
    plan_load = fields.Integer(related='plan_load_id.load', store=True)

