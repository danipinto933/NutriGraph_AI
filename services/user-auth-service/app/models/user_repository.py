import logging
from typing import Any

from app.core.config import settings
from neo4j import AsyncDriver, AsyncGraphDatabase

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        self.driver: AsyncDriver | None = None

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")

    async def close(self):
        if self.driver:
            await self.driver.close()
            logger.info("Closed Neo4j connection")

    async def create_user(self, email: str, hashed_password: str, first_name: str, is_verified: bool = False) -> bool:
        query = """
        CREATE (u:User {
            email: $email, 
            hashed_password: $hashed_password, 
            first_name: $first_name,
            role: 'user',
            is_verified: $is_verified
        })
        RETURN u.email AS email
        """
        async with self.driver.session() as session:
            result = await session.run(query, email=email, hashed_password=hashed_password, first_name=first_name, is_verified=is_verified)
            record = await result.single()
            return record is not None

    async def verify_user_email(self, email: str) -> bool:
        query = """
        MATCH (u:User {email: $email})
        SET u.is_verified = true
        RETURN u.email AS email
        """
        async with self.driver.session() as session:
            result = await session.run(query, email=email)
            record = await result.single()
            return record is not None

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        query = """
        MATCH (u:User {email: $email})
        RETURN u.email AS email, u.hashed_password AS hashed_password, u.first_name AS first_name, u.role AS role, coalesce(u.is_verified, false) AS is_verified
        """
        async with self.driver.session() as session:
            result = await session.run(query, email=email)
            record = await result.single()
            if record:
                return dict(record)
            return None


    async def update_user_biometrics(self, email: str, biometrics: dict[str, Any], intolerances: list[str]) -> bool:
        query_bio = """
        MATCH (u:User {email: $email})
        SET u += $biometrics
        RETURN u.email AS email
        """
        
        query_intolerances = """
        MATCH (u:User {email: $email})
        OPTIONAL MATCH (u)-[r:HAS_INTOLERANCE]->()
        DELETE r
        WITH u
        UNWIND $intolerances AS intl
        MERGE (a:Allergen {name: intl})
        MERGE (u)-[:HAS_INTOLERANCE]->(a)
        """
        
        async with self.driver.session() as session:
            # We must use the current email to find the node, but if biometrics contains a new 'email', 
            # it will be updated by 'SET u += $biometrics'. 
            # Wait, if email is updated in biometrics, the next step (query_intolerances) MUST use the new email!
            # So we should get the email returned by the first query.
            result_bio = await session.run(query_bio, email=email, biometrics=biometrics)
            record = await result_bio.single()
            if not record:
                return False
                
            updated_email = record["email"]
                
            if intolerances is not None:  # Empty list should still clear intolerances
                await session.run(query_intolerances, email=updated_email, intolerances=intolerances)
            return True

    async def get_user_profile(self, email: str) -> dict[str, Any] | None:
        query = """
        MATCH (u:User {email: $email})
        OPTIONAL MATCH (u)-[:HAS_INTOLERANCE]->(i:Allergen)
        RETURN u.email AS email, 
               u.first_name AS first_name,
               u.role AS role,
               u.sex AS sex, 
               u.weight_kg AS weight_kg, 
               u.height_cm AS height_cm, 
               u.age_years AS age_years, 
               u.activity_factor AS activity_factor,
               u.bmi AS bmi,
               u.bmr AS bmr,
               u.tdee AS tdee,
               u.diet_type AS diet_type,
               collect(i.name) AS intolerances
        """
        async with self.driver.session() as session:
            result = await session.run(query, email=email)
            record = await result.single()
            if record:
                return dict(record)
            return None

    async def get_all_users(self) -> list[dict[str, Any]]:
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:HAS_INTOLERANCE]->(i:Allergen)
        RETURN u.email AS email, 
               u.first_name AS first_name,
               coalesce(u.role, 'user') AS role,
               u.sex AS sex, 
               u.weight_kg AS weight_kg, 
               u.height_cm AS height_cm, 
               u.age_years AS age_years, 
               u.activity_factor AS activity_factor,
               u.bmi AS bmi,
               u.bmr AS bmr,
               u.tdee AS tdee,
               u.diet_type AS diet_type,
               collect(i.name) AS intolerances
        ORDER BY u.email
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            return await result.data()

    async def update_user_admin(self, email: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        if not updates:
            return await self.get_user_profile(email)
            
        intolerances = updates.pop("intolerances", None)
            
        if updates:
            set_statements = []
            for key in updates.keys():
                set_statements.append(f"u.{key} = ${key}")
            set_clause = "SET " + ", ".join(set_statements)
            
            query = f"""
            MATCH (u:User {{email: $email}})
            {set_clause}
            RETURN u.email AS email
            """
            async with self.driver.session() as session:
                await session.run(query, email=email, **updates)
                
        if intolerances is not None:
            query_intolerances = """
            MATCH (u:User {email: $email})
            OPTIONAL MATCH (u)-[r:HAS_INTOLERANCE]->()
            DELETE r
            WITH u
            UNWIND $intolerances AS intl
            MERGE (a:Allergen {name: intl})
            MERGE (u)-[:HAS_INTOLERANCE]->(a)
            """
            async with self.driver.session() as session:
                await session.run(query_intolerances, email=email, intolerances=intolerances)

        return await self.get_user_profile(email)

    async def delete_user(self, email: str) -> bool:
        query = """
        MATCH (u:User {email: $email})
        DETACH DELETE u
        RETURN count(u) AS deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query, email=email)
            record = await result.single()
            return record and record["deleted_count"] > 0

    async def get_diet_types(self) -> list[str]:
        query = """
        MATCH (d:DietType)
        RETURN d.name AS name
        ORDER BY name
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            return [record["name"] for record in await result.data()]

    async def create_diet_type(self, name: str) -> bool:
        query = """
        MERGE (d:DietType {name: $name})
        RETURN d.name AS name
        """
        async with self.driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()
            return record is not None

    async def update_diet_type(self, old_name: str, new_name: str) -> bool:
        query_diet = """
        MATCH (d:DietType {name: $old_name})
        SET d.name = $new_name
        RETURN d.name AS name
        """
        query_users = """
        MATCH (u:User {diet_type: $old_name})
        SET u.diet_type = $new_name
        """
        async with self.driver.session() as session:
            result = await session.run(query_diet, old_name=old_name, new_name=new_name)
            record = await result.single()
            if record:
                # Update cascading users
                await session.run(query_users, old_name=old_name, new_name=new_name)
                return True
            return False

    async def delete_diet_type(self, name: str) -> bool:
        query_diet = """
        MATCH (d:DietType {name: $name})
        DETACH DELETE d
        RETURN count(d) AS deleted_count
        """
        query_users = """
        MATCH (u:User {diet_type: $name})
        SET u.diet_type = null
        """
        async with self.driver.session() as session:
            # First set users' diet_type to null
            await session.run(query_users, name=name)
            # Then delete the diet type
            result = await session.run(query_diet, name=name)
            record = await result.single()
            return record and record["deleted_count"] > 0

    async def get_allergens(self) -> list[str]:
        query = """
        MATCH (a:Allergen)
        RETURN a.name AS name
        ORDER BY name
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            return [record["name"] for record in await result.data()]

    async def create_allergen(self, name: str) -> bool:
        query = """
        MERGE (a:Allergen {name: $name})
        RETURN a.name AS name
        """
        async with self.driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()
            return record is not None

    async def update_allergen(self, old_name: str, new_name: str) -> bool:
        query_allergen = """
        MATCH (a:Allergen {name: $old_name})
        SET a.name = $new_name
        RETURN a.name AS name
        """
        async with self.driver.session() as session:
            result = await session.run(query_allergen, old_name=old_name, new_name=new_name)
            record = await result.single()
            return record is not None

    async def delete_allergen(self, name: str) -> bool:
        query_allergen = """
        MATCH (a:Allergen {name: $name})
        DETACH DELETE a
        RETURN count(a) AS deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query_allergen, name=name)
            record = await result.single()
            return record and record["deleted_count"] > 0

    async def get_ingredients(self) -> list[dict[str, Any]]:
        query = """
        MATCH (i:Ingredient)
        OPTIONAL MATCH (i)-[:CONTAINS_ALLERGEN]->(a:Allergen)
        RETURN i.name AS name,
               coalesce(i.calorias_100g, 0.0) AS calorias_100g,
               coalesce(i.proteinas_100g, 0.0) AS proteinas_100g,
               coalesce(i.grasas_100g, 0.0) AS grasas_100g,
               coalesce(i.carbohidratos_100g, 0.0) AS carbohidratos_100g,
               coalesce(i.origen, 'vegetal') AS origen,
               coalesce(i.categoria, 'varios') AS categoria,
               collect(a.name) AS allergens
        ORDER BY name
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            return await result.data()

    async def create_ingredient(self, data: dict[str, Any]) -> dict[str, Any] | None:
        allergens = data.get("allergens", [])
        query_node = """
        MERGE (i:Ingredient {name: $name})
        SET i.calorias_100g = $calorias_100g,
            i.proteinas_100g = $proteinas_100g,
            i.grasas_100g = $grasas_100g,
            i.carbohidratos_100g = $carbohidratos_100g,
            i.origen = $origen,
            i.categoria = $categoria
        RETURN i.name AS name
        """
        query_allergens = """
        MATCH (i:Ingredient {name: $name})
        UNWIND $allergens AS allergen_name
        MERGE (a:Allergen {name: allergen_name})
        MERGE (i)-[:CONTAINS_ALLERGEN]->(a)
        """
        async with self.driver.session() as session:
            res = await session.run(query_node, **data)
            rec = await res.single()
            if not rec:
                return None
            if allergens:
                res_all = await session.run(query_allergens, name=data["name"], allergens=allergens)
                await res_all.consume()
        return data

    async def update_ingredient(self, old_name: str, data: dict[str, Any]) -> dict[str, Any] | None:
        allergens = data.get("allergens", [])
        query_node = """
        MATCH (i:Ingredient {name: $old_name})
        SET i.name = $name,
            i.calorias_100g = $calorias_100g,
            i.proteinas_100g = $proteinas_100g,
            i.grasas_100g = $grasas_100g,
            i.carbohidratos_100g = $carbohidratos_100g,
            i.origen = $origen,
            i.categoria = $categoria
        RETURN i.name AS name
        """
        query_clear_rel = """
        MATCH (i:Ingredient {name: $name})-[r:CONTAINS_ALLERGEN]->()
        DELETE r
        """
        query_allergens = """
        MATCH (i:Ingredient {name: $name})
        UNWIND $allergens AS allergen_name
        MERGE (a:Allergen {name: allergen_name})
        MERGE (i)-[:CONTAINS_ALLERGEN]->(a)
        """
        async with self.driver.session() as session:
            res = await session.run(query_node, old_name=old_name, **data)
            rec = await res.single()
            if not rec:
                return None
            
            res_clear = await session.run(query_clear_rel, name=data["name"])
            await res_clear.consume()
            if allergens:
                res_all = await session.run(query_allergens, name=data["name"], allergens=allergens)
                await res_all.consume()
        return data

    async def delete_ingredient(self, name: str) -> bool:
        query = """
        MATCH (i:Ingredient {name: $name})
        DETACH DELETE i
        RETURN count(i) AS deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()
            return record and record["deleted_count"] > 0

    async def get_recipes(self) -> list[dict[str, Any]]:
        query = """
        MATCH (r:Recipe)
        OPTIONAL MATCH (r)-[rel:CONTAINS_INGREDIENT]->(i:Ingredient)
        WITH r, 
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.calorias_100g, 0.0)) AS total_calories,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.proteinas_100g, 0.0)) AS total_protein,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.grasas_100g, 0.0)) AS total_fat,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.carbohidratos_100g, 0.0)) AS total_carbs,
             collect(CASE WHEN i IS NOT NULL THEN {name: i.name, grams: rel.grams} ELSE NULL END) AS raw_ingredients
        RETURN r.id AS id,
               r.name AS name,
               coalesce(r.description, '') AS description,
               round(total_calories, 2) AS calories,
               round(total_protein, 2) AS protein_g,
               round(total_fat, 2) AS fat_g,
               round(total_carbs, 2) AS carbs_g,
               [x IN raw_ingredients WHERE x IS NOT NULL] AS ingredients
        ORDER BY r.name
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            return await result.data()

    async def get_recipe_by_id(self, recipe_id: str) -> dict[str, Any] | None:
        query = """
        MATCH (r:Recipe {id: $recipe_id})
        OPTIONAL MATCH (r)-[rel:CONTAINS_INGREDIENT]->(i:Ingredient)
        WITH r, 
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.calorias_100g, 0.0)) AS total_calories,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.proteinas_100g, 0.0)) AS total_protein,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.grasas_100g, 0.0)) AS total_fat,
             sum(coalesce(rel.grams, 0) / 100.0 * coalesce(i.carbohidratos_100g, 0.0)) AS total_carbs,
             collect(CASE WHEN i IS NOT NULL THEN {name: i.name, grams: rel.grams} ELSE NULL END) AS raw_ingredients
        RETURN r.id AS id,
               r.name AS name,
               coalesce(r.description, '') AS description,
               round(total_calories, 2) AS calories,
               round(total_protein, 2) AS protein_g,
               round(total_fat, 2) AS fat_g,
               round(total_carbs, 2) AS carbs_g,
               [x IN raw_ingredients WHERE x IS NOT NULL] AS ingredients
        """
        async with self.driver.session() as session:
            result = await session.run(query, recipe_id=recipe_id)
            record = await result.single()
            if record:
                return dict(record)
            return None

    async def create_recipe(self, data: dict[str, Any]) -> dict[str, Any] | None:
        import uuid
        recipe_id = data.get("id") or f"r_{uuid.uuid4().hex[:8]}"
        name = data.get("name", "")
        description = data.get("description", "")
        raw_ings = data.get("ingredients", [])
        ingredients = [ing if isinstance(ing, dict) else ing.model_dump() for ing in raw_ings]

        query_create = """
        MERGE (r:Recipe {id: $recipe_id})
        SET r.name = $name,
            r.description = $description
        RETURN r.id AS id
        """

        query_rel = """
        MATCH (r:Recipe {id: $recipe_id})
        UNWIND $ingredients AS ing
        MATCH (i:Ingredient {name: ing.name})
        MERGE (r)-[:CONTAINS_INGREDIENT {grams: ing.grams}]->(i)
        """

        async with self.driver.session() as session:
            res = await session.run(query_create, recipe_id=recipe_id, name=name, description=description)
            rec = await res.single()
            if not rec:
                return None
            if ingredients:
                res_rel = await session.run(query_rel, recipe_id=recipe_id, ingredients=ingredients)
                await res_rel.consume()

        return await self.get_recipe_by_id(recipe_id)

    async def update_recipe(self, recipe_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        name = data.get("name", "")
        description = data.get("description", "")
        raw_ings = data.get("ingredients", [])
        ingredients = [ing if isinstance(ing, dict) else ing.model_dump() for ing in raw_ings]

        query_update = """
        MATCH (r:Recipe {id: $recipe_id})
        SET r.name = $name,
            r.description = $description
        RETURN r.id AS id
        """

        query_clear_rel = """
        MATCH (r:Recipe {id: $recipe_id})-[rel:CONTAINS_INGREDIENT]->()
        DELETE rel
        """

        query_rel = """
        MATCH (r:Recipe {id: $recipe_id})
        UNWIND $ingredients AS ing
        MATCH (i:Ingredient {name: ing.name})
        MERGE (r)-[:CONTAINS_INGREDIENT {grams: ing.grams}]->(i)
        """

        async with self.driver.session() as session:
            res = await session.run(query_update, recipe_id=recipe_id, name=name, description=description)
            rec = await res.single()
            if not rec:
                return None

            clear_res = await session.run(query_clear_rel, recipe_id=recipe_id)
            await clear_res.consume()

            if ingredients:
                res_rel = await session.run(query_rel, recipe_id=recipe_id, ingredients=ingredients)
                await res_rel.consume()

        return await self.get_recipe_by_id(recipe_id)

    async def delete_recipe(self, recipe_id: str) -> bool:
        query = """
        MATCH (r:Recipe {id: $recipe_id})
        DETACH DELETE r
        RETURN count(r) AS deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query, recipe_id=recipe_id)
            record = await result.single()
            return record and record["deleted_count"] > 0

    async def get_user_analytics(self) -> dict[str, Any]:
        query_users = """
        MATCH (u:User)
        RETURN count(u) AS total_users,
               count(CASE WHEN u.sex = 'm' OR u.sex = 'male' THEN 1 END) AS males,
               count(CASE WHEN u.sex = 'f' OR u.sex = 'female' THEN 1 END) AS females,
               count(CASE WHEN u.sex IS NULL OR u.sex = '' THEN 1 END) AS unspecified_sex,
               round(avg(u.weight_kg), 1) AS avg_weight_kg,
               round(avg(u.height_cm), 1) AS avg_height_cm,
               round(avg(u.age_years), 1) AS avg_age_years,
               count(CASE WHEN u.weight_kg < 60 THEN 1 END) AS weight_under_60,
               count(CASE WHEN u.weight_kg >= 60 AND u.weight_kg < 75 THEN 1 END) AS weight_60_75,
               count(CASE WHEN u.weight_kg >= 75 AND u.weight_kg < 90 THEN 1 END) AS weight_75_90,
               count(CASE WHEN u.weight_kg >= 90 THEN 1 END) AS weight_over_90,
               count(CASE WHEN u.age_years < 25 THEN 1 END) AS age_under_25,
               count(CASE WHEN u.age_years >= 25 AND u.age_years < 40 THEN 1 END) AS age_25_40,
               count(CASE WHEN u.age_years >= 40 AND u.age_years < 60 THEN 1 END) AS age_40_60,
               count(CASE WHEN u.age_years >= 60 THEN 1 END) AS age_over_60,
               count(CASE WHEN u.activity_factor = 1.2 THEN 1 END) AS act_sedentary,
               count(CASE WHEN u.activity_factor = 1.375 THEN 1 END) AS act_light,
               count(CASE WHEN u.activity_factor = 1.55 THEN 1 END) AS act_moderate,
               count(CASE WHEN u.activity_factor = 1.725 THEN 1 END) AS act_very_active,
               count(CASE WHEN u.activity_factor = 1.9 THEN 1 END) AS act_extra_active
        """
        
        query_diets = """
        MATCH (u:User)
        WHERE u.diet_type IS NOT NULL AND u.diet_type <> ''
        RETURN u.diet_type AS diet_type, count(u) AS count
        ORDER BY count DESC
        """
        
        query_intolerances = """
        MATCH (u:User)-[:HAS_INTOLERANCE]->(a:Allergen)
        RETURN a.name AS intolerance, count(u) AS count
        ORDER BY count DESC
        """

        async with self.driver.session() as session:
            res_users = await session.run(query_users)
            user_data = dict(await res_users.single() or {})
            
            res_diets = await session.run(query_diets)
            diet_data = [dict(record) for record in await res_diets.data()]
            
            res_into = await session.run(query_intolerances)
            into_data = [dict(record) for record in await res_into.data()]

        return {
            "total_users": user_data.get("total_users", 0),
            "sex_distribution": {
                "males": user_data.get("males", 0),
                "females": user_data.get("females", 0),
                "unspecified": user_data.get("unspecified_sex", 0)
            },
            "weight_stats": {
                "avg_weight_kg": user_data.get("avg_weight_kg", 0.0),
                "distribution": {
                    "< 60 kg": user_data.get("weight_under_60", 0),
                    "60 - 75 kg": user_data.get("weight_60_75", 0),
                    "75 - 90 kg": user_data.get("weight_75_90", 0),
                    "> 90 kg": user_data.get("weight_over_90", 0)
                }
            },
            "height_stats": {
                "avg_height_cm": user_data.get("avg_height_cm", 0.0)
            },
            "age_stats": {
                "avg_age_years": user_data.get("avg_age_years", 0.0),
                "distribution": {
                    "< 25": user_data.get("age_under_25", 0),
                    "25 - 40": user_data.get("age_25_40", 0),
                    "40 - 60": user_data.get("age_40_60", 0),
                    "> 60": user_data.get("age_over_60", 0)
                }
            },
            "activity_stats": {
                "Sedentario": user_data.get("act_sedentary", 0),
                "Ligeramente activo": user_data.get("act_light", 0),
                "Moderadamente activo": user_data.get("act_moderate", 0),
                "Muy activo": user_data.get("act_very_active", 0),
                "Hiperactivo": user_data.get("act_extra_active", 0)
            },
            "diet_types_distribution": diet_data,
            "intolerances_distribution": into_data
        }

user_repository = UserRepository()



