# -*- coding: utf-8 -*-
from odoo import models


class RoleManager(models.TransientModel):
    """
    Менеджер ролей для AI Chat модуля.
    Визначає ролі користувачів та перевіряє дозволи для команд.
    """
    _name = 'ai_chat.role_manager'
    _description = 'AI Chat Role Manager'

    # Константи з командами для кожної ролі
    PM_COMMANDS = [
        'create_task',  # Створити завдання
        'change_task',  # Змінити завдання
        'edit_task',  # Редагувати завдання
        'complete_task',  # Завершити завдання
        'return_task',  # Повернути завдання
        'approve_task',  # Затвердити завдання
        'list_tasks',  # Список завдань
        'comment_task',  # Коментар до завдання
        'assign_task',  # Призначити завдання
        'cancel_task',  # Скасувати завдання
        'pause_task',  # Призупинити завдання
        'resume_task',  # Відновити завдання
        'help'  # Допомога (загальна команда)
    ]

    DEV_COMMANDS = [
        'complete_task',  # Завершити завдання
        'comment_task',  # Коментар до завдання
        'return_task',  # Повернути завдання PM
        'list_tasks',  # Список завдань
        'help'  # Допомога (загальна команда)
    ]

    def get_user_role(self, user):
        """
        Визначає роль користувача на основі Odoo груп.
        """
        # Перевіряємо чи користувач є Project Manager
        if user.has_group('project.group_project_manager'):
            return 'PM'

        # Перевіряємо чи користувач є Project User (Developer)
        elif user.has_group('project.group_project_user'):
            return 'Dev'

        # Якщо не входить в жодну групу
        else:
            return 'Dev'

    def check_permission(self, user, command):
        """
        Перевіряє чи має користувач дозвіл на виконання команди.
        """
        # Отримуємо роль користувача
        role = self.get_user_role(user)

        # Якщо роль невідома - забороняємо все
        if role == 'Unknown':
            return False

        # PM може все
        if role == 'PM':
            return command in self.PM_COMMANDS

        # Dev має обмежені права
        elif role == 'Dev':
            return command in self.DEV_COMMANDS

        # На всякий випадок
        return False

    def can_edit_task(self, user, task):
        """
        Перевіряє чи може користувач редагувати конкретне завдання.

        Згідно ТЗ: "виконавці не можуть редагувати чужі завдання"
        """
        # Отримуємо роль користувача
        role = self.get_user_role(user)

        # PM може редагувати будь-які завдання
        if role == 'PM':
            return True

        # Dev може редагувати тільки свої завдання
        elif role == 'Dev':
            # Перевіряємо чи користувач є виконавцем завдання
            return user in task.user_ids

        # Невідома роль - забороняємо
        return False

    def get_available_commands(self, user):
        """
        Повертає список доступних команд для користувача.
        """
        role = self.get_user_role(user)

        if role == 'PM':
            return self.PM_COMMANDS
        elif role == 'Dev':
            return self.DEV_COMMANDS
        else:
            return ['help']  # Тільки допомога для невідомих ролей

    def get_role_description(self, role):
        """
        Повертає опис ролі для користувача.
        """
        descriptions = {
            'PM': 'Project Manager - може створювати, редагувати та керувати всіма завданнями',
            'Dev': 'Developer - може завершувати завдання, додавати коментарі та повертати на доопрацювання',
            'Unknown': 'Невідома роль - зверніться до адміністратора для налаштування прав'
        }

        return descriptions.get(role, 'Невідома роль')
