"""
Automated validation test suite for DMI(F-N) infobot.
Tests database, scraper, notifier, and configuration.
"""

import os
import tempfile
import unittest
import database
import scraper
import notifier
import config


class TestDmiBot(unittest.TestCase):

    def setUp(self):
        # Use a temporary SQLite database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        database.init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_database_user_lifecycle(self):
        # 1. Register new user
        is_new = database.register_user(1234567, "angelo_test", "Angelo", self.db_path)
        self.assertTrue(is_new)

        # 2. Get user
        user = database.get_user(1234567, self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["chat_id"], 1234567)
        self.assertEqual(user["username"], "angelo_test")
        self.assertEqual(user["first_name"], "Angelo")
        self.assertEqual(user["is_active"], 1)
        self.assertEqual(user["include_cds"], 0)

        # 3. Toggle CdS setting
        new_val = database.toggle_user_cds(1234567, self.db_path)
        self.assertTrue(new_val)
        user = database.get_user(1234567, self.db_path)
        self.assertEqual(user["include_cds"], 1)

        # 4. Toggle back
        new_val = database.toggle_user_cds(1234567, self.db_path)
        self.assertFalse(new_val)
        user = database.get_user(1234567, self.db_path)
        self.assertEqual(user["include_cds"], 0)

        # 5. Deactivate user
        database.set_user_active(1234567, False, self.db_path)
        active_users = database.get_all_active_users(self.db_path)
        self.assertEqual(len(active_users), 0)

        # 6. Reactivate user
        database.set_user_active(1234567, True, self.db_path)
        active_users = database.get_all_active_users(self.db_path)
        self.assertEqual(len(active_users), 1)

    def test_database_seen_notices(self):
        notice = {
            "id": "https://web.dmi.unict.it/avvisi-docente/test-notice",
            "title": "Avviso Test",
            "author": "Prof. Test",
            "date": "12/10/2026",
            "link": "https://web.dmi.unict.it/avvisi-docente/test-notice",
            "reason": "Test"
        }

        # Notice not seen yet
        self.assertFalse(database.is_notice_seen(notice["id"], self.db_path))

        # Mark seen
        inserted = database.mark_notice_seen(notice, self.db_path)
        self.assertTrue(inserted)
        self.assertTrue(database.is_notice_seen(notice["id"], self.db_path))

        # Re-marking should not error
        inserted_again = database.mark_notice_seen(notice, self.db_path)
        self.assertFalse(inserted_again)

    def test_notifier_html_formatting(self):
        notice = {
            "title": "Test <Special> & Title",
            "author": "Prof. Mario Rossi",
            "date": "12/10/2026",
            "link": "https://web.dmi.unict.it/avvisi/test",
            "reason": "Docente Canale F-N: Rossi",
            "body": "Corpo dell'avviso con caratteri <b>html</b> e simboli < > &"
        }

        msg = notifier.format_notice_message(notice, is_alert=True)
        # Check that HTML special characters are escaped
        self.assertIn("&lt;Special&gt;", msg)
        self.assertIn("&amp; Title", msg)
        self.assertIn("Prof. Mario Rossi", msg)
        self.assertIn("https://web.dmi.unict.it/avvisi/test", msg)

    def test_scraper_fn_professors(self):
        profs = scraper.get_fn_professors()
        self.assertGreater(len(profs), 0)
        # Check known F-N professors are detected
        profs_lower = {k.lower() for k in profs.keys()}
        has_calvagna = any("calvagna" in p for p in profs_lower)
        has_spata = any("spata" in p for p in profs_lower)
        self.assertTrue(has_calvagna, "Prof. Calvagna dovrebbe essere tra i docenti F-N")
        self.assertTrue(has_spata, "Prof. Spata dovrebbe essere tra i docenti F-N")

    def test_scraper_fn_notices_live(self):
        notices = scraper.fetch_all_fn_notices(max_pages=2, include_cds_general=False)
        self.assertIsInstance(notices, list)
        for n in notices:
            self.assertIn("id", n)
            self.assertIn("title", n)
            self.assertIn("link", n)
            self.assertIn("reason", n)


if __name__ == "__main__":
    unittest.main()
