#  -*- coding: utf-8 -*-
#  Odoo, Open Source Ballester Hr Attendance.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
{
    'name': 'Ballester Hr Attendance',
    'category': 'Hr',
    'author': 'ITMusketeers Consultancy Services LLP',
    'description': """
================================================================================

1.  To View Hr Attendance.

================================================================================
""",
    'depends': ['hr_attendance','ballester_survey_extend',  'itm_material',  'base', 'web', 'hr'],
    'summary': 'To View Hr Attendance.',

    'data': [ 
             'views/asset.xml',
             'views/web.xml',
             'views/sidebar.xml',
             'views/user_view.xml',
            ],
    'qweb': [
        "static/src/xml/hr_attendance_extend.xml",
    ],
    'installable': True,

}
