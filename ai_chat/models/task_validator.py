# -*- coding: utf-8 -*-
from odoo import models
from datetime import datetime, timedelta
import re


class TaskValidator(models.TransientModel):
    """
    Валідатор для перевірки завдань згідно ТЗ.
    TransientModel - тимчасова модель, не зберігається в БД.
    """
    _name = 'ai_chat.task_validator'
    _description = 'AI Chat Task Validator'

    def validate_task_data(self, task_data):
        """
        Головний метод валідації згідно ТЗ.
        Повертає: (bool: чи валідні дані, list: список помилок)
        """
        errors = []

        # 1. Перевірка назви (>5 слів)
        if not self._validate_title(task_data.get('name', '')):
            errors.append("Назва занадто коротка (мінімум 5 слів)")

        # 2. Перевірка опису (достатньо зрозумілий)
        if not self._validate_description(task_data.get('description', '')):
            errors.append("Опис занадто короткий або незрозумілий")

        # 3. Перевірка дедлайну (не раніше завтра, не більше року)
        deadline_error = self._validate_deadline(task_data.get('date_deadline'))
        if deadline_error:
            errors.append(deadline_error)

        # 4. Перевірка виконавця (обов'язково вибраний)
        if not self._validate_assignee(task_data.get('user_ids')):
            errors.append("Виконавець обов'язково має бути вибраний")

        # 5. Перевірка файлів (якщо потрібно)
        file_error = self._validate_files(task_data.get('description', ''), task_data.get('attachments'))
        if file_error:
            errors.append(file_error)

        return len(errors) == 0, errors

    def _validate_title(self, title):
        """
        ТЗ: Назва >5 слів.
        """
        if not title:
            return False

        words = [word for word in title.split() if word.strip()]
        return len(words) > 5

    def _validate_description(self, description):
        """
        ТЗ: Опис достатньо зрозумілий.
        Простий критерій: мінімум 20 символів.
        """
        if not description:
            return False

        # Видаляємо зайві пробіли та рахуємо довжину
        clean_description = description.strip()
        return len(clean_description) >= 20

    def _validate_deadline(self, deadline):
        """
        ТЗ: Дедлайн не раніше ніж завтра, не більше ніж через рік.
        """
        if not deadline:
            return None  # Дедлайн не обов'язковий

        try:
            # Перетворюємо string в дату (якщо потрібно)
            if isinstance(deadline, str):
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            else:
                deadline_date = deadline

            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            max_date = today + timedelta(days=365)  # Рік

            if deadline_date < tomorrow:
                return "Дедлайн не може бути раніше ніж завтра"

            if deadline_date > max_date:
                return "Дедлайн не може бути більше ніж через рік"

        except (ValueError, TypeError):
            return "Неправильний формат дедлайну"

        return None  # Все ОК

    def _validate_assignee(self, user_ids):
        """
        ТЗ: Виконавець обов'язково вибраний.
        """
        if not user_ids:
            return False

        # user_ids може бути списком кортежів [(4, user_id)] в Odoo
        if isinstance(user_ids, list) and len(user_ids) > 0:
            return True

        return False

    def _validate_files(self, description, attachments):
        """
        ТЗ: Якщо в описі є "специфікація"/"API" → обов'язковий файл.
        """
        if not description:
            return None

        # Шукаємо ключові слова в описі (без урахування регістру)
        description_lower = description.lower()
        keywords = ['специфікація', 'специфікации', 'api', 'апі']

        needs_file = any(keyword in description_lower for keyword in keywords)

        if needs_file:
            # Поки що attachments не реалізовано, тому завжди помилка
            return "Для завдань з API або специфікацією потрібно додати файл"

        return None  # Файл не потрібен
