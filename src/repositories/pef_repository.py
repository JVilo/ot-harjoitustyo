from entities.pef import Pef
from repositories.user_repository import user_repository
from config import PEF_FILE_PATH

class PefRepository:

    def __init__(self, file_path):
        self._file_path = file_path

    def find_all(self):
        return self._read()

    def find_by_user(self, user):
        pefs = self.find_all()
        for pef in pefs:
            if pef.user.id == user.id:
                return pef
        return None

    def create(self, pef):
        pefs = self.find_all()
        pefs.append(pef)
        self._write(pefs)
        return pef

    def count_reference(self, height, age, gender):

        if gender == "male":
            # Adult Men PEF calculation
            height_in_m = height / 100  # Convert cm to meters
            reference_pef = (((height_in_m * 5.48) + 1.58) - (age * 0.041)) * 60
        elif gender == "female":
            # Adult Women PEF calculation
            height_in_m = height / 100  # Convert cm to meters
            reference_pef = (((height_in_m * 3.72) + 2.24) - (age * 0.03)) * 60
        else:
            # Children PEF calculation
            reference_pef = ((height - 100) * 5) + 100

        return reference_pef

    def _read(self):

        pefs = []
        with open(self._file_path, encoding="utf-8") as file:
            for row in file:
                row = row.strip()  # Remove newlines
                parts = row.split(";")

                pef_id = int(parts[0])
                value = float(parts[1])
                user_id = int(parts[2])

                # Assuming that the user repository can find a user by ID
                user = user_repository.find_by_id(user_id) if user_id else None

                pefs.append(Pef(pef_id=pef_id, user=user, value=value))

        return pefs

    def _write(self, pefs):
        """Writes the PEF records to the file."""
        with open(self._file_path, "w", encoding="utf-8") as file:
            for pef in pefs:
                user_id = pef.user.id if pef.user else ""
                file.write(f"{pef.id};{pef.value};{user_id}\n")


# Initialize the repository
pef_repository = PefRepository(PEF_FILE_PATH)
