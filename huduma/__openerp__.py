# -*- coding: utf-8 -*-
{
    'name': "huduma",

    'summary': """
        KenGen Huduma Service for the MDs Office""",

    'description': """
        KenGen Huduma Tool for MDs Office
    """,

    'author': "KenGen ICT",
    'website': "http://www.kengen.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'mail',
                'contacts',
                'portal',
                ],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'wizards/wizards.xml',        
        'views/views.xml',
        'views/sequences.xml',
        'views/styles.xml',
        'views/email.xml',
        'views/workflows.xml',
        'automation/automation.xml',
        'views/res_partner.xml',
        'data/default_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
} 