{
'name': "website_therp",
'description': """
Website module for educational purposes
""",
'depends': ['base',
            'website',
           ],
'data': [
        'templates/templates.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        ],
}
