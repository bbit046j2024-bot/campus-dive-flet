import sqlite3
import os
import bcrypt
import tempfile

# FIX #4: Use proper data directory instead of app root
# Store database in user's home directory instead of app installation folder
APP_DATA_DIR = os.path.expanduser("~/.campus_dive")
os.makedirs(APP_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(APP_DATA_DIR, "campus_recruitment.db")

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def execute_query(query, params=(), commit=True):
    """Executes a single query and optionally commits the transaction."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def fetch_one(query, params=()):
    """Fetches a single row from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def fetch_all(query, params=()):
    """Fetches all rows from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def init_db():
    """Initializes all database tables, foreign key indexes, and inserts seed data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Core tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        category TEXT DEFAULT 'general'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (role_id, permission_id),
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        google_id TEXT UNIQUE DEFAULT NULL,
        phone TEXT NOT NULL,
        student_id TEXT DEFAULT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'student', 'admin', 'manager', 'interviewer')) DEFAULT 'student',
        role_id INTEGER DEFAULT NULL,
        avatar TEXT DEFAULT NULL,
        avatar_image TEXT DEFAULT NULL,
        status TEXT CHECK(status IN ('submitted', 'pending', 'documents_uploaded', 'under_review', 'interview_scheduled', 'approved', 'rejected')) DEFAULT 'submitted',
        recruitment_letter TEXT DEFAULT NULL,
        verification_token TEXT DEFAULT NULL,
        email_verified INTEGER DEFAULT 0,
        reset_token TEXT DEFAULT NULL,
        reset_token_expires TEXT DEFAULT NULL,
        profile_score INTEGER DEFAULT 0,
        bio TEXT DEFAULT NULL,
        location TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        document_name TEXT DEFAULT NULL,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        attachment_path TEXT DEFAULT NULL,
        type TEXT CHECK(type IN ('text', 'file', 'system')) DEFAULT 'text',
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruitment_letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        letter_content TEXT NOT NULL,
        sent_by INTEGER NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (sent_by) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT NULL,
        action TEXT NOT NULL,
        details TEXT DEFAULT NULL,
        ip_address TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS application_stages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stage_name TEXT NOT NULL,
        entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        exited_at TIMESTAMP DEFAULT NULL,
        duration_seconds INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Marketing campaigns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT DEFAULT NULL,
        body_content TEXT NOT NULL,
        type TEXT CHECK(type IN ('email', 'sms')) NOT NULL DEFAULT 'email',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        template_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('email', 'sms')) NOT NULL DEFAULT 'email',
        segment_criteria TEXT DEFAULT NULL,
        scheduled_at TIMESTAMP DEFAULT NULL,
        status TEXT CHECK(status IN ('draft', 'scheduled', 'processing', 'completed', 'cancelled')) DEFAULT 'draft',
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (template_id) REFERENCES marketing_templates(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        recipient_contact TEXT NOT NULL,
        message_content TEXT NOT NULL,
        subject TEXT DEFAULT NULL,
        status TEXT CHECK(status IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
        sent_at TIMESTAMP DEFAULT NULL,
        error_message TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        queue_id INTEGER NOT NULL,
        event_type TEXT CHECK(event_type IN ('open', 'click')) NOT NULL,
        ip_address TEXT DEFAULT NULL,
        user_agent TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Advanced docs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        version_num INTEGER NOT NULL DEFAULT 1,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        content TEXT DEFAULT NULL,
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)

    # Interview slots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        status TEXT CHECK(status IN ('open', 'booked', 'completed', 'cancelled')) DEFAULT 'open',
        booked_by INTEGER DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (booked_by) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # Social hub
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT NULL,
        category TEXT DEFAULT 'General',
        avatar_url TEXT DEFAULT NULL,
        cover_image TEXT DEFAULT NULL,
        is_public INTEGER DEFAULT 1,
        is_private INTEGER DEFAULT 0,
        manager_id INTEGER DEFAULT NULL,
        status TEXT CHECK(status IN ('active', 'archived', 'pending')) DEFAULT 'active',
        post_approval_required INTEGER DEFAULT 0,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT CHECK(role IN ('member', 'moderator', 'manager', 'admin')) DEFAULT 'member',
        status TEXT CHECK(status IN ('active', 'pending', 'blocked')) DEFAULT 'active',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES social_groups(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER DEFAULT NULL,
        content TEXT NOT NULL,
        media_url TEXT DEFAULT NULL,
        media_type TEXT CHECK(media_type IN ('image', 'video', 'link')) DEFAULT 'image',
        status TEXT CHECK(status IN ('pending', 'published', 'rejected')) DEFAULT 'published',
        pinned INTEGER DEFAULT 0,
        like_count INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (group_id) REFERENCES social_groups(id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (post_id, user_id),
        FOREIGN KEY (post_id) REFERENCES group_posts(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES group_posts(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # ── CREATE PERFORMANCE INDEXES (Resolves Issue #3 & DB Standards) ──
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_group_id ON group_posts(group_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON group_posts(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_post_id ON post_comments(post_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_likes_post_id ON post_likes(post_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status_role ON users(status, role);")

    # ── SEED DATA ──
    # Insert Roles
    cursor.execute("INSERT OR IGNORE INTO roles (id, name, description) VALUES (1, 'Admin', 'Full system access')")
    cursor.execute("INSERT OR IGNORE INTO roles (id, name, description) VALUES (2, 'Manager', 'Can manage students and documents')")
    cursor.execute("INSERT OR IGNORE INTO roles (id, name, description) VALUES (3, 'Interviewer', 'Can conduct interviews and update status')")
    cursor.execute("INSERT OR IGNORE INTO roles (id, name, description) VALUES (4, 'Student', 'Regular user access')")

    # Insert Permissions
    permissions = [
        ("View Students", "view_students", "students"),
        ("Approve Applications", "approve_applications", "students"),
        ("Reject Applications", "reject_applications", "students"),
        ("Delete Students", "delete_students", "students"),
        ("Move to Review", "move_review", "workflow"),
        ("Schedule Interview", "schedule_interview", "workflow"),
        ("Send Messages", "send_messages", "communication"),
        ("Manage Settings", "manage_settings", "system"),
        ("Manage Roles", "manage_roles", "system"),
        ("View Analytics", "view_analytics", "system")
    ]
    for name, slug, cat in permissions:
        cursor.execute("INSERT OR IGNORE INTO permissions (name, slug, category) VALUES (?, ?, ?)", (name, slug, cat))

    # Map Admin role (id=1) to all permissions
    cursor.execute("SELECT id FROM permissions")
    perm_ids = [row[0] for row in cursor.fetchall()]
    for p_id in perm_ids:
        cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (1, ?)", (p_id,))

    # Map Student role (id=4) to basic permissions
    # Send Messages (id of 'send_messages')
    cursor.execute("SELECT id FROM permissions WHERE slug = 'send_messages'")
    send_msg_row = cursor.fetchone()
    if send_msg_row:
        cursor.execute("INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (4, ?)", (send_msg_row[0],))

    # Insert default admin user if not exists
    cursor.execute("SELECT id FROM users WHERE email = 'admin@campusdive.com'")
    admin_exists = cursor.fetchone()
    if not admin_exists:
        # Secure password hashing (resolves Hardcoded Credentials vulnerability)
        hashed_pw = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("""
        INSERT INTO users (firstname, lastname, email, phone, password, role, role_id, avatar, status, email_verified)
        VALUES ('Admin', 'User', 'admin@campusdive.com', '+254700000000', ?, 'admin', 1, 'AU', 'approved', 1)
        """, (hashed_pw,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
