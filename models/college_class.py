from odoo import models, fields, api


class CollegeClass(models.Model):
    _name = "college.class"
    _rec_name = "name"

    name = fields.Char(compute="_name_display", store=True)
    semester_id = fields.Many2one("college.semester", string="Semester")
    course_id = fields.Many2one("college.courses", string="Course")
    academic_year_id = fields.Many2one("college.academic",
                                       string="Academic Year")
    student_ids = fields.One2many("college.students",
                                  "class_students_id",
                                  string="Students")
    promotion_class_id = fields.Many2one("college.class",
                                         string="Promotion Class")

    @api.depends("semester_id")
    def _name_display(self):
        for record in self:
            if record.semester_id.name and record.academic_year_id:
                record.name = "%s" ":" % record.semester_id.name + \
                              "%s" % record.academic_year_id.academic_year
            else:
                record.name = False

    @api.onchange("semester_id", "academic_year_id", "course_id")
    def student_class(self):
        if self.semester_id and self.academic_year_id and self.course_id:
            rec = self.env['college.students'].search(
                [('semester_id', '=', self.semester_id.id),
                 ('course_id', '=', self.course_id.id),
                 ('academic_year_id', '=', self.academic_year_id.id)])
            for record in rec:
                record.class_students_id = self.id
