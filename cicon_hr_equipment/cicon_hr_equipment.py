from openerp import models, fields, api


class HrEquipmentCategoryProperty(models.Model):
    _name = 'hr.equipment.category.property'
    _description = "Equipment Category Property"

    name = fields.Char('Property Name', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Property Name Should be Unique" )]

HrEquipmentCategoryProperty()


class HrEquipmentStatus(models.Model):
    _name = 'hr.equipment.status'
    _description = "Equipment Status"

    name = fields.Char('Status', required=True)
    sequence=fields.Integer('Sequence')

    _order = 'sequence'

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', "Status should be Unique")]

HrEquipmentStatus()


class HrEquipmentPropertyValue(models.Model):
    _name = 'hr.equipment.property.value'
    _description = "Equipment Category Property"

    equipment_id = fields.Many2one('hr.equipment', string="Equipment")
    property_id = fields.Many2one('hr.equipment.category.property', "Property")
    property_value = fields.Char('Value', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(equipment_id,property_id)', "Property Should be Unique")]

HrEquipmentCategoryProperty()


class HrEquipment(models.Model):
    _inherit = 'hr.equipment'

    @api.one
    @api.depends('name', 'serial_no')
    def _get_asset_name(self):
        if self.name:
            self.asset_code = str(self.name)
            if self.serial_no:
                self.asset_code += '-' + str(self.serial_no)

    def _get_default_status(self):
        _status = self.env['hr.equipment.status'].search([], order='sequence desc', limit=1)
        return _status

    property_ids = fields.Many2many(related='category_id.property_ids', store=False, string="Properties")
    property_value_ids = fields.One2many('hr.equipment.property.value', 'equipment_id', string="Property Values")
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id, track_visibility='onchange')
    asset_code = fields.Char(compute=_get_asset_name, string="Asset Code", store=True)
    status_id = fields.Many2one('hr.equipment.status', string='Status', track_visibility='onchange', default=_get_default_status)

    _sql_constraints = [('UniqueAsset', 'UNIQUE(asset_code)', 'Asset Name Should be Unique !')]

HrEquipment()


class HrEquipmentRequestCategory(models.Model):
    _name = 'hr.equipment.request.category'
    _description = "Request Category"

    name = fields.Char('Category', required=True)
    asset_categ_ids = fields.Many2many('hr.equipment.category', 'hr_equip_categ_req_categ_rel',
                                    'req_categ_id', "asset_categ_id", string="Asset Categories")
    parent_id = fields.Many2one('hr.equipment.request.category', string="Parent")
    child_ids = fields.One2many('hr.equipment.request.category', 'parent_id', string='Children Categories')
    note = fields.Text(string='Required Information', help="Required information to solve this category issues, "
                                                           "will apper on description in requests")

    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'Unique Category')]

    @api.multi
    def name_get(self):
        res = []
        for cat in self:
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res

    @api.one
    @api.constrains
    def _check(self):
        parent = self._parent_name
        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
        current_id = self.id
        while current_id is not None:
            self._cr.execute(query, (current_id,))
            result = self._cr.fetchone()
            current_id = result[0] if result else None
            if current_id == self.id:
                return False
        return True

HrEquipmentRequestCategory()

class HrEquipmentRequest(models.Model):
    _inherit = 'hr.equipment.request'

    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    solution = fields.Text('Solution')
    request_categ_id = fields.Many2one('hr.equipment.request.category',  string="Request Category")
    request_sub_categ_id = fields.Many2one('hr.equipment.request.category', string="Sub Category")

    @api.onchange('request_sub_categ_id')
    def onchange_request_categ(self):
        if not self.description:
            self.description = self.request_sub_categ_id.note


HrEquipmentRequest()


class HrEquipmentCategory(models.Model):
    _inherit = 'hr.equipment.category'

    property_ids = fields.Many2many('hr.equipment.category.property', 'hr_equipment_categ_property_rel',
                                    'category_id', "property_id", string="Properties")

HrEquipmentCategory()


