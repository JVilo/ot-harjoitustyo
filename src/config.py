import os
from dotenv import load_dotenv

dirname = os.path.dirname(__file__)

try:
    load_dotenv(dotenv_path=os.path.join(dirname, "..", ".env"))
except FileNotFoundError:
    pass

PEF_FILENAME = os.getenv("PEF_FILENAME") or "pef.csv"
PEF_FILE_PATH = os.path.join(dirname, "..", "data", PEF_FILENAME)

DATABASE_FILENAME = os.getenv("DATABASE_FILENAME") or "database.sqlite"
DATABASE_FILE_PATH = os.path.join(dirname, "..", "data", DATABASE_FILENAME)
print(DATABASE_FILE_PATH, "the path in config")