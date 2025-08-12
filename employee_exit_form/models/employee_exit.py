from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date

from src.odoo.tools.view_validation import relaxng


class EmployeeExit(models.Model):
    _name = 'hr.employee.exit'
    _rec_name = 'employee_id'
    _description = 'Employee Exit Interview'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id.id
    )
    designation = fields.Char(related='employee_id.job_title', string="Designation")
    supervisor_id = fields.Many2one('hr.employee', string="Dept. Manager", )
    supervisor_title = fields.Char(related='supervisor_id.job_title', string="Dept. Manager Designation")
    interview_date = fields.Date(
        string="Interview Date",
        default=lambda self: date.today()
    )
    last_date = fields.Date(string="Last Date of Work")
    length_of_service = fields.Char(string="Length of Service")
    reason_instruction = fields.Text(
        string='',
        default="Please indicate reason(s) below, which contributed to your decision to resign from your current position."
    )

    reason_resignation = fields.Boolean("Resignation")
    reason_new_position = fields.Boolean("Took another position")
    reason_family = fields.Boolean("Home/family needs")
    reason_health = fields.Boolean("Health")
    reason_relocation = fields.Boolean("Relocation")
    reason_travel = fields.Boolean("Travel requirements")
    reason_training = fields.Boolean("Lack of training")
    reason_opportunities = fields.Boolean("Lack of opportunities")
    reason_culture = fields.Boolean("Culture")
    reason_study = fields.Boolean("To return to study")
    reason_type_work = fields.Boolean("Dissatisfaction with type of work")
    reason_salary = fields.Boolean("Dissatisfaction with salary/benefits")
    reason_conditions = fields.Boolean("Dissatisfaction with working conditions")
    reason_other_1 = fields.Char("Other Reason 1")
    reason_laid_off = fields.Boolean("Laid Off")
    reason_performance = fields.Boolean("Poor performance")
    reason_conduct = fields.Boolean("Inappropriate Conduct")
    reason_policy = fields.Boolean("Violation of Company Policy")
    reason_other_2 = fields.Char("Other Reason 2")
    reason_retirement = fields.Boolean("Retirement")
    reason_other_3 = fields.Char("Other Reason 3")
    feedback_leave_factor = fields.Text(
        string='',
        default="1.What factors contributed to your decision to leave the company?"
    )
    feedback_leave_entry = fields.Html(
        string='',

    )

    feedback_most_satisfyingss = fields.Text(string='',
                                             default="2.What did you find most satisfying about your role?")

    feedback_most_entry = fields.Html(
        string='',

    )
    feedback_least_satisfyings = fields.Text(string='',
                                             default="3.What did you find least satisfying about your role?")

    feedback_least_entry = fields.Html(
        string='',

    )
    feedback_job_expectationss = fields.Text(string='',
                                             default="4.Did your job duties turn out as expected?")

    feedback_job_expet_entry = fields.Html(
        string='',

    )
    feedback_supervisor_expect = fields.Text(string='',
                                             default="5.Did your job duties turn out as expected?")

    feedback_supervisor_rating = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string="Supervisor Relationship (1-5)"
    )
    overall_satisfy_expect = fields.Text(string='',
                                         default="6.Overall satisfaction and enjoyment in your current position.")
    overall_satisfy_expect_rating = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string="Overall Satisfaction (1-5)"
    )
    had_problemssss = fields.Text(string='',
                                  default="7.Did you encounter any problems in your current position")
    had_problems = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Did you encounter any problems in your current position?", default="no"
    )
    had_prblm_expect = fields.Text(string='',
                                   default="If yes, please briefly comment:")
    had_prblm_entry = fields.Text(string='',
                                  )

    employee_acknowledgement = fields.Text(
        string='',
        default="I hereby acknowledge that I have provided accurate information in this Employee Exit Form. "
                "I also acknowledge that I have returned all company property and equipment (if any) assigned to me during my employment.",
        readonly=True
    )

    employee_acknowledgement_signature = fields.Binary(
        string="Employee Signature",
        attachment=True
    )

    employee_acknowledgement_sign_date = fields.Date(
        string="Date"
    )

    hr_supervisor_acknowledgement = fields.Text(
        string='',
        default="I hereby acknowledge that the information provided in this Employee Exit Form has been reviewed. "
                "I also acknowledge receipt of all company property and equipment (if any) from the employee.",
        readonly=True
    )

    hr_supervisor_signature = fields.Binary(
        string="HR  Signature",
        attachment=True
    )

    hr_supervisor_sign_date = fields.Date(
        string="Date",
        default=fields.Date.context_today
    )

    exit_form_note = fields.Text(
        string='',
        default="Note: This Employee Exit Form is confidential and should be kept in the employee's personnel file.",
        readonly=True
    )

    equipment_return_note = fields.Text(
        string='',
        default="Please list all company property and equipment that you have returned.",
        readonly=True
    )

    equipment_lines = fields.One2many('hr.employee.exit.equipment', 'exit_id', string="Returned Items")

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('supervisor_submitted', 'Department Manager Approval'),
            ('hr_approved', 'HR Approved'),
            ('cao_approved', 'CAO Approved'),
            ('cao_to_hr_approval', 'Proceed To HR'),
            ('rejected', 'Rejected')
        ],
        string="Status",
        default='draft',
        tracking=True,
        required=True
    )

    reporting_to_hr = fields.Many2one(
        'res.users',
        string="Reporting To HR",
        ondelete='set null'
    )

    approval_email_hr = fields.Char(
        string="HR Email",
        compute="_compute_approval_email_hr",
        store=True,
        help="Fetches the work email from the associated employee."
    )

    @api.depends('reporting_to_hr')
    def _compute_approval_email_hr(self):
        for record in self:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', record.reporting_to_hr.id)],
                limit=1
            )
            record.approval_email_hr = employee.work_email or ''

    reporting_to_cao = fields.Many2one(
        'res.users',
        string="Reporting To CAO",
        ondelete='set null'
    )

    approval_email_cao = fields.Char(
        string="CAO Email",
        compute="_compute_approval_email_cao",
        store=True,
        help="Fetches the work email from the CAO's employee profile."
    )

    @api.depends('reporting_to_cao')
    def _compute_approval_email_cao(self):
        for record in self:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', record.reporting_to_cao.id)],
                limit=1
            )
            record.approval_email_cao = employee.work_email or ''

    def action_submit_to_supervisor(self):
        for record in self:
            if not record.employee_acknowledgement_signature:
                raise ValidationError("Employee Signature is required before submitting to Department Manager.")
            if not record.employee_acknowledgement_sign_date:
                raise ValidationError("Signature Date is required before submitting to Department Manager.")
            record.write({'state': 'supervisor_submitted'})
            template = self.env.ref(
                'employee_exit_form.mail_template_exit_submit',
                raise_if_not_found=False
            )
            if template:
                template.sudo().send_mail(self.id, force_send=True)

    def action_approve_hr(self):
        for record in self:
            # Validate HR signature fields
            if not record.manager_ack_signature:
                raise ValidationError("Manager Signature is required before HR Approval.")
            if not record.manager_ack_date:
                raise ValidationError("Manager Signature Date is required before HR Approval.")

            # Find the next approver (CAO)
            next_approver_employee = self.env['hr.employee'].sudo().search([
                ('name', '=', 'Karthikeyan A')
            ], limit=1)

            if not next_approver_employee or not next_approver_employee.user_id:
                raise UserError("Next approver 'Final Approver' not found or not linked to a user.")

            # Assign next approver and name
            record.reporting_to_hr = next_approver_employee.user_id.id
            template = self.env.ref(
                'employee_exit_form.mail_template_exit_to_hr',
                raise_if_not_found=False
            )
            if template:
                template.sudo().send_mail(self.id, force_send=True)

            # Move to next state
            record.write({'state': 'hr_approved'})

    def action_approve_cao(self):
        for record in self:

            if not record.hr_supervisor_signature:
                raise ValidationError("HR Signature is required before CAO Approval.")
            if not record.hr_supervisor_sign_date:
                raise ValidationError("HR Signature Date is required before CAO Approval.")

            # Find the next approver (CAO)
            next_approver_employee = self.env['hr.employee'].sudo().search([
                ('name', '=', 'Vidya Padmanabhan')  # You can change this to dynamic logic later
            ], limit=1)

            if not next_approver_employee or not next_approver_employee.user_id:
                raise UserError("Next approver 'CAO' not found or not linked to a user.")

            # Assign CAO user to reporting_to_cao
            record.reporting_to_cao = next_approver_employee.user_id.id

            template = self.env.ref(
                'employee_exit_form.mail_template_exit_to_cao',
                raise_if_not_found=False
            )
            if template:
                template.sudo().send_mail(self.id, force_send=True)

            # Move to next state
            record.state = 'cao_approved'

    def action_proceed_to_hr(self):
        for record in self:
            # Validate HR signature fields
            if not record.cao_signature:
                raise ValidationError("CAO Signature is required before Proceed to HR Approval.")
            if not record.cao_sign_date:
                raise ValidationError("CAO Signature Date is required before Proceed to HR Approval.")

            # Find the next approver (CAO)
            next_approver_employee = self.env['hr.employee'].sudo().search([
                ('name', '=', 'Karthikeyan A')
            ], limit=1)

            if not next_approver_employee or not next_approver_employee.user_id:
                raise UserError("Next approver 'Final Approver' not found or not linked to a user.")

            # Assign next approver and name
            record.reporting_to_hr = next_approver_employee.user_id.id
            template = self.env.ref(
                'employee_exit_form.mail_template_exit_final',
                raise_if_not_found=False
            )
            if template:
                template.sudo().send_mail(self.id, force_send=True)

            # Move to next state
            record.write({'state': 'cao_to_hr_approval'})

    def action_reject(self):
        template = self.env.ref(
            'employee_exit_form.mail_template_exit_final_reject',
            raise_if_not_found=False
        )
        if template:
            template.sudo().send_mail(self.id, force_send=True)

        self.write({'state': 'rejected'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company.id,
        required=True,
        readonly=True
    )



    manager_acknowledgement = fields.Text(
        string='',
        compute="_compute_manager_acknowledgement",
        store=True,
        readonly=True
    )

    manager_ack_signature = fields.Binary(
        string="Manager Signature",
        attachment=True
    )

    manager_ack_date = fields.Date(
        string="Date",
        default=fields.Date.context_today
    )

    @api.depends('employee_id')
    def _compute_manager_acknowledgement(self):
        for record in self:
            candidate = record.employee_id.name or 'the candidate'
            emp_code = record.employee_id.emp_code or ''
            record.manager_acknowledgement = (
                f"I hereby acknowledge that we have retrieved all the necessary data from "
                f"<b>{candidate}</b>{f' - {emp_code}' if emp_code else ''}</b>"
            )

    cao_acknowledgement = fields.Html(
        string='',
        compute="_compute_cao_acknowledgement",
        store=True,
        readonly=True
    )

    cao_signature = fields.Binary(
        string="CAO Signature",
        attachment=True
    )

    cao_sign_date = fields.Date(
        string="Date",
        default=fields.Date.context_today
    )

    @api.depends('employee_id')
    def _compute_cao_acknowledgement(self):
        for record in self:
            candidate = record.employee_id.name or ''
            emp_code = record.employee_id.emp_code or ''  # adjust if using different field
            record.cao_acknowledgement = (
                f"I hereby acknowledge that I have reviewed department heads and HRD feedbacks. "
                f"I am approving to remove the employee "
                f"<b>{candidate}</b>{f' - {emp_code}' if emp_code else ''}."
            )


class EmployeeExitEquipment(models.Model):
    _name = 'hr.employee.exit.equipment'
    _description = 'Employee Exit Equipment Return'

    exit_id = fields.Many2one('hr.employee.exit', string="Exit Interview")
    item_description = fields.Char("Item Description")
    serial_number = fields.Char("Serial Number")
    return_date = fields.Date("Date Returned")
