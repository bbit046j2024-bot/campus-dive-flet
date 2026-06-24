import bcrypt
from database import fetch_one, execute_query

def register_user(firstname, lastname, email, phone, student_id, password):
    """Registers a new student user after hashing their password."""
    # Check if email is already taken
    existing = fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        raise ValueError("Email is already registered.")

    # Hash the password securely
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Insert user (role_id=4 represents Student)
    cursor = execute_query("""
    INSERT INTO users (firstname, lastname, email, phone, student_id, password, role, role_id, status)
    VALUES (?, ?, ?, ?, ?, ?, 'student', 4, 'submitted')
    """, (firstname, lastname, email, phone, student_id or None, hashed_pw))
    
    return cursor.lastrowid

def login_user(email, password):
    """Authenticates a user and returns a public dictionary (excluding password)."""
    user = fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user:
        return None
        
    # Verify the password using bcrypt
    if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        # Strip password before returning (resolves API Overfetching / security gap)
        user_data = dict(user)
        user_data.pop("password", None)
        return user_data
    return None

def get_user_by_id(user_id):
    """Retrieves a user by ID without their password."""
    user = fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if user:
        user_data = dict(user)
        user_data.pop("password", None)
        return user_data
    return None

def update_user_profile(user_id, firstname, lastname, phone, bio, location):
    """Updates profile information for a user."""
    execute_query("""
    UPDATE users
    SET firstname = ?, lastname = ?, phone = ?, bio = ?, location = ?
    WHERE id = ?
    """, (firstname, lastname, phone, bio, location, user_id))
    
    return get_user_by_id(user_id)

def change_user_password(user_id, current_password, new_password):
    """Verifies current password and updates to a new hashed password."""
    user = fetch_one("SELECT password FROM users WHERE id = ?", (user_id,))
    if not user:
        raise ValueError("User not found.")
        
    if not bcrypt.checkpw(current_password.encode("utf-8"), user["password"].encode("utf-8")):
        raise ValueError("Incorrect current password.")
        
    hashed_new_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    execute_query("UPDATE users SET password = ? WHERE id = ?", (hashed_new_pw, user_id))
    return True
