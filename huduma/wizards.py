from openerp import models, fields, api
from datetime import date

class case_action_wizard(models.TransientModel):
	_name = 'huduma.case.action'
	_inherit = 'huduma.process.map.progress'

	user = fields.Many2one('res.users',default = lambda self:self.env.user)

	@api.onchange('case_id')
	def get_details(self):
		progress = self.env['huduma.process.map.progress'].search([
			('case_id','=',self.case_id.id),
			('current_action','=',True),
			('responsible','=',self.user.id)
			], limit = 1)
		self.name = progress.name
		self.date = date.today()
		self.stage_type = progress.stage_type

		# self.write({'name':progress.name,'date':date.today(),'stage_type':progress.stage_type})

	@api.one
	def action_confirm(self):
		pass

class case_close_action(models.TransientModel):
	_name = 'huduma.close.case.action'

	resolution_details = fields.Text(string = 'Case Resolution Details')
	state = fields.Selection([
		('resolved',"Resolved"),
		('unresolved',"Unresolved")],
		required = True, string = 'Resolution Case Status')
	date = fields.Date(default = fields.Date.today, string = 'Date Resolved')
	case_id = fields.Many2one('huduma.case.header')
	title = fields.Char()

	@api.one
	def action_close(self):
		self.case_id.workflow_signal = 'close'
		# self.case_id.assigned_to = self.case_id.department_id.responsible.id
		self.env['huduma.case.comments'].create({
			'case_id':self.case_id.id,
			'comment':self.resolution_details,
			'user_id':self.env.user.id,
			'email':self.env.user.login,
			'date':date.today()
			})
		self.case_id.resolved_date = date.today()
		self.case_id.resolution_status = self.state 
		self.case_id.currently_with = False
		if self.case_id.case_resolution == False:
			self.case_id.case_resolution = self.resolution_details
		else:
			self.case_id.case_resolution += '\n\nResolution Comment: ' + self.resolution_details

class case_reassign_action(models.TransientModel):
	_name = 'huduma.reassign.case.action'

	reassignment_details = fields.Text(required = True)
	case_id = fields.Many2one('huduma.case.header')
	title = fields.Char()
	assigned_to = fields.Many2one('res.users')
	assigned_to_email = fields.Char(string = 'E-mail', required = True)
	date = fields.Date(default = fields.Date.today)

	@api.one
	def action_reassign(self):
		self.case_id.assigned_to = self.assigned_to.id
		self.case_id.assigned_to_email = self.assigned_to_email
		self.case_id.currently_with = self.assigned_to.id
		self.case_id.workflow_signal = 'normal'
		self.env['huduma.case.header'].browse(self.case_id.id).signal_workflow('re_assign')
		self.env['huduma.case.comments'].create({
			'case_id':self.case_id.id,
			'comment':self.reassignment_details,
			'user_id':self.env.user.id,
			'email':self.env.user.login,
			'date':date.today()
			})

	@api.onchange('assigned_to')
	def get_assigned_to_email(self):
		self.assigned_to_email = self.assigned_to.login

class case_confirm_action(models.TransientModel):
	_name = 'huduma.confirmation.case.action'

	confirmation_comment = fields.Text(string = "Comment",required = True)
	case_id = fields.Many2one('huduma.case.header')
	title = fields.Char()
	date = fields.Date(default = fields.Date.today)

	@api.one
	def action_send_for_confirmation(self):
		self.case_id.workflow_signal = 'confirm'
		# self.case_id.assigned_to = self.case_id.department_id.responsible.id or self.case_id.opened_by.id
		self.case_id.currently_with = self.case_id.department_id.responsible.id or self.case_id.opened_by.id
		self.env['huduma.case.comments'].create({
			'case_id':self.case_id.id,
			'comment':self.confirmation_comment,
			'user_id':self.env.user.id,
			'email':self.env.user.login,
			'date':date.today()
			})

		if self.case_id.case_resolution == '':
			self.case_id.case_resolution = self.confirmation_comment

class KaribuCenterCasesReportWizard(models.TransientModel):
    _name = "karibu.center.report.wizard"

    start_date = fields.Date()
    end_date = fields.Date()

    @api.multi
    def print_xlsx_report(self):
        datas = {
            'ids': move_lines,
            'model': 'account.move.line',
            'form': self.read()[0]
        } 

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'karibu.center.cases.xlsx',
            'datas': datas,
            'name': 'Karibu Center Cases Report'
        }