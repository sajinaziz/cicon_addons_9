from openerp import models, fields, api


class HrEquipmentCategoryProperty(models.Model):
    _name = 'hr.equipment.category.property'
    _description = "Equipment Category Property"

    name = fields.Char('Property Name', required=True)

    _sql_constraints = [('uniq_name', 'UNIQUE(name,category_id)', "Property Name Should be Unique" )]

HrEquipmentCategoryProperty()


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

    property_ids = fields.Many2many(related='category_id.property_ids', store=False, string="Properties")
    property_value_ids = fields.One2many('hr.equipment.property.value', 'equipment_id', string="Property Values")
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)

HrEquipment()


class HrEquipmentRequest(models.Model):
    _inherit = 'hr.equipment.request'

    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)

HrEquipmentRequest()


class HrEquipmentCategory(models.Model):
    _inherit = 'hr.equipment.category'

    property_ids = fields.Many2many('hr.equipment.category.property', 'hr_equipment_categ_property_rel',
                                    'category_id', "property_id", string="Properties")

HrEquipmentCategory()


