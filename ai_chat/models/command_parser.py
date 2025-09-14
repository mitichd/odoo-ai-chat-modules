class CommandParser:
    """
    Простий парсер команд для AI чату.
    Розуміє команди типу: /create_task Написати звіт
    """

    def parse_message(self, message):
        """
        Головна функція - розбирає повідомлення.

        Вхід: "/create_task Написати звіт"
        Вихід: {
            'is_command': True,
            'command': 'create_task',
            'text': 'Написати звіт'
        }
        """
        message = message.strip()

        # Перевіряємо чи це команда
        if not message.startswith('/'):
            return {
                'is_command': False,
                'command': None,
                'text': message
            }

        # Розбираємо команду
        parts = message.split(' ', 1)
        command = parts[0][1:]  # Прибираємо '/'
        text = parts[1] if len(parts) > 1 else ''

        return {
            'is_command': True,
            'command': command,
            'text': text.strip()
        }

    def get_help(self):
        """
        Повертає список всіх доступних команд.
        """
        return {
            # Основні команди управління завданнями
            'create_task': 'Створити нове завдання',
            'change_task': 'Змінити параметри існуючого завдання',
            'edit_task': 'Відредагувати завдання після повернення',
            'list_tasks': 'Показати список завдань',

            # Команди виконання
            'complete_task': 'Позначити завдання як завершене',
            'return_task': 'Повернути завдання для доопрацювання',
            'approve_task': 'Затвердити завдання',

            # Команди управління
            'assign_task': 'Переназначити завдання на іншого виконавця',
            'cancel_task': 'Скасувати завдання',
            'pause_task': 'Призупинити завдання',
            'resume_task': 'Відновити призупинене завдання',
            'comment_task': 'Додати коментар до завдання',

            # Допоміжні
            'help': 'Показати цю довідку'
        }

    # Перевірка команд з ID
    def parse_task_id(self, text):
        """
        Витягує ID завдання з тексту команди.
        Приклад: "123 додати тести" -> (123, "додати тести")
        """
        if not text:
            return None, ""

        parts = text.split(' ', 1)
        try:
            task_id = int(parts[0])
            remaining_text = parts[1] if len(parts) > 1 else ""
            return task_id, remaining_text.strip()
        except ValueError:
            return None, text

    # Перевірка команд з користувачем
    def parse_user_mention(self, text):
        """
        Витягує згадку користувача з тексту.
        Приклад: "123 @dev2" -> (123, "dev2", "")
        """
        task_id, remaining = self.parse_task_id(text)
        if task_id is None:
            return None, None, text

        if remaining.startswith('@'):
            parts = remaining.split(' ', 1)
            username = parts[0][1:]  # Прибираємо @
            comment = parts[1] if len(parts) > 1 else ""
            return task_id, username, comment

        return task_id, None, remaining

    # Валідація команд
    def validate_command(self, command, text):
        """
        Перевіряє чи команда має правильний формат.
        """
        commands_with_id = [
            'edit_task', 'complete_task', 'approve_task',
            'cancel_task', 'pause_task', 'resume_task'
        ]

        commands_with_id_comment = [
            'return_task', 'comment_task'
        ]

        if command in commands_with_id:
            task_id, _ = self.parse_task_id(text)
            if task_id is None:
                return False, f"Команда /{command} потребує ID завдання. Приклад: /{command} 123"

        if command in commands_with_id_comment:
            task_id, _ = self.parse_task_id(text)
            if task_id is None:
                return False, f"Команда /{command} потребує ID завдання. Приклад: /{command} 123 [коментар]"

        if command == 'assign_task':
            task_id, username, _ = self.parse_user_mention(text)
            # if not task_id and not username:
            if task_id is None:
                return False, f"Команда /{command} потребує ID завдання та користувача. Приклад: /{command} 123 @dev"
            if username is None:
                return False, f"Команда /{command} потребує ID завдання та користувача. Приклад: /{command} 123 @dev"

        return True, "OK"
