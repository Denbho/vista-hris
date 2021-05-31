# -*- coding: utf-8 -*-
{
    'name': "Overtime Application",

    'summary': """
        HRIS Request Overtime Application""",

    'description': """
        Request Overtime application
    """,

    'author': "Elmo Bunani & Ruel Costob",
    'category':'Extra Tools',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'hr',
        'mail'
        ],
    'data': [
        'views/hris_overtime_req.xml',
        'data/overtime_request_seq.xml',
        # 'data/overtime_state_demo.xml',
        'security/ir.model.access.csv',
        'security/overtime_request_sec.xml'

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,

}
