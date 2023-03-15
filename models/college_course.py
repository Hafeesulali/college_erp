from odoo import models, fields


class Courses(models.Model):
    _name = "college.courses"
    _description = "college course"

    name = fields.Char(string="Name")
    year = fields.Integer(string="Year")
    category = fields.Selection(
        string="Category",
        selection=[('under_graduation', 'Under Graduation'),
                   ('post_graduation', 'Post Graduation'),
                   ('diploma', 'Diploma')]
    )
    number_of_semesters = fields.Integer(string="Number of Semester")
    course_ids = fields.One2many('college.semester',
                                 'course_ids', string="Course")
