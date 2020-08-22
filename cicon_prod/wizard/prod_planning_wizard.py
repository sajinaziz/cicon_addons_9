from openerp import models, fields, api


class ChangePlanWizard(models.TransientModel):
    _name = 'cic.change.plan.wizard'
    _description = "Plan Change Wizard"

    prod_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="Production Plan", ondelete='set null')
    prod_order_ids = fields.Many2many('cicon.prod.order', 'prod_order_plan_wizard_rel', 'wizard_id', 'prod_order_id',
                                      string='Production Orders', required=True)
    auto_load = fields.Boolean('Auto Load Assign', default=True)

    import_position = fields.Selection(selection=[('start', 'Start'), ('end', 'End')], string="Position", required=True,
                                       default='start')
    remarks = fields.Char("Remarks")



class ChangePlanWizard(models.TransientModel):
    _name = 'cic.change.plan.wizard'
    _description = "Plan Change Wizard"

    prod_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="Production Plan", ondelete='set null')
    prod_order_ids = fields.Many2many('cicon.prod.order', 'prod_order_plan_wizard_rel', 'wizard_id', 'prod_order_id',
                                      string='Production Orders', required=True)
    auto_load = fields.Boolean('Auto Load Assign', default=True)

    import_position = fields.Selection(selection=[('start', 'Start'), ('end', 'End')], string="Position", required=True,
                                       default='start')
    remarks = fields.Char("Remarks")