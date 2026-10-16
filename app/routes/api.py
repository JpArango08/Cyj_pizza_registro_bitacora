from flask import Blueprint, jsonify, request, render_template

from app.repositories.supabase_repository import (
    create_manual_measurement,
    get_measurements,
    get_parameters,
)
from app.services.evaluation import evaluate_measurement


api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.get("/")
def home():
    return render_template("index.html")

@api_bp.get("/health")
def health():
    """Confirma que Flask está respondiendo."""
    return jsonify({
        "status": "ok",
        "service": "bitacora_cloro_ph",
    }), 200


@api_bp.get("/parameters")
def parameters():
    """Devuelve los parámetros configurados en Supabase."""
    try:
        return jsonify({"parameters": get_parameters()}), 200
    except Exception:
        return jsonify({
            "error": "No fue posible consultar los parámetros en Supabase."
        }), 502


@api_bp.get("/measurements")
def measurements():
    """Devuelve una página del historial de mediciones."""
    page_text = request.args.get("page", "1")

    try:
        page = int(page_text)
        result = get_measurements(page=page)
        return jsonify(result), 200
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({
            "error": "No fue posible consultar el historial en Supabase."
        }), 502


@api_bp.post("/measurements")
def create_measurement():
    """Valida y registra una medición manual."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Envía un objeto JSON con los valores de la medición."
        }), 400

    try:
        parameters_data = get_parameters()
        evaluated = evaluate_measurement(data, parameters_data)

        if (
            evaluated["chlorine_value"] is None
            and evaluated["ph_value"] is None
        ):
            return jsonify({
                "error": "Ingresa al menos un valor de cloro o pH."
            }), 400

        saved = create_manual_measurement(evaluated)

        return jsonify({
            "message": "Medición guardada correctamente.",
            "measurement": saved,
        }), 201

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({
            "error": "No fue posible guardar la medición en Supabase."
        }), 502
