from odoo import models, fields


class Students(models.Model):
    _name = "college.students"
    _description = "college student"
    _rec_name = "first_name"
    _inherit = 'mail.thread'

    admission_no = fields.Char()
    admission_date = fields.Date()
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    father = fields.Char(string="Father")
    mother = fields.Char(string="Mother")
    communication_address = fields.Text(string="Communication Address")
    permanent_address = fields.Text(string="Permanent Address")
    same_as_communication = fields.Boolean(string="Same as Communication")
    phone = fields.Integer(string="Phone")
    email = fields.Char(string="Email")
    academic_year_id = fields.Many2one("college.academic",
                                       string="Academic Year")
    course_id = fields.Many2one("college.courses", string="Course")
    semester_id = fields.Many2one("college.semester", string="Semester")
    class_students_id = fields.Many2one('college.class',
                                        string="Class Students")
    marksheet_count = fields.Integer(compute='_compute_marksheet_count',
                                     string="Marksheet Count")

    def get_marksheet(self):
        # self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Marksheet',
            'view_mode': 'tree,form',
            'res_model': 'college.marksheet',
            'domain': [('student_id', '=', self.id)]

        }

    def _compute_marksheet_count(self):
        for record in self:
            record.marksheet_count = self.env['college.marksheet']. \
                search_count(
                [('student_id', '=', self.id)])
