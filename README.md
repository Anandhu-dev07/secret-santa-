# 🩸 SECRET SANTA : HORROR EDITION 🩸
### *The Ritual of 25 Souls — A Dark Gothic Web Application*

A complete, production-ready, dark horror/haunted-house themed Secret Santa web platform tailored for exactly 25 college students. Built with a Python Flask backend, normalized SQLite database, procedural Web Audio synthesizer, and a 25-color occult wheel with an interactive bone-and-iron dart aiming mechanism.

---

## 🏛️ System Architecture & Folder Structure

```
Secret santa/
│
├── app.py                      # Flask backend, authentication, session security, REST APIs
├── database.py                 # SQLite relational layer, schema init, derangement logic
├── seed.py                     # CLI tool to initialize or reset 25 test students & assignments
├── test_app.py                 # Automated unit and integration test suite
├── database.db                 # SQLite database file
├── requirements.txt            # Python dependencies (Flask, Werkzeug)
├── README.md                   # Complete documentation and setup manual
│
├── index.html                  # Root horror landing & authentication portal
├── style.css                   # Root stylesheet (mirrors static/css/style.css)
├── script.js                   # Root client logic (mirrors static/js/script.js)
│
├── templates/
│   ├── index.html              # Horror landing & login/register tabbed portal
│   ├── dashboard.html          # Haunted mansion sanctum dashboard
│   ├── secret_santa.html       # Occult 25-color wheel & interactive dart throwing arena
│   └── result.html             # Sealed fate grimoire displaying revealed secret friend
│
└── static/
    ├── css/
    │   └── style.css           # Master horror design system (blood drips, glitch, fog, dark glow)
    ├── js/
    │   └── script.js           # Procedural Web Audio API sound fx, canvas particles, wheel physics
    ├── images/                 # Static graphical assets
    └── sounds/                 # Static audio fallbacks
```

---

## 🗄️ Database Design & Schema

The application uses a **normalized relational database** (`database.db`). It strictly adheres to proper schema design rather than creating separate tables for individual students.

### Tables:
1. **`users`**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `name`: `TEXT NOT NULL`
   - `email`: `TEXT UNIQUE NOT NULL COLLATE NOCASE`
   - `password_hash`: `TEXT NOT NULL` (Secure PBKDF2/SHA-256 via `werkzeug.security`)
   - `created_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

2. **`gift_preferences`**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `user_id`: `INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE`
   - `preference`: `TEXT NOT NULL`
   - `updated_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

3. **`secret_santa_assignments`**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `giver_id`: `INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE`
   - `receiver_id`: `INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE`
   - `assigned_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
   - `CHECK (giver_id != receiver_id)`

4. **`participation`**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `user_id`: `INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE`
   - `has_participated`: `INTEGER DEFAULT 0` (Strictly 1 attempt per student)
   - `participated_at`: `TIMESTAMP`
   - `wheel_slice_index`: `INTEGER`

---

## 🎯 Fair Secret Santa Algorithm & Derangement Logic

- **Single Hamiltonian Cycle Derangement**:
  When seeding or regenerating assignments, the 25 student IDs are randomly permuted: $[s_0, s_1, s_2, \dots, s_{24}]$. Each student $s_i$ is assigned to give to $s_{(i+1) \pmod{25}}$.
  - **No Self-Selection**: $s_i \neq s_{(i+1) \pmod{25}}$ is mathematically guaranteed ($25 > 1$).
  - **Single Closed Loop**: No disjoint sub-cycles; every student gives to 1 person and receives from 1 person.
  - **Strict Server-Side Secrecy**: Assignments are persisted on the server. The frontend JavaScript never receives the recipient mapping until the user physically completes their throw and clicks "OPEN IT".

### The 25-Color Wheel System:
- The wheel is divided into **25 distinct horror color sectors** (Blood Crimson, Nightshade Violet, Rotting Ochre, Abyssal Obsidian, Spectral Phantasm, Toxic Emerald, Vampiric Scarlet, etc.).
- **Self-Exclusion**: For any logged-in user, their own name is **never** among the 24 candidate sectors.
- Sector 24 is designated as the **"Forbidden Void"** ($\text{⛔}$), visually chained and locked.
- The other 24 sectors display mysterious disguised occult sigils and shadow tags (`SOUL #01`, `SOUL #02`, etc.) while spinning.
- The server determines the stop angle based on the user's pre-assigned recipient. When the user throws the dart, the wheel decelerates with realistic easing and stops precisely at their assigned sector.

---

## 🔐 One-Time Participation & Privacy Controls

1. **One-Time Attempt Limit**:
   - Each student gets exactly **ONE** throw.
   - When the user throws the dart and clicks "OPEN IT", `has_participated` is atomically set to `1` in SQLite.
   - Any further attempt to throw or access the ritual triggers the horror error:
     > *"YOU ALREADY HAD YOUR CHANCE."*
     > *"That was your last chance. No more chances remain."*
     With red flashing lights, screen glitch, and audio sting.
   - The backend `/api/throw-dart` endpoint returns `403 Forbidden` if `has_participated == 1`.
2. **Zero Sensitive Data Exposure**:
   - Passwords are never returned in responses or exposed in frontend code.
   - Recipient identities are disguised during the wheel spin.

---

## 🚀 Setup & Local Execution Instructions

### Prerequisites
- Python 3.9+ installed (`python --version`)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize / Seed the Database
Run the seed script to create the 25 sample students with sample gift preferences, hashed passwords, and the Secret Santa derangement:
```bash
python seed.py --reset
```

### 3. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 4. Run Automated Tests
```bash
python test_app.py
```

---

## 👥 25 Sample Students Credentials (For Testing)

All 25 pre-seeded test accounts share the universal default test cipher:
> **Default Password:** `HorrorSanta#2026`

| Student Name | Email Address | Sample Gift Wish |
| :--- | :--- | :--- |
| **Student 01** | `student01@example.com` | Vintage cursed skull coffee mug |
| **Student 02** | `student02@example.com` | Dark roast Ethiopian midnight coffee beans |
| **Student 03** | `student03@example.com` | Leatherbound collection of Edgar Allan Poe |
| **Student 04** | `student04@example.com` | Blood-orange & sandalwood apothecary candle |
| **Student 05** | `student05@example.com` | Black velvet gothic cloak with silver clasp |
| **Student 06** | `student06@example.com` | Gargoyle stone bookends for dorm library |
| **Student 07** | `student07@example.com` | Horror movie synthwave vinyl soundtrack |
| **Student 08** | `student08@example.com` | Ancient Tarot deck of shadow archetypes |
| **Student 09** | `student09@example.com` | Obsidian dagger letter opener |
| **Student 10** | `student10@example.com` | Haunted Victorian mansion puzzle box |
| **Student 11** | `student11@example.com` | Nocturnal bat specimen taxidermy frame |
| **Student 12** | `student12@example.com` | Bram Stoker Dracula illustrated edition |
| **Student 13** | `student13@example.com` | Cold forged iron dice set with skulls |
| **Student 14** | `student14@example.com` | Grimoire style blank parchment notebook |
| **Student 15** | `student15@example.com` | Antique brass pocket compass |
| **Student 16** | `student16@example.com` | Alchemist herbal tea sampler with hibiscus |
| **Student 17** | `student17@example.com` | Midnight raven plush companion |
| **Student 18** | `student18@example.com` | Black ceramic cauldron ramen bowl |
| **Student 19** | `student19@example.com` | Vintage horror VHS-style LED mood lamp |
| **Student 20** | `student20@example.com` | Haunted vinyl record player slipmat |
| **Student 21** | `student21@example.com` | Gothic cathedral stained glass enamel pins |
| **Student 22** | `student22@example.com` | Ghost story anthology & red wax seal kit |
| **Student 23** | `student23@example.com` | Distressed charcoal oversized dorm hoodie |
| **Student 24** | `student24@example.com` | Onyx crystal protection bracelet |
| **Student 25** | `student25@example.com` | Cursed carnival vintage fortune card deck |

*Tip: On the login page, you can click any of the **Quick Soul Portal (S-01 to S-25)** buttons to instantly populate the credentials!*

---

## 🔄 How to Replace the 25 Sample Students with Real Students

You can replace the 25 sample students without modifying any core application logic:

### Method A: Edit the List in `seed.py` / `database.py`
In `database.py`, modify the student data generator in `seed_sample_students()` to use a list of real student names and emails:
```python
REAL_STUDENTS = [
    {"name": "Alice Vance", "email": "alice@college.edu", "preference": "Sci-fi books"},
    {"name": "Bob Martinez", "email": "bob@college.edu", "preference": "Mechanical keyboard switches"},
    # ... up to 25 students
]
```
Then run:
```bash
python seed.py --reset
```

### Method B: Inscribe via Registration Portal
1. Clear the database: delete `database.db`.
2. Run `python -c "import database; database.init_db()"` to generate an empty schema.
3. Have the 25 students register via the **"INSCRIBE THY SOUL"** registration tab on `http://127.0.0.1:5000`.
4. Run `python seed.py` or trigger assignment cycle generation once all 25 students have registered.

---

## 🔊 Procedural Web Audio API Engine
The application includes a fully synthesized Web Audio engine built directly into `script.js`. It does not rely on external MP3 downloads or codecs and is 100% immune to missing asset errors:
- **`tick`**: Mechanical wheel clicks during deceleration.
- **`whoosh`**: Bandpass noise burst simulating the dart flying through the air.
- **`impact`**: Deep sub-frequency bone/wood thud upon landing.
- **`chime` / `bell`**: Sinister occult bell harmonies on reveal.
- **`warning`**: Distorted sawtooth glitch sting for the "YOU ALREADY HAD YOUR CHANCE" modal.

Includes a persistent **Sound ON/OFF** toggle button in the header that remembers user preference via `localStorage`.

---

## 📱 Mobile & Desktop Accessibility
- **Desktop**: Aim using mouse movement; click anywhere to cast the dart.
- **Mobile / Touch**: Touch & drag anywhere on the ritual stage to aim; release or tap to cast the dart.
- **Visuals**: Full SVG/Canvas scaling, responsive layout, CSS vignette, floating embers, and `@media (prefers-reduced-motion: reduce)` accessibility compliance.
