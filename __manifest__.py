{'name': 'College Erp',
 'sequence': -1,
 'version': '16.0.1.0.0',
 'depends': ['mail', 'sale'],

 'data': ['security/ir.model.access.csv',
          'data/email_template.xml',
          'data/reject_email_template.xml',
          'wizard/marksheet_wizard_view.xml',
          'report/student_wise_report.xml',
          'report/class_wise_report.xml',
          'views/college_student_views.xml',
          'views/college_courses_views.xml',
          'views/college_admission_views.xml',
          'views/college_marksheet_views.xml',
          'views/college_semester_views.xml',
          'views/college_class_views.xml',
          'views/college_promotion_views.xml',
          'views/college_paper_views.xml',
          'views/college_subject_views.xml',
          'views/college_exam_views.xml',
          'views/college_academic_views.xml',
          'views/college_erp_menus.xml'],
 'assets': {
     "web.assets_backend": ['college_erp/static/src/js/xls_action_manager.js']
 },
 'installable': True,
 'application': True,
 'auto_install': False

 }
