from odoo import models, fields


class CollegePromotion(models.Model):
    _name = "college.promotion"
    _description = "College Promotion"
    _rec_name = "exam_id"

    exam_id = fields.Many2one("college.exam", string="Exam")
    class_id = fields.Many2one("college.class", string="Class")
    semester_id = fields.Many2one("college.semester", string="Semester")
    promoted_students_ids = fields.One2many('college.marksheet',
                                            'promotion_id',
                                            string="Promotion")
    state = fields.Selection(
        string="State",
        selection=[('pending', 'Pending'),
                   ('completed', 'Completed')
                   ],
        default="pending"
    )
    next_class_id = fields.Many2one("college.class",
                                    string="Next Promotion Class")
    button_visibility = fields.Boolean(default=True,
                                       string="Generate Visibility")
    promote = fields.Boolean(default=True, string="Promote Visibility")

    def generate_promotion(self):
        self.write({'button_visibility': False})
        self.write({'promote': False})
        if self.exam_id and self.class_id:
            rec = self.env['college.marksheet'].search(
                [('exam_id', '=', self.exam_id.id),
                 ('class_id', '=', self.class_id.id),
                 ('is_pass', '=', True)])
            for record in rec:
                record.promotion_id = self.id

    def do_promote(self):
        self.write({'promote': True})
        self.write({'state': 'completed'})
        for record in self.promoted_students_ids:
            record.student_id.class_students_id = self.next_class_id.id
            record.student_id.semester_id = self.next_class_id.semester_id.id
