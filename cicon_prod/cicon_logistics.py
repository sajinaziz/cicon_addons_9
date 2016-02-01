from openerp import models, fields, api
import time


class CiconTripSummary(models.Model):
    _name = 'cicon.trip.summary'
    _description = "CICON Steel Trip Summary"

    @api.depends('trip_date_time')
    @api.multi
    def _get_date(self):
        for t in self:
            t.trip_date = None
            if t.trip_date_time:
                t.trip_date = time.strftime('%Y-%m-%d', time.strptime(t.trip_date_time, '%Y-%m-%d %H:%M:%S'))

    name = fields.Char('Trip Reference')
    customer = fields.Char('Customer')
    project = fields.Char('Project')
    location = fields.Char('Location')
    trip_date_time = fields.Datetime('Trip Date & Time')
    trip_date = fields.Date(compute=_get_date, string='Trip Date', store=True)
    truck_no = fields.Char('Truck No')
    driver = fields.Char('Driver')
    transport = fields.Char('Transport By')
    wb_weight = fields.Float("Weight Bridge Weight", digits=(18, 3))
    do_weight = fields.Float('Do Weight', digits=(20,0))

    _order = 'trip_date_time'

    @api.v7
    def load(self, cr, uid, fields, data, context=None):
        res = super(CiconTripSummary, self).load(cr, uid, fields, data, context=context)
        return res
    #
    # def run_sql(self, qry):
    #     self._cr.execute(qry)
    #     _res = self._cr.dictfetchall()
    #     return _res

CiconTripSummary()





