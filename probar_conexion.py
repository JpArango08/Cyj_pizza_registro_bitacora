
import os
import sys

from dotenv import load_dotenv
from supabase import create_client


def main() -> int:
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print(
            "ERROR: faltan SUPABASE_URL o SUPABASE_KEY "
            "en el archivo .env."
        )
        return 1

    try:
        supabase = create_client(url, key)

        # Consultamos parámetros sin modificar la base de datos.
        params = (
            supabase.table("measurement_parameters")
            .select(
                "parameter_key, unit, evaluation_min, "
                "evaluation_max, simulation_min, simulation_max"
            )
            .order("parameter_key")
            .execute()
        )

        # Consultamos únicamente el primer registro, si existe.
        measurements = (
            supabase.table("measurements")
            .select("id, measured_at, record_type")
            .order("measured_at", desc=True)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        print("CONEXIÓN CORRECTA")
        print(f"Parámetros encontrados: {len(params.data)}")
        print(
            "Última medición: "
            + (
                "existe al menos una"
                if measurements.data
                else "todavía no hay mediciones"
            )
        )

        for parameter in params.data:
            print(
                f"{parameter['parameter_key']}: "
                f"{parameter['evaluation_min']} - "
                f"{parameter['evaluation_max']} "
                f"{parameter['unit']}"
            )

        return 0

    except Exception as exc:
        # No imprimimos la clave ni la configuración completa.
        print(f"ERROR DE CONEXIÓN O PERMISOS: {type(exc).__name__}")
        print(
            "Comprueba la URL, la clave publicable, "
            "las políticas RLS y la conexión a Internet."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
