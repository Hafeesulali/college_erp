from odoo import models, fields


class AcademicYear(models.Model):
    _name = "college.academic"
    _description = "Academic Year"
    _rec_name = "academic_year"

    academic_year = fields.Char(compute="_compute_year",
                                string="Academic Year", store=True)
    from_date = fields.Date(string="From Date")
    end_date = fields.Date(string="End Date")

    def _compute_year(self):
        for i in self:
            i.academic_year = "%s" "-" % i.from_date.year + \
                              "%s" % i.end_date.year
