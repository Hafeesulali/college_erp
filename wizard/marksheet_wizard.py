import xlsxwriter

from odoo import models, fields
import json
import io
from odoo.tools import date_utils


class MarkSheet(models.TransientModel):
    _name = "marksheet.wizard"
    _description = "Marksheet Wizard"

    report_wise = fields.Selection(string="Student Wise/Class Wise",
                                   selection=[('student_wise', 'Student Wise'),
                                              ('class_wise', 'Class Wise')],
                                   default='student_wise')
    student_id = fields.Many2one("college.students", string="Student")
    class_id = fields.Many2one("college.class", string="Class")
    semester_id = fields.Many2one("college.semester",
                                  string="Semester",
                                  required=True)
    exam_type = fields.Selection(
        string="Exam Type",
        selection=[('internal', 'Internal'),
                   ('semester', 'Semester'),
                   ('unit_test', 'Unit Test')],
        required=True)
    result = fields.Char(string="Pass/Fail", default=True)

    def action_print(self):
        query = """select college_subjects.name,college_paper.mark,college_students.first_name,
                    college_paper.pass_mark,college_paper.is_pass
                    ,college_marksheet.grand_total,college_marksheet.total_mark,
                    college_marksheet.student_id,college_marksheet.
                    is_pass as pass_fail,college_exam.exam_type from college_subjects
                    inner join college_paper on college_paper.subject_id=college_subjects.id 
                    inner join college_marksheet on college_paper.marksheet_id=college_marksheet.id
                    inner join college_students on college_marksheet.
                    student_id = college_students.id
                    inner join college_exam on college_marksheet.
                    exam_id=college_exam.id where 1=1"""
        if self.report_wise == 'student_wise':
            cr = self._cr

            if self.exam_type:
                query += """ AND college_exam.exam_type = '%s' """ % \
                         self.exam_type
            if self.semester_id:
                query += """ AND college_marksheet.semester_id= '%s' """ % \
                         self.semester_id.id

            if self.student_id:
                query += """ AND college_marksheet.student_id= %s """ % \
                         self.student_id.id
            else:
                cr.execute(query)
                sql_dict = cr.dictfetchall()
                student_list = [*set([student['student_id']
                                      for student in sql_dict])]
                mark_dict = {}

                for student in student_list:
                    for i in sql_dict:
                        if not mark_dict.get(student, False) and student == i['student_id']:
                            mark_dict[student] = {'name': i['first_name'],
                                                  i['name']: i['mark'],
                                                  'pass_fail': i['pass_fail']}
                        else:
                            if student == i['student_id']:
                                mark_dict[student][i['name']] = i['mark']

                subjects = [*set([i.get("name") for i in sql_dict])]
                data = {
                    'model_id': self.id,
                    'exam_type': self.exam_type,
                    'semester': self.semester_id.name,
                    'subjects': subjects,
                    'sql_data': mark_dict
                }
                return self.env.ref('college_erp.action_report_marksheet'). \
                    report_action(None, data=data)

            cr.execute(query)
            sql_dict = cr.dictfetchall()

            for i in sql_dict:
                if not i.get('pass_fail'):
                    self.result = False
                    break

            data = {

                'model_id': self.id,
                'student_id': self.student_id.first_name,
                'class_id': self.class_id.id,
                'exam_type': self.exam_type,
                'result': self.result,
                'course': self.student_id.course_id.name,
                'academic_year': self.student_id.academic_year_id.academic_year,
                'sql_data': sql_dict

            }
            return self.env.ref('college_erp.action_report_marksheet'). \
                report_action(None, data=data)
        else:

            cr = self._cr

            if self.class_id:
                query += """ and college_marksheet.class_id = %s""" % \
                         self.class_id.id
            if self.semester_id:
                query += """ and college_marksheet.semester_id = %s""" % \
                         self.semester_id.id
            if self.exam_type:
                query += """ and college_exam.exam_type = '%s'""" % \
                         self.exam_type

            cr.execute(query)
            sql_dict = cr.dictfetchall()
            student_list = [*set([student['student_id'] for student in sql_dict])]
            mark_dict = {}

            for student in student_list:
                for i in sql_dict:
                    if not mark_dict.get(student, False) and student == i['student_id']:
                        mark_dict[student] = {'name': i['first_name'],
                                              i['name']: i['mark'],
                                              'grand_total': i['grand_total'],
                                              'pass_fail': i['pass_fail'],
                                              'total_mark': i['total_mark']}

                    else:
                        if student == i['student_id']:
                            mark_dict[student][i['name']] = i['mark']
            print(mark_dict)
            subjects = [*set([i.get("name") for i in sql_dict])]
            result_list = [(mark_dict[i]["pass_fail"]) for i in mark_dict]
            pass_count = result_list.count(True)
            fail_count = result_list.count(False)
            student_count = len([i for i in mark_dict])

            data = {
                'model_id': self.id,
                'class_id': self.class_id.name,
                'exam_type': self.exam_type,
                'subjects': subjects,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'student_count': student_count,
                'course': self.class_id.course_id.name,
                'academic_year': self.class_id.academic_year_id.academic_year,
                'sql_data': mark_dict
            }
            return self.env.ref('college_erp.action_report_classwise'). \
                report_action(None, data=data)

    def print_xlsx_report(self):
        query = """select college_subjects.name,college_paper.mark,college_students.first_name,
                            college_paper.pass_mark,college_paper.is_pass
                            ,college_marksheet.grand_total,college_marksheet.total_mark,
                            college_marksheet.student_id,college_marksheet.
                            is_pass as pass_fail,college_exam.exam_type from college_subjects
                            inner join college_paper on college_paper.subject_id=college_subjects.id 
                            inner join college_marksheet on college_paper.marksheet_id=college_marksheet.id
                            inner join college_students on college_marksheet.
                            student_id = college_students.id
                            inner join college_exam on college_marksheet.
                            exam_id=college_exam.id where 1=1"""
        if self.report_wise == 'student_wise':
            cr = self._cr

            if self.exam_type:
                query += """ AND college_exam.exam_type = '%s' """ % \
                         self.exam_type
            if self.semester_id:
                query += """ AND college_marksheet.semester_id= '%s' """ % \
                         self.semester_id.id

            if self.student_id:
                query += """ AND college_marksheet.student_id= %s """ % \
                         self.student_id.id
            else:
                cr.execute(query)
                sql_dict = cr.dictfetchall()
                student_list = [*set([student['student_id']
                                      for student in sql_dict])]
                mark_dict = {}

                for student in student_list:
                    for i in sql_dict:
                        if not mark_dict.get(student, False) and student == i['student_id']:
                            mark_dict[student] = {'name': i['first_name'],
                                                  i['name']: i['mark'],
                                                  'pass_fail': i['pass_fail']}
                        else:
                            if student == i['student_id']:
                                mark_dict[student][i['name']] = i['mark']

                subjects = [*set([i.get("name") for i in sql_dict])]
                data = {
                    'model_id': self.id,
                    'student_id': self.student_id.id,
                    'report_wise': self.report_wise,
                    'exam_type': self.exam_type,
                    'semester': self.semester_id.name,
                    'subjects': subjects,
                    'sql_data': mark_dict
                }
                return {
                    'type': 'ir.actions.report',
                    'data': {'model': 'marksheet.wizard',
                             'options': json.dumps(data,
                                                   default=date_utils.json_default),
                             'output_format': 'xlsx',
                             'report_name': 'MarkSheet Excel Report',
                             },
                    'report_type': 'xlsx',
                }

            cr.execute(query)
            sql_dict = cr.dictfetchall()

            for i in sql_dict:
                if not i.get('pass_fail'):
                    self.result = False
                    break

            data = {

                'model_id': self.id,
                'report_wise': self.report_wise,
                'student_id': self.student_id.first_name,
                'class_id': self.class_id.id,
                'exam_type': self.exam_type,
                'result': self.result,
                'course': self.student_id.course_id.name,
                'academic_year': self.student_id.academic_year_id.academic_year,
                'sql_data': sql_dict

            }

        else:

            cr = self._cr

            if self.class_id:
                query += """ and college_marksheet.class_id = %s""" % \
                         self.class_id.id
            if self.semester_id:
                query += """ and college_marksheet.semester_id = %s""" % \
                         self.semester_id.id
            if self.exam_type:
                query += """ and college_exam.exam_type = '%s'""" % \
                         self.exam_type

            cr.execute(query)
            sql_dict = cr.dictfetchall()
            student_list = [*set([student['student_id'] for student in sql_dict])]
            mark_dict = {}

            for student in student_list:
                for i in sql_dict:
                    if not mark_dict.get(student, False) and student == i['student_id']:
                        mark_dict[student] = {'name': i['first_name'],
                                              i['name']: i['mark'],
                                              'grand_total': i['grand_total'],
                                              'pass_fail': i['pass_fail'],
                                              'total_mark': i['total_mark']}

                    else:
                        if student == i['student_id']:
                            mark_dict[student][i['name']] = i['mark']

            subjects = [*set([i.get("name") for i in sql_dict])]
            result_list = [(mark_dict[i]["pass_fail"]) for i in mark_dict]
            pass_count = result_list.count(True)
            fail_count = result_list.count(False)
            student_count = len([i for i in mark_dict])

            data = {
                'model_id': self.id,
                'report_wise': self.report_wise,
                'class_id': self.class_id.name,
                'exam_type': self.exam_type,
                'subjects': subjects,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'student_count': student_count,
                'course': self.class_id.course_id.name,
                'academic_year': self.class_id.academic_year_id.academic_year,
                'sql_data': mark_dict
            }

        return {
            'type': 'ir.actions.report',
            'data': {'model': 'marksheet.wizard',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'MarkSheet Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        report_wise = data["report_wise"]
        exam_type = data["exam_type"]
        sql_data = data["sql_data"]
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center', 'color': '#5A5A5A'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px', 'border': 1, 'color': 'black'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center', 'border': 1, 'color': 'black'})
        border = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '12', 'border': 1, 'color': 'black'})

        if report_wise == "student_wise":
            if data['student_id']:
                result = data["result"]
                course = data["course"]
                academic_year = data["academic_year"]
                if result:
                    res = "Pass"
                else:
                    res = "Fail"
                sheet.merge_range('A2:K3', 'MarkSheet Report', head)
                sheet.merge_range('A7:C7', 'Exam:' + exam_type, cell_format)
                sheet.merge_range('D4:H4', data['student_id'] + ' : Marklist', cell_format)
                sheet.merge_range('D5:H5', course + ':' + academic_year, cell_format)
                sheet.merge_range('A8:C8', 'Result:' + res, cell_format)
                sheet.merge_range('A10:C10', 'Subject', border)
                sheet.merge_range('D10:F10', 'Mark', border)
                sheet.merge_range('G10:I10', 'Pass Mark', border)
                sheet.merge_range('J10:K10', 'Pass/Fail', border)
                row = 9
                for line in sql_data:
                    row += 1
                    sheet.merge_range(f'A{row + 1}:C{row + 1}', line['name'], txt)
                    sheet.merge_range(f'D{row + 1}:F{row + 1}', line['mark'], txt)
                    sheet.merge_range(f'G{row + 1}:I{row + 1}', line['pass_mark'], txt)
                    if line['is_pass']:
                        sheet.merge_range(f'J{row + 1}:K{row + 1}', "Pass", txt)
                    else:
                        sheet.merge_range(f'J{row + 1}:K{row + 1}', "Fail", txt)
            else:
                semester = data["semester"]
                subjects = data["subjects"]
                sheet.set_column(0, 4, 20)
                sheet.merge_range('A2:D3', 'MarkSheet Report', head)
                sheet.write(7, 0, "Sem: " + semester, cell_format)
                sheet.write(8, 0, "Exam: " + exam_type, cell_format)
                sheet.write(10, 0, 'Student', border)
                column = 0
                for subject in subjects:
                    column += 1
                    sheet.write(10, column, subject, border)
                sheet.write(10, column + 1, "Pass/Fail", border)
                row = 10
                for line in sql_data:
                    row += 1
                    sheet.write(row, 0, sql_data[line]['name'], txt)
                    column = 0
                    for subject in subjects:
                        column += 1
                        sheet.write(row, column, sql_data[line][subject], txt)
                    if sql_data[line]['pass_fail']:
                        sheet.write(row, column + 1, "Pass", txt)
                    else:
                        sheet.write(row, column + 1, "Fail", txt)
        else:
            class_id = data["class_id"]
            course = data["course"]
            academic_year = data["academic_year"]
            students_count = data["student_count"]
            subjects = data["subjects"]
            pass_count = data["pass_count"]
            fail_count = data["pass_count"]
            sheet.merge_range('A2:F3', 'MarkSheet Report', head)
            sheet.set_column(0, 12, 20)
            if class_id:
                sheet.merge_range('B4:D4', class_id, cell_format)
                sheet.merge_range('B5:D5', course + ':' + academic_year, cell_format)
            sheet.write(6, 0, "Exam: " + exam_type, cell_format)
            sheet.write(7, 0, "Total: " + str(students_count), cell_format)
            sheet.write(8, 0, "Pass: " + str(pass_count), cell_format)
            sheet.write(9, 0, "Fail:" + str(fail_count), cell_format)
            sheet.write(10, 0, "Ratio:" + str(pass_count) + ":" + str(fail_count), cell_format)
            sheet.write(13, 0, "Students", border)
            column = 0
            for subject in subjects:
                column += 1
                sheet.write(13, column, subject, border)
            sheet.write(13, column + 1, "Obtained Mark", border)
            sheet.write(13, column + 2, "Total Mark", border)
            sheet.write(13, column + 3, "Pass/Fail", border)
            row = 13
            for line in sql_data:
                row += 1
                sheet.write(row, 0, sql_data[line]['name'], txt)
                column = 0
                for subject in subjects:
                    column += 1
                    sheet.write(row, column, sql_data[line][subject], txt)
                sheet.write(row, column + 1, sql_data[line]['grand_total'], txt)
                sheet.write(row, column + 2, sql_data[line]['total_mark'], txt)
                if sql_data[line]['pass_fail']:
                    sheet.write(row, column + 3, "Pass", txt)
                else:
                    sheet.write(row, column + 3, "Fail", txt)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
