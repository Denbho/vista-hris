# -*- coding: utf-8 -*-
{
    'name': "Employee: Health and Medicard",
    'summary': """
            Health and Medicard Management
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
    ],
    'installable': True,
    'auto_install': False,
}
