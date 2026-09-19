# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    state = fields.Selection([
        ('draft', 'Pending'),
        ('loaded', 'In POS Cart'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, index=True)

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.price_subtotal for line in order.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cafe.order') or 'New'
        return super(CafeOrder, self).create(vals_list)

    @api.model
    def get_pending_orders(self):
        """Returns pending cafe orders (state='draft') for POS consumption."""
        orders = self.search([('state', '=', 'draft')])
        result = []
        for order in orders:
            lines = []
            for line in order.line_ids:
                lines.append({
                    'id': line.id,
                    'product_id': line.product_id.id,
                    'product_name': line.product_id.display_name,
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'price_subtotal': line.price_subtotal,
                })
            result.append({
                'id': order.id,
                'name': order.name,
                'order_time': fields.Datetime.to_string(order.order_time),
                'customer_name': order.customer_name,
                'mobile_phone': order.mobile_phone or '',
                'table_number': order.table_number,
                'amount_total': order.amount_total,
                'lines': lines,
            })
        return result

    @api.model
    def action_set_loaded(self, order_id):
        """Marks a cafe order as loaded into POS."""
        order = self.browse(order_id)
        if order and order.state == 'draft':
            order.write({'state': 'loaded'})
            return True
        return False

    @api.model
    def action_set_done(self, order_id):
        """Marks a cafe order as completed."""
        order = self.browse(order_id)
        if order:
            order.write({'state': 'done'})
            return True
        return False


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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('price_unit') and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                if product:
                    vals['price_unit'] = product.lst_price
        return super(CafeOrderLine, self).create(vals_list)

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
