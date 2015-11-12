from openerp import models, fields, api


class DrawingCreator(models.Model):
    _name = "tech.drawing.creator"
    _description = "Drawing Creator"

    start_no = fields.Integer('Start No', required=True)
    end_no = fields.Integer('End No', required=True)
    # renamed Prefix Field as many2many_tags widget not support _rec_name concept on build : 20151011
    name = fields.Char('Document Prefix', size=32, required=False)
    suffix = fields.Char('Document Suffix', size=32, required=False)
    status = fields.Char('Revision Status', size=32)
    description = fields.Char('Document Description', size=255, required=False)
    padding_zero = fields.Integer('Zero padding', default=2)

    _sql_constraints = [('padding_count', 'CHECK(padding_zero < 5)', 'Padding Zero Value Should be < 5 ')]

DrawingCreator()
