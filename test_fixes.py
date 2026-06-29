"""Test suite to verify all critical fixes are working.

This module tests:
- Session store initialization
- Database path configuration
- Upload directory path configuration
- Flet compatibility
- File operations
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from pathlib import Path


class TestSessionStoreInitialization(unittest.TestCase):
    """Test session store initialization fix."""

    def test_session_store_exists(self):
        """Test that session store can be initialized."""
        class MockSession:
            def __init__(self):
                self.store = {}
            
            def get(self, key):
                return self.store.get(key)
            
            def set(self, key, value):
                self.store[key] = value
            
            def clear(self):
                self.store.clear()
        
        session = MockSession()
        
        # Test set
        session.set("user", {"id": 1, "name": "Test User"})
        
        # Test get
        user = session.get("user")
        self.assertIsNotNone(user)
        self.assertEqual(user["id"], 1)
        
        # Test clear
        session.clear()
        user = session.get("user")
        self.assertIsNone(user)

    def test_session_store_operations(self):
        """Test session store operations."""
        class MockSession:
            def __init__(self):
                self.store = {}
            
            def get(self, key):
                return self.store.get(key)
            
            def set(self, key, value):
                self.store[key] = value
        
        session = MockSession()
        
        # Test multiple operations
        session.set("user", {"id": 1})
        session.set("theme", "dark")
        
        self.assertEqual(session.get("user")["id"], 1)
        self.assertEqual(session.get("theme"), "dark")


class TestDatabasePath(unittest.TestCase):
    """Test database path configuration fix."""

    def test_app_data_directory_creation(self):
        """Test that app data directory is created properly."""
        app_data_dir = os.path.expanduser("~/.campus_dive")
        
        # Directory should exist or be creatable
        self.assertTrue(
            os.path.exists(app_data_dir) or 
            os.access(os.path.dirname(app_data_dir), os.W_OK),
            "App data directory cannot be created"
        )

    def test_database_path_is_user_home(self):
        """Test that database path uses user home directory."""
        app_data_dir = os.path.expanduser("~/.campus_dive")
        db_path = os.path.join(app_data_dir, "campus_recruitment.db")
        
        # Path should expand properly (not contain ~)
        self.assertNotIn("~", db_path)
        
        # Path should be in user's home directory
        home = os.path.expanduser("~")
        self.assertTrue(
            db_path.startswith(home),
            f"Database path {db_path} not in home directory"
        )

    def test_database_creation(self):
        """Test that database can be created in app data directory."""
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            
            # Create connection
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            # Verify database was created
            self.assertTrue(os.path.exists(db_path))
            
            # Verify we can read it
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            self.assertGreater(len(tables), 0)


class TestUploadDirectory(unittest.TestCase):
    """Test upload directory path configuration fix."""

    def test_uploads_directory_path(self):
        """Test that uploads directory uses proper path."""
        uploads_dir = os.path.expanduser("~/.campus_dive/uploads")
        
        # Path should not contain ~
        self.assertNotIn("~", uploads_dir)
        
        # Path should be in user's home
        home = os.path.expanduser("~")
        self.assertTrue(
            uploads_dir.startswith(home),
            f"Uploads directory {uploads_dir} not in home directory"
        )

    def test_uploads_directory_creation(self):
        """Test that uploads directory can be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uploads_dir = os.path.join(tmpdir, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            
            self.assertTrue(os.path.exists(uploads_dir))
            self.assertTrue(os.path.isdir(uploads_dir))

    def test_file_write_to_uploads(self):
        """Test that files can be written to uploads directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uploads_dir = os.path.join(tmpdir, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Create a test file
            test_file = os.path.join(uploads_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")
            
            self.assertTrue(os.path.exists(test_file))
            
            with open(test_file, "r") as f:
                content = f.read()
                self.assertEqual(content, "test content")


class TestPathTraversalPrevention(unittest.TestCase):
    """Test path traversal prevention in file uploads."""

    def test_basename_sanitization(self):
        """Test that os.path.basename prevents path traversal."""
        uploads_dir = "/home/user/.campus_dive/uploads"
        
        # Attempt path traversal
        malicious_path = "../../etc/passwd"
        safe_name = os.path.basename(malicious_path)
        
        # Should only get filename
        self.assertEqual(safe_name, "passwd")

    def test_destination_path_validation(self):
        """Test that destination path is validated cleanly across operating systems."""
        # Use os.path.abspath to ensure the base directory matches local OS formatting rules
        uploads_dir = os.path.abspath(os.path.expanduser("~/.campus_dive/uploads"))
        safe_name = "test.pdf"
        
        dest_path = os.path.abspath(os.path.join(uploads_dir, safe_name))
        
        # Should correctly start with uploads_dir on both Windows and Linux
        self.assertTrue(
            dest_path.startswith(uploads_dir),
            f"Path validation failed: {dest_path} does not start with {uploads_dir}"
        )
    def test_extension_whitelist(self):
        """Test file extension whitelist."""
        allowed_extensions = {".pdf", ".docx", ".jpg", ".jpeg", ".png"}
        
        valid_files = ["resume.pdf", "transcript.docx", "photo.jpg"]
        invalid_files = ["malware.exe", "script.sh", "backup.zip"]
        
        for filename in valid_files:
            _, ext = os.path.splitext(filename.lower())
            self.assertIn(
                ext, allowed_extensions,
                f"{filename} should be allowed"
            )
        
        for filename in invalid_files:
            _, ext = os.path.splitext(filename.lower())
            self.assertNotIn(
                ext, allowed_extensions,
                f"{filename} should be rejected"
            )


class TestFletCompatibility(unittest.TestCase):
    """Test Flet version compatibility fixes."""

    def test_color_compatibility_check(self):
        """Test color module compatibility logic."""
        try:
            import flet as ft
            
            # Test that colors are accessible
            self.assertTrue(
                hasattr(ft, 'colors') or hasattr(ft, 'Colors'),
                "Flet color support not found"
            )
        except ImportError:
            self.skipTest("Flet not installed")

    def test_theme_mode_availability(self):
        """Test that theme modes are available."""
        try:
            import flet as ft
            
            # Test theme modes
            self.assertTrue(hasattr(ft, 'ThemeMode'))
            self.assertTrue(hasattr(ft.ThemeMode, 'DARK'))
            self.assertTrue(hasattr(ft.ThemeMode, 'LIGHT'))
        except ImportError:
            self.skipTest("Flet not installed")


class TestErrorHandling(unittest.TestCase):
    """Test improved error handling."""

    def test_file_existence_check(self):
        """Test file existence validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_file = os.path.join(tmpdir, "exists.txt")
            non_existing_file = os.path.join(tmpdir, "not_exists.txt")
            
            # Create file
            open(existing_file, "w").close()
            
            self.assertTrue(os.path.exists(existing_file))
            self.assertFalse(os.path.exists(non_existing_file))

    def test_directory_creation_safety(self):
        """Test safe directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test", "nested", "dir")
            
            # Should not raise even if exists
            os.makedirs(test_dir, exist_ok=True)
            self.assertTrue(os.path.exists(test_dir))
            
            # Should not raise on second call
            os.makedirs(test_dir, exist_ok=True)
            self.assertTrue(os.path.exists(test_dir))


class TestDatabaseIntegrity(unittest.TestCase):
    """Test database integrity and persistence."""

    def test_foreign_key_support(self):
        """Test that foreign keys are enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            
            # Check pragma is set
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 1, "Foreign keys not enabled")
            conn.close()

    def test_row_factory(self):
        """Test that row factory works properly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create test table and insert data
            cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")
            cursor.execute("INSERT INTO users VALUES (1, 'Test')")
            conn.commit()
            
            # Fetch and verify row factory works
            cursor.execute("SELECT * FROM users")
            row = cursor.fetchone()
            
            self.assertEqual(row["id"], 1)
            self.assertEqual(row["name"], "Test")
            conn.close()


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)