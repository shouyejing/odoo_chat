# -*- coding: utf-8 -*-
# © 2016 Minh.ld

from openerp.osv import osv, orm, fields
from datetime import datetime


class SendMailProjectTask(osv.osv):
    _inherit = "res.partner"

    def reminder_project_task(self, cr, uid, ids=None, context=None):
        current_date = datetime.now().strftime('%Y-%m-%d')
        list_task = self.pool.get('project.task').search(cr, uid, [('date_deadline', '=', current_date)])
        for task in list_task:
            list_followers = self.pool.get('mail.followers').search_read(cr, uid, [('res_id', '=', task), ('res_model', '=', 'project.task')], ['partner_id'])
            for followers in list_followers:
                partner = self.browse(cr, uid, followers['partner_id'][0])
                temp_obj = self.pool.get('mail.template')
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cnf_project_task_reminder', 'email_template_task_reminder')[1]

                values = temp_obj.generate_email(cr, uid, template_id, partner.id, context=context)

                menu_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'menu_action_view_task')
                action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'project', 'action_view_task')
                base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
                link = '#'
                if menu_id and action_id and base_url:
                    link = 'web?#id=%s&view_type=form&model=project.task&menu_id=%s&action=%s' % (
                    task, menu_id[1], action_id[1])

                values['email_to'] = partner.email
                values['body_html'] = values['body_html'].replace('@@link@@', link)

                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)

                # temp_obj.send_mail(cr, uid, template_id, partner.id, force_send=True, context=context)

