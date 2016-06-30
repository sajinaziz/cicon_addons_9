{
    'name': 'CICON Email Request',
    'version': '0.1',
    'author': 'CICON',
    #'sequence': 99,
    'summary': 'CICON Email Request Form',
    'description': """CICON Email Request""",
    'website': 'http://www.cicon.net',
    'category': 'CICON IT',
    'depends': ['hr_equipment','mail'],
    'data': [
                'view/cicon_email_view.xml',
                'view/cicon_email_seq.xml',
                'view/cicon_email_report.xml',
                'view/cicon_email_print_view.xml',
                'security/ir.model.access.csv'
    ],
    'update_xml': [],
    'description': 'CICON Email Request',
    'active': False,
    'installable': True,
    'application': False,
    'auto_install': False
}
