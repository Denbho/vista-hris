# -*- coding: utf-8 -*-
{
    'name': "Employee Resume and Skills",
    'summary': """
            Added menu in the HR Config
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'hr_skills',
        'hr_access'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/resume.xml',
    ],
    'installable': True,
    'auto_install': False,
}
