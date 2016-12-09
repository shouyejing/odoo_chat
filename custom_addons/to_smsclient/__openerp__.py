# -*- coding: utf-8 -*-
##############################################################################
#
#    @package to_hr_insurance TO SMS Client for Odoo 8.0
#    @copyright Copyright (C) 2015 T.V.T Marine Automation (aka TVTMA). All rights reserved.#
#    @license http://www.gnu.org/licenses GNU Affero General Public License version 3 or later; see LICENSE.txt
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 OpenERP SA (<http://openerp.com>)
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'TO SMS Client',
    'version': '1.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'http://ma.tvtmarine.com',
    'summary': 'Sending SMSs very easily',
    'sequence': 25,
    'category': 'Tools',
    'description':"""
Sending SMSs very easily, individually or collectively:
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
