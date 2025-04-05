from pathlib import Path
from entities.pef import Pef
from repositories.user_repository import user_repository
from config import PEF_FILE_PATH


class PefRepository:
    """Repository class for managing PEF references."""

    def __init__(self, file_path):
        """Constructor for the PefRepository class.

        Args:
            file_path: Path to the file where the PEF references are saved.
        """
        self._file_path = file_path

    def find_all(self):
        """Returns all PEF references.

        Returns:
            List of Pef objects.
        """
        return self._read()

    def find_by_user(self, user):
        """Returns the PEF reference for a specific user.

        Args:
            user: The user whose PEF reference is being fetched.

        Returns:
            List of Pef objects belonging to the user.
        """
        pefs = self.find_all()
        user_pefs = filter(
            lambda pef: pef.user and pef.user.username == user.username, pefs)
        return list(user_pefs)

    def create(self, reference_pef):
        """Saves the reference PEF value for a user in the repository.

        Args:
            user_id: The ID of the user to save the reference PEF for.
            reference_pef: The reference PEF value to store.

        Returns:
            The saved PEF record.
        """
        # Create a new PEF entry
        new_referenc = self.find_all()
        # Append the new PEF record to the list of existing records
        new_referenc.append(reference_pef)

        # Write the updated data back to the file
        self._write(new_referenc)

        return new_referenc

    def get_latest_for_user(self, username):
        ref = self.find_all()

        # Adjust based on your actual repository code
        return [pef for pef in ref if pef.user and pef.user.username == username]

    def _ensure_file_exists(self):
        """Ensures the file exists."""
        # Make sure the directory exists
        directory = Path(self._file_path).parent
        # Create the directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)

        # Create the file if it doesn't exist
        Path(self._file_path).touch()

    def _read(self):
        """Reads the PEF references from the file.

        Returns:
            List of Pef objects.
        """
        pefs = []
        self._ensure_file_exists()

        with open(self._file_path, encoding="utf-8") as file:
            for row in file:
                row = row.strip()
                parts = row.split(";")
                pef_id = parts[0]
                value = float(parts[1])
                username = parts[2]
                user = user_repository.find_by_username(
                    username) if username else None
                pefs.append(Pef(value=value, user=user, pef_id=pef_id))

        return pefs

    def _write(self, pefs):
        """Writes the PEF references to the file.

        Args:
            pefs: The list of Pef objects to be saved.
        """
        self._ensure_file_exists()

        with open(self._file_path, "w", encoding="utf-8") as file:
            for pef in pefs:
                row = f"{pef.pef_id};{pef.value};{pef.user.username if pef.user else ''}"
                file.write(row + "\n")


pef_repository = PefRepository(PEF_FILE_PATH)
