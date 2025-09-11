from odoo import models, fields, api


class ProjectTask(models.Model):
    """
    Розширення стандартної моделі завдань Odoo
    Додаємо поля для AI-чату та управління завданнями
    """
    _inherit = 'project.task'

    ai_priority = fields.Selection([
        ('low', 'Low'),
        ('high', 'High')
    ], string='AI Priority', default='low')

    ai_tags = fields.Char(string='AI Tags')

    ai_status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Needs Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused')
    ], string='AI Status', default='todo')

    ai_feedback = fields.Text(string='AI Feedback')

    created_by_user_id = fields.Many2one('res.users', string='Created by')

    ai_validated = fields.Boolean(string='AI Validated', default=False)

    chat_created = fields.Boolean(string='Created via Chat', default=False)
