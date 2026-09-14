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

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            spreadsheet_credentials=self.env['ir.config_parameter'].sudo().get_param('cafe.spreadsheet_credentials', default=''),
            direct_database_name=self.env['ir.config_parameter'].sudo().get_param('cafe.direct_database_name', default=''),
            direct_domain_url=self.env['ir.config_parameter'].sudo().get_param('cafe.direct_domain_url', default='')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('cafe.spreadsheet_credentials', self.spreadsheet_credentials or '')
        self.env['ir.config_parameter'].sudo().set_param('cafe.direct_database_name', self.direct_database_name or '')
        self.env['ir.config_parameter'].sudo().set_param('cafe.direct_domain_url', self.direct_domain_url or '')
