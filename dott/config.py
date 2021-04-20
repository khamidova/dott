import os

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_SOCKET_DIR = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

if DB_HOST:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
else:
    DB_HOST = f"{DB_SOCKET_DIR}/{CLOUD_SQL_CONNECTION_NAME}"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={DB_HOST}"

#SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:1234/dott"

IMPORT_CSV_FILES_LOCATION = "/home/okhamidova/Desktop/dott/"
RIDES_FOLDER = "rides"
DEPLOYMENTS_FOLDER = "deployments"
PICKUPS_FOLDER = "pickups"
