from pathlib import Path
from entities.pef import Pef
from repositories.user_repository import user_repository
from config import PEF_FILE_PATH


class PefRepository:
    """Repository for managing PEF references stored in a file."""

    def __init__(self, file_path):
        """Initializes the repository with the file path.

        Args:
            file_path: Path to the file storing PEF references.
        """
        self._file_path = file_path

    def find_all(self):
        """Retrieves all PEF references from the file.

        Returns:
            List of Pef objects.
        """
        return self._read()

    def find_by_user(self, user):
        """Finds all PEF references associated with a specific user.

        Args:
            user: The User object to filter references.

        Returns:
            List of Pef objects for the user.
        """
        pefs = self.find_all()
        user_pefs = filter(
            lambda pef: pef.user and pef.user.username == user.username, pefs)
        return list(user_pefs)

    def create(self, reference_pef):
        """Saves a new reference PEF for a user.

        Args:
            reference_pef: The Pef object to save.

        Returns:
            The list of Pef objects after addition.
        """
        pefs = self.find_all()
        pefs.append(reference_pef)
        self._write(pefs)
        return pefs

    def get_latest_for_user(self, username):
        """Retrieves the latest PEF references for a username.

        Args:
            username: The username to filter references.

        Returns:
            List of Pef objects for the user.
        """
        all_pefs = self.find_all()
        return [pef for pef in all_pefs if pef.user and pef.user.username == username]

    def _ensure_file_exists(self):
        """Ensures the reference file exists, creating directories and file if necessary."""
        directory = Path(self._file_path).parent
        directory.mkdir(parents=True, exist_ok=True)
        Path(self._file_path).touch(exist_ok=True)

    def _read(self):
        """Reads PEF references from the file.

        Returns:
            List of Pef objects.
        """
        pefs = []
        self._ensure_file_exists()
        with open(self._file_path, encoding="utf-8") as file:
            for row in file:
                row = row.strip()
                if not row:
                    continue
                parts = row.split(";")
                pef_id = parts[0]
                value = float(parts[1])
                username = parts[2]
                user = user_repository.find_by_username(
                    username) if username else None
                pefs.append(Pef(value=value, user=user, pef_id=pef_id))
        return pefs

    def _write(self, pefs):
        """Writes the list of Pef objects to the file.

        Args:
            pefs: List of Pef objects to write.
        """
        self._ensure_file_exists()
        with open(self._file_path, "w", encoding="utf-8") as file:
            for pef in pefs:
                username_str = pef.user.username if pef.user else ''
                row = f"{pef.pef_id};{pef.value};{username_str}"
                file.write(row + "\n")


pef_repository = PefRepository(PEF_FILE_PATH)
