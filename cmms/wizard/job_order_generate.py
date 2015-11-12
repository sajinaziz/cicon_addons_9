from openerp import models, fields, api


JOB_ORDER_TYPE = [('breakdown','BREAKDOWN'), ('general', 'GENERAL')]

class CmmsJobOrderMasterWizard(models.TransientModel):
    _name = "cmms.job.order.master.wizard"
    _description = "CMMS Job Order Master Wizard"

    job_order_type = fields.Selection(JOB_ORDER_TYPE, "Job Order Type", required=True)
    last_code = fields.Char('Last Job Code', readonly=True, store=False)
    to_number = fields.Integer('To')

    @api.onchange('job_order_type')
    def _get_last(self):
        _master_obj = self.env['cmms.job.order.code']
        _rec = _master_obj.search([('job_order_type','=',self.job_order_type), ('company_id', '=',  self.env.user.company_id.id)], order='id desc', limit=1)
        if _rec:
            self.last_code = _rec.name
        else:
            self.last_code = '/'

    @api.multi
    def generate_job_order(self):
        _job_obj = self.env['cmms.job.order.code']
        _j_ids =[]
        for x in range(1, self.to_number):
            _job = {
                'created': False,
                'printed': False,
                'cancelled': False,
                'job_order_type': self.job_order_type,
                'company_id': self.env.user.company_id.id
            }
            _seq_obj = self.env['ir.sequence']
            if self.job_order_type == 'breakdown':
                _job.update({'name': _seq_obj.get('cmms.job.order.master.breakdown')})
            elif self.job_order_type == 'general':
                _job.update({'name': _seq_obj.get('cmms.job.order.master.general')})
            _j_ids.append(_job_obj.create(_job))
        return True

CmmsJobOrderMasterWizard()
