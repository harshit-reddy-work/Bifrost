# create_db.py
import importlib, sys
from models import db
from flask import Flask

MODULE_NAME = "main"   # change to the module filename without .py if different

try:
    m = importlib.import_module(MODULE_NAME)
except Exception as e:
    print(f"Failed to import module '{MODULE_NAME}': {e}")
    sys.exit(1)

# find Flask instance in module
flask_app = None
for name in dir(m):
    try:
        obj = getattr(m, name)
    except Exception:
        continue
    if isinstance(obj, Flask):
        flask_app = obj
        flask_name = name
        break

# If factory function create_app exists, call it
if not flask_app and hasattr(m, "create_app"):
    try:
        flask_app = m.create_app()
        flask_name = "create_app()"
    except Exception as e:
        print("Module has create_app but calling it failed:", e)

if not flask_app:
    print(f"No Flask instance found in module '{MODULE_NAME}'.")
    print("Open your main.py and ensure you create a Flask instance (e.g. app = Flask(__name__)) or provide a create_app() factory.")
    sys.exit(1)

print(f"Found Flask instance '{flask_name}' in module '{MODULE_NAME}'. Creating tables...")
with flask_app.app_context():
    db.create_all()
    print("Database tables created/updated successfully.")
