
from functools import lru_cache

from supabase import create_client

from config import Config


@lru_cache(maxsize=1)
def get_client():
    """Crea y reutiliza el cliente de Supabase."""
    Config.validate()
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


def get_parameters():
    """Consulta los parámetros configurados para cloro y pH."""
    response = (
        get_client()
        .table("measurement_parameters")
        .select(
            "parameter_key, unit, evaluation_min, evaluation_max, "
            "simulation_min, simulation_max, updated_at"
        )
        .order("parameter_key")
        .execute()
    )

    parameters = {
        item["parameter_key"]: item
        for item in (response.data or [])
    }

    required = {"chlorine", "ph"}
    if not required.issubset(parameters):
        raise RuntimeError(
            "Faltan parámetros de cloro o pH en Supabase."
        )

    return parameters


def get_measurements(page=1, page_size=None):
    """Obtiene el historial más reciente con paginación."""
    if page_size is None:
        page_size = Config.PAGE_SIZE

    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise ValueError("La página debe ser un entero mayor que cero.")

    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or page_size < 1
        or page_size > 100
    ):
        raise ValueError("El tamaño de página debe estar entre 1 y 100.")

    offset = (page - 1) * page_size

    response = (
        get_client()
        .table("measurements")
        .select("*")
        .order("measured_at", desc=True)
        .order("id", desc=True)
        .range(offset, offset + page_size)
        .execute()
    )

    # Se solicita un registro adicional para saber si hay otra página.
    rows = response.data or []

    return {
        "items": rows[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(rows) > page_size,
    }


def create_manual_measurement(measurement):
    """Guarda una medición manual y devuelve el registro creado."""
    if not isinstance(measurement, dict):
        raise ValueError("Los datos de la medición no son válidos.")

    payload = dict(measurement)

    # El cliente solo puede crear registros manuales mediante esta función.
    payload["record_type"] = "manual"
    payload.pop("automation_date", None)

    response = (
        get_client()
        .table("measurements")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Supabase no devolvió la medición creada.")

    return response.data[0]
