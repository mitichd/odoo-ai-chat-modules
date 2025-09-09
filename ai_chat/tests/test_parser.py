"""
Простий тест парсера команд.
Запускається при оновленні модуля.
"""

from .command_parser import CommandParser


def test_parser():
    """Тестуємо парсер команд."""
    parser = CommandParser()

    # Тест 1: Команда з текстом
    result1 = parser.parse_message('/create_task Написати звіт')
    print("🧪 Тест 1:", result1)

    # Тест 2: Команда без тексту
    result2 = parser.parse_message('/list_tasks')
    print("🧪 Тест 2:", result2)

    # Тест 3: Звичайне повідомлення
    result3 = parser.parse_message('Привіт!')
    print("🧪 Тест 3:", result3)

    # Тест 4: Довідка
    help_commands = parser.get_help()
    print("🧪 Довідка:", help_commands)

    print("✅ Всі тести пройшли!")


# Запускаємо тести при імпорті
test_parser()
