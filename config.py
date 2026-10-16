
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Carga las variables desde el archivo .env ubicado en la raíz del proyecto.
load_dotenv(BASE_DIR / ".env")


class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    TIMEZONE = "America/Bogota"
    PAGE_SIZE = 10

    @classmethod
    def validate(cls):
        missing = []

        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")

        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")

        if missing:
            names = ", ".join(missing)
            raise RuntimeError(
                f"Faltan variables en el archivo .env: {names}"
            )
