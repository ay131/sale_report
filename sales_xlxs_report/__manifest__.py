{
    'name': "Sales Xlxs Report",
    'summary': """ """,
    'author': "ay",
    'website': "",
    'sequence': -100,

    'category': '',
    'version': '0.1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': ['base','sale','sale_management'],

    'data': [
        'data/server_action.xml',

        'security/ir.model.access.csv',
        'wizard/sale_xlxs_report.xml',

    ],

}
