{
    'name': 'website vote',
    'category': 'Website vote',
    'sequence': 55,
    'summary': 'Vote image',
    'website': 'https://www.odoo.com/page/vote',
    'version': '1.0',
    'description': """
OpenERP E-Commerce
==================

        """,
    'depends': ['website', 'website_blog'],
    'data': [
        'data/data.xml',
        'views/website_vote_form.xml',
        # 'views/templates.xml',
        # 'views/payment.xml',
        # 'views/sale_order.xml',
        # 'views/snippets.xml',
        # 'views/report_shop_saleorder.xml',
        # 'res_config_view.xml',
        'security/ir.model.access.csv',
        # 'security/website_sale.xml',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}
