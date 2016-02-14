from openerp import models,  fields, api
from datetime import time

class cic_qc_summary(models.Model):
    _name = 'cic.qc.summary'
    _description = "QC Summary Sheet"

    @api.one
    @api.depends('dn_line_ids', 'certificate_line_ids')
    def _get_order_codes(self):
        self.order_codes = self.env['cic.qc.order.code']
        self.heat_numbers = self.env['cic.qc.mill.cert']
        _code_ids = []
        _mill_ids = []
        for d in self.dn_line_ids:
            _code_ids.extend([o.id for o in d.order_code_ids])
        for m in self.certificate_line_ids:
            _mill_ids.extend([h.id for h in m.certificate_ids])
        self.order_codes = _code_ids
        self.heat_numbers = _mill_ids

    def _search_order_code(self, operator, value):
        _order_codes = self.env['cic.qc.order.code'].search([('name', operator, value)])
        _order_ids = [o.id for o in _order_codes]
        _dn_ids = self.env['cic.qc.dn.line'].search([('order_code_ids', 'in', _order_ids)])
        _summary_ids = [s.qc_summary_id.id for s in _dn_ids]
        return [('id', 'in', _summary_ids)]

    def _search_heat_number(self, operator, value):
        _heat_nos = self.env['cic.qc.mill.cert'].search([('name', operator, value)])
        _heat_ids = [o.id for o in _heat_nos]
        _cert_line_ids = self.env['cic.qc.cert.line'].search([('certificate_ids', 'in', _heat_ids)])
        _summary_ids = [s.qc_summary_id.id for s in _cert_line_ids]
        return [('id', 'in', _summary_ids)]

    name = fields.Char('Trip Reference', readonly=True)
    dn_date = fields.Date('DN Date', required=True, default=fields.Date.context_today)
    delivery_date = fields.Date('Delivery Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', domain="[('customer','=',True)]", string="Customer", required=True)
    project_id = fields.Many2one('res.partner.project', 'Project', domain="[('partner_id','=',partner_id)]")
    certificate_line_ids = fields.One2many('cic.qc.cert.line', 'qc_summary_id', string="Mill Certificates")
    dn_line_ids = fields.One2many('cic.qc.dn.line', 'qc_summary_id', string="Delivery Notes")
    wb_ticket = fields.Integer('Weigh Bridge')
    loading_list = fields.Boolean('Loading List')
    order_codes = fields.Many2many('cic.qc.order.code', compute=_get_order_codes, search=_search_order_code, store=False, string='Order Codes', readonly=True)
    heat_numbers = fields.Many2many('cic.qc.mill.cert', compute=_get_order_codes, search=_search_heat_number, store=False, string='Heat Numbers', readonly=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id ,required=True)

    _sql_constraints = [('uniq_summary', 'UNIQUE(name)', 'Summary Name Must be Unique')]

    _order = 'id desc'

    @api.model
    def create(self, vals):
        _qc_summary_seq = self.env['ir.sequence'].search([('company_id', '=', self.env.user.company_id.id),
                                                          ('code', '=', 'cic.qc.summary.seq')])
        vals.update({'name': _qc_summary_seq.next_by_id() or time.strftime('%Y/%m/%d/%H/%M')})
        return super(cic_qc_summary, self).create(vals)

cic_qc_summary()


class cic_qc_cert_line(models.Model):
    _name = 'cic.qc.cert.line'
    _description = 'CICON Certificates Note'

    qc_summary_id = fields.Many2one('cic.qc.summary',string='QC Summary',required=True, ondelete='cascade')
    dia_attrib_value_id = fields.Many2one('product.attribute.value', domain="[('attribute_id.name','=','Diameter' )]", string='Diameter')
    origin_attrib_value_id = fields.Many2one('product.attribute.value', domain="[('attribute_id.name','=','Steel Origin' )]", string='Origin')
    certificate_ids = fields.Many2many('cic.qc.mill.cert', 'cert_line_id', 'cert_id', string='Heat Numbers')
    quantity = fields.Float('Remarks', digits=(10,3))

    _sql_constraints = [('uniq_line', 'UNIQUE(qc_summary_id,dia_attrib_value_id,origin_attrib_value_id)', 'Cert Line Name Must be Unique')]

cic_qc_cert_line()


# class cic_qc_mill_cert_file(models.Model):
#     _name = 'cic.qc.mill.cert.file'
#     _description = "CICON Mill Certificate file"
#
#     name = fields.Char('Page Number',size=32 , required=True)
#
#         #'type': fields.selection([('coil','COIL'),('bar','Steel Bar')],string='Type',required=True)
#     issued_date = fields.Date('Issued Date',required=True)
#     certificates_ids = fields.One2many('cic.qc.mill.cert','cert_file_id',string='Certificates',required=True)
#
# cic_qc_mill_cert_file()


class cic_qc_mill_cert(models.Model):
    _name = 'cic.qc.mill.cert'
    _description = 'CICON Mill Certificates'

    name = fields.Char('Heat Numbers', size=64, required=True)
    # cert_file_id = fields.Many2one('cic.qc.mill.cert.file', string='Certificate File',ondelete='cascade')
    dia_attrib_value_id = fields.Many2one('product.attribute.value', string='Diameter')

    _sql_constraints = [('uniq_summary', 'UNIQUE(name)', 'Summary Name Must be Unique')]

cic_qc_mill_cert()


class cic_qc_dn_line(models.Model):
    _name = 'cic.qc.dn.line'
    _description = 'CICON Delivery Note'
    _rec_name = 'dn_no'

    dn_no = fields.Char('Delivery Note Number', required=True)
    qc_summary_id = fields.Many2one('cic.qc.summary', string='QC Summary', ondelete='cascade')
    order_code_ids = fields.Many2many('cic.qc.order.code', 'dn_line_id', 'order_code_id', string='Order Codes')

    _sql_constraints = [('uniq_dn', 'UNIQUE(dn_no)', 'DN  Must be Unique')]

cic_qc_dn_line()


class cic_qc_order_code(models.Model):
    _name = 'cic.qc.order.code'
    _description = 'CICON Order Code'

    name = fields.Char('Order Code', size=12)

    _sql_constraints = [('uniq_order_code', 'UNIQUE(name)', 'Order Code Must be Unique')]
cic_qc_order_code()




