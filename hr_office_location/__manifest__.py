# -*- coding: utf-8 -*-
{
    'name': "Employee: Office Location",
    'summary': """
            Employee Office Location
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'localize_address'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/office_location.xml',
    ],
    'installable': True,
    'auto_install': False,
}
