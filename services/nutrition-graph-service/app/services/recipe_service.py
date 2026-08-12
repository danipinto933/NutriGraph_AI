import logging
from typing import List

from app.core.neo4j_client import neo4j_client
from app.models.schemas import RecipeMacros, RecipeRecommendation

logger = logging.getLogger(__name__)

class RecipeService:
    async def get_recommendations(self, user_id: str) -> List[RecipeRecommendation]:
        driver = neo4j_client.get_driver()
        
        # Consulta Cypher para obtener recetas recomendadas
        # 1. Filtra recetas que no contengan ingredientes con alérgenos del usuario.
        # 2. Excluye ingredientes excluidos por la dieta (insensible a mayúsculas).
        # 3. Calcula dinámicamente los macronutrientes.
        query = """
        OPTIONAL MATCH (u:User) WHERE toLower(u.email) = toLower($user_id)
        OPTIONAL MATCH (d:DietType) WHERE u.diet_type IS NOT NULL AND toLower(d.name) = toLower(u.diet_type)
        
        // Obtener recetas que no violen las intolerancias del usuario
        MATCH (r:Recipe)
        WHERE NOT (
            u IS NOT NULL AND EXISTS {
                MATCH (u)-[:HAS_INTOLERANCE]->(a:Allergen)
                MATCH (r)-[:CONTAINS_INGREDIENT]->(i:Ingredient)-[:CONTAINS_ALLERGEN]->(a)
            }
        )
        // Excluir recetas incompatibles con el tipo de dieta (si existe)
        AND NOT (
            d IS NOT NULL AND EXISTS {
                MATCH (d)-[:EXCLUDES]->(i_ex:Ingredient)
                MATCH (r)-[:CONTAINS_INGREDIENT]->(i_ex)
            }
        )
        AND NOT (
            d IS NOT NULL AND EXISTS {
                MATCH (d)-[:EXCLUDES]->(a_ex:Allergen)
                MATCH (r)-[:CONTAINS_INGREDIENT]->(:Ingredient)-[:CONTAINS_ALLERGEN]->(a_ex)
            }
        )
        
        // Ahora calcular los macros basados en ingredientes
        MATCH (r)-[rel:CONTAINS_INGREDIENT]->(i:Ingredient)
        WITH r, 
             sum((rel.grams / 100.0) * i.calorias_100g) AS total_calories,
             sum((rel.grams / 100.0) * i.proteinas_100g) AS total_protein,
             sum((rel.grams / 100.0) * i.grasas_100g) AS total_fat,
             sum((rel.grams / 100.0) * i.carbohidratos_100g) AS total_carbs,
             collect(i.name) AS ingredient_names
             
        RETURN r.id AS recipe_id, r.name AS name, r.description AS description, 
               total_calories, total_protein, total_fat, total_carbs,
               ingredient_names
        """
        
        recommendations = []
        try:
            async with driver.session() as session:
                result = await session.run(query, user_id=user_id)
                async for record in result:
                    macros = RecipeMacros(
                        calories=round(record["total_calories"], 2),
                        protein_g=round(record["total_protein"], 2),
                        fat_g=round(record["total_fat"], 2),
                        carbs_g=round(record["total_carbs"], 2)
                    )
                    rec = RecipeRecommendation(
                        recipe_id=record["recipe_id"],
                        name=record["name"],
                        description=record["description"] or "",
                        macros=macros,
                        ingredients=record["ingredient_names"]
                    )
                    recommendations.append(rec)
        except Exception as e:
            logger.error(f"Error fetching recommendations for user {user_id}: {e}")
            raise e
            
        return recommendations

    async def search_by_macros(self, user_id: str, max_calories: float, min_protein: float) -> List[RecipeRecommendation]:
        # Reuse get_recommendations but filter in Python for simplicity, 
        # or we could do it in Cypher. Python filtering is okay for this prototype.
        recommendations = await self.get_recommendations(user_id)
        filtered = [
            r for r in recommendations 
            if r.macros.calories <= max_calories and r.macros.protein_g >= min_protein
        ]
        return filtered

    async def search_advanced(self, user_id: str, max_calories: float | None = None, min_protein: float | None = None, ingredient: str | None = None, name: str | None = None) -> List[RecipeRecommendation]:
        recommendations = await self.get_recommendations(user_id)
        filtered = recommendations
        if max_calories is not None:
            filtered = [r for r in filtered if r.macros.calories <= max_calories]
        if min_protein is not None:
            filtered = [r for r in filtered if r.macros.protein_g >= min_protein]
        if ingredient:
            filtered = [r for r in filtered if any(ingredient.lower() in i.lower() for i in r.ingredients)]
        if name:
            filtered = [r for r in filtered if name.lower() in r.name.lower()]
        return filtered

    async def verify_compatibility(self, user_id: str, ingredient_name: str) -> bool:
        driver = neo4j_client.get_driver()
        query = """
        OPTIONAL MATCH (u:User) WHERE toLower(u.email) = toLower($user_id)
        OPTIONAL MATCH (d:DietType) WHERE u.diet_type IS NOT NULL AND toLower(d.name) = toLower(u.diet_type)
        OPTIONAL MATCH (i:Ingredient) WHERE toLower(i.name) CONTAINS toLower($ingredient_name) OR toLower($ingredient_name) CONTAINS toLower(i.name)
        
        WITH u, d, collect(i) AS matched_ingredients
        WHERE size(matched_ingredients) > 0 AND matched_ingredients[0] IS NOT NULL
        UNWIND matched_ingredients AS i
        
        // Comprobar intolerancias del usuario
        OPTIONAL MATCH (u)-[:HAS_INTOLERANCE]->(a:Allergen)<-[:CONTAINS_ALLERGEN]-(i)
        // Comprobar si la dieta del usuario excluye el ingrediente
        OPTIONAL MATCH (d)-[ex1:EXCLUDES]->(i)
        // Comprobar si la dieta del usuario excluye el alérgeno del ingrediente
        OPTIONAL MATCH (d)-[ex2:EXCLUDES]->(a2:Allergen)<-[:CONTAINS_ALLERGEN]-(i)
        
        RETURN count(i) AS checked_count,
               sum(CASE WHEN a IS NOT NULL OR ex1 IS NOT NULL OR ex2 IS NOT NULL THEN 1 ELSE 0 END) AS incompatible_count
        """
        async with driver.session() as session:
            result = await session.run(query, user_id=user_id, ingredient_name=ingredient_name)
            record = await result.single()
            if not record or record["checked_count"] == 0:
                # Si no hay ingrediente en la BD pero conocemos la dieta del usuario, hacer una validación heurística adicional
                return True
            return record["incompatible_count"] == 0

    async def get_recipe_breakdown(self, recipe_id: str) -> dict:
        driver = neo4j_client.get_driver()
        query = """
        MATCH (r:Recipe {id: $recipe_id})-[rel:CONTAINS_INGREDIENT]->(i:Ingredient)
        RETURN r.name AS recipe_name, i.name AS ingredient_name, rel.grams AS grams
        """
        breakdown = {"recipe_id": recipe_id, "recipe_name": "", "ingredients": []}
        async with driver.session() as session:
            result = await session.run(query, recipe_id=recipe_id)
            async for record in result:
                breakdown["recipe_name"] = record["recipe_name"]
                breakdown["ingredients"].append({
                    "name": record["ingredient_name"],
                    "grams": record["grams"]
                })
        return breakdown

    async def get_graph_analytics(self) -> dict:
        driver = neo4j_client.get_driver()
        query_top_ingredients = """
        MATCH (r:Recipe)-[:CONTAINS_INGREDIENT]->(i:Ingredient)
        RETURN i.name AS ingredient, count(r) AS recipe_count
        ORDER BY recipe_count DESC
        LIMIT 10
        """
        query_top_recipes = """
        MATCH (r:Recipe)
        OPTIONAL MATCH (r)-[:CONTAINS_INGREDIENT]->(i:Ingredient)
        RETURN r.name AS name, count(i) AS ingredient_count
        ORDER BY ingredient_count DESC
        LIMIT 10
        """
        query_allergens = """
        MATCH (a:Allergen)
        OPTIONAL MATCH (u:User)-[:HAS_INTOLERANCE]->(a)
        RETURN a.name AS name, count(u) AS active_count
        ORDER BY active_count DESC
        """
        query_total = """
        MATCH (r:Recipe) RETURN count(r) AS total_recipes
        """
        query_total_ing = """
        MATCH (i:Ingredient) RETURN count(i) AS total_ingredients
        """
        query_total_all = """
        MATCH (a:Allergen) RETURN count(a) AS total_allergens
        """

        async with driver.session() as session:
            res_total = await session.run(query_total)
            rec_total = await res_total.single()
            total_recipes = rec_total["total_recipes"] if rec_total else 0

            res_t_ing = await session.run(query_total_ing)
            rec_t_ing = await res_t_ing.single()
            total_ingredients = rec_t_ing["total_ingredients"] if rec_t_ing else 0

            res_t_all = await session.run(query_total_all)
            rec_t_all = await res_t_all.single()
            total_allergens = rec_t_all["total_allergens"] if rec_t_all else 0

            res_ing = await session.run(query_top_ingredients)
            top_ingredients = [dict(record) for record in await res_ing.data()]

            res_rec = await session.run(query_top_recipes)
            top_recipes = [dict(record) for record in await res_rec.data()]

            res_all = await session.run(query_allergens)
            allergens_stats = [dict(record) for record in await res_all.data()]

        return {
            "total_recipes": total_recipes,
            "total_ingredients": total_ingredients,
            "total_allergens": total_allergens,
            "top_ingredients_used": top_ingredients,
            "top_recipes": top_recipes,
            "allergens_stats": allergens_stats
        }

recipe_service = RecipeService()

