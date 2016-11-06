from openerp import fields,models,api


_inv_lines = None


class ReportPartsbyProductTypeSummary(models.AbstractModel): # Report File Name
    _name = 'report.cmms.report_partsby_producttype_summary_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.report_partsby_producttype_summary_template')
        _docs = self._get_report_data()

       # _get_category = self._get_categories
        docargs = {
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
            'get_total': self._get_parts_total,
            'get_category': self._get_categories,
            'get_machine': self._get_machines,
            'get_invoice': self._get_invoices,
            'get_grand_total': self._get_grand_total,
            'get_all_categ': self._get_all_categories,
            'get_types_for_categ': self._get_type_for_categories ,
            'get_total_categ_type': self._get_total_for_categ_type,
            'get_total_for_machine_type': self._get_total_for_machine_type

        }
        return report_obj.render('cmms.report_partsby_producttype_summary_template', docargs)

    def _get_report_data(self):
        _start_date = self._context.get('from_date')
        _end_date = self._context.get('to_date')
        self._inv_lines = self.env['cmms.store.invoice.line'].search([('invoice_date', '>=', _start_date),
                                                                      ('invoice_date', '<=', _end_date)])
        _partTypes = self._inv_lines.mapped('spare_part_type_id')
        return _partTypes

    def _get_parts_total(self, _type):
        _total = sum([x.amount for x in self._inv_lines if x.spare_part_type_id.id == _type])
        return _total

    def _get_categories(self, _type):
        _categs = self._inv_lines.filtered(lambda r: r.spare_part_type_id.id == _type).mapped('machine_id.category_id')
        return _categs

    def _get_all_categories(self):
        _categs = self._inv_lines.mapped('machine_id.type_id')
        return _categs

    def _get_type_for_categories(self,categ):
        _types = self._inv_lines.filtered(lambda r: r.machine_id.type_id.id == categ).mapped('spare_part_type_id')
        return _types

    def _get_total_for_categ_type(self, _type, _categ):
        _total = sum([x.amount for x in self._inv_lines if x.spare_part_type_id.id == _type and x.machine_id.type_id.id == _categ])
        return _total

    def _get_total_for_machine_type(self, _machinetype):
        _total = sum([x.amount for x in self._inv_lines if x.machine_id.type_id.id == _machinetype])
        return _total

    def _get_machines(self, _type, _categ):
       _machines = self._inv_lines.filtered(lambda r: r.machine_id.category_id == _categ and r.spare_part_type_id.id == _type).mapped('machine_id')
       return _machines

    def _get_invoices(self, _machine):
        _invoices = self._inv_lines.filtered(lambda r: r.machine_id == _machine)
        return _invoices

    def _get_grand_total(self):
        _total = sum([x.amount for x in self._inv_lines])
        return _total