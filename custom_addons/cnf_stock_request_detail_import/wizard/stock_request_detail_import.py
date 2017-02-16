# -*- coding: utf-8 -*-
import xlrd
import base64
import tempfile
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning


class StockRequestDetailImport(models.TransientModel):
    _name = 'import.stock.request.detail.wizard'

    name = fields.Binary(string='Import Excel')
    filename = fields.Char('Filename')

    @api.multi
    def _prepare_stock_request_detail(self, request_id, product, qty):
        vals = {
            'request_id': request_id,
            'product_id': product.id,
            'qty': qty,
        }
        return vals

    @api.multi
    def create_stock_request_detail(self):
        product_product = self.env['product.product']
        stock_request_detail = self.env['stock.request.detail']
        # file_path = self.env['ir.config_parameter'].get_param('import_stock_request_detail_path')
        # file_object = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
        # filename = file_path + str(self.filename)
        # with open(self.name, 'wb') as file_object:
        #     data = base64.b64decode(self.name)
        #     file_object.write(data)
        data = base64.b64decode(self.name)
        wb = xlrd.open_workbook(file_contents=data)

        active_id = self.env.context.get('active_id')
        error_product = ''
        for sheet in wb.sheets():
            for row in range(1, sheet.nrows):
                product_default_code = sheet.cell(row, 0).value
                product_qty = sheet.cell(row, 1).value

                if product_default_code:
                    product = product_product.search([('default_code', '=', product_default_code)])
                    if product:
                        request_detail = self._prepare_stock_request_detail(active_id, product, product_qty)
                        stock_request_detail.create(request_detail)
                    else:
                        error_product += product_default_code + _(' in row ') + str(row + 1) + '\n'
            if error_product:
                raise Warning(_('Cannot find products: \n') + error_product[:len(error_product) - 1])

        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Orders'),
            'res_model': 'stock.request',
            'res_id': active_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
        }
