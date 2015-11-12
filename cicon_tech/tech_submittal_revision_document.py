from openerp import models, fields, api


class SubmittalRevisionDocument(models.Model):
    _name = 'tech.submittal.revision.document'
    _description = "Submittal Documents"

    name = fields.Char('Document No', size=250, required=True)
    document_type_id = fields.Many2one('tech.document_type', 'Document Types', help="Document Type : Drawing ,BBS, etc.." )
    submittal_id = fields.Many2one('tech.submittal', 'Submittal', ondelete='cascade', required=True)
    documents_revision_ids = fields.One2many('tech.submittal.document.revision', 'document_id', string="Documents")

    _sql_constraints = [('uniq_doc', 'UNIQUE(name,submittal_id,document_type_id)', 'Unique Drawing Number per Submittal Revision')]

    @api.model
    def create(self, vals):
        _rec = self.search([('name', '=', vals.get('name')),('submittal_id', '=', vals.get('submittal_id'))],limit=1)
        if _rec:
            return _rec
        else:
            return super(SubmittalRevisionDocument, self).create(vals)

SubmittalRevisionDocument()


class SubmittalDocumentRevision(models.Model):
    _name = 'tech.submittal.document.revision'
    _inherits = {
        'tech.submittal.revision.document': 'document_id',
                 }
    _description = "Submittal Documents"

    document_id = fields.Many2one('tech.submittal.revision.document', string="Document", ondelete='cascade', required=True)
    revision_id = fields.Many2one('tech.submittal.revision', 'Submittal Revisions', required=True, ondelete='cascade')
    description = fields.Char('Description', size=255)
    document_status = fields.Char('Document Status', size=10)
    rev_no = fields.Integer('Revision No')
    parent_id = fields.Many2one('tech.submittal.document.revision', "Previous Revision")
    draft_time = fields.Float('Draft/Detail Time', digits=(2, 2))
    is_revised = fields.Boolean('Revised', default=False)
    date = fields.Date('Revised Date')
    created_by = fields.Many2one('res.users', 'Revision Done By')
    state = fields.Selection(related='revision_id.state', store=True, string="State")

    _order = "name,revision_id"

    @api.model
    def create(self, vals):
        print vals
        if not vals.get('created_by') or not vals.get('date') or not vals.get('submittal_id'):
            sub_revision = self.env['tech.submittal.revision'].search([('id', '=', vals.get('revision_id'))], limit=1)
            if not vals.get('created_by'):
                vals.update({'created_by': sub_revision.submitted_by.id})
            if not vals.get('date'):
                vals.update({'date': sub_revision.submittal_date})
            if not vals.get('submittal_id'):
                vals.update({'submittal_id': sub_revision.submittal_id.id})
        res = super(SubmittalDocumentRevision, self).create(vals)
        if res:
            _rec = res.parent_id
            _rec.write({'is_revised': True})
        return res

    @api.multi
    def doc_revision(self):
        self.ensure_one()#One Record
        form_id = self.env.ref('cicon_tech.tech_submittal_doc_form_view')
        _status = self.document_status
        _rev = self.rev_no + 1
        _rev_val = _status[-1]
        if _rev_val.isdigit():
            _status = _status[:-1] + str((int(_status[-1]) + 1))
        else:
            _status = _status + str(_rev)
        ctx = dict(
            default_parent_id=self.id,
            default_name=self.document_id.name,
            default_document_type_id=self.document_id.document_type_id.id,
            default_description=self.description,
            default_document_status=_status,
            default_rev_no=_rev,
            default_revision_id=self.revision_id.id,
            default_document_id=self.document_id.id,
            default_created_by=self.revision_id.submitted_by.id,
            default_date=self.revision_id.submittal_date

        )
        return {
            'type': 'ir.actions.act_window',
            'name': "Document Revision",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tech.submittal.document.revision',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'target': 'current',
            'context': ctx,
        }


SubmittalDocumentRevision()

