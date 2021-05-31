# -*- coding: utf-8 -*-
{
    'name': "Recruitment: Personnel Requisition",
    'summary': """
            Personnel Requisition Management
        """,
    'author': "Dennis Boy Silva & Ruel Costob",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'hr_skills',
        'hr_contract',
        'hr_recruitment',
        'document_approval',
        'hr_employee_ranking',
        'hr_office_location',
        'hr_employee_movement',
        'hr_department_group'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/scheduler_data.xml',
        'report/personnel_requisition_report.xml',
        'report/personnel_requisition_report_template.xml',
        'views/recruitment.xml',
        'views/employee.xml',
        'views/movement.xml',
    ],
    'installable': True,
    'auto_install': False,
}
