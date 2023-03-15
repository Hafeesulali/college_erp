from odoo import models, fields, api


class Semester(models.Model):
    _name = "college.semester"
    _description = "College semester"
    _rec_name = "name"

    name = fields.Char(compute="_name_display", string="Name", store=True)
    number_of_semester = fields.Integer(string="Number of semester")
    course_ids = fields.Many2one('college.courses', string="Course")
    syllabus_ids = fields.One2many('college.subjects',
                                   'subject_ids',
                                   string="Subject")

    @api.depends("number_of_semester", "course_ids")
    def _name_display(self):
        for record in self:
            # print(record, "hai")
            # print(self, "hello")
            if record.number_of_semester and record.course_ids:
                record.name = "sem%s" ":" % record.number_of_semester + \
                              "%s" % record.course_ids.name
            else:
                record.name = False


