# -*- coding: utf-8 -*-
# © 2016 Minh.ld

from openerp import fields, models


class DesignCate(models.Model):
    _name = "design.cate"

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class Style(models.Model):
    _name = 'product.option.style'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class Form(models.Model):
    _name = 'product.form'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class MaterialGroup(models.Model):
    _name = 'material.group'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class Material(models.Model):
    _name = 'material'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')
    material_group = fields.Many2one('material.group', 'Material Group')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class ProductFunction(models.Model):
    _name = 'product.function'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class Pattern(models.Model):
    _name = 'pattern'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', 'Please enter Unique Code'),
    ]


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    design_cate = fields.Many2one('design.cate', string='Cate')
    style = fields.Many2one('product.option.style', string='Option Style')
    form = fields.Many2one('product.form', string='Form')
    material = fields.Many2one('material', string='Material')
    function = fields.Many2one('product.function', string='Function')
    pattern = fields.Many2one('pattern', string='Design/ Pattern')
