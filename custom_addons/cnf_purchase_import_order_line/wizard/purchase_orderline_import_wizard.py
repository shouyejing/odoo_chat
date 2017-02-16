# -*- coding: utf-8 -*-
import xlrd
import base64
import tempfile
import time
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning


# class purchase_inherit(models.Model):
#     _inherit = 'purchase.order'
#
#     @api.multi
#     def open_import_purchase(self):
#         """
#         Method to open create customer invoice form
#         """
#         # Get the client id from transport form
#         # purchase_id = self.id
#
#         # Initialize required parameters for opening the form view of invoice
#         # Get the view ref. by paasing module & name of the required form
#         view_ref = self.env['ir.model.data'].get_object_reference('cnf_import_purchase_order_line', 'view_import_purchase_orders')
#         view_id = view_ref[1] if view_ref else False
#
#         # Let's prepare a dictionary with all necessary info to open create invoice form with
#         # customer/client pre-selected
#         res = {
#             'type': 'ir.actions.act_window',
#             'name': _('Import'),
#             'res_model': 'wiz.import.purchase.order',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'target': 'new',
#             # 'context': {'po_id': purchase_id},
#             'nodestroy': True,
#         }
#
#         return res


class UploadPurchaseOrderLineWizard(models.TransientModel):
    _name = 'import.purchase.order.line.wizard'
    _description = 'Importer Purchase Orders'
    
    name = fields.Binary(string='Import Excel')
    state = fields.Selection([('init', 'init'), ('done', 'done')], string='state', readonly=True, default='init')
    filename = fields.Char('Filename')
    
    @api.multi
    def _prepare_order_line(self, product_id=False, date_planned=False, product_qty=False, partner_id=False, date_order=False, price_unit=0.0, order_id=False):
        vals = {}

        product_product = self.env['product.product']
        if not product_id:
            return

        seller = product_product._select_seller(
            product_id,
            partner_id=partner_id,
            quantity=product_qty,
            date=date_order and date_order[:10],
            uom_id=product_id.uom_id)

        if seller or not date_planned:
            date_planned = self.env['purchase.order.line']._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if seller:
            price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, product_id.supplier_taxes_id, product_id.taxes_id)
        if price_unit and seller and order_id.currency_id and seller.currency_id != order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)
        #
        # if seller and self.product_uom and seller.product_uom != self.product_uom:
        #     price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)

        if product_id and date_planned and product_qty and partner_id:
            vals = {
                  'product_id': product_id and product_id.id or False,
                  'date_planned': date_planned,
                  'product_uom': product_id and product_id.product_tmpl_id.uom_po_id.id or False,
                  'order_id': order_id.id,
                  'price_unit': price_unit,
                  'product_qty': product_qty or 0.0,
                  'state': 'draft',
                  'name': product_id.product_tmpl_id.description or product_id.name_template,
            }

        return vals

    @api.multi
    def create_purchase_order_lines(self):
        product_product = self.env['product.product']
        # product_uom = self.env['product.uom']
        purchase_order = self.env['purchase.order']
        purchase_order_line = self.env['purchase.order.line']
        file_path = self.env['ir.config_parameter'].get_param('import_po_line_file_path')
        file_object = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
        filename = file_path + str(self.filename)
        with open(filename, 'wb') as file_object:
            data = base64.b64decode(self.name)
            file_object.write(data)
        wb = xlrd.open_workbook(filename)
        # view_ref = self.pool.get('ir.model.data').get_object_reference(self.env.cr,self.env.uid, 'purchase', 'purchase_order_form')
        # view_id = view_ref and view_ref[1] or False

        # search_view_ref = self.pool.get('ir.model.data').get_object_reference(self.env.cr,self.env.uid, 'purchase', 'view_purchase_order_filter')
        # search_view_id = search_view_ref and search_view_ref[1] or False
        active_id = self.env.context.get('active_id')
        for s in wb.sheets():
            date_plan = False
            product_id = False
            product_qty = 0.0
            price_unit = 0.0
            for row in range(1, s.nrows):
                product = s.cell(row, 0).value
                product_qty = s.cell(row, 1).value
                date_plan = s.cell(row, 2).value
                price_unit = s.cell(row, 3).value

                if date_plan:
                    try:
                        if date_plan:
                            date_obj = time.strptime(date_plan, "%d/%m/%Y %H:%M:%S")
                            mk_time = time.mktime(date_obj)
                            gm_time = time.gmtime(mk_time)
                            date_plan = time.strftime("%Y-%m-%d %H:%M:%S", gm_time)  # convert to utc
                    except:
                        pass
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

                po = purchase_order.browse(active_id)
                order_line = self._prepare_order_line(product_id, date_plan, product_qty, po.partner_id, po.date_order, price_unit, po)

                purchase_order_line.create(order_line)

                # list_line = []
                # list_line.appFend([0,0, order_line])
                # list_line.append([0,0, order_line1])
                # result.update({'order_line':list_line})
                # purchase_order.create(result)

        return{
            'type': 'ir.actions.act_window',
            'name': _('Request for Quotation'),
            'res_model': 'purchase.order',
            'res_id': active_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
            # 'views': [(False, 'list'), (False, 'kanban'), (view_id, 'form'), (False, 'pivot'), (False, 'graph'), (False, 'calendar')],
            # 'search_view_id': search_view_id,
            # 'context': self.env.context,
        }
