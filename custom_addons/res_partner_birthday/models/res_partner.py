# -*- coding: utf-8 -*-
# © 2016 Minh.ld

from openerp import fields, models


class PartnerBirthday(models.Model):
    _inherit = "res.partner"

    birthday = fields.Date(string='Birthday')


class PartnerCard(models.Model):
    _name = 'res.partner.card'

    code = fields.Char('Code')
    name = fields.Char('Name')
    type = fields.Selection([('Employee', 'Employee'), ('Green', 'Green'), ('Gold', 'Gold')])
    point = fields.Float('Point')


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_card_id = fields.Many2one('res.partner.card', string='Card')
