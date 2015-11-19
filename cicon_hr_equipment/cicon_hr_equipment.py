from openerp import models, fields, api


class HrEquipmentCategoryProperty(models.Model):
    _name = 'hr.equipment.category.property'
    _description = "Equipment Category Property"

    name = fields.Char('Property Name', required=True)
    category_id = fields.Many2one('hr.equipment.category', string="EquipmentCategory")

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

    property_value_ids = fields.One2many('hr.equipment.property.value', 'equipment_id', string="Property Values")

HrEquipment()


class HrEquipmentCategory(models.Model):
    _inherit = 'hr.equipment.category'

    property_ids = fields.One2many('hr.equipment.category.property', 'category_id', "Properties")

HrEquipmentCategory()


