# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ImexInventoryReportWizard(models.TransientModel):
    _name = "imex.inventory.report.wizard"
    _description = "Imex Inventory Report Wizard"

    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location")
    product_ids = fields.Many2many(
        comodel_name="product.product", string="Products")
    product_category_ids = fields.Many2many(
        comodel_name="product.category", string="Product Categories")
    is_groupby_location = fields.Boolean(string="Group Locations", default=True,
                                         help="If checked qty will groupby location mean count internal transfer qty else will not count internal transfer qty")

    def _prepare_imex_inventory_report(self):
        return {
            "date_from": self.date_from or "1900-01-01",
            "date_to": self.date_to or fields.Date.context_today(self),
            "product_ids": [(6, 0, self.product_ids.ids)] or None,
            "location_id": self.location_id.id or None,
            "product_category_ids": [(6, 0, self.product_category_ids.ids)] or None,
            "is_groupby_location": self.is_groupby_location,
        }

    def button_view(self):
        vals = {}
        report = self.create(self._prepare_imex_inventory_report())

        self.env["imex.inventory.report"].init_results(report)
        action = self.env.ref(
            "imex_inventory_report.action_imex_inventory_report_tree_view")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        vals["context"] = context
        return vals
