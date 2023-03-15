from odoo import models, fields, _, api
from odoo.exceptions import UserError


class Admission(models.Model):
    _name = "college.admission"
    _description = "College Admission"
    _rec_name = "first_name"
    _inherit = 'mail.thread'

    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    father = fields.Char(string="Father")
    mother = fields.Char(string="Mother")
    communication_address = fields.Text(string="Communication Address")
    permanent_address = fields.Text(string="Permanent Address")
    same_as_communication = fields.Boolean(string="Same as Communication")
    phone = fields.Integer(string="Phone")
    email = fields.Char(string="Email")
    course_id = fields.Many2one("college.courses", string="Course")
    date_of_application = fields.Date(string="Date of Application")
    academic_year_id = fields.Many2one("college.academic",
                                       string="Academic Year")
    previous_educational_qualification = fields.Selection(
        string="Previous Educational Qualification",
        selection=[('higher_secondary', 'Higher Secondary'),
                   ('ug', 'UG'),
                   ('pg', 'PG')]
    )
    education_institute = fields.Char(string="Educational Institute")
    transfer_certificate = fields.Binary(string="Transfer Certificate")
    state = fields.Selection(
        string="State",
        selection=[('draft', 'Draft'),
                   ('application', 'Application'),
                   ('approved', 'Approved'),
                   ('done', 'Done'),
                   ('rejected', 'Rejected')
                   ],
        default="draft"
    )

    admission_no = fields.Char(string='Admission No', required=True,
                               readonly=True, default=lambda self: _('New'))
    admission_date = fields.Date(default=lambda self: fields.Date.today())
    student_count = fields.Integer(compute='_compute_count')

    @api.constrains("transfer_certificate")
    def validate_tc(self):
        if not self.transfer_certificate:
            raise UserError("please upload Tc")

    def button_application(self):
        self.write({'state': "application"})

    def button_done(self):
        self.write(({'state': 'done',
                     'admission_no': self.env['ir.sequence'].next_by_code(
                         'college.admission') or _('New')}))
        mail_template = self.env.ref('college_erp.done_email_template')
        mail_template.send_mail(self.id, force_send=True)
        self.env['college.students'].create({
            'admission_no': self.admission_no,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'father': self.father,
            'mother': self.mother,
            'communication_address': self.communication_address,
            'permanent_address': self.permanent_address,
            'phone': self.phone,
            'email': self.email,
            'academic_year_id': self.academic_year_id.id,
            'course_id': self.course_id.id

        })

    def button_rejected(self):
        self.state = 'rejected'
        self.write(({'state': 'rejected'}))
        mail_template = self.env.ref('college_erp.reject_template')
        mail_template.send_mail(self.id, force_send=True)

    def get_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'view_mode': 'tree,form',
            'res_model': 'college.students',
            'domain': [('admission_no', '=', self.admission_no)],
            'context': "{'create': False}"
        }

    def _compute_count(self):
        for record in self:
            record.student_count = self.env['college.students'].search_count(
                [('admission_no', '=', self.admission_no)])
