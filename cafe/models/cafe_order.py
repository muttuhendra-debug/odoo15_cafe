# -*- coding: utf-8 -*-

import json
import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CafeOrder(models.Model):
    _name = 'cafe.order'
    _description = 'Cafe Order'
    _order = 'order_time desc, id desc'

    name = fields.Char(
        string='Order Number',
        required=True,
        readonly=True,
        default=lambda self: 'New',
        copy=False
    )
    order_time = fields.Datetime(
        string='Order Time',
        default=fields.Datetime.now,
        required=True,
        readonly=True
    )
    customer_name = fields.Char(
        string='Customer Name',
        required=True
    )
    mobile_phone = fields.Char(
        string='Mobile Phone'
    )
    table_number = fields.Char(
        string='Table Number',
        required=True
    )
    line_ids = fields.One2many(
        'cafe.order.line',
        'order_id',
        string='Menu Orders'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )
    amount_total = fields.Monetary(
        string='Total Price',
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id'
    )
    is_synced = fields.Boolean(
        string='Synced to Spreadsheet',
        default=False
    )

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.price_subtotal for line in order.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cafe.order') or 'New'
        records = super(CafeOrder, self).create(vals_list)
        # Auto trigger spreadsheet sync if active
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('cafe.spreadsheet_sync_active'):
            try:
                self.env['cafe.order.line'].sync_to_spreadsheet()
            except Exception as e:
                _logger.warning("Auto sync spreadsheet on order create warning: %s", e)
        return records


class CafeOrderLine(models.Model):
    _name = 'cafe.order.line'
    _description = 'Cafe Order Line'

    order_id = fields.Many2one(
        'cafe.order',
        string='Order Reference',
        ondelete='cascade',
        required=True
    )
    order_time = fields.Datetime(
        string='Order Time',
        related='order_id.order_time',
        store=True,
        readonly=True
    )
    customer_name = fields.Char(
        string='Customer Name',
        related='order_id.customer_name',
        store=True,
        readonly=True
    )
    mobile_phone = fields.Char(
        string='Mobile Phone',
        related='order_id.mobile_phone',
        store=True,
        readonly=True
    )
    table_number = fields.Char(
        string='Table Number',
        related='order_id.table_number',
        store=True,
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    barcode = fields.Char(
        string='Barcode',
        related='product_id.barcode',
        readonly=False,
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='order_id.currency_id',
        store=True,
        readonly=True
    )
    price_unit = fields.Monetary(
        string='Sales Price',
        currency_field='currency_id'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True
    )
    price_subtotal = fields.Monetary(
        string='Total Price',
        compute='_compute_price_subtotal',
        store=True,
        currency_field='currency_id'
    )
    is_synced = fields.Boolean(
        string='Synced to Spreadsheet',
        default=False
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            if self.product_id.barcode:
                self.barcode = self.product_id.barcode

    @api.depends('price_unit', 'quantity')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.quantity

    @api.model
    def sync_to_spreadsheet(self):
        """ Sync order lines to Google Spreadsheet """
        ICP = self.env['ir.config_parameter'].sudo()
        sync_active = ICP.get_param('cafe.spreadsheet_sync_active')
        if not sync_active:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Disabled'),
                    'message': _('Spreadsheet synchronization is not enabled in settings.'),
                    'type': 'warning',
                }
            }

        spreadsheet_id = ICP.get_param('cafe.spreadsheet_id')
        credentials_json = ICP.get_param('cafe.spreadsheet_credentials')

        if not spreadsheet_id:
            raise UserError(_("Please configure Spreadsheet ID / URL in Cafe Settings."))

        lines = self.search([('is_synced', '=', False)]) if not self else self
        if not lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Completed'),
                    'message': _('No new order lines to sync.'),
                    'type': 'info',
                }
            }

        count = 0
        sync_success = False

        if credentials_json and credentials_json.strip():
            try:
                import gspread
                creds_dict = json.loads(credentials_json)
                gc = gspread.service_account_from_dict(creds_dict)
                sh = gc.open_by_key(spreadsheet_id) if not spreadsheet_id.startswith('http') else gc.open_by_url(spreadsheet_id)
                worksheet = sh.get_worksheet(0)

                if worksheet.row_count == 0 or not worksheet.cell(1, 1).value:
                    worksheet.append_row(['Order Time', 'Customer Name', 'Mobile Phone', 'Table Number', 'Product', 'Barcode'])

                rows_to_append = []
                for line in lines:
                    rows_to_append.append([
                        str(line.order_time or ''),
                        line.customer_name or '',
                        line.mobile_phone or '',
                        line.table_number or '',
                        line.product_id.display_name if line.product_id else '',
                        line.barcode or ''
                    ])
                if rows_to_append:
                    worksheet.append_rows(rows_to_append)
                sync_success = True
                count = len(lines)
            except Exception as e:
                _logger.warning("gspread sync failed: %s", str(e))

        if not sync_success and spreadsheet_id and spreadsheet_id.startswith('http'):
            http_success = True
            for line in lines:
                payload = {
                    'order_time': str(line.order_time or ''),
                    'customer_name': line.customer_name or '',
                    'mobile_phone': line.mobile_phone or '',
                    'table_number': line.table_number or '',
                    'product': line.product_id.display_name if line.product_id else '',
                    'barcode': line.barcode or ''
                }
                try:
                    resp = requests.post(spreadsheet_id, json=payload, timeout=5)
                    if resp.status_code not in (200, 201):
                        http_success = False
                except Exception as req_err:
                    _logger.error("HTTP sync error: %s", req_err)
                    http_success = False
            if http_success:
                sync_success = True
                count = len(lines)

        if sync_success:
            lines.write({'is_synced': True})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Successful'),
                    'message': _('%s order line(s) synced to Google Spreadsheet.') % count,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Warning'),
                    'message': _('Could not reach Google Spreadsheet service. Unsynced orders will be retried.'),
                    'type': 'warning',
                }
            }
