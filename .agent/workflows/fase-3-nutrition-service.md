---
description: Microservicio Nutrition Graph Service (Neo4j, Cypher, Agregación de Macros)
---

Fase 3: Microservicio nutrition-graph-service
Objetivo

Desarrollar la ontología de alimentos en Neo4j, el consumidor de eventos Kafka y los endpoints de consulta y agregación estricta de macronutrientes.
Instrucciones para el Agente

    Crea la estructura en services/nutrition-graph-service/.

    Configura la conexión asíncrona a Neo4j mediante el driver oficial de Python (neo4j).

    Implementa el Consumidor Kafka (aiokafka) que escucha UserRegistered y UserIntolerancesUpdated para crear/actualizar nodos :User y relaciones :HAS_INTOLERANCE en Neo4j.

    Implementa el modelo de datos en Cypher:

        Nodos: :User, :Recipe, :Ingredient, :Nutrient, :Allergen, :DietType.

        Propiedades del ingrediente: calorias_100g, proteinas_100g, grasas_100g, carbohidratos_100g.

    Escribe consultas Cypher parametrizadas que:

        Sumen dinámicamente las calorías y gramos de proteínas, grasas y carbohidratos de todos los ingredientes componentes de una receta en función de la cantidad en gramos.

        Excluyan el 100% de las recetas que contengan alérgenos vinculados al usuario o violen su tipo de dieta (:EXCLUDES).

    Desarrolla un script de ingesta inicial (seed_data.py) para popular el grafo con datos de prueba.

    Crea el Dockerfile y configura los tests en tests/ con pytest y testcontainers-python.

Criterios de Verificación

    Ejecutar el script seed_data.py y verificar nodos en Neo4j Browser.

    Pruebas unitarias para validar que la sumatoria de macros por receta coincide exactamente con la suma de sus ingredientes.

    Test de exclusión de alérgenos que compruebe que no se recomiendan ingredientes prohibidos.