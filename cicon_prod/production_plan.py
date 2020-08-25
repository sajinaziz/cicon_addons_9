from openerp import models, osv, fields, api
from openerp.exceptions import UserError
from datetime import datetime
import xlsxwriter
from xlsxwriter.utility import xl_range
import cStringIO
import base64


class cicon_prod_plan(models.Model):
    _name = 'cicon.prod.plan'
    _description = "CICON Production Plan"
    _rec_name = 'display_name'

    @api.multi
    def _display_name(self):
        for rec in self:
            rec.display_name = rec.plan_date + '/' + str(rec.work_shift).upper()
            rec.order_count_not_planned = self.env['cicon.prod.order'].search_count([('plan_load_id', '=', False),
                                                                                       ('state', 'not in', ['delivered', 'cancel', 'transfer', 'hold'])])

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('plan_date', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('plan_date', operator, name)] + args, limit=limit)
        return recs.name_get()


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

    @api.multi
    def action_done(self):
        self.ensure_one()
        _pending_orders = self.prod_order_ids.filtered(lambda p: p.state not in ('delivered'))
        if _pending_orders:
            raise UserError(" ( %d ) Pending Orders found in plan, Please clear before closing Plan !" % (len(_pending_orders)))
        else:
            self.state = 'done'

    @api.multi
    def action_pending(self):
        self.ensure_one()
        self.state = 'pending'

    @api.multi
    def excel_plan(self):
        self.ensure_one()
        if self.plan_load_ids and self.prod_order_ids:
            self._create_excel()

    def _clean_templ_str(self, _temp_str):
        _res = []
        _str_val = _temp_str.split(',')
        print _res
        if ('TH' or 'CO') in _str_val:
            _res.append('T')
        if 'ST' in _str_val:
            _res.append('ST')
        print _temp_str , _res
        if _res:
            return ','.join(_res)
        else:
            return ''

    def _create_excel(self):
        _header_cols = ['Load', 'Customer', 'Project', 'Items', 'Order Date', 'Code', 'Order',  'Description',
                        'Tonnage', 'Required', 'Remarks','Status']

        output = cStringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        _title_format = workbook.add_format()
        _title_format.set_bold()
        _title_format.set_bottom()
        _number_format = workbook.add_format()
        _number_format.set_num_format('###0.000')
        _number_format.set_bold()
        worksheet = workbook.add_worksheet("Plan")

        _fill_aling = workbook.add_format()
        _fill_aling.set_align('fill')
        worksheet.set_default_row(13)
        _row = 0
        _col = 0
        for _head in _header_cols:
            worksheet.write(_row, _col, _head, _title_format)
            _col += 1

        _start_row = 0
        for _load in self.plan_load_ids:
            _row += 1
            _start_row = _row
            worksheet.write(_row, 0, _load.load)
            _customer_order_ids = _load.prod_order_ids.mapped('customer_order_id')
            for _customer_order in _customer_order_ids:
                worksheet.write(_row, 1, _customer_order.partner_id.name, _fill_aling)
                worksheet.write(_row, 2, _customer_order.project_id.name, _fill_aling)
                _prod_orders = _load.prod_order_ids.filtered(lambda c: c.customer_order_id.id == _customer_order.id)
                for _prod_order in _prod_orders:
                    worksheet.write(_row, 3, self._clean_templ_str(_prod_order.template_str))
                    worksheet.write(_row, 4, datetime.strptime(_customer_order.order_date, "%Y-%m-%d").strftime('%d-%b'))
                    worksheet.write(_row, 5, _prod_order.name)
                    worksheet.write(_row, 6, _prod_order.customer_order_id.name)
                    worksheet.write(_row, 7, _prod_order.description, _fill_aling)
                    worksheet.write(_row, 8, _prod_order.total_tonnage, _number_format)
                    if _prod_order.required_date:
                        worksheet.write(_row, 9, datetime.strptime(_prod_order.required_date, "%Y-%m-%d").strftime('%d-%b'))
                    if _prod_order.remarks:
                        worksheet.write(_row, 10, _prod_order.remarks)
                    worksheet.write(_row, 11, _prod_order.state)
                    _row += 1

            if _start_row < _row - 1: #If Need total display
                worksheet.write_blank(_row, 0, None, _title_format)
                worksheet.write_blank(_row, 1, None, _title_format)
                if _load.note:
                    worksheet.write(_row, 2, _load.note, _title_format)
                else:
                    worksheet.write_blank(_row, 2, None, _title_format)
                for i in range(3, 7):
                    worksheet.write_blank(_row, i, None, _title_format)
                worksheet.write(_row, 7, "Total", _title_format)
                _sum_range = xl_range(_start_row, 8, _row-1, 8)
                worksheet.write_formula(_row, 8, '=SUM(%s)' % _sum_range, _title_format)
                for i in range(9, 12):
                    worksheet.write_blank(_row, i, None, _title_format)
                _row += 1
            else:
                for i in range(12):
                    worksheet.write_blank(_row, i, None, _title_format)
                _row += 1

        worksheet.set_column(0, 0, 4)
        worksheet.set_column(1, 1, 24)
        worksheet.set_column(2, 2, 27)
        worksheet.set_column(3, 3, 5)
        worksheet.set_column(4, 4, 7.5)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 8)
        worksheet.set_column(7, 7, 50)
        worksheet.set_column(8, 8, 8)
        worksheet.set_column(9, 9, 8)
        worksheet.set_column(10, 10, 10)
        worksheet.set_column(11, 11, 8)

        workbook.close()
        output.seek(0)
        _r_name = 'Production Plan' + datetime.strptime(self.plan_date, "%Y-%m-%d").strftime('%d-%b-%Y')
        _file_name = 'production Plan' + datetime.strptime(self.plan_date, "%Y-%m-%d").strftime('%d-%b-%Y') + '.xlsx'
        vals = {
            'name': _r_name,
            'datas_fname': _file_name,
            'description': 'Production Plan',
            'type': 'binary',
            'db_datas': base64.encodestring(output.read()),
            'res_name': _r_name,
            'res_model': 'cicon.prod.plan',
            'res_id': self.id
        }
        file_id = self.env['ir.attachment'].create(vals)
        return file_id


class cicon_prod_plan_load(models.Model):
    _name = 'cicon.prod.plan.load'
    _description = "Load Priority"
    _rec_name = 'display_name'

    # def _calc_load(self):
    #     _default_name = self.env.context.get('default_name', False)
    #     _plan_id = self.env.context.get('default_prod_plan_id', False)
    #     if _plan_id:
    #         _loads = self.env['cicon.prod.plan'].browse(_plan_id).plan_load_ids.mapped('load')
    #         if _loads:
    #             _range = list(range(1, max(_loads) + 1, 1))
    #             _miss = list(set(_range).difference(_loads))
    #             if _miss:
    #                 return min(_miss)
    #             else:
    #                 return max(_loads) + 1
    #         else:
    #             return 1
    #
    #     if _default_name:
    #         return _default_name

    @api.model
    def default_get(self, fields):
        _res = super(cicon_prod_plan_load, self).default_get(fields)
        if _res.get('load', False) and not _res.get('prod_plan_id', False):
            _plans = self.env['cicon.prod.plan'].search([('state', '=', 'pending')])
            if len(_plans) == 1:
                _res['prod_plan_id'] = _plans.id

        return _res

    @api.multi
    def _get_order_code(self):
        for rec in self:
            if rec.prod_order_ids:
                _codes = ', '.join(rec.prod_order_ids.mapped('name'))
                _tons = sum(rec.prod_order_ids.mapped('total_tonnage'))
                rec.prod_order_codes = _codes
                rec.prod_order_tonnage = _tons

    @api.multi
    @api.depends('search_prod_order_ids', 'prod_order_ids.plan_load_id')
    def _get_customer(self):
        for rec in self:
            if rec.search_prod_order_ids or rec.prod_order_ids:
                _partner = rec.search_prod_order_ids.mapped('partner_id')
                _partner |= rec.prod_order_ids.mapped('partner_id')
                if len(_partner) == 1:
                    rec.search_partner_id = _partner

    @api.multi
    @api.depends('load', 'prod_plan_id.plan_date')
    def _display_name(self):
        for rec in self:
            if rec.prod_plan_id:
                _plan_date = datetime.strptime(rec.prod_plan_id.plan_date, "%Y-%m-%d").strftime('%d-%b')
                rec.display_name = str(rec.load) + '(' + str(_plan_date) + ')'

    _LOAD_STATES = [('no_order', 'No Order'), ('pending', 'Pending'), ('delivered', 'Delivered'), ('partial', 'Partial')]

    @api.multi
    @api.depends('prod_order_ids.state', 'prod_order_ids')
    def _load_state(self):
        for rec in self:
            if rec.prod_order_ids:
                _states = list(set(rec.prod_order_ids.mapped('state')))
                if _states:
                    if len(_states) == 1:
                        if _states[0] != 'delivered':
                            rec.state = 'pending'
                        elif _states[0] == 'delivered':
                            rec.state = 'delivered'
                    else:
                        rec.state = 'partial'
            else:
                rec.state = 'no_order'

    display_name = fields.Char("Load #", compute=_display_name, store=True)
    load = fields.Integer('Load Priority', required=True)
    note = fields.Char(string="Notes")
    re_arrange = fields.Boolean('Re Arrange', help="Re Arrange load if exists !", default=False)

    search_prod_order_ids = fields.Many2many('cicon.prod.order',  string="Code Search",
                                             domain="[('plan_load_id','=',False), ('state','not in',['delivered','cancel','transfer','hold'])]")
    search_partner_id = fields.Many2one('res.partner', compute=_get_customer,
                                        string="Customer Search", domain="[('customer','=',True)]", store=True)

    prod_order_ids = fields.One2many('cicon.prod.order', 'plan_load_id',
                                     string='Production Orders')
    prod_order_codes = fields.Char(compute=_get_order_code, string="Codes",  store=False)
    prod_order_tonnage = fields.Float(compute=_get_order_code, string="Tonnage", digits=(10, 3), store=False)

    prod_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="Production Plan", ondelete='restrict')
    state = fields.Selection(selection=_LOAD_STATES, string='Status',
                             compute=_load_state, readonly=True, store=True)

    _sql_constraints = [('uniq_plan_load', 'UNIQUE(load,prod_plan_id)', "Unique Plan Load !")]

    _order = 'load'

    @api.onchange('search_prod_order_ids' )
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

    @api.onchange('prod_plan_id')
    def onchange_plan(self):
        if self.prod_plan_id:
            _loads = self.prod_plan_id.plan_load_ids.mapped('load')
            if _loads:
                _range = list(range(1, max(_loads) + 1, 1))
                _miss = list(set(_range).difference(_loads))
                if _miss:
                    self.load = min(_miss)
                else:
                    self.load = max(_loads) + 1
            else:
                return 1

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
    @api.depends('prod_order_ids')
    def _check_customer(self):
        for rec in self:
            _customers = rec.prod_order_ids.mapped('partner_id')
            if len(_customers) > 1:
                return False
            else:
                return True

    @api.model
    def create(self, vals):
        if vals.get('re_arrange', False):
            self._add_load_position(_load=vals.get('load'), _plan=vals.get('prod_plan_id'))
            vals['re_arrange'] = False
        res = super(cicon_prod_plan_load, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('re_arrange', False):
            self._add_load_position(_load=vals.get('load'), _plan=self.prod_plan_id.id)
            vals['re_arrange'] = False
        res = super(cicon_prod_plan_load, self).write(vals)
        return res

    def _add_load_position(self, _load , _plan):
        _load_exist = self.env['cicon.prod.plan.load'].search([('load', '=', _load), ('prod_plan_id', '=', _plan)],
                                                              limit=1)
        if _load_exist:
            _loads = self.env['cicon.prod.plan.load'].search([('load', '>=', _load), ('prod_plan_id', '=', _plan)],
                                                             order='load desc')
            for _ld in _loads:
                _ld.write({'load': _ld.load + 1})
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

    
    #
    # @api.multi
    # @api.depends('plan_load_id')
    # def _check_customer(self):
    #     for _rec in self:
    #         _prod_orders = self.env['cicon.prod.order'].search([('plan_load_id', '=', _rec.plan_load_id.id)])
    #         _customers = _prod_orders.mapped('partner_id')
    #         print _customers
    #         if len(_customers) > 1:
    #             return False
    #         else:
    #             return True
    #
    # _constraints = [
    #     (_check_customer, 'Different Customers found !', ['plan_load_id']),
    # ]

    @api.model
    def remove_plan(self):
        if self._context.get('active_ids'):
            _orders = self.env['cicon.prod.order'].search([('id', 'in', self._context.get('active_ids'))])
            _orders.write({'plan_load_id': False})


