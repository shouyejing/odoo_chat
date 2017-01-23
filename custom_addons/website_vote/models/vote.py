# -*- coding: utf-8 -*-
from openerp import fields, models


class Vote(models.Model):

    _name = 'vote'

    vote_count = fields.Integer('Vote Count')
    user_id = fields.Many2one('res.users', 'User')
    blog_post_id = fields.Many2one('blog.post', 'Blog Post')


class BlogPost(models.Model):
    _inherit = "blog.post"

    author_email = fields.Char('Author/Email')
