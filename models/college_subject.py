from odoo import models, fields


class Subject(models.Model):
    _name = "college.subjects"
    _description = "College subjects"

    name = fields.Char(string="Name")
    maximum_mark = fields.Integer(string="Maximum mark")
    subject_ids = fields.Many2one('college.semester',
                                  string='Subjects',
                                  required=True)
