# -*- coding: utf-8 -*-
{
    'name': "Employee: Payroll Company",
    'summary': """
            Employee: Payroll Company
        """,
    'author': "Dennis Boy Silva",
    'category': 'HR',
    'version': '13.0.1',
    'depends': [
        'hr',
        'hr_contract',
        'hr_employee_movement',
    ],
    'data': [
        'views/employee.xml',
    ],
    'installable': True,
    'auto_install': False,
}
