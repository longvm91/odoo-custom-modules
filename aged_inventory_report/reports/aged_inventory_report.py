
from odoo import api, fields, models, tools
from odoo.tools.safe_eval import safe_eval


class AgedInventoryReport(models.Model):
    _name = "aged.inventory.report"
    _description = "Aged Inventory Report"
    _auto = False

    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    product_uom = fields.Many2one(comodel_name="uom.uom", readonly=True)
    product_category = fields.Many2one(
        comodel_name="product.category", readonly=True)
    location = fields.Many2one(comodel_name="stock.location", readonly=True)
    aged_1_30_days = fields.Float()
    aged_1_30_days_amount = fields.Float()
    aged_31_90_days = fields.Float()
    aged_31_90_days_amount = fields.Float()
    aged_91_180_days = fields.Float()
    aged_91_180_days_amount = fields.Float()
    aged_181_360_days = fields.Float()
    aged_181_360_days_amount = fields.Float()
    aged_over_360_days = fields.Float()
    aged_over_360_days_amount = fields.Float()
    total_product_out = fields.Float()

    def init_results(self, filter_fields):
        # groupby location
        query_ = """
            SELECT 
                row_number() over () as id,
                a.product_id,
                a.product_uom,
                a.location,
                sum(a.aged_1_30_days) as aged_1_30_days,
                sum(a.aged_1_30_days_amount) as aged_1_30_days_amount,
                sum(a.aged_31_90_days) as aged_31_90_days,
                sum(a.aged_31_90_days_amount) as aged_31_90_days_amount,
                sum(a.aged_91_180_days) as aged_91_180_days,
                sum(a.aged_91_180_days_amount) as aged_91_180_days_amount,
                sum(a.aged_181_360_days) as aged_181_360_days,
                sum(a.aged_181_360_days_amount) as aged_181_360_days_amount,
                sum(a.aged_over_360_days) as aged_over_360_days,
                sum(a.aged_over_360_days_amount) as aged_over_360_days_amount,
                SUM(a.total_product_out) as total_product_out
            FROM
                (SELECT 
                    sm.product_id, 
                    sm.product_uom, 
                    sm.location_dest_id as location,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '30days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE
                        THEN sm.product_qty ELSE 0 END
                    ) as aged_1_30_days,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '30days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE
                        THEN sm.product_qty*svl.unit_cost ELSE 0 END
                    ) as aged_1_30_days_amount,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '90days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '30days'
                        THEN sm.product_qty ELSE 0 END
                    ) as aged_31_90_days,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '90days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '30days'
                        THEN sm.product_qty*svl.unit_cost ELSE 0 END
                    ) as aged_31_90_days_amount,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '180days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '90days'
                        THEN sm.product_qty ELSE 0 END
                    ) as aged_91_180_days,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '180days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '90days'
                        THEN sm.product_qty*svl.unit_cost ELSE 0 END
                    ) as aged_91_180_days_amount,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '360days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '180days'
                        THEN sm.product_qty ELSE 0 END
                    ) as aged_181_360_days,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) >= CURRENT_DATE - INTERVAL '360days'
                            and CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '180days'
                        THEN sm.product_qty*svl.unit_cost ELSE 0 END
                    ) as aged_181_360_days_amount,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '360days'
                        THEN sm.product_qty ELSE 0 END
                    ) as aged_over_360_days,
                    SUM(CASE WHEN
                            CAST(sm.date AS DATE) < CURRENT_DATE - INTERVAL '360days'
                        THEN sm.product_qty*svl.unit_cost ELSE 0 END
                    ) as aged_over_360_days_amount,
                    null as total_product_out
                FROM 
                    stock_move sm
                    LEFT JOIN stock_valuation_layer svl ON sm.id = svl.stock_move_id
                    LEFT JOIN stock_location location_dst ON sm.location_dest_id = location_dst.id
                    LEFT JOIN product_product product ON sm.product_id = product.id
                        LEFT JOIN product_template template ON product.product_tmpl_id = template.id
                WHERE 
                    sm.state='done'
                    and location_dst.usage = 'internal'
                GROUP BY
                    sm.product_id,
                    sm.product_uom,
                    sm.location_dest_id
                UNION ALL
                SELECT 
                    sm.product_id, 
                    sm.product_uom, 
                    sm.location_id as location,
                    null as aged_1_30_days,
                    null as aged_1_30_days_amount,
                    null as aged_31_90_days,
                    null as aged_31_90_days_amount,
                    null as aged_91_180_days,
                    null as aged_91_180_days_amount,
                    null as aged_181_360_days,
                    null as aged_181_360_days_amount,
                    null as aged_over_360_days,
                    null as aged_over_360_days_amount,
                    SUM(sm.product_qty) as total_product_out
                FROM 
                    stock_move sm
                    LEFT JOIN stock_valuation_layer svl ON sm.id = svl.stock_move_id
                    LEFT JOIN stock_location location_src ON sm.location_id = location_src.id
                    LEFT JOIN product_product product ON sm.product_id = product.id
                        LEFT JOIN product_template template ON product.product_tmpl_id = template.id
                WHERE 
                    sm.state='done'
                    and location_src.usage = 'internal'
                GROUP BY
                    sm.product_id,
                    sm.product_uom,
                    sm.location_id) as a
            GROUP BY 
                a.product_id,
                a.product_uom,
                a.location
        """
        params = ()
        tools.drop_view_if_exists(self._cr, self._table)
        res = self._cr.execute(
            """CREATE VIEW {} as ({})""".format(self._table, query_), params)
        return res
