from django.test import TestCase
from accidentes.shared.repositories import PinotRepository


class EscapeSqlStrTest(TestCase):
    def test_simple_string(self):
        self.assertEqual(PinotRepository.escape_sql_str("hello"), "hello")

    def test_single_quote(self):
        self.assertEqual(PinotRepository.escape_sql_str("O'Brien"), "O''Brien")

    def test_double_quote(self):
        result = PinotRepository.escape_sql_str("he said \"hi\"")
        self.assertIn("he said", result)

    def test_backslash(self):
        self.assertEqual(PinotRepository.escape_sql_str("path\\to"), "path\\\\to")

    def test_mixed_escaping(self):
        result = PinotRepository.escape_sql_str("it's a \\path\\")
        self.assertEqual(result, "it''s a \\\\path\\\\")

    def test_empty_string(self):
        self.assertEqual(PinotRepository.escape_sql_str(""), "")

    def test_sql_injection_attempt(self):
        malicious = "'; DROP TABLE accidentes; --"
        result = PinotRepository.escape_sql_str(malicious)
        self.assertEqual(result.count("'") % 2, 0)
        self.assertIn("''", result)
