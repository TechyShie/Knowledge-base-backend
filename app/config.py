# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# app directory (this file lives in app/)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# project root (one level up from app/)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# ensure the instance folder exists at project root/instance
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# default absolute sqlite path (guaranteed)
default_sqlite_path = os.path.join(INSTANCE_DIR, "knowledge.db")
default_sqlite_url = f"sqlite:///{default_sqlite_path}"

# read DATABASE_URL from env if provided; otherwise use absolute default
DATABASE_URL = os.environ.get("DATABASE_URL", default_sqlite_url)

# If DATABASE_URL is a relative sqlite URL like "sqlite:///instance/knowledge.db",
# convert it to an absolute path to avoid nested-instance problems.
if DATABASE_URL.startswith("sqlite:///"):
    # path part after scheme
    path_part = DATABASE_URL[len("sqlite:///"):]
    # If path_part is not absolute, make it absolute relative to project root
    if not os.path.isabs(path_part):
        abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, path_part))
        # Normalize to forward slashes for SQLAlchemy URL
        DATABASE_URL = "sqlite:///" + abs_path.replace("\\", "/")

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
