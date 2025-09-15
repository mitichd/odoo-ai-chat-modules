from odoo import http
from odoo.http import request
from ..models.command_parser import CommandParser
import re


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

        # Валідація команди
        is_valid, validation_message = parser.validate_command(command, text)
        if not is_valid:
            return {'reply': f"❌ {validation_message}"}

        # Перевірка ролі
        role_manager = request.env['ai_chat.role_manager']

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

        # Перевірка прав відповідно ролі
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
                     f"ℹ️ {role_description}\n\n"
                     f"{commands_text}\n\n"
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
        """Обробка команди /list_tasks - показує список завдань користувача"""
        try:
            user = request.env.user

            # Отримуємо завдання користувача
            tasks = request.env['project.task'].search([
                ('user_ids', 'in', [user.id])
            ], order='date_deadline asc, id asc')

            if not tasks:
                return {
                    'reply': "📋 **Список завдань:**\n\n"
                             "🔍 У вас немає призначених завдань"
                }

            # Форматуємо список завдань
            tasks_list = []
            for task in tasks:
                # Статус завдання
                status_emoji = {
                    'todo': '📝',
                    'in_progress': '👨‍💻',
                    'done': '✅',
                    'cancelled': '❌',
                    'paused': '⏸️',
                    'review': '👀'
                }.get(task.ai_status or 'todo', '📝')

                # Дедлайн
                deadline = task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else 'Не вказано'

                # Пріоритет
                priority = '🔥' if task.ai_priority == 'high' else '🐌'

                # Форматуємо рядок завдання
                task_line = f"{status_emoji} **#{task.id}: {task.name}**|{deadline}|{priority}"
                tasks_list.append(task_line)

            # Збираємо результат
            tasks_text = '\n'.join(tasks_list)

            return {
                'reply': f"📋 **Список ваших завдань({len(tasks)}):**\n\n"
                         f"🔍ID|Назва|Дедлайн|Пріоритет\n"
                         f"━━━━━━━━━━━━━━━\n"
                         f"{tasks_text}\n\n"
                         f"💡 *Використовуйте /complete_task ID для завершення*"
            }

        except Exception as e:
            return {
                'reply': f"❌ Помилка отримання списку завдань: {str(e)}"
            }

    def _handle_task_action(self, command, text, parser, role_manager):
        """Обробка команд дій з завданнями з перевіркою доступу"""
        task_id, comment = parser.parse_task_id(text)

        # Перевірка доступу до завдання
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

        # Реальна обробка return_task
        if command == 'return_task':
            return self._handle_return_task(task_id, comment)

        # Реальна обробка complete_task
        if command == 'complete_task':
            return self._handle_complete_task(task_id, comment)

        # Реальна обробка approve_task
        if command == 'approve_task':
            return self._handle_approve_task(task_id, comment)

        # Інші команди (поки що заглушки)
        actions = {
            'edit_task': f"✏️ **Редагування завдання #{task_id}**",
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

        # Перевірка доступу до завдання
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

        # Реальна обробка cancel_task
        if command == 'cancel_task':
            return self._handle_cancel_task(task_id, comment)

        # Реальна обробка pause_task
        if command == 'pause_task':
            return self._handle_pause_task(task_id, comment)

        # Реальна обробка resume_task
        if command == 'resume_task':
            return self._handle_resume_task(task_id, comment)

        actions = {
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

    def _handle_complete_task(self, task_id, comment):
        """
        Обробка команди /complete_task - завершення завдання виконавцем
        """
        try:
            if not task_id:
                return {
                    'reply': "❌ Неправильний формат команди\n\n"
                             "💡 Використовуйте: /complete_task 123"
                }

            # Знаходимо завдання
            task = request.env['project.task'].browse(int(task_id))
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Перевірка ролі та прав
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            # PM може завершувати будь-які завдання
            if user_role == 'PM':
                # PM може завершувати все
                pass
            # Dev може завершувати тільки свої завдання
            elif user_role == 'Dev':
                if user not in task.user_ids:
                    return {
                        'reply': f"❌ Завдання #{task_id} не призначене вам\n\n"
                                 f"👤 Ви можете завершувати тільки свої завдання"
                    }
            else:
                return {
                    'reply': f"❌ У вас немає прав для завершення завдань\n\n"
                             f"�� Ваша роль: {user_role}"
                }

            # Змінюємо статус на "Done"
            task.write({
                'ai_status': 'done',
            })

            # Форматуємо відповідь з урахуванням ролі
            if user_role == 'PM':
                assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'
                return {
                    'reply': f"✅ **Завдання #{task_id} завершено PM!**\n\n"
                             f"�� Назва: {task.name}\n"
                             f"👤 Виконавець: {assignee_name}\n"
                             f" Завершив: {user.name}\n\n"
                             f"🎯 Статус змінено на: Done"
                }
            else:
                return {
                    'reply': f"✅ **Завдання #{task_id} завершено!**\n\n"
                             f"�� Назва: {task.name}\n"
                             f"👤 Виконавець: {user.name}\n\n"
                             f"�� Статус змінено на: Done"
                }

        except (ValueError, TypeError):
            return {
                'reply': f"❌ Неправильний ID завдання: {task_id}"
            }
        except Exception as e:
            return {
                'reply': f"❌ Помилка завершення завдання: {str(e)}"
            }

    def _handle_return_task(self, task_id, comment):
        """
        Обробка команди /return_task - повернення завдання PM для доопрацювання
        """
        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(int(task_id))
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Перевіряємо роль та права
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            # PM може повертати будь-які завдання
            if user_role == 'PM':
                pass
            # Dev може повертати тільки свої завдання
            elif user_role == 'Dev':
                if user not in task.user_ids:
                    return {
                        'reply': f"❌ Завдання #{task_id} не призначене вам\n\n"
                                 f"👤 Ви можете повертати тільки свої завдання"
                    }
            else:
                return {
                    'reply': f"❌ У вас немає прав для повернення завдань\n\n"
                             f"👤 Ваша роль: {user_role}"
                }

            # Змінюємо статус на "Needs Review" і додаємо тег
            task.write({
                'ai_status': 'review',
                'ai_tags': (task.ai_tags or '') + ', #needs_review' if task.ai_tags else '#needs_review'
            })

            # Форматуємо відповідь з урахуванням ролі
            if user_role == 'PM':
                assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'
                return {
                    'reply': f"↩️ Завдання #{task_id} повернено PM!\n\n"
                             f"📌 Назва: {task.name}\n"
                             f"🦾 Виконавець: {assignee_name}\n"
                             f"🧐 Повернув: {user.name}\n\n"
                             f"💬 Комент: {comment}\n\n"
                             f"🎯 Статус змінено на: Needs Review\n"
                             f"🏷️ Додано тег: #needs_review"
                }
            else:
                return {
                    'reply': f"↩️ Завдання #{task_id} повернено!\n\n"
                             f"📌 Назва: {task.name} \n"
                             f"🧐 Повернув: {user.name} \n\n"
                             f"🎯 Статус змінено на: Needs Review\n"
                             f"🏷️ Додано тег: #needs_review"
                }

        except (ValueError, TypeError):
            return {
                'reply': f"❌ Неправильний ID завдання: {task_id}"
            }
        except Exception as e:
            return {
                'reply': f"❌ Помилка повернення завдання: {str(e)}"
            }

    def _handle_approve_task(self, task_id, comment):
        """
        Обробка команди /approve_task - затвердження завдання PM
        """
        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Перевіряємо роль - тільки PM може затверджувати
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            if user_role != 'PM':
                return {
                    'reply': f"❌ Тільки Project Manager може затверджувати завдання\n\n"
                             f"👤 Ваша роль: {user_role}"
                }

            # Визначаємо статус на основі поточного
            current_status = task.ai_status

            if current_status == 'done':
                new_status = 'done'  # Closed
                status_text = "Closed"
            elif current_status == 'review':
                new_status = 'in_progress'  # In Progress
                status_text = "In Progress"
            else:
                new_status = 'in_progress'
                status_text = "In Progress"

            # Змінюємо статус і додаємо тег
            task.write({
                'ai_status': new_status,
                'ai_tags': (task.ai_tags or '') + ', #approved' if task.ai_tags else '#approved'
            })

            # Форматуємо відповідь
            assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'

            return {
                'reply': f"✅ **Завдання #{task_id} затверджено!**\n\n"
                         f"📌 Назва: {task.name}\n"
                         f"🦾 Виконавець: {assignee_name}\n"
                         f"👤 Затвердив: {user.name}\n\n"
                         f"🎯 Статус змінено на: {status_text}"
                         f"️🏷️ Додано тег: #approved"
            }

        except (ValueError, TypeError) as e:
            return {
                'reply': f"❌ Неправильний ID завдання: {task_id}"
            }
        except Exception as e:
            return {
                'reply': f"❌ Помилка затвердження завдання: {str(e)}"
            }

    def _handle_assign_task(self, text, parser, role_manager):
        """Обробка команди /assign_task з перевіркою прав"""
        # Тільки PM може призначати завдання
        user_role = role_manager.get_user_role(request.env.user)
        if user_role != 'PM':
            return {
                'reply': f"❌ Тільки Project Manager може призначати завдання\n\n"
                         f" Ваша роль: {user_role}"
            }

        # Парсимо параметри
        task_id, username, comment = parser.parse_user_mention(text)

        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Знаходимо користувача по login або по частині login
            assignee = request.env['res.users'].search([
                '|',  # АБО
                ('login', '=', username),  # Точний пошук: "demo"
                ('login', 'ilike', f"{username}@%"),  # Пошук по email: "test@%"
                ('share', '=', False)
            ], limit=1)

            if not assignee:
                return {
                    'reply': f"❌ Користувач @{username} не знайдено\n\n"
                             f"💡 Перевірте правильність імені користувача"
                }

            # Призначаємо завдання
            task.write({
                'user_ids': [(4, assignee.id)]  # Додаємо користувача до списку виконавців
            })

            # Форматуємо відповідь
            comment_text = f"\n Коментар: '{comment}'" if comment else ""

            return {
                'reply': f"✅ **Завдання #{task_id} призначено!**\n\n"
                         f"📌 Назва: {task.name}\n"
                         f"⚡️ Новий виконавець: @{assignee.login}\n"
                         f"👤 Призначив: {request.env.user.name}{comment_text}\n\n"
                         f"🎯 Завдання успішно переназначено"
            }

        except Exception as e:
            return {
                'reply': f"❌ Помилка призначення завдання: {str(e)}"
            }

    def _handle_cancel_task(self, task_id, reason):
        """
        Обробка команди /cancel_task - скасування завдання
        """
        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Перевіряємо роль та права
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            # PM може скасовувати будь-які завдання
            if user_role == 'PM':
                pass
            # Dev не може скасовувати завдання
            elif user_role == 'Dev':
                return {
                    'reply': f"❌ У вас немає прав для скасування завдань\n\n"
                             f" Ваша роль: {user_role}"
                }

            # Перевірка наявності причини скасування
            if not reason or reason.strip() == "":
                return {
                    'reply': "❌ Необхідно вказати причину скасування\n\n"
                             "💡 Використовуйте: /cancel_task 123 [причина]"
                }

            # Змінюємо статус на "Cancelled" і додаємо тег
            task.write({
                'ai_status': 'cancelled',
                'ai_tags': (task.ai_tags or '') + ', #cancelled' if task.ai_tags else '#cancelled'
            })

            # Форматуємо відповідь
            reason_text = f"\n Причина: '{reason}'" if reason else ""
            assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'

            return {
                'reply': f"❌ **Завдання #{task_id} скасовано!**\n\n"
                         f"📌 Назва: {task.name}\n"
                         f"👤 Виконавець: {assignee_name}\n"
                         f"🙅‍♂️ Скасував: {user.name}{reason_text}\n\n"
                         f"🎯 Статус змінено на: Cancelled\n"
                         f"️🏷️ Додано тег: #cancelled"
            }

        except Exception as e:
            return {
                'reply': f"❌ Помилка скасування завдання: {str(e)}"
            }

    def _handle_pause_task(self, task_id, reason):
        """
        Обробка команди /pause_task - призупинення завдання
        """
        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }

            # Перевіряємо роль - тільки PM може призупиняти
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            # PM може призупиняти будь-які завдання
            if user_role == 'PM':
                pass
            # Dev НЕ може призупиняти завдання
            elif user_role == 'Dev':
                return {
                    'reply': f"❌ У вас немає прав для призупинення завдань\n\n"
                             f" Ваша роль: {user_role}"
                }
            else:
                return {
                    'reply': f"❌ У вас немає прав для призупинення завдань\n\n"
                             f" Ваша роль: {user_role}"
                }

            # Перевірка наявності причини призупинення
            if not reason or reason.strip() == "":
                return {
                    'reply': "❌ Необхідно вказати причину призупинення\n\n"
                             "💡 Використовуйте: /pause_task 123 [причина]"
                }

            # Змінюємо статус на "Paused" і додаємо тег
            task.write({
                'ai_status': 'paused',
                'ai_tags': (task.ai_tags or '') + ', #paused' if task.ai_tags else '#paused'
            })

            # Форматуємо відповідь
            assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'

            return {
                'reply': f"⏸️ **Завдання #{task_id} призупинено!**\n\n"
                         f"📌 Назва: {task.name}\n"
                         f"👤 Виконавець: {assignee_name}\n"
                         f"🤚 Призупинив: {user.name}\n"
                         f"⚠️ Причина: '{reason}'\n\n"
                         f"🎯 Статус змінено на: Paused\n"
                         f"️🏷️ Додано тег: #paused"
            }

        except Exception as e:
            return {
                'reply': f"❌ Помилка призупинення завдання: {str(e)}"
            }

    def _handle_resume_task(self, task_id, comment):
        """
        Обробка команди /resume_task - відновлення завдання
        Формат: /resume_task 123 [статус]
        """
        try:
            # Знаходимо завдання
            task = request.env['project.task'].browse(task_id)
            if not task.exists():
                return {
                    'reply': f"❌ Завдання #{task_id} не знайдено"
                }
            # Перевіряємо чи завдання на паузі
            if task.ai_status != 'paused':
                return {
                    'reply': f"❌ Завдання #{task_id} не на паузі\n\n"
                             f"👤 Поточний статус: {task.ai_status}"
                }

            # Перевіряємо роль (п.с.реалізувати це окремо, щоб не дублювати кругом)
            user = request.env.user
            role_manager = request.env['ai_chat.role_manager']
            user_role = role_manager.get_user_role(user)

            # тільки PM може відновлювати завдання
            if user_role != 'PM':
                return {
                    'reply': f"❌ У вас немає прав для відновлення завдань\n\n"
                             f" Ваша роль: {user_role}"
                }

            # ПАРСИМО СТАТУС З КОМЕНТАРЯ
            new_status = self._parse_resume_status(comment)

            # Змінюємо статус
            task.write({
                'ai_status': new_status,
            })

            # Форматуємо відповідь
            assignee_name = task.user_ids[0].name if task.user_ids else 'Не призначено'
            status_text = "To Do" if new_status == 'todo' else "In Progress"

            return {
                'reply': f"▶️ **Завдання #{task_id} відновлено!**\n\n"
                         f"📌 Назва: {task.name}\n"
                         f"👤 Виконавець: {assignee_name}\n"
                         f"👌 Відновив: {user.name}\n\n"
                         f"🎯 Статус змінено на: {status_text}\n"
            }

        except Exception as e:
            return {
                'reply': f"❌ Помилка відновлення завдання: {str(e)}"
            }

    def _parse_resume_status(self, comment):
        """
        Парсить статус з коментаря для команди /resume_task за допомогою regex
        Повертає: new_status
        """
        if not comment or comment.strip() == "":
            # Якщо коментар порожній - за замовчуванням "todo"
            return 'todo'

        comment = comment.strip().lower()

        # REGEX для "In Progress" (нечутливий до регістру)
        if re.match(r'^(in\s+progress|inprogress|in_progress|inprogres)$', comment):
            return 'in_progress'

        # REGEX для "To Do" (нечутливий до регістру)
        if re.match(r'^(to\s+do|todo|todos)$', comment):
            return 'todo'

        # Якщо не розпізнали статус - за замовчуванням "todo"
        return 'todo'

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
