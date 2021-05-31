# -*- coding: utf-8 -*-
{
    'name': "Employee Movement",
    'summary': """
            Employee Movement Management
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'hr_contract',
        'hr_employee_ranking',
        'hr_employee_number',
        'document_approval',
        'hr_department_group',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/movement.xml',
        'views/scheduler_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
