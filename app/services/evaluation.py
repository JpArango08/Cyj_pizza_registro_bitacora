
from decimal import Decimal, InvalidOperation


VALID_PARAMETER_STATUSES = {
    "BAJO",
    "DENTRO DEL RANGO",
    "ALTO",
    "INVÁLIDO",
    "SIN DATOS",
}


def parse_measurement(value, field_name):
    """Convierte una entrada en Decimal; los campos vacíos son datos ausentes."""
    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError(f"El valor de {field_name} no es válido.")

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        # Acepta coma decimal en entradas como 0,5.
        value = value.replace(",", ".")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"El valor de {field_name} debe ser numérico."
        ) from None

    if not number.is_finite():
        raise ValueError(
            f"El valor de {field_name} debe ser un número finito."
        )

    if number < 0:
        raise ValueError(
            f"El valor de {field_name} no puede ser negativo."
        )

    return number


def evaluate_parameter(value, minimum, maximum):
    """Evalúa un valor frente a sus límites inclusivos."""
    if value is None:
        return "SIN DATOS"

    value = Decimal(str(value))
    minimum = Decimal(str(minimum))
    maximum = Decimal(str(maximum))

    if not value.is_finite():
        return "INVÁLIDO"

    if minimum > maximum:
        raise ValueError("El límite mínimo no puede superar al máximo.")

    if value < minimum:
        return "BAJO"

    if value > maximum:
        return "ALTO"

    return "DENTRO DEL RANGO"


def evaluate_overall(chlorine_status, ph_status):
    """Determina el cumplimiento conjunto de cloro y pH."""
    statuses = {chlorine_status, ph_status}

    if "INVÁLIDO" in statuses:
        return "INVÁLIDO"

    if "SIN DATOS" in statuses:
        return "SIN DATOS"

    if (
        chlorine_status == "DENTRO DEL RANGO"
        and ph_status == "DENTRO DEL RANGO"
    ):
        return "CUMPLE"

    return "NO CUMPLE"


def evaluate_measurement(data, parameters):
    """Valida y evalúa una medición manual usando los parámetros actuales."""
    if not isinstance(data, dict):
        raise ValueError("Los datos de la medición deben ser un objeto.")

    chlorine = parse_measurement(
        data.get("chlorine_value"),
        "cloro residual libre",
    )
    ph = parse_measurement(
        data.get("ph_value"),
        "pH",
    )

    chlorine_parameters = parameters.get("chlorine")
    ph_parameters = parameters.get("ph")

    if not chlorine_parameters or not ph_parameters:
        raise RuntimeError("No están configurados los parámetros de cloro y pH.")

    chlorine_status = evaluate_parameter(
        chlorine,
        chlorine_parameters["evaluation_min"],
        chlorine_parameters["evaluation_max"],
    )
    ph_status = evaluate_parameter(
        ph,
        ph_parameters["evaluation_min"],
        ph_parameters["evaluation_max"],
    )

    overall_status = evaluate_overall(chlorine_status, ph_status)

    return {
        "chlorine_value": (
            float(chlorine) if chlorine is not None else None
        ),
        "chlorine_status": chlorine_status,
        "ph_value": float(ph) if ph is not None else None,
        "ph_status": ph_status,
        "overall_status": overall_status,
        "record_type": "manual",
    }
