# import_clubs_chapters.py (robust version)
import csv
import os
from app import create_app
from models import db, Club, StudentChapter

# If your CSV files are elsewhere, set absolute paths here:
CLUBS_CSV = os.path.join(os.getcwd(), "data of vnr clubs.csv")
CHAPTERS_CSV = os.path.join(os.getcwd(), "data of vnr student clubs.csv")

app = create_app()

def normalize_key(k):
    if k is None:
        return ""
    return k.strip().lower()

def get_val_from_row(row_norm, keys):
    """
    Given a normalized-row dict (keys already normalized),
    try each candidate key (normalized) and return the first non-empty value.
    """
    for k in keys:
        kn = normalize_key(k)
        if kn in row_norm and row_norm[kn] is not None and str(row_norm[kn]).strip() != "":
            return str(row_norm[kn]).strip()
    return ""

with app.app_context():
    db.create_all()
    print("Using DB:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    # ---------- Clubs ----------
    if os.path.exists(CLUBS_CSV):
        with open(CLUBS_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # print detected headers for debugging
            detected_headers = reader.fieldnames
            print("Clubs CSV headers detected:", detected_headers)

            # show first 3 rows for debugging
            sample = []
            for i, r in enumerate(reader):
                if i < 3:
                    sample.append(r)
                else:
                    break

            if sample:
                print("Sample rows (first 3):")
                for s in sample:
                    print(s)
            # rewind file to start: reopen
        # Re-open to actually iterate (because we consumed some rows)
        with open(CLUBS_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            added = 0
            for row in reader:
                # build normalized row dict
                row_norm = {normalize_key(k): (v or "").strip() for k, v in row.items()}

                # possible header names (exact ones you provided plus common variants)
                name = get_val_from_row(row_norm, ['club name', 'club', 'name', 'clubs names', 'clubs names '])
                description = get_val_from_row(row_norm, ['description', 'desc'])
                instagram = get_val_from_row(row_norm, ['instagram link', 'instagram', 'insta'])
                youtube = get_val_from_row(row_norm, ['youtube link', 'youtube', 'yt'])

                if not name:
                    continue

                # skip duplicates
                if Club.query.filter_by(name=name).first():
                    continue

                # combine socials
                social_list = []
                if instagram:
                    social_list.append(f"Instagram: {instagram}")
                if youtube:
                    social_list.append(f"Youtube: {youtube}")
                contact_info = " | ".join(social_list) if social_list else None

                club = Club(
                    name=name,
                    description=description or None,
                    contact=contact_info
                )
                db.session.add(club)
                added += 1
            db.session.commit()
            print(f"✅ Clubs imported successfully: {added}")
    else:
        print(f"⚠️ Clubs CSV not found at: {CLUBS_CSV}")

    # ---------- Student Chapters ----------
    if os.path.exists(CHAPTERS_CSV):
        with open(CHAPTERS_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            print("Chapters CSV headers detected:", reader.fieldnames)

            sample = []
            for i, r in enumerate(reader):
                if i < 3:
                    sample.append(r)
                else:
                    break
            if sample:
                print("Sample rows (first 3):")
                for s in sample:
                    print(s)
        with open(CHAPTERS_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            added = 0
            for row in reader:
                row_norm = {normalize_key(k): (v or "").strip() for k, v in row.items()}

                name = get_val_from_row(row_norm, ['proffesional student chapters', 'professional student chapters', 'chapter', 'name'])
                description = get_val_from_row(row_norm, ['description', 'desc'])
                instagram = get_val_from_row(row_norm, ['instagram', 'instagram link', 'insta'])

                if not name:
                    continue

                if StudentChapter.query.filter_by(name=name).first():
                    continue

                chapter = StudentChapter(
                    name=name,
                    description=description or None,
                    contact=instagram or None
                )
                db.session.add(chapter)
                added += 1
            db.session.commit()
            print(f"✅ Student chapters imported successfully: {added}")
    else:
        print(f"⚠️ Chapters CSV not found at: {CHAPTERS_CSV}")
