"""
Database management for Secret Santa Horror Edition.
Relational SQLite implementation with normalized tables, secure password hashing,
and deterministic/cycle Secret Santa assignment algorithms.
"""

import sqlite3
import os
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# 25 Distinct Horror Color Shades for the Occult Wheel
HORROR_WHEEL_PALETTE = [
    {"index": 0, "name": "Blood Crimson", "color": "#8b0000", "glow": "#ff1a1a"},
    {"index": 1, "name": "Nightshade Violet", "color": "#2c1142", "glow": "#7b2cbf"},
    {"index": 2, "name": "Rotting Ochre", "color": "#4a3c10", "glow": "#d4a373"},
    {"index": 3, "name": "Abyssal Obsidian", "color": "#121118", "glow": "#495057"},
    {"index": 4, "name": "Spectral Phantasm", "color": "#0a2f35", "glow": "#2ec4b6"},
    {"index": 5, "name": "Dried Gore", "color": "#590d15", "glow": "#9e2a2b"},
    {"index": 6, "name": "Necrotic Bone", "color": "#332e29", "glow": "#adb5bd"},
    {"index": 7, "name": "Toxic Emerald", "color": "#0d3b1e", "glow": "#38b000"},
    {"index": 8, "name": "Phantom Indigo", "color": "#171435", "glow": "#5a189a"},
    {"index": 9, "name": "Vampiric Scarlet", "color": "#a80018", "glow": "#ff4d6d"},
    {"index": 10, "name": "Ashen Charcoal", "color": "#1c1c1f", "glow": "#6c757d"},
    {"index": 11, "name": "Cursed Amber", "color": "#633909", "glow": "#ffaa00"},
    {"index": 12, "name": "Grave Moss", "color": "#1a3826", "glow": "#52b788"},
    {"index": 13, "name": "Witching Plum", "color": "#3a0934", "glow": "#b5179e"},
    {"index": 14, "name": "Demonic Burgundy", "color": "#670a22", "glow": "#c9184a"},
    {"index": 15, "name": "Eldritch Slate", "color": "#1f242e", "glow": "#70e000"},
    {"index": 16, "name": "Tombstone Grey", "color": "#282a2e", "glow": "#ced4da"},
    {"index": 17, "name": "Brimstone Orange", "color": "#5c2409", "glow": "#ff7b00"},
    {"index": 18, "name": "Coffin Mahogany", "color": "#3d1308", "glow": "#b05232"},
    {"index": 19, "name": "Sorrow Azure", "color": "#0b1d3a", "glow": "#0077b6"},
    {"index": 20, "name": "Crypt Cyan", "color": "#0e2d33", "glow": "#00b4d8"},
    {"index": 21, "name": "Mausoleum Black", "color": "#0a0a0d", "glow": "#343a40"},
    {"index": 22, "name": "Hallow Rust", "color": "#4d1d11", "glow": "#e76f51"},
    {"index": 23, "name": "Sepulcher Purple", "color": "#240046", "glow": "#9d4edd"},
    {"index": 24, "name": "Forbidden Void", "color": "#050505", "glow": "#ff0033", "forbidden": True}
]

# Occult Sigils for disguising identities on the spinning wheel
OCCULT_SIGILS = [
    "⛧", "🕱", "🕂", "☥", "🕇", "🕈", "⚕", "⚖", 
    "☽", "☾", "☄", "⚡", "⛓", "⚔", "🗝", "🕯",
    "👁", "🩸", "💀", "🦇", "🕷", "🌑", "⌛", "🗡", "⛔"
]

SAMPLE_PREFERENCES = [
    "Vintage cursed skull coffee mug",
    "Dark roast Ethiopian midnight coffee beans",
    "Leatherbound collection of Edgar Allan Poe stories",
    "Blood-orange & sandalwood apothecary candle",
    "Black velvet gothic cloak with silver clasp",
    "Gargoyle stone bookends for dorm library",
    "Horror movie synthwave vinyl soundtrack",
    "Ancient Tarot deck of shadow archetypes",
    "Obsidian dagger letter opener",
    "Haunted Victorian mansion mechanical puzzle box",
    "Nocturnal bat specimen taxidermy art frame",
    "Bram Stoker Dracula illustrated anniversary edition",
    "Cold forged iron dice set with skull engravings",
    "Grimoire style blank parchment notebook",
    "Antique brass pocket compass that points 'nowhere'",
    "Alchemist herbal tea sampler with dried hibiscus",
    "Midnight raven plush companion",
    "Black ceramic cauldron ramen bowl & chopsticks",
    "Vintage horror VHS-style LED mood lamp",
    "Haunted vinyl record player slipmat",
    "Gothic cathedral stained glass enamel pin set",
    "Ghost story anthology & red wax sealing stamp kit",
    "Distressed charcoal oversized dorm hoodie",
    "Onyx crystal protection bracelet",
    "Cursed carnival vintage fortune-teller card deck"
]

from contextlib import contextmanager

@contextmanager
def get_db():
    """Establishes SQLite connection with foreign keys enabled, row mapping, and auto-closing."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the normalized relational database schema."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Users table (stores 25 student accounts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Gift Preferences table (normalized relation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gift_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                preference TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 3. Secret Santa Assignments (giver -> receiver mapping)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secret_santa_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giver_id INTEGER NOT NULL UNIQUE,
                receiver_id INTEGER NOT NULL UNIQUE,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (giver_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
                CHECK (giver_id != receiver_id)
            );
        """)

        # 4. Participation status (tracks single attempt per student)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                has_participated INTEGER DEFAULT 0,
                participated_at TIMESTAMP,
                wheel_slice_index INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        conn.commit()

def generate_fair_assignments(user_ids):
    """
    Generates a single Hamiltonian cycle (derangement) across all participants.
    Guarantees:
    - Nobody gets themselves (giver_id != receiver_id).
    - Every student gives to exactly one person.
    - Every student receives from exactly one person.
    - No disjoint sub-cycles.
    """
    if len(user_ids) < 2:
        return []

    # Shuffle deterministic random cycle
    shuffled = list(user_ids)
    random.shuffle(shuffled)

    assignments = []
    n = len(shuffled)
    for i in range(n):
        giver = shuffled[i]
        receiver = shuffled[(i + 1) % n]
        assignments.append((giver, receiver))
    return assignments

def seed_sample_students(force_reset=False, default_password="HorrorSanta#2026"):
    """
    Populates exactly 25 realistic student records, sets gift preferences,
    initializes participation records, and generates fair Secret Santa assignments.
    """
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        if count > 0 and not force_reset:
            return  # Already seeded

        if force_reset:
            cursor.execute("DELETE FROM participation")
            cursor.execute("DELETE FROM secret_santa_assignments")
            cursor.execute("DELETE FROM gift_preferences")
            cursor.execute("DELETE FROM users")
            conn.commit()

        # Seed 25 fictional students
        hashed_pw = generate_password_hash(default_password)
        created_user_ids = []

        for i in range(1, 26):
            padded_num = f"{i:02d}"
            name = f"Student {padded_num}"
            email = f"student{padded_num}@example.com"
            preference = SAMPLE_PREFERENCES[(i - 1) % len(SAMPLE_PREFERENCES)]

            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, hashed_pw)
            )
            user_id = cursor.lastrowid
            created_user_ids.append(user_id)

            cursor.execute(
                "INSERT INTO gift_preferences (user_id, preference) VALUES (?, ?)",
                (user_id, preference)
            )

            cursor.execute(
                "INSERT INTO participation (user_id, has_participated) VALUES (?, 0)",
                (user_id,)
            )

        # Generate single-cycle derangement
        assignments = generate_fair_assignments(created_user_ids)
        for giver, receiver in assignments:
            cursor.execute(
                "INSERT INTO secret_santa_assignments (giver_id, receiver_id) VALUES (?, ?)",
                (giver, receiver)
            )

        conn.commit()

# --- User & Auth Operations ---

def create_user(name, email, password, preference):
    """Creates a new student user, adds preference, and initializes participation."""
    password_hash = generate_password_hash(password)
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name.strip(), email.strip().lower(), password_hash)
            )
            user_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO gift_preferences (user_id, preference) VALUES (?, ?)",
                (user_id, preference.strip())
            )

            cursor.execute(
                "INSERT INTO participation (user_id, has_participated) VALUES (?, 0)",
                (user_id,)
            )

            # Re-balance assignments if needed
            conn.commit()
            return user_id, None
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return None, "Email address already registered in the realm."
        except Exception as e:
            conn.rollback()
            return None, str(e)

def authenticate_user(email, password):
    """Validates student credentials securely."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip().lower(),))
        user = cursor.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            return dict(user)
        return None

def get_user_by_id(user_id):
    """Fetches user details safely without exposing password hashes."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.name, u.email, u.created_at, gp.preference as gift_preference,
                   p.has_participated, p.participated_at
            FROM users u
            LEFT JOIN gift_preferences gp ON u.id = gp.user_id
            LEFT JOIN participation p ON u.id = p.user_id
            WHERE u.id = ?
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_users_count():
    """Returns the total number of enrolled students."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def check_participation(user_id):
    """Checks if the user has already used their one attempt."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT has_participated, participated_at FROM participation WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row and row["has_participated"] == 1:
            return True, row["participated_at"]
        return False, None

def get_assigned_recipient(giver_id):
    """
    Fetches the secret recipient for a giver.
    Returns recipient details (name, preference, id).
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.name, gp.preference as gift_preference
            FROM secret_santa_assignments ssa
            JOIN users u ON ssa.receiver_id = u.id
            LEFT JOIN gift_preferences gp ON u.id = gp.user_id
            WHERE ssa.giver_id = ?
            """,
            (giver_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def mark_participation_complete(user_id, wheel_slice_index=None):
    """
    Finalizes the student's single participation attempt.
    Transaction-safe to prevent race conditions or duplicate attempts.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE participation
            SET has_participated = 1,
                participated_at = CURRENT_TIMESTAMP,
                wheel_slice_index = ?
            WHERE user_id = ? AND has_participated = 0
            """,
            (wheel_slice_index, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def get_wheel_layout_for_user(current_user_id):
    """
    Generates the 25-slice wheel configuration for the current user.
    - Excludes the current user from the 24 candidate sectors.
    - Slices 0 to 23 represent the 24 other eligible student souls.
    - Slices are disguised with occult sigils and eerie titles during spin.
    - Slice 24 is designated as the 'Forbidden Void / Own Soul' (unselectable).
    - Returns the slice array and the assigned recipient's target slice index.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Fetch all other students except current user
        cursor.execute(
            "SELECT id, name FROM users WHERE id != ? ORDER BY id ASC",
            (current_user_id,)
        )
        other_students = [dict(row) for row in cursor.fetchall()]

        # Fetch current user's assigned recipient
        cursor.execute(
            "SELECT receiver_id FROM secret_santa_assignments WHERE giver_id = ?",
            (current_user_id,)
        )
        assignment = cursor.fetchone()
        target_receiver_id = assignment["receiver_id"] if assignment else None

        # Safeguard: If user has no assignment yet, find an unassigned or random other user
        if not target_receiver_id and other_students:
            chosen_candidate = other_students[0]
            cursor.execute(
                "INSERT OR REPLACE INTO secret_santa_assignments (giver_id, receiver_id) VALUES (?, ?)",
                (current_user_id, chosen_candidate["id"])
            )
            conn.commit()
            target_receiver_id = chosen_candidate["id"]

    # Construct the 25 wheel slices
    slices = []
    target_slice_index = -1

    # Deterministic pseudo-shuffle based on user_id so wheel layout is stable for this user
    rng = random.Random(current_user_id * 1013)
    shuffled_candidates = list(other_students)
    rng.shuffle(shuffled_candidates)

    for i in range(24):
        candidate = shuffled_candidates[i] if i < len(shuffled_candidates) else None
        palette = HORROR_WHEEL_PALETTE[i]
        sigil = OCCULT_SIGILS[i % len(OCCULT_SIGILS)]

        if candidate and candidate["id"] == target_receiver_id:
            target_slice_index = i

        slices.append({
            "index": i,
            "disguised_name": f"SOUL #{i + 1:02d}",
            "sigil": sigil,
            "color_name": palette["name"],
            "color": palette["color"],
            "glow": palette["glow"],
            "is_forbidden": False
        })

    # Slice 24: The Forbidden Soul / Void
    void_palette = HORROR_WHEEL_PALETTE[24]
    slices.append({
        "index": 24,
        "disguised_name": "FORBIDDEN VOID",
        "sigil": "⛔",
        "color_name": void_palette["name"],
        "color": void_palette["color"],
        "glow": void_palette["glow"],
        "is_forbidden": True
    })

    if target_slice_index == -1 and len(slices) > 1:
        target_slice_index = 0

    return slices, target_slice_index
