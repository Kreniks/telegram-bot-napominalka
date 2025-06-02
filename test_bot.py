"""
Тесты для Telegram-бота "Напоминалка"
"""
import unittest
from datetime import time
from utils.time_utils import validate_time_format, parse_time_string, format_time, is_time_equal
from utils.reminder_manager import ReminderManager


class TestTimeUtils(unittest.TestCase):
    """Тесты для утилит работы со временем"""
    
    def test_validate_time_format_valid(self):
        """Тест валидации корректных форматов времени"""
        valid_times = ["00:00", "12:30", "23:59", "9:15", "01:05"]
        for time_str in valid_times:
            with self.subTest(time_str=time_str):
                self.assertTrue(validate_time_format(time_str))
    
    def test_validate_time_format_invalid(self):
        """Тест валидации некорректных форматов времени"""
        invalid_times = ["24:00", "12:60", "abc", "12", "12:", ":30", "12:30:45", "25:30"]
        for time_str in invalid_times:
            with self.subTest(time_str=time_str):
                self.assertFalse(validate_time_format(time_str))
    
    def test_parse_time_string_valid(self):
        """Тест парсинга корректных строк времени"""
        test_cases = [
            ("12:30", time(12, 30)),
            ("00:00", time(0, 0)),
            ("23:59", time(23, 59)),
            ("9:15", time(9, 15))
        ]
        for time_str, expected in test_cases:
            with self.subTest(time_str=time_str):
                result = parse_time_string(time_str)
                self.assertEqual(result, expected)
    
    def test_parse_time_string_invalid(self):
        """Тест парсинга некорректных строк времени"""
        invalid_times = ["24:00", "12:60", "abc", "12", "25:30"]
        for time_str in invalid_times:
            with self.subTest(time_str=time_str):
                with self.assertRaises(ValueError):
                    parse_time_string(time_str)
    
    def test_format_time(self):
        """Тест форматирования времени"""
        test_cases = [
            (time(12, 30), "12:30"),
            (time(0, 0), "00:00"),
            (time(23, 59), "23:59"),
            (time(9, 5), "09:05")
        ]
        for time_obj, expected in test_cases:
            with self.subTest(time_obj=time_obj):
                result = format_time(time_obj)
                self.assertEqual(result, expected)
    
    def test_is_time_equal(self):
        """Тест сравнения времени"""
        time1 = time(12, 30, 45)  # с секундами
        time2 = time(12, 30, 0)   # без секунд
        time3 = time(12, 31, 0)   # другая минута
        
        self.assertTrue(is_time_equal(time1, time2))
        self.assertFalse(is_time_equal(time1, time3))


class TestReminderManager(unittest.TestCase):
    """Тесты для менеджера напоминаний"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = ReminderManager()
    
    def test_set_and_get_reminder(self):
        """Тест установки и получения напоминания"""
        user_id = 123
        reminder_time = time(15, 30)
        chat_id = 456
        
        # Устанавливаем напоминание
        self.manager.set_reminder(user_id, reminder_time, chat_id)
        
        # Проверяем, что напоминание установлено
        self.assertTrue(self.manager.has_reminder(user_id))
        
        # Получаем напоминание
        result = self.manager.get_reminder(user_id)
        self.assertIsNotNone(result)
        self.assertEqual(result, (reminder_time, chat_id))
    
    def test_remove_reminder(self):
        """Тест удаления напоминания"""
        user_id = 123
        reminder_time = time(15, 30)
        chat_id = 456
        
        # Устанавливаем напоминание
        self.manager.set_reminder(user_id, reminder_time, chat_id)
        self.assertTrue(self.manager.has_reminder(user_id))
        
        # Удаляем напоминание
        result = self.manager.remove_reminder(user_id)
        self.assertTrue(result)
        self.assertFalse(self.manager.has_reminder(user_id))
        
        # Попытка удалить несуществующее напоминание
        result = self.manager.remove_reminder(user_id)
        self.assertFalse(result)
    
    def test_get_due_reminders(self):
        """Тест получения напоминаний к отправке"""
        user1, user2, user3 = 123, 456, 789
        chat1, chat2, chat3 = 111, 222, 333
        time1 = time(15, 30)
        time2 = time(16, 45)
        
        # Устанавливаем напоминания
        self.manager.set_reminder(user1, time1, chat1)
        self.manager.set_reminder(user2, time2, chat2)
        self.manager.set_reminder(user3, time1, chat3)
        
        # Проверяем напоминания для time1
        due_reminders = self.manager.get_due_reminders(time1)
        self.assertEqual(len(due_reminders), 2)
        
        # Проверяем, что правильные пользователи
        user_ids = [reminder[0] for reminder in due_reminders]
        self.assertIn(user1, user_ids)
        self.assertIn(user3, user_ids)
        self.assertNotIn(user2, user_ids)
    
    def test_clear_all_reminders(self):
        """Тест очистки всех напоминаний"""
        # Добавляем несколько напоминаний
        self.manager.set_reminder(123, time(15, 30), 111)
        self.manager.set_reminder(456, time(16, 45), 222)
        
        self.assertEqual(self.manager.get_reminders_count(), 2)
        
        # Очищаем все
        count = self.manager.clear_all_reminders()
        self.assertEqual(count, 2)
        self.assertEqual(self.manager.get_reminders_count(), 0)


def run_tests():
    """Запуск всех тестов"""
    print("Запуск тестов для Telegram-бота 'Напоминалка'...")
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestTimeUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestReminderManager))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    if result.wasSuccessful():
        print("\n✅ Все тесты прошли успешно!")
        return True
    else:
        print(f"\n❌ Тесты завершились с ошибками: {len(result.failures)} failures, {len(result.errors)} errors")
        return False


if __name__ == "__main__":
    run_tests()
