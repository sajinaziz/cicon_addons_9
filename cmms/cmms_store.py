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
    _rec_name = 'qb_ref'

    qb_ref = fields.Char('QB Reference')
    inv_id = fields.Integer("ID")
    inv_ref = fields.Char("Reference", required=True)
    inv_date = fields.Date("Date", required=True)
    inv_name = fields.Char('Name')
    edited_date_time = fields.Datetime('Last Edited Time')
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    invoice_line_ids = fields.One2many('cmms.store.invoice.line', 'invoice_id', string="Invoice Lines")

    _sql_constraints = [('uniq_name', 'UNIQUE(qb_ref,company_id)', 'Unique Reference Per Company')]

    _order = 'inv_date desc'

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

CmmsStoreInvoice()


class CmmsStoreInvoiceLine(models.Model):
    _name = 'cmms.store.invoice.line'
    _description = "Store Invoice Lines"
    _rec_name = 'qb_line_ref'

    @api.depends('prod_desc')
    def _set_job_code(self):
        for rec in self:
            if rec.prod_desc:
                _ex_code = rec.prod_desc.split(' ')[-1]
                _prefix = _ex_code.split('-')[0]

                #TODO:  Check other Criteria for Job Order Code
                rec.job_code = _ex_code

    @api.depends('prod_desc')
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

    qb_line_ref = fields.Char('QB Line Reference')
    invoice_id = fields.Many2one('cmms.store.invoice', ondelete='cascade', string='Invoice')
    product_id = fields.Many2one('product.product', string='Product')
    prod_name = fields.Char('Product Name', index=True)
    prod_desc = fields.Char('Description')
    quantity = fields.Float('Quantity')
    product_uom_id = fields.Many2one('product.uom', string='Unit')
    unit_price = fields.Float('Unit Price')
    amount = fields.Float("Amount", compute=_total_amount)
    job_code = fields.Char('Job Code', compute=_set_job_code)
    job_order_id = fields.Many2one('cmms.job.order', string="Job order", compute=_set_job_order, store=True)
    machine_id = fields.Many2one('cmms.machine', related='job_order_id.machine_id', string="Machine", store=True)
    spare_part_type_id = fields.Many2one('cmms.spare.part.type', string="Part Type")

    @api.v7 # Server Action for re-construct job order link
    def set_job_order(self, cr, uid, ids, context=None):
        if ids:
            lines = self.browse(cr, uid, ids)
            for rec in lines:
                if rec.job_code:
                    _job_obj = self.pool['cmms.job.order']
                    _job = _job_obj.search(cr, uid, [('name', '=', rec.job_code)], limit=1)
                    if _job:
                        rec.write({'job_order_id': _job[0]})

CmmsStoreInvoiceLine()

