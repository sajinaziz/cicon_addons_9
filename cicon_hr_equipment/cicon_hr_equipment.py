from openerp import models,fields, api


class HrEquipment(models.Model):
    _inherit = 'hr.equipment'

HrEquipment()


class HrEquipmentCategory(models.Model):
    _inherit = 'hr.equipment.category'

HrEquipmentCategory()


