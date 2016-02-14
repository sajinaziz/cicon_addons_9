from openerp import models, fields, api


class CiconProdDeliveryOrder(models.Model):
    _name = 'cicon.prod.delivery.order'
    _description = "Delivery Order"

    name = fields.Char("DN Number", required=True)
    dn_date = fields.Date("DN Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer",related="customer_order_id.partner_id", store=True)
    project_id = fields.Many2one('res.partner.project', string="Project", related="customer_order_id.project_id", store=True)
    customer_order_id = fields.Many2one('cicon.customer.order', " Customer Order", required=True)
    prod_order_ids = fields.Many2many('cicon.prod.order', 'cicon_prod_order_dn_rel', 'dn_id', 'prod_order_id', "Production Orders",
                                      domain="[('customer_order_id','=', customer_order_id)]")
    remarks = fields.Char("Remarks")
    product_tmpl_ids = fields.Many2many('product.template','cicon_dn_product_tmpl_rel','dn_id', 'product_tmpl_id', "Product Templates")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Delivered')], string="Status", required=True, default='pending' )
    dn_line_ids = fields.One2many('cicon.prod.delivery.order.line', 'dn_id', string="DN Lines")

    _sql_constraints = [('uniq_dn', 'UNIQUE(name)', "DN Should be unique")]

    @api.onchange('prod_order_ids')
    def _change_prod_order(self):
        if self.prod_order_ids:
            _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', self.prod_order_ids._ids)])
            _product_tmpls = _order_lines.mapped('product_tmpl_id')
            _dm = {'product_tmpl_ids': [('id', 'in', _product_tmpls._ids)]}
            return {'domain': _dm}

    @api.onchange('product_tmpl_ids')
    def _change_prod_tmpl(self):
        _dn_lines = []
        if self.prod_order_ids and self.product_tmpl_ids:
            _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', 'in', self.prod_order_ids._ids),
                                                                     ('product_tmpl_id', 'in', self.product_tmpl_ids._ids)])
            for _order_line in _order_lines:
                _dn_lines.append({
                    'product_id': _order_line.product_id,
                    'prod_order_id': _order_line.prod_order_id,
                    'product_qty': _order_line.product_qty
                })
        self.dn_line_ids = _dn_lines


CiconProdDeliveryOrder()


class CiconProdDeliveryOerderLine(models.Model):
    _name = 'cicon.prod.delivery.order.line'
    _description = "Delivery Line"

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
            if self.prod_order_id:
                _order_lines = self.env['cicon.prod.order.line'].search([('prod_order_id', '=', self.prod_order_id.id),
                                                                         ('product_id', '=', self.product_id.id)])
                self.prod_order_qty = sum([x.product_qty for x in _order_lines])

    dn_id = fields.Many2one('cicon.prod.delivery.order', string="DN")
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string='Product', required=True)
    prod_order_id = fields.Many2one('cicon.prod.order', string="Production Order")
    product_qty = fields.Float('Quantity', digits=(10, 3), required=True)
    prod_order_qty = fields.Float('Order Quantity', compute=_get_dia_value, digits=(10, 3),
                                  readonly=True)
    unit_id = fields.Many2one('product.uom', related='product_id.uom_id', string='Unit', readonly=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', readonly=True)
    dia_attrib_value_id = fields.Many2one('product.attribute.value', compute=_get_dia_value, string='Diameter',
                                          store=True)


CiconProdDeliveryOrder()

