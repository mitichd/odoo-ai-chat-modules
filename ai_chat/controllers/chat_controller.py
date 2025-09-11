from odoo import http
from odoo.http import request
from ..models.command_parser import CommandParser


class ChatController(http.Controller):

    @http.route('/ai_chat/process_message', type='json', auth='user')
    def process_message(self, message):
        """
        Обробляє повідомлення від чату.
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

        # ✅ ДОДАЄМО: Валідація команди
        is_valid, validation_message = parser.validate_command(command, text)
        if not is_valid:
            return {'reply': f"❌ {validation_message}"}

        # Обробка команд
        if command == 'help':
            return self._handle_help(parser)
        elif command == 'create_task':
            return self._handle_create_task(text)
        elif command == 'change_task':
            return self._handle_change_task(text)
        elif command == 'list_tasks':
            return self._handle_list_tasks()
        elif command in ['edit_task', 'complete_task', 'return_task', 'approve_task']:
            return self._handle_task_action(command, text, parser)
        elif command == 'assign_task':
            return self._handle_assign_task(text, parser)
        elif command in ['cancel_task', 'pause_task', 'resume_task', 'comment_task']:
            return self._handle_task_management(command, text, parser)
        else:
            return {
                'reply': f"❓ Невідома команда: /{command}\n\n"
                         f"Спробуй /help для списку команд"
            }

        # ✅ ДОДАЄМО: Окремі методи для кожної команди

    def _handle_help(self, parser):
        """Обробка команди /help"""
        help_commands = parser.get_help()
        commands_text = '\n'.join([f"• /{cmd} - {desc}" for cmd, desc in help_commands.items()])
        return {
            'reply': f"📋 **Доступні команди:**\n\n{commands_text}\n\n"
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
                         f"(Повна форма буде реалізована на наступному кроці)"
            }
        else:
            # Повна форма створення
            return {
                'reply': "📝 **Створення нового завдання**\n\n"
                         "🔄 Тут буде інтерактивна форма:\n"
                         "• Проект\n"
                         "• Назва\n"
                         "• Опис\n"
                         "• Виконавець\n"
                         "• Дедлайн\n"
                         "• Пріоритет\n"
                         "• Мітки\n"
                         "• Файли\n\n"
                         "(Форма буде реалізована на наступному кроці)"
            }

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

    def _handle_task_action(self, command, text, parser):
        """Обробка команд дій з завданнями"""
        task_id, comment = parser.parse_task_id(text)

        actions = {
            'edit_task': f"✏️ **Редагування завдання #{task_id}**",
            'complete_task': f"✅ **Завершення завдання #{task_id}**",
            'return_task': f"↩️ **Повернення завдання #{task_id}**",
            'approve_task': f"👍 **Затвердження завдання #{task_id}**"
        }

        action_text = actions.get(command, f"Дія {command}")
        comment_text = f"\n💬 Коментар: '{comment}'" if comment else ""

        return {
            'reply': f"{action_text}{comment_text}\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }

    def _handle_assign_task(self, text, parser):
        """Обробка команди /assign_task"""
        task_id, username, comment = parser.parse_user_mention(text)
        return {
            'reply': f"👤 **Переназначення завдання #{task_id}**\n\
            n🔄 Новий виконавець: @{username}\n"
                     f"💬 Коментар: '{comment}'\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }

    def _handle_task_management(self, command, text, parser):
        """Обробка команд управління завданнями"""
        task_id, comment = parser.parse_task_id(text)

        actions = {
            'cancel_task': f"❌ **Скасування завдання #{task_id}**",
            'pause_task': f"⏸️ **Призупинення завдання #{task_id}**",
            'resume_task': f"▶️ **Відновлення завдання #{task_id}**",
            'comment_task': f"💬 **Коментар до завдання #{task_id}**"
        }

        action_text = actions.get(command, f"Дія {command}")
        comment_text = f"\n📝 Текст: '{comment}'" if comment else ""

        return {
            'reply': f"{action_text}{comment_text}\n\n"
                     f"(Реальна обробка буде реалізована на наступному кроці)"
        }
