from odoo import models, fields, api


class CollegeExam(models.Model):
    _name = "college.exam"
    _description = "College Exam"

    name = fields.Char(compute="_name_display", store=True)
    exam_type = fields.Selection(
        string="Exam Type",
        selection=[('internal', 'Internal'),
                   ('semester', 'Semester'),
                   ('unit_test', 'Unit Test')],
    )
    class_id = fields.Many2one("college.class", string="Class", )
    semester_id = fields.Many2one("college.semester", string="Semester")
    course_id = fields.Many2one("college.courses", string="Course")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    state = fields.Selection(
        string="State",
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('completed', 'Completed')
                   ],
        default="draft"
    )
    exam_paper_ids = fields.One2many("college.paper",
                                     "college_exam_id",
                                     string="Exam Paper")
    student_count = fields.Integer(compute='compute_student_count')
    button_visibility = fields.Boolean(string="Generate button visibilty",
                                       default=True)
    marksheet_count = fields.Integer(compute='compute_marksheet_count')

    @api.onchange('exam_type')
    def _semester(self):
        if self.exam_type == "semester" and self.semester_id:
            self.write({
                'exam_paper_ids': [(5, 0)]
            })
            for rec in self.semester_id.syllabus_ids:
                self.env["college.paper"].create({
                    "college_exam_id": self.id,
                    "maximum_mark": rec.maximum_mark,
                    'subject_id': rec.id,
                })

    @api.depends("exam_type", "semester_id", "course_id")
    def _name_display(self):
        for record in self:
            if record.exam_type and record.semester_id and record.course_id:
                record.name = "%s" ":" % record.exam_type + \
                              "%s"":" % record.semester_id.name + \
                              "%s" % record.course_id.name
            else:
                record.name = False

    def action_end_date(self):
        for record in self.env["college.exam"]. \
                search([('state', '=', 'draft')]):
            if record.end_date:
                if record.end_date <= fields.Date.today():
                    record.write({'state': "completed"})

    def get_exam_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'view_mode': 'tree,form',
            'res_model': 'college.students',
            'domain': [('semester_id', '=', self.semester_id.id)],
            'context': "{'create': False}"
        }

    def compute_student_count(self):
        for record in self:
            record.student_count = self.env['college.students'].search_count(
                [('semester_id', '=', self.semester_id.id)])

    def generate_mark(self):
        self.write({'button_visibility': False})

        for record in self.class_id.student_ids:
            self.env["college.marksheet"].create({
                'exam_id': self.id,
                'class_id': self.class_id.id,
                'course_id': self.course_id.id,
                'semester_id': self.semester_id.id,
                'student_id': record.id,
                'paper_ids': [(0, 0, {
                    'subject_id': line.subject_id.id,
                    'pass_mark': line.pass_mark,
                    'maximum_mark': line.maximum_mark,
                }) for line in self.exam_paper_ids]
            })

    def get_marksheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Marksheet',
            'view_mode': 'tree,form',
            'res_model': 'college.marksheet',
            'domain': [('exam_id', '=', self.id)],
        }

    def compute_marksheet_count(self):
        for record in self:
            record.marksheet_count = self.env['college.marksheet']. \
                search_count(
                [('exam_id', '=', self.id)])
