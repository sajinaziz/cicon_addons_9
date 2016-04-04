from openerp import models, fields,api


class CiconReportingModel(models.Model):
    _name = 'cicon.reporting.model'
    _description = "CICON Reporting Models"

    name = fields.Char("Title", required=True)
    report_model_id = fields.Many2one("ir.model", string="Model", required=True)
    report_action_id = fields.Many2one('cicon.reporting.action', string="Report 1")
    report2_action_id = fields.Many2one('cicon.reporting.action', string="Report 2")
    report3_action_id = fields.Many2one('cicon.reporting.action', string="Report 3")
    report4_action_id = fields.Many2one('cicon.reporting.action', string="Report 4")

    @api.multi
    def show_report(self):
        self.ensure_one()
        rept_act = self._context.get('rpt', 0)
        rpt_obj = self.report_action_id
        if rept_act == 2:
            rpt_obj = self.report2_action_id
        elif rept_act == 3:
            rpt_obj = self.report3_action_id
        elif rept_act == 4:
            rpt_obj = self.report4_action_id

        return {
            'name': rpt_obj.name,
            'view_type': 'form',
            'view_mode': rpt_obj.view_mode.lower(),
            'view_id': self.env.ref(rpt_obj.view_ref_id.xml_id).id,
            'res_model': rpt_obj.action_model_id.model,
            'domain': rpt_obj.action_ref_id.domain,
            'type': 'ir.actions.act_window',
            'context': rpt_obj.action_ref_id.context
        }

    # @api.multi
    # def show_report_2(self):
    #     self.ensure_one()
    #     return {
    #         'name': self.report2_action_id.name,
    #         'view_type': 'form',
    #         'view_mode': self.report2_action_id.view_mode.lower(),
    #         'view_id': self.env.ref(self.report2_action_id.view_ref_id.xml_id).id,
    #         'res_model': self.report2_action_id.action_model_id.model,
    #         'domain': self.report2_action_id.action_ref_id.domain,
    #         'type': 'ir.actions.act_window',
    #         'context': self.report2_action_id.action_ref_id.context
    #     }





        # form_id = self.env.ref('cicon_reporting.action_cicon_report_tech_submittal_revision')
        # ctx = {}
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'cicon.',
        #     'view_id': form_id.id,
        #     'target': 'current',
        #     'context': ctx,
        # }



    #
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(CiconReportingModel, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                          toolbar=toolbar, submenu=submenu)
    #     if view_type == 'kanban':
    #         eview = etree.fromstring(res['arch'])
    #         print etree.tostring(eview)
    #         _button_div = eview.find(".//div[@id='button_box']")
    #         _button_div.insert(0, etree.Element('field', {'name': 'name'}))
    #         res['arch'] = etree.tostring(eview)
    #
    #     return res

CiconReportingModel()


class CiconReportAction(models.Model):
    _name = 'cicon.reporting.action'
    _description = "CICON Report Actions"

    name = fields.Char("Action Name", required=True)
    action_model_id = fields.Many2one('ir.model', string="Model")
    model_name = fields.Char(related='action_model_id.model', readonly=True, string='Model Name', store=False)
    view_ref_id = fields.Many2one('ir.ui.view',  string="View Ref")
    action_ref_id = fields.Many2one('ir.actions.act_window', string="Action")
    view_mode = fields.Selection([('tree', 'Tree'), ('pivot', 'Pivot'), ('graph', 'Graph'), ('form','Form')], required=True,  string="View Mode")


CiconReportAction()


