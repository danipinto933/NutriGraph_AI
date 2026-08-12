import logging
from typing import Any

import httpx
from app.core.client import http_client
from app.core.config import settings
from langchain_core.tools import StructuredTool
from nutrigraph_common.exceptions.base import InfrastructureException
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

async def _fetch(url: str, user_id: str = None, params: dict = None) -> Any:
    """Realiza una petición GET con reintentos automáticos pasando identidades en cabeceras seguras."""
    headers = {}
    if user_id:
        headers["X-User-Email"] = user_id

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(InfrastructureException),
        reraise=True,
    ):
        with attempt:
            try:
                response = await http_client.get(url, params=params, headers=headers)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                text = response.text.strip()
                if "application/json" not in content_type and not (text.startswith("{") or text.startswith("[")):
                    logger.error(f"Se recibió HTML/texto plano en lugar de JSON desde {url}: {text[:200]}")
                    raise InfrastructureException(
                        message=f"La URL del servicio de nutrición ({url}) devolvió HTML/index.html en lugar de JSON. "
                                f"Revisa en Render que la variable NUTRITION_GRAPH_SERVICE_URL apunte al servicio backend de nutrición y no al frontend.",
                        details={"url": url, "snippet": text[:200]}
                    )
                return response.json()
            except json.JSONDecodeError as exc:
                logger.error("JSONDecodeError al parsear respuesta de %s: %s", url, response.text[:200])
                raise InfrastructureException(
                    message=f"Respuesta inválida (no es JSON) desde {url}. Verifica NUTRITION_GRAPH_SERVICE_URL en Render.",
                    details={"url": url, "snippet": response.text[:200]},
                ) from exc
            except httpx.HTTPStatusError as exc:
                logger.error("Error calling %s: %s", url, exc.response.text)
                raise InfrastructureException(
                    message=f"Error from nutrition service: {exc.response.text}",
                    details={"url": url, "status": exc.response.status_code},
                ) from exc
            except Exception as exc:
                logger.error("Connection error to %s: %s", url, exc)
                raise InfrastructureException(
                    message=f"Connection error: {exc}",
                    details={"url": url},
                ) from exc


def _get_base_url() -> str:
    base = settings.NUTRITION_GRAPH_SERVICE_URL.rstrip('/')
    if not base.endswith('/api/v1'):
        base = f"{base}/api/v1"
    return base

async def _buscar_receta_por_macros(user_id: str, max_calories: float, min_protein: float) -> str:
    """Busca recetas recomendadas para un usuario que cumplan con requisitos de calorías máximas y proteína mínima. Devuelve las recetas y sus macros."""
    url = f"{_get_base_url()}/recipes/search"
    params = {
        "max_calories": max_calories,
        "min_protein": min_protein,
    }
    try:
        result = await _fetch(url, user_id=user_id, params=params)
    except InfrastructureException as e:
        return f"Error al consultar recetas: {e.message}"

    if not result:
        return "No se encontraron recetas que cumplan con esos criterios y tus restricciones dietéticas."

    formatted = "Recetas encontradas:\n"
    for r in result:
        formatted += (
            f"- ID: {r['recipe_id']}, Nombre: {r['name']}, "
            f"Calorías: {r['macros']['calories']}, Proteína: {r['macros']['protein_g']}g\n"
        )
    return formatted


async def _buscar_recetas_avanzado(
    user_id: str, 
    max_calories: float = None, 
    min_protein: float = None, 
    ingrediente: str = None, 
    nombre_receta: str = None
) -> str:
    """
    Busca recetas para un usuario aplicando filtros opcionales. 
    Puedes filtrar por máximo de calorías, mínimo de proteína, contener un ingrediente específico o por el nombre de la receta.
    Devuelve las recetas (ID, nombre, macros, ingredientes).
    """
    url = f"{_get_base_url()}/recipes/search_advanced"
    params = {}
    if max_calories is not None:
        params["max_calories"] = max_calories
    if min_protein is not None:
        params["min_protein"] = min_protein
    if ingrediente:
        params["ingredient"] = ingrediente
    if nombre_receta:
        params["name"] = nombre_receta
        
    try:
        result = await _fetch(url, user_id=user_id, params=params)
    except InfrastructureException as e:
        return f"Error al consultar recetas: {e.message}"

    if not result:
        return "No se encontraron recetas que cumplan con esos criterios y tus restricciones dietéticas."

    formatted = "Recetas encontradas:\n"
    for r in result:
        ingredients_str = ", ".join(r.get('ingredients', []))
        formatted += (
            f"- ID: {r['recipe_id']}, Nombre: {r['name']}, "
            f"Calorías: {r['macros']['calories']}, Proteína: {r['macros']['protein_g']}g, "
            f"Ingredientes principales: {ingredients_str}\n"
        )
    return formatted

async def _verificar_compatibilidad_alimento(user_id: str, ingredient_name: str) -> str:
    """Verifica si un ingrediente específico es compatible con el usuario (revisa alergias y tipo de dieta en la base de datos)."""
    url = f"{_get_base_url()}/recipes/verify"
    params = {
        "ingredient_name": ingredient_name,
    }
    try:
        result = await _fetch(url, user_id=user_id, params=params)
    except InfrastructureException as e:
        return f"Error al verificar compatibilidad: {e.message}"

    is_compatible = result.get("compatible", False)
    if is_compatible:
        return f"El ingrediente '{ingredient_name}' es SEGURO y compatible para tu perfil."
    else:
        return (
            f"ALERTA: El ingrediente '{ingredient_name}' NO ES COMPATIBLE "
            f"(viola alergias o restricciones de tu dieta en la base de datos)."
        )


async def _obtener_desglose_receta(recipe_id: str) -> str:
    """Obtiene los ingredientes y cantidades en gramos de una receta específica dada su ID."""
    url = f"{_get_base_url()}/recipes/{recipe_id}/breakdown"
    try:
        result = await _fetch(url)
    except InfrastructureException as e:
        return f"Error al obtener receta: {e.message}"

    recipe_name = result.get("recipe_name", "Desconocida")
    ingredients = result.get("ingredients", [])

    formatted = f"Receta: {recipe_name}\nIngredientes:\n"
    for item in ingredients:
        formatted += f"- {item['name']}: {item['grams']}g\n"
    return formatted


# --- Registro de herramientas con StructuredTool (compatible con async coroutines) ---

buscar_receta_por_macros = StructuredTool.from_function(
    coroutine=_buscar_receta_por_macros,
    name="buscar_receta_por_macros",
    description=(
        "Busca recetas recomendadas para un usuario que cumplan con requisitos de calorías "
        "máximas y proteína mínima. Devuelve las recetas y sus macros."
    ),
)

buscar_recetas_avanzado = StructuredTool.from_function(
    coroutine=_buscar_recetas_avanzado,
    name="buscar_recetas_avanzado",
    description=(
        "OBLIGATORIO: Busca recetas e ingredientes en la base de datos de grafos de nutrición. "
        "SIEMPRE debes llamar a esta herramienta cuando el usuario pida sugerencias de comida, cena, recetas, "
        "ingredientes o menús. Puedes enviar diet_type='Vegana' si el usuario es o indica ser vegano."
    ),
)

verificar_compatibilidad_alimento = StructuredTool.from_function(
    coroutine=_verificar_compatibilidad_alimento,
    name="verificar_compatibilidad_alimento",
    description=(
        "Verifica si un ingrediente específico es compatible con el usuario "
        "(revisa alergias y tipo de dieta como Vegana)."
    ),
)

obtener_desglose_receta = StructuredTool.from_function(
    coroutine=_obtener_desglose_receta,
    name="obtener_desglose_receta",
    description="Obtiene los ingredientes y cantidades en gramos de una receta específica dada su ID.",
)

# Lista de herramientas disponibles para el agente
tools = [buscar_recetas_avanzado, verificar_compatibilidad_alimento, obtener_desglose_receta]
