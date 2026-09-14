# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    spreadsheet_id = fields.Char(
        string='Spreadsheet ID / URL',
        config_parameter='cafe.spreadsheet_id'
    )
    spreadsheet_credentials = fields.Text(
        string='Google Service Account JSON / Credentials'
    )
    spreadsheet_sync_active = fields.Boolean(
        string='Enable Spreadsheet Sync',
        config_parameter='cafe.spreadsheet_sync_active'
    )
    direct_domain_active = fields.Boolean(
        string='Direct Domain to Database',
        config_parameter='cafe.direct_domain_active'
    )
    direct_database_name = fields.Char(
        string='Database',
        config_parameter='cafe.direct_database_name'
    )
    direct_domain_url = fields.Char(
        string='Direct Domain URL',
        config_parameter='cafe.direct_domain_url'
    )
    product_category_active = fields.Boolean(
        string='Product Category Active',
        config_parameter='cafe.product_category_active'
    )
    product_category_ids = fields.Many2many(
        'product.category',
        string='Product Categories'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        category_ids_str = ICP.get_param('cafe.product_category_ids', default='')
        category_ids = [int(x) for x in category_ids_str.split(',') if x.strip().isdigit()]
        res.update(
            spreadsheet_credentials=ICP.get_param('cafe.spreadsheet_credentials', default=''),
            direct_database_name=ICP.get_param('cafe.direct_database_name', default=''),
            direct_domain_url=ICP.get_param('cafe.direct_domain_url', default=''),
            product_category_ids=[(6, 0, category_ids)]
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('cafe.spreadsheet_credentials', self.spreadsheet_credentials or '')
        ICP.set_param('cafe.direct_database_name', self.direct_database_name or '')
        ICP.set_param('cafe.direct_domain_url', self.direct_domain_url or '')
        category_ids_str = ','.join(str(cid) for cid in self.product_category_ids.ids)
        ICP.set_param('cafe.product_category_ids', category_ids_str)
