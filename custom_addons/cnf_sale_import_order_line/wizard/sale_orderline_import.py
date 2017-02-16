# -*- coding: utf-8 -*-
import xlrd
import base64
import tempfile
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning


class SaleOrderLineImport(models.TransientModel):
    _name = 'import.sale.order.line.wizard'

    name = fields.Binary(string='Import Excel')
    state = fields.Selection([('init', 'init'), ('done', 'done')],
                             string='state', readonly=True, default='init')
    filename = fields.Char('Filename')

    @api.multi
    def _prepare_order_line(self, product, qty, price_unit, order_id):
        vals = {
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'price_unit': price_unit,  # TODO
            'order_id': order_id
        }

        return vals

    @api.multi
    def create_sale_order_line(self):

        product_product = self.env['product.product']

        product_uom = self.env['product.uom']
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']
        filepath = self.env['ir.config_parameter'].get_param('import_so_line_file_path')
        file_object = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
        filename = filepath + str(self.filename)
        with open(filename, 'wb') as file_object:
            data = base64.b64decode(self.name)
            file_object.write(data)
        wb = xlrd.open_workbook(filename)

        # view_ref = self.pool.get('ir.model.data').get_object_reference(self.env.cr, self.env.uid, 'sale',
        #                                                                'view_order_form')
        # view_id = view_ref and view_ref[1] or False
        active_id = self.env.context.get('active_id')
        for s in wb.sheets():
            product_id = False
            product_qty = 0.0
            price_unit = 0.0

            for row in range(1, s.nrows):

                product = s.cell(row, 0).value
                product_qty = s.cell(row, 1).value
                price_unit = s.cell(row, 2).value

                if product:
                    product_id = product_product.search([('name_template', '=', product)])
                else:
                    raise Warning(_('Please input product in line: ') + str(row + 1))
                if not product_id:
                    raise Warning(_('Cannot find product: ') + str(product))
                # if product_uom:
                #     uom_id = product_uom
                # result = self._make_draft_purchase_order(partner_id, eff_dt, location_id,
                #                                   plan_dt, invoice_method, company_id)

                so = sale_order.browse(active_id)
                order_line = self._prepare_order_line(product_id, product_qty, price_unit, so.id)

                record = sale_order_line.create(order_line)
                record.product_id_change()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Orders'),
            'res_model': 'sale.order',
            'res_id': active_id,
            'view_type': 'form',
            'view_mode': 'form',
            # 'views': [(False, 'list'), (False, 'kanban'), (view_id, 'form'), (False, 'pivot'), (False, 'graph'), (False, 'calendar')],
            'target': 'current',
            'nodestroy': True,
            # 'search_view_id': search_view_id,
            # 'context': self.env.context,
        }
