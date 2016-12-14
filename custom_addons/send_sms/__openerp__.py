# -*- coding: utf-8 -*-
##############################################################################
#
#    @copyright Copyright (C) 2016 Canifa. All rights reserved.#
#    @license http://www.gnu.org/licenses GNU Affero General Public License version 3 or later; see LICENSE.txt
#
##############################################################################
{
    'name' : 'Send sms',
    'version': '1.0.1',
    'author' : 'Canifa',
    'website': 'http://canifa.com',
    'summary': 'Sending sms',
    'sequence': 25,
    'category': 'Tool',
    'description':"""
    Sending SMS
=======================================================

    """,
    'depends': ['base','mail'],
    'data': [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/smsclient_view.xml",
        "views/serveraction_view.xml",
#        "smsclient_wizard.xml",
        "data/smsclient_data.xml",
        "wizard/mass_sms_view.xml",
        "views/partner_sms_send_view.xml",
        "views/smstemplate_view.xml"                                         
    ],
    'installable': True,
    'application': False,
}
