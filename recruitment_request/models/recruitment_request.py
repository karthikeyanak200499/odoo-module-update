from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class RecruitmentRequest(models.Model):
    _name = 'hr.recruitment.request'
    _rec_name = 'position_title_1'
    _description = 'Recruitment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Recruitment Name", )
    number = fields.Char(string="", readonly=True, default='New')

    notes = fields.Text(string="Other Info")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'MRF HR Approval'),
        ('approved', 'MRF CAO Approval'),
        ('hr_approved', 'MRF Approved'),
        ('recruitment', 'MRF Published'),
        ('done', 'Done'),
        ('rejected', 'Rejected')
    ], string="Status", default="draft", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            company_id = vals.get('company_id') or self.env.company.id
            try:
                sequence = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code(
                    'hr.recruitment.request')
                vals['number'] = sequence or _('New')
            except Exception as e:
                raise UserError(f"Sequence generation failed: {str(e)}")
        return super().create(vals)

    def action_submit(self):
        self.ensure_one()

        # Automatically assign reporting_to_1 if not already set
        if not self.reporting_to_1:
            # Search for employee named 'Janaki S'
            janaki_employee = self.env['hr.employee'].sudo().search([
                ('name', '=', 'Janaki S')
            ], limit=1)

            if not janaki_employee or not janaki_employee.user_id:
                raise UserError("The employee 'Janaki S' must exist and be linked to a system user.")

            self.reporting_to_1 = janaki_employee.user_id
            self.approved_hr_email = janaki_employee.work_email or ''

        # Prevent submitting to self
        if self.reporting_to_1.id == self.env.uid:
            raise UserError("You cannot submit a request to yourself.")

        # Update state and assign HR approver
        self.state = 'submitted'
        self.approved_hr = self.env.user

        # Send email to the approver
        template = self.env.ref('recruitment_request.recruitment_request_submit_email_templatesssss',
                                raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def action_approve(self):
        if not self.reporting_to_1:
            raise UserError("No current approver assigned.")

        if not self.approved_by_sign:
            raise UserError("HR approval signature is required before proceeding.")

            # Define next approver by employee name (update logic as needed)
        next_approver_employee = self.env['hr.employee'].sudo().search([
            ('name', '=', 'Administrator')  # change to desired user/employee
        ], limit=1)

        if not next_approver_employee or not next_approver_employee.user_id:
            raise UserError("Next approver 'Final Approver' not found or not linked to a user.")

        # Assign next approver
        self.reporting_to_1 = next_approver_employee.user_id
        self.cao_approval_email = next_approver_employee.work_email or ''
        self.approval_cao_name = next_approver_employee.user_id

        # Optional: Change state
        self.state = 'approved'
        self.approved_cao = self.env.user

        # Send approval notification email
        template = self.env.ref(
            'recruitment_request.recruitment_request_submit_email_hr_required',
            raise_if_not_found=False
        )
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def action_reject(self):
        self.state = 'rejected'
        self.rejected_by = self.env.user

        template = self.env.ref(
            'recruitment_request.recruitment_request_rejected_email_template',
            raise_if_not_found=False
        )
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def action_set_to_draft(self):
        self.state = 'draft'

    def action_mark_done(self):
        self.state = 'done'

    job_id = fields.Many2one('hr.job', string="Job Created")

    def action_create_recruitment(self):
        self.ensure_one()

        if not self.job_id:
            job = self.env['hr.job'].create({
                'name': self.position_title_1 or self.name,
                'department_id': self.department_id.id if self.department_id else False,
                'contract_type_id': self.contract_type_id.id if self.contract_type_id else False,
                'no_of_recruitment': self.number_of_positions_1,
            })
            self.job_id = job.id
        else:
            job = self.job_id

        self.state = 'recruitment'

        return {
            'type': 'ir.actions.act_window',
            'name': f'Job Applications for {job.name}',
            'view_mode': 'form',
            'res_model': 'hr.applicant',
            'domain': [('job_id', '=', job.id)],
            'context': {'default_job_id': job.id},
        }

    def action_open_recruitment_job(self):
        self.ensure_one()

        # If the job already exists, open it
        if self.job_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Job Position',
                'res_model': 'hr.job',
                'view_mode': 'form',
                'res_id': self.job_id.id,
                'target': 'current',
            }

        # If job does not exist, optionally handle or raise error
        raise UserError("No Job Position is linked to this request.")

    # def action_cao_to_hr(self):
    #     self.state = 'hr_approved'

    def action_cao_to_hr(self):
        self.ensure_one()

        if not self.approval_by_sign_cao:
            raise UserError("CAO approval signature is required before proceeding.")

        # Always assign 'Janaki S' as the HR approver from hr.employee
        janaki_employee = self.env['hr.employee'].sudo().search([
            ('name', '=', 'Janaki S')
        ], limit=1)

        if not janaki_employee or not janaki_employee.user_id:
            raise UserError("Employee 'Janaki S' was not found or is not linked to a system user.")

        # Reassign regardless of existing value
        self.reporting_to_1 = janaki_employee.user_id

        # Update the state and assign CAO approver
        self.state = 'hr_approved'
        self.approval_cao_name = self.env.user
        # Send approval notification email
        template = self.env.ref(
            'recruitment_request.recruitment_request_approveddd_email_template',
            raise_if_not_found=False
        )
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    # Meta
    request_date = fields.Date(string="Date of Request", default=fields.Date.today)
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    department_id = fields.Many2one('hr.department', string="Department")

    # Position 1
    position_title_1 = fields.Char(string="Position Title")
    requirement_type_1 = fields.Selection([('new', 'New Position'), ('replace', 'Replacement')],
                                          string="Type of Requirement")
    replacement_name_1 = fields.Char(string="Replacement Name")
    number_of_positions_1 = fields.Integer(string="Number of Positions")
    contract_type_id = fields.Many2one(
        'hr.contract.type',
        string="Employment Type"
    )

    location_1 = fields.Char(string="Work Location")
    joining_date_1 = fields.Date(string="Expected Joining Date")
    # reporting_to_1 = fields.Char(string="Reporting To")
    reporting_to_1 = fields.Many2one(
        'res.users',
        string="Reporting To"
    )

    # Candidate Profile
    edu_essential = fields.Text(string="Educational Qualification (Essential)")
    edu_desirable = fields.Text(string="Educational Qualification (Desirable)")
    experience_required = fields.Text(string="Experience Required")
    preferred_gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                                        string="Preferred Gender")
    age_range = fields.Selection(
        selection=[
            ('20_25', '20 - 25'),
            ('25_30', '25 - 30'),
            ('31_35', '31 - 35'),
            ('36_40', '36 - 40'),
            ('41_45', '41 - 45'),
            ('46_50', '46 - 50'),
            ('50_above', '50 and above'),
            ('60_above', '60 and above'),
        ],
        string="Age Range"
    )

    key_skills = fields.Text(string="Key Skills Required")
    job_description = fields.Text(string="Job Description")
    salary_range = fields.Char(string="Salary Range (CTC)")

    # Approvals
    approved_hr = fields.Many2one('res.users', string="Requested By", related="requested_by")
    approved_cao = fields.Many2one('res.users', string="HR Approved By")
    approved_hr_email = fields.Char("HR EMAIL")
    request_by_sign = fields.Binary(string="Requested By Signature")
    approved_by_sign = fields.Binary(string="HR Signature")
    approval_cao_name = fields.Many2one('res.users', string="CAO Approved By")
    approval_by_sign_cao = fields.Binary(string="CAO By Signature")
    rejected_by = fields.Many2one('res.users', string="Rejected By")
    # company_id = fields.Many2one(
    #     'res.company',
    #     string="Company",
    #     default=lambda self: self.env.company,
    #
    # )

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    # mail

    approval_email = fields.Char(
        string="HR Email",
        compute="_compute_approval_email",
        store=True,
        help="Fetches the work email from the associated employee."
    )

    @api.depends('reporting_to_1')
    def _compute_approval_email(self):
        """
        Compute the `approval_email` field to show the work email of the employee
        associated with the reporting_to_1 user.
        """
        for record in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', record.reporting_to_1.id)],
                limit=1
            )
            record.approval_email = employee.work_email if employee else ''

    requested_email = fields.Char(
        string="Requested Email",
        compute="_compute_requested_emailss",
        store=True,
        help="Fetches the work email of the user in 'approved_hr'."
    )

    @api.depends('approved_hr')
    def _compute_requested_emailss(self):
        """
        Compute the 'requested_email' field from the employee record
        linked to the approved_hr user.
        """
        for record in self:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', record.approved_hr.id)],
                limit=1
            )
            record.requested_email = employee.work_email if employee else ''

    cao_approval_email = fields.Char(
        string="CAO Email",
        compute="_compute_cao_approval_email",
        store=True,
        help="Fetches the work email of the employee linked to the CAO approver."
    )

    @api.depends('approval_cao_name')
    def _compute_cao_approval_email(self):
        for record in self:
            if record.approval_cao_name:
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', record.approval_cao_name.id)
                ], limit=1)
                record.cao_approval_email = employee.work_email if employee else ''
            else:
                record.cao_approval_email = ''
