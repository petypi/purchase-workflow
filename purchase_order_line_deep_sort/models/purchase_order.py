# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models
from .res_company import SORTING_CRITERIA, SORTING_DIRECTION


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    line_order = fields.Selection(
        selection=SORTING_CRITERIA,
        string='Sort Lines By',
        default=lambda self: self.env.user.company_id.default_po_line_order,
    )
    line_direction = fields.Selection(
        selection=SORTING_DIRECTION,
        string='Sort Direction',
        default=lambda self:
            self.env.user.company_id.default_po_line_direction,
    )

    @api.onchange('line_order')
    def onchange_line_order(self):
        if not self.line_order:
            self.line_direction = False

    @api.multi
    def _sort_purchase_line(self):
        def resolve_subfields(obj, line_order):
            subfields = line_order.split('.')
            res = obj
            for subfield in subfields:
                res = getattr(res, subfield)
            return res

        if not self.line_order and not self.line_direction:
            return
        reverse = self.line_direction == 'desc'
        sequence = 0
        sorted_lines = self.order_line.sorted(
            key=lambda p: resolve_subfields(p, self.line_order),
            reverse=reverse,
        )
        for line in sorted_lines:
            sequence += 10
            line.sequence = sequence

    @api.multi
    def write(self, values):
        res = super(PurchaseOrder, self).write(values)
        if 'order_line' in values or 'line_order' in values or \
                'line_direction' in values:
            self._sort_purchase_line()
        return res

    @api.model
    def create(self, values):
        purchase = super(PurchaseOrder, self).create(values)
        purchase._sort_purchase_line()
        return purchase
