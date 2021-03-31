from openerp import models, fields, api

class res_partner(models.Model):
	_inherit = 'res.partner'

	huduma_user = fields.Boolean()