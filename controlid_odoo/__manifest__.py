# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Controlid Odoo',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'summary': 'Integration controlid with Odoo hr Attendance',
    'description': """
This module integrates the Controlid biometric system with Odoo's HR Attendance module. 
It allows for the synchronization of attendance records, including check-in and check-out times, as well as interval times. 
This integration helps streamline attendance management and ensures accurate record-keeping for employees using 
Controlid devices.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['hr_attendance', 'l10n_br_hr'],
    'data': [
        'views/attendance_view.xml',
        'data/ir_parameter_data.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
}
