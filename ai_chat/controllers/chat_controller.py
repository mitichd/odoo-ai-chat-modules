from odoo import http
from odoo.http import request
from ..models.command_parser import CommandParser


class ChatController(http.Controller):

    @http.route('/ai_chat/process_message', type='json', auth='user')
    def process_message(self, message):
        """
        Обробляє повідомлення від чату з фільтрацією команд по ролях.
        """
        parser = CommandParser()
        result = parser.parse_message(message)

        if not result['is_command']:
            return {
                'reply': f"Ти написав: '{message}'\n\n"
                         f"💡 Спробуй команди:\n"
                         f"• /help - список команд\n"
                         f"• /create_task - створити завдання\n"
                         f"• /list_tasks - показати завдання"
            }

        command = result['command']
        text = result['text']

        # Перевірка ролей перед обробкою команди
        role_manager = request.env['ai_chat.role_manager']
        if not role_manager.check_permission(request.env.user, command):
            # Отримуємо список доступних команд для користувача
            available_commands = role_manager.get_available_commands(request.env.user)
            user_role = role_manager.get_user_role(request.env.user)
            role_description = role_manager.get_role_description(user_role)

            return {
                'reply': f"❌ У вас немає прав для команди /{command}\n\n"
                         f"👤 Ваша роль: {user_role}\n"
                         f"📝 {role_description}\n\n"
                         f"✅ Доступні команди:\n" +
                         '\n'.join([f"• /{cmd}" for cmd in available_commands if cmd != 'help'])
            }

        # Валідація команди
        is_valid, validation_message = parser.validate_command(command, text)
        if not is_valid:
            return {'reply': f"❌ {validation_message}"}

        # Обробка команд
        if command == 'help':
            return self._handle_help(parser, role_manager)
        elif command == 'create_task':
            return self._handle_create_task(text)
        elif command == 'change_task':
            return self._handle_change_task(text)
        elif command == 'list_tasks':
            return self._handle_list_tasks()
        elif command in ['edit_task', 'complete_task', 'return_task', 'approve_task']:
            return self._handle_task_action(command, text, parser, role_manager)
        elif command == 'assign_task':
            return self._handle_assign_task(text, parser, role_manager)
        elif command in ['cancel_task', 'pause_task', 'resume_task', 'comment_task']:
            return self._handle_task_management(command, text, parser, role_manager)
        else:
            return {
                'reply': f"❓ Невідома команда: /{command}\n\n"
                         f"Спробуй /help для списку команд"
            }

        # Окремі методи для кожної команди

    def _handle_help(self, parser, role_manager):
        """Обробка команди /help з урахуванням ролі користувача"""
        # Отримуємо доступні команди для поточного користувача
        available_commands = role_manager.get_available_commands(request.env.user)
        user_role = role_manager.get_user_role(request.env.user)
        role_description = role_manager.get_role_description(user_role)

        # Отримуємо описи команд з парсера
        help_commands = parser.get_help()

        # Фільтруємо тільки доступні команди
        filtered_commands = {cmd: desc for cmd, desc in help_commands.items()
                             if cmd in available_commands}

        commands_text = '\n'.join([f"• /{cmd} - {desc}" for cmd, desc in filtered_commands.items()])

        return {
            'reply': f"📋 **Доступні команди для {user_role}:**\n\n"
                     f"�� {role_description}\n\n"
                     f"{commands_text}\n\n"
                     f"💡 Для детальної інформації про команду використовуй: /команда"
        }

    def _handle_create_task(self, text):
        """Обробка команди /create_task"""
        if text:
            # Швидке створення з назвою
            return {
                'reply': f"🚀 **Швидке створення завдання:**\n\n"
                         f"📝 Назва: '{text}'\n\n"
                         f"⚡ Для повного створення з усіма параметрами використовуй просто /create_task\n\n"
            }
        else:
            # Повна HTML форма
            projects = self._get_projects()
            users = self._get_users()

            html_form = f"""
            <div class="ai-task-form">
                <h3>📝 Створення нового завдання</h3>
                <form id="ai-create-task-form">

                    <div class="form-group">
                        <label>🎯 Проект:</label>
                        <input type="text" name="project" list="projects-list" required 
                               placeholder="Оберіть або введіть назву проекту">
                        <datalist id="projects-list">
                            {projects}
                        </datalist>
                        <small>💡 Почніть друкувати або натисніть ▼ для вибору</small>
                    </div>

                    <div class="form-group">
                        <label>📝 Назва завдання:</label>
                        <input type="text" name="task_name" required placeholder="Наприклад: Додати фільтр до API">
                    </div>

                    <div class="form-group">
                        <label>📋 Детальний опис:</label>
                        <textarea name="task_description" required rows="4" placeholder="Опишіть завдання детально..."></textarea>
                    </div>

                    <div class="form-group">
                        <label>👤 Виконавець:</label>
                        <select name="assignee_id">
                            <option value="">Оберіть виконавця...</option>
                            {users}
                        </select>
                    </div>

                    <div class="form-group">
                        <label>📅 Дедлайн:</label>
                        <input type="date" name="deadline">
                    </div>

                    <div class="form-group">
                        <label>⚡ Пріоритет:</label>
                        <label><input type="radio" name="priority" value="low" checked> Low</label>
                        <label><input type="radio" name="priority" value="high"> High</label>
                    </div>

                    <div class="form-group">
                        <label>🏷️ Мітки:</label>
                        <input type="text" name="tags" placeholder="#bug, #feature, #urgent">
                        <small>Розділяйте комами</small>
                    </div>

                    <div class="form-buttons">
                        <button type="submit" class="btn-primary">Створити</button>
                        <button type="button" class="btn-cancel" onclick="cancelTaskForm()">Скасувати</button>
                    </div>

                </form>
            </div>
            """

            return {
                'reply': html_form,
                'is_html': True
            }

    # Допоміжні методи для отримання даних
    def _get_projects(self):
        """Отримуємо список проектів для форми"""
        projects = request.env['project.project'].search([])
        options = ""
        for project in projects:
            options += f'<option value="{project.name}" data-id="{project.id}"></option>'
        return options

    def _get_users(self):
        """Отримуємо список користувачів для форми"""
        users = request.env['res.users'].search([('share', '=', False)])  # Тільки внутрішні користувачі
        options = ""
        for user in users:
            options += f'<option value="{user.id}">@{user.login}</option>'
        return options

    def _handle_change_task(self, text):
        """Обробка команди /change_task"""
        if text:
            # Швидка зміна з ID завдання
            return {
                'reply': f"🔄 **Зміна завдання:**\n\n"
                         f"📝 Параметри: '{text}'\n\n"
                         f"⚡ Для повної зміни використовуй просто /change_task\n\n"
                         f"(Повна форма буде реалізована на наступному кроці)"
            }
        else:
            # Повна форма зміни
            return {
                'reply': "🔄 **Зміна існуючого завдання**\n\n"
                         "🎯 Тут буде форма для зміни:\n"
                         "• Вибір завдання для зміни\n"
                         "• Зміна виконавця\n"
                         "• Зміна дедлайну\n"
                         "• Зміна пріоритету\n"
                         "• Зміна міток\n"
                         "• Додавання файлів\n\n"
                         "(Форма буде реалізована разом з /create_task)"
            }

    def _handle_list_tasks(self):
        """Обробка команди /list_tasks"""
        return {
            'reply': "📋 **Список завдань:**\n\n"
                     "🔍 ID | Назва | Статус | Виконавець | Дедлайн\n"
                     "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                     "📌 001 | Тестове завдання | To Do | @dev1 | 2025-09-15\n"
                     "📌 002 | Додати API | In Progress | @dev2 | 2025-09-20\n\n"
                     "(Реальні дані будуть підключені на наступному кроці)"
        }

    def _handle_task_action(self, command, text, parser, role_manager):
        """Обробка команд дій з завданнями з перевіркою доступу"""
        task_id, comment = parser.parse_task_id(text)

        # ✅ ДОДАЄМО: Перевірка доступу до завдання
        if task_id:
            try:
                task = request.env['project.task'].browse(int(task_id))
                if task.exists():
                    if not role_manager.can_edit_task(request.env.user, task):
                        return {
                            'reply': f"❌ У вас немає прав для редагування завдання #{task_id}\n\n"
                                     f"👤 Ви можете редагувати тільки свої завдання"
                        }
            except (ValueError, TypeError):
                return {'reply': f"❌ Неправильний ID завдання: {task_id}"}

        actions = {
            'edit_task': f"✏️ **Редагування завдання #{task_id}**",
            'complete_task': f"✅ **Завершення завдання #{task_id}**",
            'return_task': f"↩️ **Повернення завдання #{task_id}**",
            'approve_task': f"�� **Затвердження завдання #{task_id}**"
        }

        action_text = actions.get(command, f"Дія {command}")
        comment_text = f"\n💬 Коментар: '{comment}'" if comment else ""

        return {
            'reply': f"{action_text}{comment_text}\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }

    def _handle_assign_task(self, text, parser, role_manager):
        """Обробка команди /assign_task з перевіркою прав"""
        # Тільки PM може призначати завдання
        user_role = role_manager.get_user_role(request.env.user)
        if user_role != 'PM':
            return {
                'reply': f"❌ Тільки Project Manager може призначати завдання\n\n"
                         f"�� Ваша роль: {user_role}"
            }

        task_id, username, comment = parser.parse_user_mention(text)
        return {
            'reply': f"�� **Переназначення завдання #{task_id}**\n\n"
                     f"🔄 Новий виконавець: @{username}\n"
                     f"�� Коментар: '{comment}'\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }

    def _handle_task_management(self, command, text, parser, role_manager):
        """Обробка команд управління завданнями з перевіркою доступу"""
        task_id, comment = parser.parse_task_id(text)

        # ✅ ДОДАЄМО: Перевірка доступу до завдання
        if task_id:
            try:
                task = request.env['project.task'].browse(int(task_id))
                if task.exists():
                    if not role_manager.can_edit_task(request.env.user, task):
                        return {
                            'reply': f"❌ У вас немає прав для управління завданням #{task_id}\n\n"
                                     f"👤 Ви можете керувати тільки своїми завданнями"
                        }
            except (ValueError, TypeError):
                return {'reply': f"❌ Неправильний ID завдання: {task_id}"}

        actions = {
            'cancel_task': f"❌ **Скасування завдання #{task_id}**",
            'pause_task': f"⏸️ **Призупинення завдання #{task_id}**",
            'resume_task': f"▶️ **Відновлення завдання #{task_id}**",
            'comment_task': f"💬 **Коментар до завдання #{task_id}**"
        }

        action_text = actions.get(command, f"Дія {command}")
        comment_text = f"\n�� Текст: '{comment}'" if comment else ""

        return {
            'reply': f"{action_text}{comment_text}\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }

    @http.route('/ai_chat/save_task', type='json', auth='user')
    def save_task(self, **kwargs):
        """
        Зберігає завдання з форми в базу даних
        """
        try:
            # Отримуємо дані з форми
            task_data = {
                'name': kwargs.get('task_name'),
                'description': kwargs.get('task_description'),
                'date_deadline': kwargs.get('deadline') if kwargs.get('deadline') else False,
                'user_ids': [(4, int(kwargs.get('assignee_id')))] if kwargs.get('assignee_id') else [],

                # Наші AI поля
                'ai_priority': kwargs.get('priority', 'low'),
                'ai_tags': kwargs.get('tags', ''),
                'ai_status': 'todo',
                'created_by_user_id': request.env.user.id,
                'chat_created': True,
                'ai_validated': False,
            }

            # Обробляємо нове поле project
            project_name = kwargs.get('project')
            if project_name:
                # Спочатку шукаємо існуючий проект
                existing_project = request.env['project.project'].search([
                    ('name', '=', project_name)
                ], limit=1)

                if existing_project:
                    task_data['project_id'] = existing_project.id
                    project_text = f"(існуючий проект)"
                else:
                    # Створюємо новий проект
                    new_project = request.env['project.project'].sudo().create({
                        'name': project_name
                    })
                    task_data['project_id'] = new_project.id
                    project_text = f"(новий проект)"

            # Валідація даних ДО створення завдання
            validator = request.env['ai_chat.task_validator']
            is_valid, errors = validator.validate_task_data(task_data)

            if not is_valid:
                return {
                    'success': False,
                    'reply': f"❌ Завдання не пройшло перевірку:\n\n" +
                             '\n'.join([f"• {error}" for error in errors]) +
                             "\n\n🔧 Виправте помилки та спробуйте ще раз."
                }

            # Позначаємо як валідоване
            task_data['ai_validated'] = True

            # Створюємо завдання
            task = request.env['project.task'].create(task_data)

            return {
                'success': True,
                'reply': f"✅ Завдання '{task.name}' створено успішно!\n\n"
                         f"🆔 ID: {task.id}\n"
                         f"📁 Проект: {task.project_id.name} {project_text}\n"
                         f"👤 Виконавець: {task.user_ids[0].name if task.user_ids else 'Не призначено'}"
                         f"✅ Валідація пройдена"
            }

        except Exception as e:
            return {
                'success': False,
                'reply': f"❌ Помилка створення завдання: {str(e)}"
            }
