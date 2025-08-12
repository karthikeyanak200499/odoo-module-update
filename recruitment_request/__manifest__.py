{
    'name': 'Recruitment Request Workflow',
    'version': '17.0.1.0.0',
    'summary': 'Custom recruitment request workflow with multi-company and role-based approvals',
    'description': """
Recruitment Request Workflow
============================

This module adds a custom recruitment request process with the following flow:
- Raise Request (Department User)
- HR Approval
- CAO Approval
- HR Recruitment Creation

**Key Features**
----------------
- Multi-company & role-based access control
- Email trigger on every approval stage
- HR action to convert request into recruitment
- Attachment uploads per stage
- Integration with `hr_recruitment` module
    """,
    'author': 'Karthikeyan A',
    'category': 'Human Resources',
    "depends": ["base", "hr", "mail", "hr_recruitment"],
    "data": [
        "security/security.xml",
        "models/hr_recruitment_request.xml",
        "security/ir.model.access.csv",
        "views/recruitment_request_views.xml",
        "data/email_templates.xml"
    ],
    'images': ['static/description/request_recruitment.png'],
    "installable": True,
    "application": True,
}
