# -*- coding: utf-8 -*-
{
    'name': 'Cost Price as Code in Barcode',
    'version': '11.0.1.0.0',
    'summary': """Print user defined product labels.""",
    'description': """The module enables user to print customized product labels.
                    """,
    'category': 'Tools',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'web', 'product', 'account'],
    'website': 'https://www.cybrosys.com',
    'data': [
        'report/product_label_template.xml',
        'views/barcode_generator_view.xml',
    ],
    'qweb': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
