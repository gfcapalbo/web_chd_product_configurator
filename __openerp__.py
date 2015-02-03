{
'name': "website_chd_product_configurator",
'description': """
Web front for chindu product configurator
""",
'author' : 'therp B.V.',
'depends': ['website',
            'chd_product_configurator',
           ],
'data': [
        'templates/templates.xml',
        ],
    'installable': True,
    'application': True,
}
