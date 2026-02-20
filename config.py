import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Neon PostgreSQL (cloud — syncs across all devices)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_u6LWVnjJQ2vc@ep-super-resonance-a1k2ct3w-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    )

    # Local SQLite fallback (uncomment below & comment above to use locally)
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instances", "cloudroom.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, "instances", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
