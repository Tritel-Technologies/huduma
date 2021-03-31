# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime,timedelta, date
from openerp.exceptions import ValidationError
from openerp import http
from openerp import workflow
from openerp.osv import osv
from urlparse import urljoin
from urllib import urlencode

class huduma_case(models.Model):
    _name = 'huduma.case.header'
    _inherit = 'mail.thread'
    _order = 'name desc'
    

    name = fields.Char(string = 'No.')
    case_type = fields.Many2one('karibu.type', string = 'Nature')
    title = fields.Char(required = True)
    assigned_to = fields.Many2one('res.users',track_visibility = 'onchange')
    assigned_to_email = fields.Char(string = 'Assigned to E-mail')
    email_cc = fields.Many2many('huduma.case.email.cc', 'case_email_cc_rel', 'case_id', 'email_cc_id', string = 'Copy To (cc)')
    email_cc_emails = fields.Char(string = 'Copy To(cc)', compute = 'get_email_cc')
    customer = fields.Many2one('res.partner',domain = [('huduma_user','=',False)])
    opened_by = fields.Many2one('res.users',default = lambda self:self.env.user)
    opened_date = fields.Date(default = fields.Date.today)
    priority = fields.Selection([("0","Low"),("1","Normal"),("2","High")], default = '0')
    resolved_date = fields.Date(track_visibility='onchange')
    due_date = fields.Date()
    case_information = fields.Text()
    case_resolution = fields.Text()
    related_cases = fields.Many2one('huduma.case.header')
    color = fields.Integer()
    stage_id = fields.Many2one('huduma.stages')
    tag_ids = fields.Many2many('huduma.tags', string = 'Tags', store=True)
    kanban_state = fields.Selection([("normal","In Progress"),("blocked","Blocked"),("done","Ready for next stage")], default = 'normal',track_visibility='onchange')
    department_id = fields.Many2one('huduma.department', string = 'Department', required = True)
    call_ids = fields.One2many('huduma.scheduled.calls','case_id')
    meeting_ids = fields.One2many('huduma.scheduled.meetings','case_id')
    meeting_count = fields.Integer(compute = 'count_meetings')
    days_lapsed = fields.Integer(compute = 'compute_overdue', store = True)
    state = fields.Selection([
        ('flow_start',"Start"),
        ('normal',"In Progress"),
        ('escalated',"Escalated"),
        ('confirm',"Confirmation"),
        ('closed',"Closed")],
         default = 'flow_start',track_visibility='onchange')
    resolution_status = fields.Selection([
        ('draft',""),
        ('resolved',"Resolved"),
        ('unresolved',"Unresolved")],
        string = 'Case Resolution Status')
    process_map_id = fields.Many2one('huduma.process.map', string = 'Process Map',track_visibility='onchange')
    process_map_progress_ids = fields.One2many('huduma.process.map.progress','case_id')
    current_action = fields.Char(track_visibility='onchange', compute='track_map')
    current_responsible = fields.Many2one('res.users', string="Currently With", track_visibility='onchange', compute='track_map')
    administrator = fields.Many2one('res.users')
    url = fields.Char(compute = 'get_url')
    workflow_signal = fields.Selection([
        ('flow_start',"Start Case"),
        ('normal',"Convert to In Progress"),
        ('escalate',"Escalate Case"),
        ('confirm',"Confirm Case"),
        ('close',"Close Case")],
         default = 'flow_start')
    comment_ids = fields.One2many('huduma.case.comments','case_id')
    test = fields.Char()
    attachments = fields.Many2many('ir.attachment','huduma_case_attachment_rel','case_ids','attachment_ids','Attachments')
    quarter = fields.Char(compute = 'compute_quarter', store = '_check_to_recompute')
    currently_with = fields.Many2one('res.users')

    @api.one
    def _check_to_recompute(self):
        return [self.id]

    @api.one
    @api.depends('opened_date')
    def compute_quarter(self):
         if self.opened_date != False:
            month = datetime.strptime(str(self.opened_date), '%Y-%m-%d').month
            if month in [1,2,3]:
                self.quarter = 'Q1'
            elif month in [4,5,6]:
                self.quarter = 'Q2'
            elif month in [7,8,9]:
                self.quarter = 'Q3'
            elif month in [10,11,12]:
                self.quarter = 'Q4'

    @api.one
    def worker(self):
        cases = self.env['huduma.case.header'].search([])
        for case in cases:
            if case.opened_date != False:
                month = datetime.strptime(str(case.opened_date), '%Y-%m-%d').month
                if month in [1,2,3]:
                    case.quarter = 'Q1'
                elif month in [4,5,6]:
                    case.quarter = 'Q2'
                elif month in [7,8,9]:
                    case.quarter = 'Q3'
                elif month in [10,11,12]:
                    case.quarter = 'Q4'
        #pass
        # self.notify()
        # customers = self.env['res.partner'].search([('customer','=',True)])
        # customers.write({'is_company':True})
        # cases = self.env['huduma.case.header'].search([])
        # for case in cases:
        #   user = self.env['res.users'].search([('login','=',case.assigned_to_email)])
        #   if len(user)>0:#if user has account associated with them
        #       case.assigned_to = user.id
        #   else:
        #       case.assigned_to = False

    @api.one
    @api.depends('email_cc')
    def get_email_cc(self):
        cc = ''
        counter = 0
        for mail in self.email_cc:
            counter += 1
            if counter ==1:
                cc += mail.email
            else:
                cc+= ','+mail.email
        self.email_cc_emails = cc

    @api.one
    def get_sequence(self):
        setup = self.env['huduma.setup'].search([('id','=',1)])
        sequence = self.env['ir.sequence'].search([('id','=',setup.huduma_case_nos.id)])
        self.name = sequence.next_by_id(sequence.id, context = None)
        self.state = 'flow_start'
        self.administrator = setup.huduma_admin_account.id


    @api.onchange('case_type')
    def get_title(self):
        if self.title == False:
            self.title = self.case_type.description
            self.department_id = self.case_type.department_id
            self.assigned_to = self.case_type.default_assigned_to
            self.assigned_to_email = self.case_type.default_assigned_to_email
            # self.email_cc = self.case_type.default_email_cc
            self.case_information = self.case_type.default_case_information
            self.case_resolution = self.case_type.default_case_resolution
        

    @api.onchange('assigned_to')
    def get_assigned_to_email(self):
        self.assigned_to_email = self.assigned_to.login


    @api.one 
    @api.depends('meeting_ids')
    def count_meetings(self):
        self.meeting_count = len(self.meeting_ids)

    @api.onchange('opened_date')
    def calculate_due_date(self):
        start = datetime.strptime(str(self.opened_date),'%Y-%m-%d').date()
        due = start + timedelta(days = 0)#will change this to be dependent on SLAs
        self.due_date = due

    @api.one
    @api.depends('due_date')
    # @api.model
    def compute_overdue(self):
        today = date.today()
        days_lapsed = 0
        if self.due_date:
            due = datetime.strptime(str(self.due_date),'%Y-%m-%d').date()
            if today > due:
                delta = today - due
                days_lapsed = delta.days
        
        self.days_lapsed = days_lapsed
        #change color based on days lapsed
        if days_lapsed in range(6):
            self.color = self.color
        elif days_lapsed in range(6,11):
            self.color = 4
        elif days_lapsed in range(11,16):
            self.color = 3
        else:
            self.color = 2

    @api.model
    def compute_overdues_all(self):
        cases = self.env['huduma.case.header'].search([])
        for case in cases:
            if case.state != 'closed':
                case.compute_overdue()
            

    @api.model
    def _get_stage_groups(self, present_ids, domain, **kwargs):
        stages = self.env['huduma.stages'].search([],order='sequence asc').name_get()
        stage_fold = self.env['huduma.stages'].search([])
        fold = {}
        for stage in stage_fold:
            fold[stage.id] = stage.fold or None
        return stages, fold

    _group_by_full = {
        'stage_id': _get_stage_groups,
    }

    @api.one
    def close_case(self):
        self.workflow_signal = 'close'

    @api.one
    def mark_as_closed(self):
        self.state = 'closed' 

    @api.one
    def manual_escalate(self):
        if self.days_lapsed > 5:
            self.workflow_signal = 'escalate'
            self.env['huduma.case.header'].browse(self.id).signal_workflow('escalate')
        else:
            raise ValidationError('You can only escalate after lapse of SLA. Consider re-assigning!')

    @api.model
    def automated_escalate(self):
        cases = self.env['huduma.case.header'].search([('days_lapsed','>',5)])
        for case in cases:
            case.workflow_signal = 'escalate'
            self.env["huduma.case.header"].browse(case.id).signal_workflow("escalate")

    @api.model
    def update_user(self):
        # If assigned_to is blank, try to find login with similar email and update id of 
        # assigned to with the correct details
        cases = self.env['huduma.case.header'].search([])
        for case in cases:
            if len(case.assigned_to)<=0:
                user = self.env['res.users'].search([('login','=',case.assigned_to_email)])
                if len(user)>0:
                    case.assigned_to = user.id

        # Ensure that all case users have emails on their related partner records
        users = self.env['res.users'].search([])
        for user in users:
            partner = self.env['res.partner'].search([('id','=',user.partner_id.id)])
            partner.email = user.login
                        


    @api.one
    def mark_as_escalated(self):
        # Escalate through scheduled actions
        # We'll convert to use SLAs on process maps
        # self.env['huduma.case.header'].search([('days_lapsed','>',5)]).write({'state':'escalated'})
        self.state = 'escalated'
                

    @api.one
    def mark_as_assigned(self):
        if self.assigned_to_email == '':#len(self.assigned_to)<1
            raise ValidationError('Assigned to must have a value before proceeding with case')
        self.state = 'normal'

    # @api.one
    # def mark_as_re_assigned(self):
    #   self.state = 'normal'

    @api.one
    def mark_as_open(self):
        self.state = 'flow_start'

    @api.one
    def mark_as_ready_for_confirmation(self):
        self.state = 'confirm'

    @api.one
    def reset(self):
        # Reset record and workflow to draft
        pass



    @api.multi
    def send_mail_template(self):
        #find template
        template = self.env.ref('huduma.example_email_template')
        self.env['email.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def notify(self):
        #find template
        template = self.env.ref('huduma.assignment_notification_email_template')
        ids = []
        for attachment in self.attachments:
            ids.append(attachment.id)
        template.attachment_ids = [(6,0,ids)]
        self.env['email.template'].browse(template.id).send_mail(self.id)
        

    @api.multi
    def notify_escalation(self):
        template = self.env.ref('huduma.escalation_notification_email_template')
        ids = []
        for attachment in self.attachments:
            ids.append(attachment.id)
        template.attachment_ids = [(6,0,ids)]
        self.env['email.template'].browse(template.id).send_mail(self.id) 

    @api.multi
    def notify_confirmation(self):
        template = self.env.ref('huduma.confirmation_notification_email_template')
        ids = []
        for attachment in self.attachments:
            ids.append(attachment.id)
        template.attachment_ids = [(6,0,ids)]
        self.env['email.template'].browse(template.id).send_mail(self.id) 

    @api.multi
    def notify_case_closing(self):
        template = self.env.ref('huduma.case_closing_notification_email_template')
        self.env['email.template'].browse(template.id).send_mail(self.id)

    @api.onchange('process_map_id')
    def get_process_map(self):
        self.process_map_progress_ids.unlink()
        lines = []
        process_map = self.env['huduma.process.map'].search([('id','=',self.process_map_id.id)])
        for line in process_map.process_map_stage_ids:
            val = {
            'case_id':self.id,
            'name':line.name,
            'stage_type':line.stage_type,
            'next_action_accept':line.next_action_accept.id,
            'next_action_reject':line.next_action_reject.id,
            'sequence':line.sequence
            }
            lines += [val]
        self.update({'process_map_progress_ids':lines})

    @api.one
    @api.depends('process_map_progress_ids') 
    def track_map(self):
        progress = self.env['huduma.process.map.progress'].search([('current_action','=',True),('case_id','=',self.id)],limit = 1)
        self.current_action = progress.name
        self.current_responsible = progress.responsible


    @api.one
    def match_stage_with_state(self):
        stage = self.env['huduma.stages'].search([('state','=',self.state)], limit = 1)
        if len(stage)<=0:
            raise ValidationError('No stage with matching state')
        self.stage_id = stage.id

    @api.one
    def match_all_stages_with_state(self):
        cases = self.env['huduma.case.header'].search([])
        for case in cases:
            stage = self.env['huduma.stages'].search([('state','=',case.state)])
            case.stage_id = stage.id

    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, uid, ids[0], context=context)
        contex_signup = dict(context, signup_valid=True)
        return self.pool['res.partner']._get_signup_url_for_action(
            cr, uid, [document.assigned_to.id], action='mail.action_mail_redirect',
            model=self._name, res_id=document.id, context=contex_signup,
        )[document.assigned_to.id] 

    @api.one
    @api.depends('name')
    def get_url(self):
        document = self.browse(self.id)
        res = False
        query = {'db':self._cr.dbname}
        fragment = {'action': 'huduma.huduma_case_action','type': "signup",'view_type' : 'form','model' : 'huduma.case.header','id': document.id,'login': document.assigned_to_email}
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        self.url = res

    @api.one
    def process_process_map(self):
        if self.process_map_id is None:
            pass #consider raising a validation error 
        else:
            process = self.env['huduma.process.map'].search([('id','=',self.process_map_id.id)])
            if process.process_map_type == 'normal':
                self.kanban_state = 'done'
            elif process.process_map_type == 'workflow':
                # start traversing stages
                if len(self.process_map_progress_ids) <= 0:
                    raise ValidationError("No process map stages associated with this case!")
                else:
                    # commence first stage if not yet started
                    progress = self.env['huduma.process.map.progress'].search([('current_action','=',True),('case_id','=',self.id)], limit = 1)
                    if len(progress)==0:#no action started yet.
                        progress_record = self.env['huduma.process.map.progress'].search([('case_id','=',self.id)], order='sequence asc', limit = 1)
                        progress_record.write({'current_action':True,'date':date.today(),'state':'pending'})
                    else:
                        #search for next record for action
                        next_progress_record = self.env['huduma.process.map.progress'].search([('case_id','=',self.id),('sequence','>',progress.sequence)], order='sequence asc', limit = 1)
                        if len(next_progress_record) > 0:
                            progress.write({'current_action':False,'state':'done','date':date.today()})
                            next_progress_record.write({'current_action':True,'date':date.today(),'state':'pending'})

    @api.multi
    def print_xlsx_report(self):
        datas = {
            'ids': self.ids,
            'model': 'huduma.case.header',
            'form': self.read()[0]
        } 

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'karibu.center.cases.xlsx',
            'datas': datas,
            'name': 'Karibu Center Cases Report'
        }



class huduma_case_comments(models.Model):
    _name = 'huduma.case.comments'

    case_id = fields.Many2one('huduma.case.header')
    user_id = fields.Many2one('res.users')
    email = fields.Char()
    comment = fields.Char()
    date = fields.Date()

class huduma_stages(models.Model):
    _name = 'huduma.stages'

    name = fields.Char()
    sequence = fields.Integer()
    case_default = fields.Boolean(string = 'Default for new cases')
    fold = fields.Boolean(string = 'Folded in Kanban View')
    final_stage = fields.Boolean()
    final_stage_status = fields.Selection([("complete","Closed Resolved"),('incomplete',"Closed Unresolved")])
    state = fields.Selection([
        ('flow_start',"Start"),
        ('normal',"In Progress"),
        ('escalated',"Escalated"),
        ('confirm',"Confirmation"),
        ('closed',"Closed")])


    @api.one
    @api.onchange('case_default')
    def toggle_case_default(self):
        if self.case_default:
            stages = self.env['huduma.stages'].search([('name','!=',self.name)]).write({'case_default':False})

    @api.one
    @api.onchange('state')
    def check_for_state_in_other_stages(self):
        stage = self.env['huduma.stages'].search([('state','=',self.state),('state','!=',False)])
        if len(stage)>0:
            self.state = None
            raise ValidationError('Another stage exists with the same status')


class huduma_department(models.Model):
    _name = 'huduma.department'

    name = fields.Char()
    description = fields.Text()
    color = fields.Integer()
    case_ids = fields.One2many('huduma.case.header','department_id', domain = [('stage_id.fold', '=', False)])
    case_count = fields.Integer(compute = 'count_cases')
    members = fields.Many2many('res.users')
    responsible = fields.Many2one('res.users')

    @api.one
    @api.depends('case_ids')
    def count_cases(self):
        self.case_count = len(self.case_ids)

class huduma_tags(models.Model):
    _name = 'huduma.tags'

    name = fields.Char()
    description = fields.Text()
    department_id = fields.Many2one('huduma.department')

class huduma_case_cc(models.Model):
    _name = 'huduma.case.email.cc'
    _rec_name = 'email'

    case_id = fields.Many2one('huduma.case.header')
    email = fields.Char()

class huduma_scheduled_calls(models.Model):
    _name = 'huduma.scheduled.calls'

    responsible = fields.Many2one('res.users')
    customer = fields.Many2one('res.partner')
    date = fields.Datetime()
    agenda = fields.Text()
    case_id = fields.Many2one('huduma.case.header') 


class huduma_scheduled_meetings(models.Model):
    _name = 'huduma.scheduled.meetings'

    name = fields.Char(string = 'Title')
    agenda = fields.Text(string = 'Description')
    date = fields.Date(string = 'Date')
    responsible = fields.Many2one('res.users')
    customer = fields.Many2one('res.partner')
    case_id = fields.Many2one('huduma.case.header')


class huduma_setup(models.Model):
    _name = 'huduma.setup'

    name = fields.Char()
    huduma_case_nos = fields.Many2one('ir.sequence')
    huduma_admin_account = fields.Many2one('res.users')

class huduma_process_map(models.Model):
    _name = 'huduma.process.map'

    name = fields.Char()
    description = fields.Text()
    process_map_stage_ids = fields.One2many('huduma.process.map.stages','process_map_id')
    process_map_type = fields.Selection([
        ('normal',"Normal"),
        ('workflow',"Workflow")],
        default = 'normal', required = True, string = 'Type'
        )
    sla = fields.Integer(string = 'SLA')

class huduma_process_map_stages(models.Model):
    _name = 'huduma.process.map.stages'

    name = fields.Char()
    sequence = fields.Integer()
    process_map_id = fields.Many2one('huduma.process.map')
    stage_type = fields.Selection([
        ('start',"Start Stage"),
        ('action',"Action Stage"),
        ('decision',"Decision Stage"),
        ('end',"End Stage")
        ])
    next_action_accept = fields.Many2one('huduma.process.map.stages')
    next_action_reject = fields.Many2one('huduma.process.map.stages')
    responsible = fields.Many2one('res.users')

class huduma_process_map_progress(models.Model):
    _name = 'huduma.process.map.progress'
    _inherit = 'huduma.process.map.stages'
    
    case_id = fields.Many2one('huduma.case.header')
    date = fields.Datetime(string = 'Last Modified')
    comment = fields.Text() #this field will be editable through a wizard
    days_to_resolution = fields.Integer()
    current_action = fields.Boolean()
    state = fields.Selection([('open',"Open"),('pending',"Pending"),('done',"Done")], default = 'open')

class karibu_type(models.Model):
    _name = 'karibu.type'

    name = fields.Char()
    description = fields.Text()
    department_id = fields.Many2one('huduma.department', string = 'Department')
    default_assigned_to = fields.Many2one('res.users')
    default_assigned_to_email = fields.Char()
    default_email_cc = fields.Many2many('huduma.case.email.cc')
    default_case_information = fields.Text()
    default_case_resolution = fields.Text()

    @api.onchange('default_assigned_to')
    def get_assigned_to_email(self):
        self.default_assigned_to_email = self.default_assigned_to.login

        