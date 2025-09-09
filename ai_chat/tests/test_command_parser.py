from odoo.tests.common import TransactionCase
from ..models.command_parser import CommandParser


class TestCommandParser(TransactionCase):
    """
    Тести для парсера команд.
    """

    def setUp(self):
        super().setUp()
        self.parser = CommandParser()

    def test_parse_command_with_params(self):
        """Тест розбору команди з параметрами."""
        result = self.parser.parse('/create_task Написати звіт')

        self.assertTrue(result['is_command'])
        self.assertEqual(result['command'], 'create_task')
        self.assertEqual(result['params'], 'Написати звіт')
        self.assertEqual(result['original'], '/create_task Написати звіт')

    def test_parse_command_without_params(self):
        """Тест розбору команди без параметрів."""
        result = self.parser.parse('/list_tasks')

        self.assertTrue(result['is_command'])
        self.assertEqual(result['command'], 'list_tasks')
        self.assertEqual(result['params'], '')

    def test_parse_regular_message(self):
        """Тест розбору звичайного повідомлення."""
        result = self.parser.parse('Привіт! Як справи?')

        self.assertFalse(result['is_command'])
        self.assertIsNone(result['command'])
        self.assertEqual(result['original'], 'Привіт! Як справи?')

    def test_get_available_commands(self):
        """Тест отримання списку команд."""
        commands = self.parser.get_available_commands()

        self.assertIn('create_task', commands)
        self.assertIn('list_tasks', commands)
        self.assertIn('help', commands)
