from odoo import models, fields


class MarkSheet(models.Model):
    _name = "college.marksheet"
    _description = "College marksheet"
    _rec_name = "student_id"

    student_id = fields.Many2one("college.students", string="Students")
    exam_id = fields.Many2one("college.exam", string="Exam")
    class_id = fields.Many2one("college.class", string="Class")
    course_id = fields.Many2one("college.courses", string="Course")
    semester_id = fields.Many2one("college.semester", string="Semester")
    is_pass = fields.Boolean(string="Pass/Fail")
    paper_ids = fields.One2many("college.paper",
                                "marksheet_id", string="Mark list")
    grand_total = fields.Float(string="Grand Total")
    promotion_id = fields.Many2one("college.promotion", string="Promotion")
    button_visibility = fields.Boolean(string="Button Visibility")
    total_mark = fields.Integer(string="Total Mark")

    def generate_total(self):
        self.write({"button_visibility": True})
        for record in self.paper_ids:
            if not record.is_pass:
                self.is_pass = False
                break
            else:
                self.is_pass = True
        for record in self:
            self.grand_total = sum(record.paper_ids.mapped('mark'))
            self.total_mark = sum(record.paper_ids.mapped('maximum_mark'))
