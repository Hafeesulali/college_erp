from odoo import models, fields, api


class ExamPaper(models.Model):
    _name = "college.paper"
    _description = "College Paper"

    subject_id = fields.Many2one("college.subjects", string="Subject")
    pass_mark = fields.Float(string="Pass Mark")
    maximum_mark = fields.Float(string="Maximum Mark")
    mark = fields.Float(string="Mark")
    college_exam_id = fields.Many2one("college.exam", string="Exam")
    marksheet_id = fields.Many2one("college.marksheet", string="Mark Sheet")
    is_pass = fields.Boolean(string="Pass/Fail")

    @api.onchange("mark")
    def pass_or_fail(self):
        if self.mark >= self.pass_mark:
            self.is_pass = True
        else:
            self.is_pass = False
