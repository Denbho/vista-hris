# -*- coding: utf-8 -*-
{
    'name': "Employee Certification",
    'summary': """
        Employee Certification Report""",
    'author': "Elmo Bunani, Ruel Costob And Dennis Boy Silva",
    'category': 'HUMAN RESOURCE',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'hr_contract',
        'hr',
        'mail',
        'document_approval',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'report/emp_certificate_view.xml',
        'report/emp_certificate_template.xml',
        'wizard/approve_coe.xml',
        'views/coe.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,

}
