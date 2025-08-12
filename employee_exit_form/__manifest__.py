{
    "name": "Employee Exit Interview Form",
    "summary": "Structured exit interview & approvals (Dept → HR → CAO)",
    "version": "17.0",
    "category": "Human Resources/Employees",
    "depends": ["base", "hr", "mail"],
    "author": "Karthikeyan A",
    "category": "Human Resources",
    "license": "LGPL-3",
    "description": "Custom module for Employee Exit Interview Forms",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/employee_exit_form.xml"
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": True,
}
