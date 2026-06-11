from django.test import TestCase
from accidentes.shared.repositories import PinotRepository, QueryTimeout
from accidentes.shared.utils import uuid_to_pinot_id


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


class SafeValueTest(TestCase):
    def test_int_value(self):
        self.assertEqual(PinotRepository.safe_value(42), "42")

    def test_float_value(self):
        self.assertEqual(PinotRepository.safe_value(3.14), "3.14")

    def test_none_value(self):
        self.assertEqual(PinotRepository.safe_value(None), "NULL")

    def test_string_value(self):
        self.assertEqual(PinotRepository.safe_value("hello"), "'hello'")

    def test_string_with_quote(self):
        self.assertEqual(PinotRepository.safe_value("O'Brien"), "'O''Brien'")

    def test_string_with_backslash(self):
        self.assertEqual(PinotRepository.safe_value("a\\b"), "'a\\\\b'")

    def test_zero_int(self):
        self.assertEqual(PinotRepository.safe_value(0), "0")

    def test_negative_int(self):
        self.assertEqual(PinotRepository.safe_value(-5), "-5")


class BuildSafeQueryTest(TestCase):
    def test_no_placeholders(self):
        sql = PinotRepository.build_safe_query("SELECT * FROM tab")
        self.assertEqual(sql, "SELECT * FROM tab")

    def test_one_int_placeholder(self):
        sql = PinotRepository.build_safe_query("SELECT * FROM t WHERE id = ?", 42)
        self.assertEqual(sql, "SELECT * FROM t WHERE id = 42")

    def test_one_str_placeholder(self):
        sql = PinotRepository.build_safe_query(
            "SELECT * FROM t WHERE name = ?", "hello"
        )
        self.assertEqual(sql, "SELECT * FROM t WHERE name = 'hello'")

    def test_multiple_placeholders(self):
        sql = PinotRepository.build_safe_query(
            "SELECT * FROM t WHERE a = ? AND b = ? AND c = ?",
            1, "test", None,
        )
        self.assertEqual(sql, "SELECT * FROM t WHERE a = 1 AND b = 'test' AND c = NULL")

    def test_quote_in_string_placeholder(self):
        sql = PinotRepository.build_safe_query(
            "SELECT * FROM t WHERE name = ?", "O'Brien"
        )
        self.assertEqual(sql, "SELECT * FROM t WHERE name = 'O''Brien'")

    def test_injection_attempt_placeholder(self):
        sql = PinotRepository.build_safe_query(
            "SELECT * FROM t WHERE name = ?",
            "'; DROP TABLE t; --",
        )
        self.assertIn("''", sql)
        self.assertNotIn("DROP", sql.split("'")[1] if len(sql.split("'")) > 1 else "")

    def test_placeholder_count_mismatch_raises(self):
        with self.assertRaises(ValueError):
            PinotRepository.build_safe_query("SELECT * FROM t WHERE a = ? AND b = ?", 1)


class UuidToPinotIdTest(TestCase):
    def test_uuid_returns_int(self):
        result = uuid_to_pinot_id("550e8400-e29b-41d4-a716-446655440000")
        self.assertIsInstance(result, int)

    def test_uuid_positive(self):
        result = uuid_to_pinot_id("550e8400-e29b-41d4-a716-446655440000")
        self.assertGreaterEqual(result, 0)

    def test_same_uuid_same_result(self):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        self.assertEqual(uuid_to_pinot_id(uid), uuid_to_pinot_id(uid))

    def test_different_uuids_different_results(self):
        self.assertNotEqual(
            uuid_to_pinot_id("550e8400-e29b-41d4-a716-446655440000"),
            uuid_to_pinot_id("660e8400-e29b-41d4-a716-446655440001"),
        )

    def test_empty_string(self):
        result = uuid_to_pinot_id("")
        self.assertIsInstance(result, int)

    def test_within_32bit_range(self):
        result = uuid_to_pinot_id("550e8400-e29b-41d4-a716-446655440000")
        self.assertLessEqual(result, 0x7FFFFFFF)


class QueryTimeoutTest(TestCase):
    def test_catalogo_timeout(self):
        self.assertEqual(QueryTimeout.CATALOGO, 3.0)

    def test_busqueda_timeout(self):
        self.assertEqual(QueryTimeout.BUSQUEDA, 5.0)

    def test_expediente_timeout(self):
        self.assertEqual(QueryTimeout.EXPEDIENTE, 10.0)

    def test_escritura_timeout(self):
        self.assertEqual(QueryTimeout.ESCRITURA, 5.0)

    def test_default_timeout(self):
        self.assertEqual(QueryTimeout.DEFAULT, 5.0)
