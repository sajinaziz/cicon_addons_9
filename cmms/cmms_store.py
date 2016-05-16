from openerp import models, fields, api


class CmmsSparePartType(models.Model):
    _name = 'cmms.spare.part.type'
    _description = "Spare Part Type"

    name = fields.Char("Spare Part Type", required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Spare Part Type Must Unique')]

CmmsSparePartType()


class CmmsStoreInvoice(models.Model):
    _name = 'cmms.store.invoice'
    _description = "Store Invoice"

    is_qb_invoice = fields.Boolean('QB Invoice Import')
    name = fields.Char('Reference', default='New', copy=False,
                       readonly=True)
    invoice_date = fields.Date("Date", required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id,
                                 required=True, readonly=True , states={'draft': [('readonly', False)]})
    machine_id = fields.Many2one('cmms.machine', string="Machine", readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirm'), ('done', 'Posted'), ('cancel', 'Cancelled')],
                             string='Status', default='draft')

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   readonly=True, states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type',
                                      readonly=True, states={'draft': [('readonly', False)]})
    src_location_id = fields.Many2one('stock.location', string='Stock Location',
                                      readonly=True, states={'draft': [('readonly', False)]})
    consu_location_id = fields.Many2one('stock.location', string='Consumed Location',
                                        readonly=True, states={'draft': [('readonly', False)]})

    qb_ref = fields.Char('QB Reference')
    qb_inv_id = fields.Integer("QB Invoice ID")
    qb_inv_ref = fields.Char("QB Invoice Ref")
    qb_inv_name = fields.Char('Machine Name')
    qb_last_updated = fields.Datetime('Last Edited Time')

    invoice_line_ids = fields.One2many('cmms.store.invoice.line', 'invoice_id', string="Invoice Lines", readonly=True, states={'draft':[('readonly', False)]})

    @api.multi
    def set_confirm(self):
        if self.src_location_id and self.consu_location_id:
            self.write({'state': 'confirmed'})

    @api.multi
    def move_consume(self):
        """
        Move the scrap/damaged product into scrap location
        """
        self.ensure_one()
        _stock_move_obj = self.env['stock.move']
        for move_prod in self.invoice_line_ids:
            if move_prod.quantity <= 0 or move_prod.state != 'confirmed' or move_prod.move_id.id:
                raise Warning('Please provide a positive quantity !')
            else:
                # 'picking_type_id': self.picking_type_id.id,
                default_val = {
                    'name': 'Consume: ' + move_prod.product_id.name,
                    'origin': self.name,
                    'product_id': move_prod.product_id.id,
                    'location_id': self.src_location_id.id,
                    'product_uom_qty': move_prod.quantity,
                    'product_uom': move_prod.product_id.uom_id.id,
                    'scrapped': True,
                    'location_dest_id': self.consu_location_id.id,
                }
            #   'restrict_lot_id': self.restrict_lot_id.id,
                scrap_move = _stock_move_obj.create(default_val)
                move_prod.write({'move_id': scrap_move.id})
                scrap_move.action_done()

    @api.onchange('picking_type_id')
    def change_picking_type(self):
        if self.picking_type_id:
            self.src_location_id = self.picking_type_id.default_location_src_id
            self.consu_location_id = self.picking_type_id.default_location_dest_id

    _sql_constraints = [('uniq_ref', 'UNIQUE(qb_ref)', 'Unique QB Reference'),
                        ('uniq_name', 'UNIQUE(name)', 'Unique Reference')]

    _order = 'invoice_date desc'

    @api.model
    def get_last_updated_datetime(self):
        """To Get Last updated  """
        #_updated_datetime = '2015-11-29 00:00:00'
        _updated_datetime = ''
        qry = "SELECT MAX(qb_last_updated) FROM cmms_store_invoice WHERE company_id = %s" % (
            self.env.user.company_id.id)
        self.env.cr.execute(qry)
        last_updated = self.env.cr.fetchone()
        if last_updated[0] is not None:
            _updated_datetime = last_updated[0]
        return _updated_datetime

    # @api.multi
    # def post_move_view(self):
    #     self.ensure_one()  # One Record
    #     # Find form view and pass context for default values
    #     _lines = []
    #     form_id = self.env.ref('cmms.view_stock_consume_wizard')
    #     for x in self.invoice_line_ids:
    #         _lines.append({'store_line_id': x.id, 'product_id': x.product_id.id, 'product_uom': x.product_id.uom_id.id,
    #                        'product_qty': x.quantity})
    #     ctx = dict(
    #         default_name=self.name,
    #         default_consu_line_ids=_lines
    #     )
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'consume.product.wizard',
    #         'views': [(form_id.id, 'form')],
    #         'view_id': form_id.id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    @api.model
    def create(self, vals):
        _seq_store_inv = self.env['ir.sequence'].search([('company_id', '=', self.env.user.company_id.id),
                                                        ('code', '=', 'cmms.store.invoice')])
        vals['name'] = _seq_store_inv.next_by_id() or 'New'
        return super(CmmsStoreInvoice,self).create(vals)


#Import

    # @api.model
    # def load(self,  fields, data):
    #     for r in data:
    #         _row = dict(zip(fields, r))
    #         _id = _row.get('id', False)
    #         if _id:
    #             ex = self.env['ir.model.data'].search([('name', '=', _id)])
    #             if ex:
    #                 _invoice = self.browse(ex.res_id)
    #                 if _invoice:
    #                     _invoice.invoice_line_ids.unlink()
    #         res = super(cmms_store_invoice, self).load(fields, data)
    #     return res
        #TODO: modify line item which is already in database with comparing import line
        #region Import With Compare Line Items
        # _line_data = []
        # _line_fields = ['invoice_id', 'qb_line_ref', 'prod_name', 'prod_desc', 'quantity', 'unit_price']
        # for r in data:
        #     _row = dict(zip(fields, r))
        #     _id = _row.get('id', False)
        #     if _id:
        #         _invoice_line_file = []
        #         _invoice_line_file.append(( _row.get('qb_ref'),
        #                                             _row.get('invoice_line_ids/qb_line_ref'),
        #                                            _row.get('invoice_line_ids/prod_name'),
        #                                            _row.get('invoice_line_ids/prod_desc'),
        #                                            _row.get('invoice_line_ids/quantity'),
        #                                           _row.get('invoice_line_ids/unit_price')))
        #
        #         ex = self.env['ir.model.data'].search([('name', '=', _id)])
        #         _invoice = self.browse(ex.res_id)
        #         _invoice_line_db = [(x.invoice_id.qb_ref, x.qb_line_ref, x.prod_name, x.prod_desc, x.quantity, x.unit_price) for x in _invoice.invoice_line_ids]
        #         flag=1
        #         _ind = data.index(r)+1
        #         while(flag == 1):
        #             if _ind < len(data):
        #                 _trow = dict(zip(fields, data[_ind]))
        #                 if _trow.get('id'):
        #                     flag = 0
        #                 else:
        #                     _invoice_line_file.append(( _row.get('qb_ref'),
        #                                             _trow.get('invoice_line_ids/qb_line_ref'),
        #                                            _trow.get('invoice_line_ids/prod_name'),
        #                                            _trow.get('invoice_line_ids/prod_desc'),
        #                                            _trow.get('invoice_line_ids/quantity'),
        #                                           _trow.get('invoice_line_ids/unit_price')))
        #             else:
        #                 flag = 0
        #             _ind = _ind + 1
        #         print _invoice_line_db
        #         print _invoice_line_file
        #         _invoice.invoice_line_ids.unlink()
        #endregion


class CmmsStoreInvoiceLine(models.Model):
    _name = 'cmms.store.invoice.line'
    _description = "Store Invoice Lines"
    _rec_name = 'product_id'

    @api.depends('qb_prod_desc')
    def _set_job_code(self):
        for rec in self:
            if rec.qb_prod_desc:
                _ex_code = rec.qb_prod_desc.split(' ')[-1]
                _prefix = _ex_code.split('-')[0]
                #TODO:  Check other Criteria for Job Order Code
                rec.job_code = _ex_code

    @api.depends('qb_prod_desc')
    def _set_job_order(self):
        for rec in self:
            if rec.job_code:
                _job = self.env['cmms.job.order'].search([('name', '=', rec.job_code)])
                if _job:
                    rec.job_order_id = _job.id

    @api.depends('unit_price', 'quantity')
    def _total_amount(self):
        for _rec in self:
            _rec.amount = _rec.unit_price * _rec.quantity

    invoice_id = fields.Many2one('cmms.store.invoice', ondelete='cascade', string='Invoice')
    invoice_date = fields.Date('Date', related='invoice_id.invoice_date', store=True, readonly=True)
    product_id = fields.Many2one('product.product', string='Product', states={'draft':[('readonly', False)]} ,required=True , readonly=True)
    product_uom_id = fields.Many2one('product.uom', realted='product_id.product_uom_id', string='Unit' , store=True , readonly=True )
    product_desc = fields.Char('Product Description', index=True, required=True ,readonly=True, states={'draft':[('readonly', False)]} )
    quantity = fields.Float('Quantity', readonly=True, states={'draft':[('readonly', False)]})
    unit_price = fields.Float('Unit Price', readonly=True, states={'draft':[('readonly', False)]} )
    amount = fields.Float("Amount", compute=_total_amount, store=True , readonly=True )
    job_code = fields.Char('Job Code', compute=_set_job_code , readonly=True )
    job_order_id = fields.Many2one('cmms.job.order', string="Job order", compute=_set_job_order, store=True, readonly=True )
    machine_id = fields.Many2one('cmms.machine', related='job_order_id.machine_id', string="Machine", store=True, readonly=True )
    company_id = fields.Many2one('res.company', "Company", related="invoice_id.company_id", store=True, readonly=True )
    spare_part_type_id = fields.Many2one('cmms.spare.part.type', string="Part Type", readonly=True , states={'draft':[('readonly', False)]} )
    move_id = fields.Many2one('stock.move', string="Stock Move", readonly=True)
    state = fields.Selection(related='invoice_id.state', string='State', readonly=True, store=True)
    move_state = fields.Selection(related='move_id.state', string='Move State', readonly=True, store=True)

    qb_line_ref = fields.Char('QB Line Reference')
    qb_prod_desc = fields.Char('QB Product Description')
    qb_amount = fields.Float('QB Total Amount', help='Sale Price in QB')
    qb_parent_product = fields.Char('QB Parent Product')

    @api.onchange('product_id')
    def _change_product(self):
        if self.product_id:
            self.product_desc = self.product_id.display_name
            self.unit_price = self.product_id.standard_price

    @api.multi
    def move_consume(self):
        """
        Move the scrap/damaged product into scrap location
        """
        self.ensure_one()
        _stock_move_obj = self.env['stock.move']
        if self.quantity <= 0 or self.state != 'confirmed' or self.move_id.id:
            raise Warning('Please provide a positive quantity !')
        else:
            default_val = {
                    'name': 'Consume: ' + self.product_id.name,
                    'origin': self.invoice_id.name,
                    'picking_type_id': self.invoice_id.picking_type_id.id,
                    'product_id': self.product_id.id,
                    'location_id': self.invoice_id.src_location_id.id,
                    'product_uom_qty': self.quantity,
                    'product_uom': self.product_id.uom_id.id,
                    'scrapped': True,
                    'location_dest_id': self.invoice_id.consu_location_id.id,
            }
                #   'restrict_lot_id': self.restrict_lot_id.id,
            scrap_move = _stock_move_obj.create(default_val)
            self.write({'move_id': scrap_move.id})
            scrap_move.action_done()

#     # @api.v7 # Server Action for re-construct job order link
#     # def set_job_order(self, cr, uid, ids, context=None):
#     #     if ids:
#     #         lines = self.browse(cr, uid, ids)
#     #         for rec in lines:
#     #             if rec.job_code:
#     #                 _job_obj = self.pool['cmms.job.order']
#     #                 _job = _job_obj.search(cr, uid, [('name', '=', rec.job_code)], limit=1)
#     #                 if _job:
#     #                     rec.write({'job_order_id': _job[0]})
#
#     _sql_constraints = [('uniq_name', 'UNIQUE(qb_line_ref)', 'Unique Line Reference')]
#
# CmmsStoreInvoiceLine()

