# -*- coding: utf-8 -*-
{
    'name': "Recruitment: Document Requirement",
    'summary': """
            Pre-employment Document Requirements
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'hr_recruitment',
        'hr_personnel_requisition',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/checklist.xml',
    ],
    'installable': True,
    'auto_install': False,
}
