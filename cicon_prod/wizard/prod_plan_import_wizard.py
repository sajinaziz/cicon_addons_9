from openerp import models, fields, api
from openerp.exceptions import UserError


class PlanImportWizard(models.TransientModel):
    _name = 'cic.plan.import.wizard'
    _description = "Plan Import Wizard"

    from_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="From Plan")
    to_plan_id = fields.Many2one('cicon.prod.plan', required=True, string="To Plan")
    import_position = fields.Selection(selection=[('start', 'Start'), ('end', 'End')], string="Position", required=True, default='start')

    @api.one
    def import_plan(self):
        self.ensure_one()
        _load_count = 0
        _pending_loads = self.from_plan_id.prod_order_ids.filtered(
            lambda o: o.state not in ['delivered', 'cancel', 'transfer', 'hold']).mapped('plan_load_id')
        if _pending_loads:
            _loads = _pending_loads.sorted(lambda l: l.load)
            if self.to_plan_id.plan_load_ids:
                if self.import_position == 'start':
                    _load_count = 0
                    _last_load = len(_loads) + len(self.to_plan_id.plan_load_ids)
                    for _splan in self.to_plan_id.plan_load_ids.sorted(lambda q: q.load, reverse=True):
                        _splan.load = _last_load
                        _last_load -= 1
                else:
                    _load_count = max(self.to_plan_id.plan_load_ids.mapped('load'))

            for _load in _loads:
                _load_count += 1
                _new_load = self.env['cicon.prod.plan.load'].create(vals={'prod_plan_id': self.to_plan_id.id, 'load': _load_count, 'note': _load.note})
                for _order in _load.prod_order_ids.filtered(lambda o: o.state not in ['delivered', 'cancel', 'transfer', 'hold']):
                    _order.plan_load_id = _new_load.id
        else:
            raise UserError("No Pending Orders to import!")












