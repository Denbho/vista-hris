# -*- coding: utf-8 -*-
{
    'name': "HRIS Interview Evaluation",
    'summary': """
        Interview Evaluation Form""",
    'author': "Dennis Boy Silva",
    'category': 'hr',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'hr',
        'mail',
        'hr_recruitment',
        'hr_pre_employment_checklist',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/interview_evaluation_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
