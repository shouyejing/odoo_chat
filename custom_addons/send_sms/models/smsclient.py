# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import urllib
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
try:
    from SOAPpy import WSDL
except :
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
    " e.g.: apt-get install python-soappy")

class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    def _get_sms_history(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for partner in self.browse(cr, uid, ids, context=context):
            result[partner.id] = len(partner.to_sms_history_ids)
        return result    
    
    _columns = {
        'to_sms_history_ids': fields.one2many('sms.smsclient.history', 'partner_id', 'SMS History', readonly=True),
        'to_sms_history_count': fields.function(_get_sms_history, string="SMS History", type='integer')
    }

class partner_sms_send(orm.Model):
    _name = "partner.sms.send"

    def _default_get_mobile(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        partner_pool = self.pool.get('res.partner')
        active_ids = fields.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(cr, uid, active_ids, context=context): 
            i += 1           
            res = partner.mobile
        if i > 1:
            raise orm.except_orm(_('Error'), _('You can only select one partner'))
        return res

    def _default_get_gateway(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False

    def onchange_gateway(self, cr, uid, ids, gateway_id, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        if not gateway_id:
            return {}
        gateway = sms_obj.browse(cr, uid, gateway_id, context=context)
        return {
            'value': {
                'validity': gateway.validity, 
                'classes': gateway.classes,
                'deferred': gateway.deferred,
                'priority': gateway.priority,
                'coding': gateway.coding,
                'tag': gateway.tag,
                'nostop': gateway.nostop,
            }
        }

    _columns = {
        'mobile_to': fields.char('To', size=256),
        'app_id': fields.char('API ID', size=256),
        'user': fields.char('Login', size=256),
        'password': fields.char('Password', size=256),
        'text': fields.text('SMS Message', required=True),
        'gateway': fields.many2one('sms.smsclient', 'SMS Gateway', required=True),
        'validity': fields.integer('Validity',
            help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0','0'),
                ('1','1'),
                ('2','2'),
                ('3','3')
            ], 'Priority', help='The priority of the message'),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='an optional tag'),
        'nostop': fields.boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
        'month_birthday': fields.integer('Month of Birthday'),
        'type_card': fields.selection([('Employee', 'Employee'), ('Green', 'Green'), ('Gold', 'Gold')], string='Card'),
        'state_ids': fields.many2many('res.country.state', string='Stage'),
    }

    _defaults = {
        'mobile_to': _default_get_mobile,
        'gateway': _default_get_gateway,        
    }

    def validate(self, data):
        if data.text and len(data.text) > 160:
            raise UserError(_("Message length not exceeding 160 characters"))
        if not data.gateway:
            raise UserError(_('No Gateway Found'))
        else:
            return True
    
    def sms_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id', False)
        if not active_id:
            raise orm.except_orm(_('Error'), _('No Partner Found'))
        client_obj = self.pool.get('sms.smsclient')
        for data in self.browse(cr, uid, ids, context=context):
            if self.validate(data):
                client_obj._send_message(cr, uid, active_id, data, context=context)
        return {}

    def manual_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        client_obj = self.pool.get('sms.smsclient')
        data = self.browse(cr, uid, ids, context=context)
        if self.validate(data):
            # partner_obj = self.pool.get('res.partner')
            condition = ''
            if data.month_birthday and data.month_birthday != 0:
                condition += "AND date_part('month', birthday) = {0}".format(data.month_birthday)
            if data.type_card:
                condition += " AND res_partner_card.type = '{0}'".format(data.type_card)
            if data.state_ids:
                condition += " AND res_partner.state_id in {0}".format(tuple(data.state_ids.ids))

            sql = """SELECT res_partner.id, mobile
                      FROM res_partner INNER JOIN
                      res_partner_card ON res_partner.partner_card_id = res_partner_card.id
                      WHERE active=True AND
                            customer=True AND
                            mobile is not null {0}""".format(condition)
            cr.execute(sql)
            list_partner = cr.fetchall()
            # list_partner_id = partner_obj.search(cr, uid, [('active', '=', True), ('mobile', '!=', None), ('customer', '=', True)])
            for partner in list_partner:
                data.mobile_to = partner[1]
                client_obj._send_message(cr, uid, partner[0], data, context=context)
        return True

class SMSClient(orm.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    _columns = {
        'name': fields.char('Gateway Name', size=256, required=True),
        'url': fields.char('Gateway URL', size=256,
            required=True, help='Base url for message'),
        'property_ids': fields.one2many('sms.smsclient.parms',
            'gateway_id', 'Parameters'),
        'history_line': fields.one2many('sms.smsclient.history',
            'gateway_id', 'History'),
        'method': fields.selection([
                ('http', 'HTTP Method'),
                ('http_post', 'HTTP Post Method'),
                ('smpp', 'SMPP Method')
            ], 'API Method', select=True),
        'state': fields.selection([
                ('new', 'Not Verified'),
                ('waiting', 'Waiting for Verification'),
                ('confirm', 'Verified'),
            ], 'Gateway Status', select=True, readonly=True),
        'users_id': fields.many2many('res.users',
            'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'code': fields.char('Verification Code', size=256),
        'body': fields.text('Message',
            help="The message text that will be send along with the email which is send through this server"),
        'validity': fields.integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class',
            help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message '),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ],'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='an optional tag'),
        'nostop': fields.boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
        'char_limit' : fields.boolean('Character Limit'),
        
    }

    _defaults = {
        'state': 'new',
        'method': 'http',
        'validity': 10,
        'classes': '1',
        'deferred': 0, 
        'priority': '3',
        'coding': '1',
        'nostop': True,
        'char_limit' : True, 
    }

    def _check_permissions(self, cr, uid, id, context=None):
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, cr, uid, partner_id, data, name, queue_type, context=None):
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity, 
            'classes': data.classes, 
            'deffered': data.deferred, 
            'priorirty': data.priority, 
            'coding': data.coding, 
            'tag': data.tag, 
            'nostop': data.nostop,
            'partner_id': partner_id,
            'type': queue_type,
        }

    def _send_message(self, cr, uid, partner_id, data, context=None):
        if context is None:
            context = {}
        gateway = data.gateway
        if gateway:
            if not self._check_permissions(cr, uid, gateway.id, context=context):
                raise orm.except_orm(_('Permission Error!'), _('You have no permission to access %s ') % (gateway.name,))
            url = gateway.url
            name = url
            mobile = data.mobile_to.replace(".", "")
            mobile = mobile.replace(" ", "")
            mobile = mobile.replace("-", "")
            mobile = mobile.replace("+", "")
            if mobile.isdigit() and len(mobile) >= 10:
                if mobile[:2] != '84':
                    mobile = '84' + mobile[1:]
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                    if p.type == 'user':
                        prms[p.name] = p.value
                    elif p.type == 'password':
                        prms[p.name] = p.value
                    elif p.type == 'to':
                        prms[p.name] = mobile
                    elif p.type == 'sms':
                        prms[p.name] = unicode(data.text).encode('utf-8')
                    elif p.type == 'extra':
                        prms[p.name] = p.value
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.pool.get('sms.smsclient.queue')
            vals = self._prepare_smsclient_queue(cr, uid, partner_id, data, name, 'immediate', context=context)
            queue_obj.create(cr, uid, vals, context=context)
        return True

    def _check_queue(self, cr, uid, queue_type='immediate', context=None):
        if context is None:
            context = {}
        queue_obj = self.pool.get('sms.smsclient.queue')
        history_obj = self.pool.get('sms.smsclient.history')
        sids = queue_obj.search(cr, uid, [
                ('state', '!=', 'send'),
                ('state', '!=', 'sending'),
                ('state', '!=', 'error'),
                ('type', '=', queue_type)
            ], limit=1000, context=context)

        error_ids = []
        sent_ids = []
        res = ""
        for sms in queue_obj.browse(cr, uid, sids, context=context):
            # if sms.gateway_id.char_limit:
            #     if len(sms.msg) > 160:
            #         error_ids.append(sms.id)
            #         continue
            if sms.gateway_id.method == 'http':
                # method http get
                try:
                    response = urllib.urlopen(sms.name)
                    res = response.read()
                    if res > 0:
                        queue_obj.write(cr, uid, sms.id, {'state': 'send'}, context=context)
                    else:
                        queue_obj.write(cr, uid, sms.id, {'state': 'error', 'error': res}, context=context)
                except Exception, e:
                    error_ids.append(sms.id)
                    continue
            if sms.gateway_id.method == 'http_post':
                api_key = ''
                api_secret = ''
                brandname = ''
                for p in sms.gateway_id.property_ids:
                    if p.name == 'api_key':
                        api_key = p.value
                    elif p.name == 'api_secret':
                        api_secret = p.value
                    elif p.name == 'brandname':
                        brandname = p.value
                try:
                    import requests
                    import json
                    queue_obj.write(cr, uid, sms.id, {'state': 'sending'}, context=context)
                    data = {"submission": {"api_key": api_key or '', "api_secret": api_secret or '',
                                           "sms": [{"brandname": brandname or '', "text": unicode(sms.msg).encode('utf-8'), "to": sms.mobile}]}}
                    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    result = requests.post(sms.gateway_id.url, data=json.dumps(data), headers=headers)
                    if result.status_code == 200:
                        if result.json()['submission']['sms'][0]['status'] == 0:
                            queue_obj.write(cr, uid, sms.id, {'state': 'send'}, context=context)
                        else:
                            queue_obj.write(cr, uid, sms.id, {'state': 'error', 'error': result.json()['submission']['sms'][0]['status']}, context=context)
                    else:
                        error_ids.append(sms.id)
                except Exception, e:
                    error_ids.append(sms.id)
                    continue
                    #raise orm.except_orm('Error', sms.name)
            ### New Send Process OVH Dedicated ###
            ## Parameter Fetch ##
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                    elif p.type == 'password':
                        pwd = p.value
                    elif p.type == 'sender':
                        sender = p.value
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    message = ''
                    if sms.coding == '2':
                        message = str(sms.msg).decode('iso-8859-1').encode('utf8')
                    if sms.coding == '1':
                        message = str(sms.msg)
                    result = soap.telephonySmsUserSend(str(login), str(pwd),
                        str(account), str(sender), str(sms.mobile), message,
                        int(sms.validity), int(sms.classes), int(sms.deferred),
                        int(sms.priority), int(sms.coding),str(sms.gateway_id.tag), int(sms.gateway_id.nostop))
                    ### End of the new process ###
                except Exception, e:
                    raise orm.except_orm('Error', e)
            history_obj.create(cr, uid, {
                            'name': _('SMS Sent'),
                            'gateway_id': sms.gateway_id.id,
                            'sms': sms.msg,
                            'to': sms.mobile,
                            'return_msg': res,
                            'partner_id': sms.partner_id.id,
                        }, context=context)
            # sent_ids.append(sms.id)
        # queue_obj.write(cr, uid, sent_ids, {'state': 'send'}, context=context)
        queue_obj.write(cr, uid, error_ids, {'state': 'error'}, context=context)
        return True

class SMSQueue(orm.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    _columns = {
        'name': fields.text('SMS Request', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'msg': fields.text('SMS Text', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'mobile': fields.char('Mobile No', size=256,
            required=True, readonly=True,
            states={'draft': [('readonly', False)]}),
        'gateway_id': fields.many2one('sms.smsclient',
            'SMS Gateway', readonly=True,
            states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Queued'),
            ('sending', 'Sending'),
            ('send', 'Sent'),
            ('error', 'Error'),
        ], 'Message Status', select=True, readonly=True),
        'error': fields.text('Last Error', size=256,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_create': fields.datetime('Date', readonly=True),
        'validity': fields.integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message '),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256,
            help='An optional tag'),
        'nostop': fields.boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'type': fields.selection([
            ('immediate', 'Immediate'),
            ('birthday', 'Birthday'),
            ('manual', 'Manual')], select=True, readonly=True)
    }
    _defaults = {
        'date_create': fields.datetime.now,
        'state': 'draft',
        'type': 'immediate',
    }

class Properties(orm.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    _columns = {
        'name': fields.char('Property name', size=256,
             help='Name of the property whom appear on the URL', required=True),
        'value': fields.char('Property value', size=256,
             help='Value associate on the property for the URL'),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type': fields.selection([
                ('user', 'User'),
                ('password', 'Password'),
                ('sender', 'Sender Name'),
                ('to', 'Recipient No'),
                ('sms', 'SMS Message'),
                ('extra', 'Extra Info')
            ], 'API Method', select=True,
            help='If parameter concern a value to substitute, indicate it', required=True),
    }

class HistoryLine(orm.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    _columns = {
        'name': fields.char('Description', size=160, required=True, readonly=True),
        'date_create': fields.datetime('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Username', readonly=True),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', ondelete='set null', required=True),
        'to': fields.char('Mobile No', size=15, readonly=True),
        'sms': fields.text('SMS', size=160, readonly=True),
        'return_msg': fields.text('Return Massage', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
    }

    _defaults = {
        'date_create': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        super(HistoryLine, self).create(cr, uid, vals, context=context)
        cr.commit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
