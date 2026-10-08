"""
Seed script for Secret Santa Horror Edition.
Seeds exactly 25 fictional student records with sample gift preferences,
initializes the database schema, and generates the Secret Santa cycle derangement.
"""

import sys
from database import init_db, seed_sample_students, get_db

def main():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    force = "--reset" in sys.argv or "-r" in sys.argv
    print("=" * 60)
    print(" [!] SECRET SANTA - HORROR EDITION DATABASE SEEDER")
    print("=" * 60)
    
    init_db()
    seed_sample_students(force_reset=force, default_password="HorrorSanta#2026")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT u.id, u.name, u.email, gp.preference FROM users u JOIN gift_preferences gp ON u.id = gp.user_id ORDER BY u.id ASC")
        rows = cursor.fetchall()
        
        print(f"\n[+] Successfully verified {len(rows)} student records in the database:")
        print(f"{'ID':<4} | {'Name':<12} | {'Email':<25} | {'Gift Wish':<30}")
        print("-" * 78)
        for r in rows:
            print(f"{r['id']:<4} | {r['name']:<12} | {r['email']:<25} | {r['preference'][:28]:<30}")

        cursor.execute("SELECT COUNT(*) FROM secret_santa_assignments")
        assign_count = cursor.fetchone()[0]
        print(f"\n[+] Total Secret Santa Assignments in cycle: {assign_count} / {len(rows)}")
        print("[+] Universal Default Password for seeded students: HorrorSanta#2026")
        print("=" * 60)

if __name__ == "__main__":
    main()
