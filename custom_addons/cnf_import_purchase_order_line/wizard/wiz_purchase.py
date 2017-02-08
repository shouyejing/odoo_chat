from openerp import models,fields,api
from openerp.tools.translate import _
import xlrd
import base64
import time
import tempfile
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


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


class wiz_import_purchase_order(models.TransientModel):
    _name = 'wiz.import.purchase.order'
    _description = 'Importer Purchase Orders'
    
    name = fields.Binary(string = 'Import Excel')
    state = fields.Selection([('init','init'),('done','done')], 
        string ='state', readonly=True, default='init')
    filename = fields.Char('Filename')
    
    @api.multi
    def _prepare_order_line(self, product_id=False, date_planned=False, product_qty=False, partner_id=False, date_order=False, order_id=False):
        vals={}

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
            plan_dt = self.env['purchase.order.line']._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, product_id.supplier_taxes_id, product_id.taxes_id) if seller else 0.0
        # if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
        #     price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)
        #
        # if seller and self.product_uom and seller.product_uom != self.product_uom:
        #     price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)




        if product_id and plan_dt and product_qty and partner_id :
            vals={
                  'product_id': product_id and product_id.id or False,
                  'date_planned': plan_dt ,
                  'product_uom': product_id and product_id.product_tmpl_id.uom_po_id.id or False,
                  'order_id': order_id,
                  'price_unit': price_unit,
                  'product_qty': product_qty or 0.0,
                  'state': 'draft',
                  'name': product_id.product_tmpl_id.description or product_id.name_template,
                  }

        return vals
    
    # @api.multi
    # def _make_draft_purchase_order(self, partner_id= False, eff_dt= False, location_id=False,
    #                                         plan_dt=False, invoice_method=False, company_id=False):
    #     vals={}
    #
    #     if partner_id and eff_dt and location_id and plan_dt and invoice_method and company_id:
    #         vals={
    #               'partner_id':partner_id and partner_id.id or False,
    #               'date_order':eff_dt ,
    #               # 'location_id':location_id and location_id.id or False,
    #               # 'minimum_planned_date':plan_dt,
    #               # 'invoice_method':str(invoice_method),
    #               'company_id':company_id and company_id.id or False,
    #               'state':'draft',
    #               # 'pricelist_id':partner_id and partner_id.property_product_pricelist_purchase.id or False
    #               }
    #     elif partner_id and eff_dt and location_id and invoice_method and company_id:
    #         vals={
    #               'partner_id':partner_id and partner_id.id or False,
    #               'date_order':eff_dt ,
    #               # 'location_id':location_id and location_id.id or False,
    #               # 'minimum_planned_date':lambda *a: time.strftime('%Y-%m-%d'),
    #               # 'invoice_method':str(invoice_method),
    #               'company_id':company_id and company_id.id or False,
    #               'state':'draft',
    #               # 'pricelist_id':partner_id and partner_id.property_product_pricelist_purchase.id or False
    #               }
    #     elif partner_id and location_id and invoice_method and company_id:
    #         vals={
    #               'partner_id': partner_id and partner_id.id or False,
    #               'date_order': lambda *a: time.strftime('%Y-%m-%d') ,
    #               # 'location_id':location_id and location_id.id or False,
    #               # 'minimum_planned_date':lambda *a: time.strftime('%Y-%m-%d'),
    #               # 'invoice_method':str(invoice_method),
    #               'company_id': company_id and company_id.id or False,
    #               'state':'draft',
    #               # 'pricelist_id':partner_id and partner_id.property_product_pricelist_purchase.id or False
    #               }
    #
    #     return vals
    
    @api.multi
    def create_purchase_orders(self):
        # product_product = self.env['product.product']
        # stock_location = self.env['stock.location']
        # res_partner = self.env['res.partner']
        # res_company = self.env['res.company']
        product_product = self.env['product.product']
        # product_template = self.env['product.template']
        product_uom = self.env['product.uom']
        purchase_order = self.env['purchase.order']
        purchase_order_line = self.env['purchase.order.line']
        filepath = self.env['ir.config_parameter'].get_param('import_po_line_file_path')
        f = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
        filename = filepath + str(self.filename)
        with open(filename, 'wb') as f:
            x = base64.b64decode(self.name)
            f.write(x)
        wb = xlrd.open_workbook(filename)
        lst = []
        view_ref = self.pool.get('ir.model.data').get_object_reference(self.env.cr,self.env.uid, 'purchase', 'purchase_order_form')
        view_id = view_ref and view_ref[1] or False

        # search_view_ref = self.pool.get('ir.model.data').get_object_reference(self.env.cr,self.env.uid, 'purchase', 'view_purchase_order_filter')
        # search_view_id = search_view_ref and search_view_ref[1] or False
        for s in wb.sheets():
            # total_rows = s.nrows
            # partner_id=False
            # location_id=False
            # company_id=False
            # date_order = False
            date_plan = False
            product_id = False
            product_qty = 0.0
            # price_unit = 0.0
            # name = False
            # uom = False
            for row in range(1, s.nrows):
                # partner = s.cell(row,0).value
                # date_order = s.cell(row,1).value
                # location = s.cell(row,2).value
                # invoice_method = s.cell(row,4).value
                # company = s.cell(row,5).value
                product = s.cell(row,0).value
                product_qty = s.cell(row,1).value
                date_plan = s.cell(row, 2).value
                # name = s.cell(row,8).value
                # uom = s.cell(row,9).value
                # price_unit = s.cell(row,10).value
                # if partner:
                #     partner_id = res_partner.search([('name','ilike',partner),('supplier','=',True)])
                # if company :
                #     company_id = res_company.search([('name','=',company)])
                # if location:
                #     location_id = stock_location.search([('name','=',location),('usage','=','internal'),('company_id','=',company_id.id)])
                # if date_order:
                #     try :
                #         if date_order and isinstance(date_order, (long, int, float)):
                #             seconds1 = (date_order - 25569) * 86400.0
                #             eff_dt=datetime.utcfromtimestamp(seconds1).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                #         elif date_order:
                #             serial1=str(date_order)
                #             # dt1=str(date_order).replace('/','-')
                #             dj_date = datetime.strptime(serial1,'%d/%m/%Y %H:%M:%S')
                #             eff_dt=dj_date.strftime('%Y/%m/%d %H:%M:%S')
                #     except :
                #         pass
                # if planned_date:
                #     try :
                #         if planned_date and isinstance(planned_date, (long, int, float)):
                #             seconds1 = (planned_date - 25569) * 86400.0
                #             plan_dt=datetime.utcfromtimestamp(seconds1).strftime('%Y-%m-%d')
                #         elif planned_date:
                #             serial1=str(planned_date)
                #             # dt1=str(planned_date).replace('/','-')
                #             dj_date = datetime.strptime(serial1,'%d/%m/%Y %H:%M:%S')
                #             plan_dt=dj_date.strftime('%Y/%m/%d %H:%M:%S')
                #     except :
                #         pass
                if product:
                    product_id = product_product.search([('name_template', '=', product)])
                # if product_uom:
                #     uom_id = product_uom
                # result = self._make_draft_purchase_order(partner_id, eff_dt, location_id,
                #                                   plan_dt, invoice_method, company_id)
                active_id = self.env.context.get('active_id')
                po = purchase_order.browse(active_id)
                order_line = self._prepare_order_line(product_id, date_plan, product_qty, po.partner_id, po.date_order, po.id)

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
            # 'views': [(False, 'list'), (False, 'kanban'), (view_id, 'form'), (False, 'pivot'), (False, 'graph'), (False, 'calendar')],
            'target': 'current',
            'nodestroy': True,
            # 'search_view_id': search_view_id,
            # 'context': self.env.context,
        }
