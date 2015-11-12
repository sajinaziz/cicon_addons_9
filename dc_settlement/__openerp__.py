{
    'name': 'CICON DC Settlement',
    'version': '0.1',
    'author': 'CICON',
    'sequence': 99,
    'summary': 'DC Settlement Printing',
    'description': """CICON DC Settlement """,
    'website': 'http://www.cicon.net',
    'category': 'CICON DC',
    'depends': ['base', 'mail'],
    'data': [
        'security/dc_settlement_security.xml',
        'security/ir.model.access.csv',
        'dc_settlement.xml',
        'dc_settlement_view.xml',
        'dc_settlement_report.xml',
        'report/dc_settlement_print.xml'
    ],
    'update_xml': [],
    'description': 'CICON Applications',
    'active': False,
    'installable': True,
    'application': False,
    'auto_install': False
}
