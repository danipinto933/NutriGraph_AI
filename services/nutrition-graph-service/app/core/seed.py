import logging
from neo4j import AsyncDriver

logger = logging.getLogger(__name__)

# Lista de 40 usuarios con biometría, dietas e intolerancias totalmente hardcodeadas
HARDCODED_USERS = [
    {
        'email': 'alejandro.martinez@gmail.com', 'first_name': 'Alejandro', 'role': 'user',
        'sex': 'm', 'weight_kg': 78.5, 'height_cm': 178.0, 'age_years': 28, 'activity_factor': 1.55,
        'bmi': 24.78, 'bmr': 1762.5, 'tdee': 2731.88, 'diet_type': 'Mediterranea', 'intolerances': ['Gluten']
    },
    {
        'email': 'carmen.lopez@gmail.com', 'first_name': 'Carmen', 'role': 'user',
        'sex': 'f', 'weight_kg': 62.0, 'height_cm': 165.0, 'age_years': 34, 'activity_factor': 1.375,
        'bmi': 22.77, 'bmr': 1320.25, 'tdee': 1815.34, 'diet_type': 'Vegetariana', 'intolerances': ['Lácteos']
    },
    {
        'email': 'david.garcia@gmail.com', 'first_name': 'David', 'role': 'user',
        'sex': 'm', 'weight_kg': 92.0, 'height_cm': 185.0, 'age_years': 42, 'activity_factor': 1.725,
        'bmi': 26.88, 'bmr': 1871.25, 'tdee': 3227.91, 'diet_type': 'Carnivora', 'intolerances': []
    },
    {
        'email': 'elena.fernandez@gmail.com', 'first_name': 'Elena', 'role': 'user',
        'sex': 'f', 'weight_kg': 54.5, 'height_cm': 162.0, 'age_years': 25, 'activity_factor': 1.2,
        'bmi': 20.77, 'bmr': 1271.5, 'tdee': 1525.8, 'diet_type': 'Vegana', 'intolerances': ['Gluten', 'Soja']
    },
    {
        'email': 'francisco.gonzalez@gmail.com', 'first_name': 'Francisco', 'role': 'user',
        'sex': 'm', 'weight_kg': 85.0, 'height_cm': 180.0, 'age_years': 50, 'activity_factor': 1.375,
        'bmi': 26.23, 'bmr': 1730.0, 'tdee': 2378.75, 'diet_type': None, 'intolerances': ['Frutos de cáscara']
    },
    {
        'email': 'isabel.rodriguez@gmail.com', 'first_name': 'Isabel', 'role': 'user',
        'sex': 'f', 'weight_kg': 70.0, 'height_cm': 168.0, 'age_years': 29, 'activity_factor': 1.55,
        'bmi': 24.8, 'bmr': 1444.0, 'tdee': 2238.2, 'diet_type': 'Mediterranea', 'intolerances': ['Crustáceos', 'Pescado']
    },
    {
        'email': 'javier.sanchez@gmail.com', 'first_name': 'Javier', 'role': 'user',
        'sex': 'm', 'weight_kg': 68.0, 'height_cm': 172.0, 'age_years': 22, 'activity_factor': 1.9,
        'bmi': 22.99, 'bmr': 1650.0, 'tdee': 3135.0, 'diet_type': None, 'intolerances': []
    },
    {
        'email': 'laura.perez@gmail.com', 'first_name': 'Laura', 'role': 'user',
        'sex': 'f', 'weight_kg': 58.0, 'height_cm': 170.0, 'age_years': 31, 'activity_factor': 1.375,
        'bmi': 20.07, 'bmr': 1326.5, 'tdee': 1823.94, 'diet_type': 'Vegetariana', 'intolerances': ['Lácteos', 'Huevos']
    },
    {
        'email': 'manuel.gomez@gmail.com', 'first_name': 'Manuel', 'role': 'user',
        'sex': 'm', 'weight_kg': 98.0, 'height_cm': 192.0, 'age_years': 38, 'activity_factor': 1.55,
        'bmi': 26.58, 'bmr': 1995.0, 'tdee': 3092.25, 'diet_type': 'Carnivora', 'intolerances': ['Apio']
    },
    {
        'email': 'marta.martin@gmail.com', 'first_name': 'Marta', 'role': 'user',
        'sex': 'f', 'weight_kg': 65.0, 'height_cm': 166.0, 'age_years': 45, 'activity_factor': 1.2,
        'bmi': 23.59, 'bmr': 1301.5, 'tdee': 1561.8, 'diet_type': 'Mediterranea', 'intolerances': ['Mostaza']
    },
    {
        'email': 'pablo.jimenez@gmail.com', 'first_name': 'Pablo', 'role': 'user',
        'sex': 'm', 'weight_kg': 75.0, 'height_cm': 176.0, 'age_years': 27, 'activity_factor': 1.725,
        'bmi': 24.21, 'bmr': 1720.0, 'tdee': 2967.0, 'diet_type': None, 'intolerances': ['Gluten']
    },
    {
        'email': 'paula.ruiz@gmail.com', 'first_name': 'Paula', 'role': 'user',
        'sex': 'f', 'weight_kg': 52.0, 'height_cm': 160.0, 'age_years': 21, 'activity_factor': 1.55,
        'bmi': 20.31, 'bmr': 1254.0, 'tdee': 1943.7, 'diet_type': 'Vegana', 'intolerances': ['Frutos de cáscara', 'Soja', 'Cacahuetes']
    },
    {
        'email': 'rafael.hernandez@gmail.com', 'first_name': 'Rafael', 'role': 'user',
        'sex': 'm', 'weight_kg': 88.0, 'height_cm': 182.0, 'age_years': 36, 'activity_factor': 1.375,
        'bmi': 26.57, 'bmr': 1842.5, 'tdee': 2533.44, 'diet_type': 'Mediterranea', 'intolerances': []
    },
    {
        'email': 'sara.diaz@gmail.com', 'first_name': 'Sara', 'role': 'user',
        'sex': 'f', 'weight_kg': 60.0, 'height_cm': 167.0, 'age_years': 26, 'activity_factor': 1.725,
        'bmi': 21.51, 'bmr': 1352.75, 'tdee': 2333.49, 'diet_type': None, 'intolerances': ['Lácteos']
    },
    {
        'email': 'sergio.moreno@gmail.com', 'first_name': 'Sergio', 'role': 'user',
        'sex': 'm', 'weight_kg': 81.0, 'height_cm': 179.0, 'age_years': 33, 'activity_factor': 1.55,
        'bmi': 25.28, 'bmr': 1768.75, 'tdee': 2741.56, 'diet_type': 'Mediterranea', 'intolerances': ['Pescado']
    },
    {
        'email': 'ana.munoz@gmail.com', 'first_name': 'Ana', 'role': 'user',
        'sex': 'f', 'weight_kg': 56.0, 'height_cm': 163.0, 'age_years': 30, 'activity_factor': 1.375,
        'bmi': 21.08, 'bmr': 1267.75, 'tdee': 1743.16, 'diet_type': 'Vegetariana', 'intolerances': ['Gluten']
    },
    {
        'email': 'carlos.alvarez@gmail.com', 'first_name': 'Carlos', 'role': 'user',
        'sex': 'm', 'weight_kg': 95.0, 'height_cm': 188.0, 'age_years': 48, 'activity_factor': 1.2,
        'bmi': 26.88, 'bmr': 1890.0, 'tdee': 2268.0, 'diet_type': None, 'intolerances': ['Lácteos', 'Huevos']
    },
    {
        'email': 'lucia.romero@gmail.com', 'first_name': 'Lucia', 'role': 'user',
        'sex': 'f', 'weight_kg': 64.0, 'height_cm': 169.0, 'age_years': 23, 'activity_factor': 1.9,
        'bmi': 22.41, 'bmr': 1420.25, 'tdee': 2698.48, 'diet_type': 'Vegana', 'intolerances': ['Gluten', 'Frutos de cáscara']
    },
    {
        'email': 'diego.alonso@gmail.com', 'first_name': 'Diego', 'role': 'user',
        'sex': 'm', 'weight_kg': 73.0, 'height_cm': 175.0, 'age_years': 29, 'activity_factor': 1.55,
        'bmi': 23.84, 'bmr': 1683.75, 'tdee': 2609.81, 'diet_type': 'Mediterranea', 'intolerances': []
    },
    {
        'email': 'rosa.gutierrez@gmail.com', 'first_name': 'Rosa', 'role': 'user',
        'sex': 'f', 'weight_kg': 72.0, 'height_cm': 164.0, 'age_years': 52, 'activity_factor': 1.2,
        'bmi': 26.77, 'bmr': 1324.0, 'tdee': 1588.8, 'diet_type': None, 'intolerances': ['Soja']
    },
    {
        'email': 'antonio.navarro@gmail.com', 'first_name': 'Antonio', 'role': 'user',
        'sex': 'm', 'weight_kg': 84.0, 'height_cm': 181.0, 'age_years': 40, 'activity_factor': 1.375,
        'bmi': 25.64, 'bmr': 1776.25, 'tdee': 2442.34, 'diet_type': 'Carnivora', 'intolerances': ['Gluten']
    },
    {
        'email': 'beatriz.torres@gmail.com', 'first_name': 'Beatriz', 'role': 'user',
        'sex': 'f', 'weight_kg': 59.0, 'height_cm': 166.0, 'age_years': 35, 'activity_factor': 1.55,
        'bmi': 21.41, 'bmr': 1291.5, 'tdee': 2001.83, 'diet_type': 'Mediterranea', 'intolerances': ['Lácteos']
    },
    {
        'email': 'daniel.dominguez@gmail.com', 'first_name': 'Daniel', 'role': 'user',
        'sex': 'm', 'weight_kg': 77.0, 'height_cm': 177.0, 'age_years': 25, 'activity_factor': 1.725,
        'bmi': 24.58, 'bmr': 1756.25, 'tdee': 3029.53, 'diet_type': None, 'intolerances': ['Crustáceos']
    },
    {
        'email': 'cristina.vazquez@gmail.com', 'first_name': 'Cristina', 'role': 'user',
        'sex': 'f', 'weight_kg': 61.0, 'height_cm': 165.0, 'age_years': 28, 'activity_factor': 1.375,
        'bmi': 22.41, 'bmr': 1340.25, 'tdee': 1842.84, 'diet_type': 'Vegetariana', 'intolerances': []
    },
    {
        'email': 'jorge.ramos@gmail.com', 'first_name': 'Jorge', 'role': 'user',
        'sex': 'm', 'weight_kg': 89.0, 'height_cm': 184.0, 'age_years': 44, 'activity_factor': 1.55,
        'bmi': 26.29, 'bmr': 1825.0, 'tdee': 2828.75, 'diet_type': None, 'intolerances': ['Pescado', 'Crustáceos']
    },
    {
        'email': 'teresa.gil@gmail.com', 'first_name': 'Teresa', 'role': 'user',
        'sex': 'f', 'weight_kg': 67.0, 'height_cm': 171.0, 'age_years': 49, 'activity_factor': 1.2,
        'bmi': 22.91, 'bmr': 1332.75, 'tdee': 1599.3, 'diet_type': 'Mediterranea', 'intolerances': ['Gluten']
    },
    {
        'email': 'luis.ramirez@gmail.com', 'first_name': 'Luis', 'role': 'user',
        'sex': 'm', 'weight_kg': 70.0, 'height_cm': 173.0, 'age_years': 24, 'activity_factor': 1.9,
        'bmi': 23.39, 'bmr': 1666.25, 'tdee': 3165.88, 'diet_type': None, 'intolerances': []
    },
    {
        'email': 'raquel.serrano@gmail.com', 'first_name': 'Raquel', 'role': 'user',
        'sex': 'f', 'weight_kg': 55.0, 'height_cm': 161.0, 'age_years': 32, 'activity_factor': 1.55,
        'bmi': 21.22, 'bmr': 1235.25, 'tdee': 1914.64, 'diet_type': 'Vegana', 'intolerances': ['Lácteos', 'Huevos', 'Pescado']
    },
    {
        'email': 'miguel.blanco@gmail.com', 'first_name': 'Miguel', 'role': 'user',
        'sex': 'm', 'weight_kg': 82.0, 'height_cm': 180.0, 'age_years': 37, 'activity_factor': 1.375,
        'bmi': 25.31, 'bmr': 1765.0, 'tdee': 2426.88, 'diet_type': 'Mediterranea', 'intolerances': ['Cacahuetes']
    },
    {
        'email': 'nuria.suarez@gmail.com', 'first_name': 'Nuria', 'role': 'user',
        'sex': 'f', 'weight_kg': 63.0, 'height_cm': 168.0, 'age_years': 39, 'activity_factor': 1.375,
        'bmi': 22.32, 'bmr': 1324.0, 'tdee': 1820.5, 'diet_type': 'Vegetariana', 'intolerances': ['Gluten']
    },
    {
        'email': 'jose.molina@gmail.com', 'first_name': 'Jose', 'role': 'user',
        'sex': 'm', 'weight_kg': 91.0, 'height_cm': 186.0, 'age_years': 55, 'activity_factor': 1.2,
        'bmi': 26.3, 'bmr': 1802.5, 'tdee': 2163.0, 'diet_type': None, 'intolerances': ['Lácteos']
    },
    {
        'email': 'irene.morales@gmail.com', 'first_name': 'Irene', 'role': 'user',
        'sex': 'f', 'weight_kg': 57.0, 'height_cm': 164.0, 'age_years': 27, 'activity_factor': 1.725,
        'bmi': 21.19, 'bmr': 1299.0, 'tdee': 2240.78, 'diet_type': 'Mediterranea', 'intolerances': []
    },
    {
        'email': 'victor.ortega@gmail.com', 'first_name': 'Victor', 'role': 'user',
        'sex': 'm', 'weight_kg': 79.0, 'height_cm': 178.0, 'age_years': 31, 'activity_factor': 1.55,
        'bmi': 24.93, 'bmr': 1752.5, 'tdee': 2716.38, 'diet_type': None, 'intolerances': ['Frutos de cáscara']
    },
    {
        'email': 'silvia.delgado@gmail.com', 'first_name': 'Silvia', 'role': 'user',
        'sex': 'f', 'weight_kg': 68.0, 'height_cm': 170.0, 'age_years': 41, 'activity_factor': 1.375,
        'bmi': 23.53, 'bmr': 1376.5, 'tdee': 1892.69, 'diet_type': 'Mediterranea', 'intolerances': ['Gluten', 'Lácteos']
    },
    {
        'email': 'alvaro.castro@gmail.com', 'first_name': 'Alvaro', 'role': 'user',
        'sex': 'm', 'weight_kg': 86.0, 'height_cm': 183.0, 'age_years': 30, 'activity_factor': 1.725,
        'bmi': 25.68, 'bmr': 1858.75, 'tdee': 3206.34, 'diet_type': 'Carnivora', 'intolerances': []
    },
    {
        'email': 'patricia.ortiz@gmail.com', 'first_name': 'Patricia', 'role': 'user',
        'sex': 'f', 'weight_kg': 53.0, 'height_cm': 162.0, 'age_years': 22, 'activity_factor': 1.55,
        'bmi': 20.19, 'bmr': 1271.5, 'tdee': 1970.83, 'diet_type': 'Vegana', 'intolerances': ['Soja']
    },
    {
        'email': 'ruben.rubio@gmail.com', 'first_name': 'Ruben', 'role': 'user',
        'sex': 'm', 'weight_kg': 76.0, 'height_cm': 176.0, 'age_years': 35, 'activity_factor': 1.375,
        'bmi': 24.53, 'bmr': 1690.0, 'tdee': 2323.75, 'diet_type': None, 'intolerances': ['Gluten']
    },
    {
        'email': 'natalia.marin@gmail.com', 'first_name': 'Natalia', 'role': 'user',
        'sex': 'f', 'weight_kg': 66.0, 'height_cm': 167.0, 'age_years': 38, 'activity_factor': 1.2,
        'bmi': 23.67, 'bmr': 1352.75, 'tdee': 1623.3, 'diet_type': 'Mediterranea', 'intolerances': ['Mostaza', 'Apio']
    },
    {
        'email': 'marcos.sanz@gmail.com', 'first_name': 'Marcos', 'role': 'user',
        'sex': 'm', 'weight_kg': 90.0, 'height_cm': 185.0, 'age_years': 29, 'activity_factor': 1.9,
        'bmi': 26.29, 'bmr': 1916.25, 'tdee': 3640.88, 'diet_type': None, 'intolerances': []
    },
    {
        'email': 'clara.iglesias@gmail.com', 'first_name': 'Clara', 'role': 'user',
        'sex': 'f', 'weight_kg': 60.0, 'height_cm': 165.0, 'age_years': 26, 'activity_factor': 1.55,
        'bmi': 22.04, 'bmr': 1340.25, 'tdee': 2077.39, 'diet_type': 'Vegetariana', 'intolerances': ['Lácteos']
    }
]

# Añadir contraseña fija encriptada a cada objeto de usuario para Cypher
for u in HARDCODED_USERS:
    u['hashed_password'] = '$2b$12$KD2TM2U.O4h4wH0SIQ7kE.p6O/kC4Q7iYbY5G7NgnygzXCgBZ4aNu'

async def run_seed(driver: AsyncDriver):
    logger.info("Iniciando proceso de seeding de la base de datos Neo4j...")
    
    query_clear = "MATCH (n) DETACH DELETE n"

    query_admin_and_allergens = """
    // 1. Crear usuario Admin (sin biometría inicial)
    CREATE (:User {email: 'admin@gmail.com', hashed_password: '$2b$12$IiBfwlvs/w4uDqPeLvS5/uNB.vzk9lLNbtooBmGyiQGYi8nZXYClO', first_name: 'Admin', role: 'admin'});

    // 2. Crear Alérgenos Base
    UNWIND [
        'Pescado', 'Lácteos', 'Huevos', 'Gluten', 'Cacahuetes', 'Soja', 
        'Frutos de cáscara', 'Crustáceos', 'Apio', 'Mostaza', 'Granos de sésamo', 
        'Dióxido de azufre', 'Sulfitos', 'Moluscos', 'Altramuces'
    ] AS nombre_alergeno
    CREATE (:Allergen {name: nombre_alergeno});
    """

    query_create_users = """
    UNWIND $users AS u
    CREATE (:User {
        email: u.email,
        hashed_password: u.hashed_password,
        first_name: u.first_name,
        role: u.role,
        sex: u.sex,
        weight_kg: u.weight_kg,
        height_cm: u.height_cm,
        age_years: u.age_years,
        activity_factor: u.activity_factor,
        bmi: u.bmi,
        bmr: u.bmr,
        tdee: u.tdee,
        diet_type: u.diet_type
    });
    """

    query_link_intolerances = """
    UNWIND $users AS u
    UNWIND u.intolerances AS intl
    MATCH (usr:User {email: u.email})
    MATCH (a:Allergen {name: intl})
    MERGE (usr)-[:HAS_INTOLERANCE]->(a);
    """

    query_graph_content = """
    // 3. Crear Ingredientes Base (por cada 100g)
    UNWIND [
        // --- PROTEÍNAS ANIMALES ---
        {name: 'Leche Entera', cal: 42, p: 3.4, g: 1.0, c: 5.0, ori: 'animal', cat: 'lacteos'},
        {name: 'Ternera Magra', cal: 143, p: 26.0, g: 4.0, c: 0.0, ori: 'animal', cat: 'carne'},
        {name: 'Lomo de Cerdo', cal: 143, p: 21.0, g: 6.0, c: 0.0, ori: 'animal', cat: 'carne'},
        {name: 'Pechuga de Pavo', cal: 114, p: 24.0, g: 1.5, c: 0.0, ori: 'animal', cat: 'carne'},
        {name: 'Atún al natural', cal: 116, p: 26.0, g: 1.0, c: 0.0, ori: 'animal', cat: 'pescado'},
        {name: 'Gambas', cal: 99, p: 24.0, g: 0.3, c: 0.2, ori: 'animal', cat: 'pescado'},
        {name: 'Merluza', cal: 89, p: 18.0, g: 1.8, c: 0.0, ori: 'animal', cat: 'pescado'},
        {name: 'Calamares', cal: 92, p: 15.6, g: 1.4, c: 3.1, ori: 'animal', cat: 'pescado'},
        {name: 'Pulpo', cal: 82, p: 15.0, g: 1.0, c: 2.2, ori: 'animal', cat: 'pescado'},
        {name: 'Claras de huevo', cal: 52, p: 11.0, g: 0.2, c: 0.7, ori: 'animal', cat: 'huevos'},
        {name: 'Queso Fresco Batido', cal: 48, p: 8.0, g: 0.1, c: 3.5, ori: 'animal', cat: 'lacteos'},
        {name: 'Yogur Griego', cal: 97, p: 9.0, g: 5.0, c: 4.0, ori: 'animal', cat: 'lacteos'},
        {name: 'Pechuga de Pollo', cal: 165, p: 31.0, g: 3.6, c: 0.0, ori: 'animal', cat: 'carne'},
        {name: 'Proteina en polvo', cal: 373, p: 82.0, g: 6.3, c: 0.9, ori: 'animal', cat: 'suplementos'},
        {name: 'Huevo de gallina', cal: 155, p: 13.0, g: 11.0, c: 1.1, ori: 'animal', cat: 'huevos'},
        {name: 'Salmón', cal: 208, p: 20.0, g: 13.0, c: 0.0, ori: 'animal', cat: 'pescado'},
        
        // --- PROTEÍNAS VEGETALES Y LEGUMBRES ---
        {name: 'Tofu Firme', cal: 144, p: 15.8, g: 8.7, c: 2.8, ori: 'vegetal', cat: 'legumbre'},
        {name: 'Soja Texturizada', cal: 364, p: 50.0, g: 4.0, c: 30.0, ori: 'vegetal', cat: 'legumbre'},
        {name: 'Lentejas (cocidas)', cal: 116, p: 9.0, g: 0.4, c: 20.0, ori: 'vegetal', cat: 'legumbre'},
        {name: 'Garbanzos (cocidos)', cal: 164, p: 8.9, g: 2.6, c: 27.4, ori: 'vegetal', cat: 'legumbre'},
        {name: 'Alubias (cocidas)', cal: 127, p: 8.7, g: 0.5, c: 22.8, ori: 'vegetal', cat: 'legumbre'},
        {name: 'Edamame', cal: 121, p: 11.9, g: 5.2, c: 8.9, ori: 'vegetal', cat: 'legumbre'},
        
        // --- CARBOHIDRATOS ---
        {name: 'Avena', cal: 389, p: 16.9, g: 6.9, c: 66.3, ori: 'vegetal', cat: 'cereal'},
        {name: 'Patata (cruda)', cal: 77, p: 2.0, g: 0.1, c: 17.0, ori: 'vegetal', cat: 'tuberculo'},
        {name: 'Boniato (crudo)', cal: 86, p: 1.6, g: 0.1, c: 20.1, ori: 'vegetal', cat: 'tuberculo'},
        {name: 'Pasta de Trigo Integral', cal: 348, p: 14.0, g: 1.5, c: 65.0, ori: 'vegetal', cat: 'cereal'},
        {name: 'Quinoa (cruda)', cal: 368, p: 14.1, g: 6.0, c: 64.0, ori: 'vegetal', cat: 'cereal'},
        {name: 'Tortitas de Maíz', cal: 387, p: 7.8, g: 3.0, c: 80.0, ori: 'vegetal', cat: 'cereal'},
        {name: 'Maíz dulce', cal: 86, p: 3.2, g: 1.2, c: 19.0, ori: 'vegetal', cat: 'cereal'},
        {name: 'Arroz Blanco', cal: 130, p: 2.7, g: 0.3, c: 28.0, ori: 'vegetal', cat: 'cereal'},
        {name: 'Pan de Trigo', cal: 265, p: 9.0, g: 3.2, c: 49.0, ori: 'vegetal', cat: 'cereal'},

        // --- GRASAS SALUDABLES ---
        {name: 'Aceite de Oliva Virgen', cal: 884, p: 0.0, g: 100.0, c: 0.0, ori: 'vegetal', cat: 'grasa'},
        {name: 'Aguacate', cal: 160, p: 2.0, g: 14.7, c: 8.5, ori: 'vegetal', cat: 'fruta'},
        {name: 'Almendras', cal: 579, p: 21.0, g: 49.0, c: 21.0, ori: 'vegetal', cat: 'frutos_secos'},
        {name: 'Crema de Cacahuete', cal: 588, p: 25.0, g: 50.0, c: 20.0, ori: 'vegetal', cat: 'frutos_secos'},
        {name: 'Semillas de Chía', cal: 486, p: 16.5, g: 30.7, c: 42.1, ori: 'vegetal', cat: 'semillas'},
        {name: 'Semillas de Calabaza', cal: 559, p: 30.2, g: 49.0, c: 10.7, ori: 'vegetal', cat: 'semillas'},
        
        // --- VEGETALES Y HORTALIZAS ---
        {name: 'Brócoli', cal: 34, p: 2.8, g: 0.4, c: 6.6, ori: 'vegetal', cat: 'verdura'},
        {name: 'Espinacas', cal: 23, p: 2.9, g: 0.4, c: 3.6, ori: 'vegetal', cat: 'verdura'},
        {name: 'Tomate', cal: 18, p: 0.9, g: 0.2, c: 3.9, ori: 'vegetal', cat: 'verdura'},
        {name: 'Cebolla', cal: 40, p: 1.1, g: 0.1, c: 9.3, ori: 'vegetal', cat: 'verdura'},
        {name: 'Ajo', cal: 149, p: 6.3, g: 0.5, c: 33.0, ori: 'vegetal', cat: 'verdura'},
        {name: 'Zanahoria', cal: 41, p: 0.9, g: 0.2, c: 9.6, ori: 'vegetal', cat: 'verdura'},
        {name: 'Pimiento Rojo', cal: 26, p: 1.0, g: 0.3, c: 6.0, ori: 'vegetal', cat: 'verdura'},
        {name: 'Calabacín', cal: 17, p: 1.2, g: 0.3, c: 3.1, ori: 'vegetal', cat: 'verdura'},
        {name: 'Berenjena', cal: 25, p: 1.0, g: 0.2, c: 5.8, ori: 'vegetal', cat: 'verdura'},
        {name: 'Champiñones', cal: 22, p: 3.1, g: 0.3, c: 3.3, ori: 'vegetal', cat: 'hongo'},
        {name: 'Apio', cal: 16, p: 0.7, g: 0.2, c: 3.0, ori: 'vegetal', cat: 'verdura'},
        {name: 'Lechuga', cal: 15, p: 1.4, g: 0.2, c: 2.9, ori: 'vegetal', cat: 'verdura'},
        {name: 'Coliflor', cal: 25, p: 1.9, g: 0.3, c: 4.9, ori: 'vegetal', cat: 'verdura'},
        
        // --- FRUTAS ---
        {name: 'Plátano', cal: 89, p: 1.1, g: 0.3, c: 22.8, ori: 'vegetal', cat: 'fruta'},
        {name: 'Manzana', cal: 52, p: 0.3, g: 0.2, c: 13.8, ori: 'vegetal', cat: 'fruta'},
        {name: 'Arándanos', cal: 57, p: 0.7, g: 0.3, c: 14.5, ori: 'vegetal', cat: 'fruta'},
        {name: 'Fresa', cal: 32, p: 0.7, g: 0.3, c: 7.7, ori: 'vegetal', cat: 'fruta'},
        {name: 'Naranja', cal: 47, p: 0.9, g: 0.1, c: 11.7, ori: 'vegetal', cat: 'fruta'},
        {name: 'Piña', cal: 50, p: 0.5, g: 0.1, c: 13.1, ori: 'vegetal', cat: 'fruta'},
        {name: 'Limón', cal: 29, p: 1.1, g: 0.3, c: 9.3, ori: 'vegetal', cat: 'fruta'},
        
        // --- CONDIMENTOS Y OTROS ---
        {name: 'Miel', cal: 304, p: 0.3, g: 0.0, c: 82.4, ori: 'animal', cat: 'miel'},
        {name: 'Salsa de Soja', cal: 53, p: 8.0, g: 0.6, c: 4.9, ori: 'vegetal', cat: 'salsa'},
        {name: 'Mostaza Antigua', cal: 66, p: 4.4, g: 4.0, c: 3.0, ori: 'vegetal', cat: 'salsa'},
        {name: 'Semillas de Sésamo', cal: 573, p: 17.7, g: 49.7, c: 23.4, ori: 'vegetal', cat: 'semillas'}
    ] AS ing
    CREATE (:Ingredient {
        name: ing.name, calorias_100g: ing.cal, proteinas_100g: ing.p, 
        grasas_100g: ing.g, carbohidratos_100g: ing.c, origen: ing.ori, categoria: ing.cat
    });

    // 4. Vincular Alérgenos dinámicamente a los ingredientes
    UNWIND [
        {ingrediente: 'Leche Entera', alergeno: 'Lácteos'},
        {ingrediente: 'Pan de Trigo', alergeno: 'Gluten'},
        {ingrediente: 'Huevo de gallina', alergeno: 'Huevos'},
        {ingrediente: 'Salmón', alergeno: 'Pescado'},
        {ingrediente: 'Nueces', alergeno: 'Frutos de cáscara'},
        {ingrediente: 'Atún al natural', alergeno: 'Pescado'},
        {ingrediente: 'Gambas', alergeno: 'Crustáceos'},
        {ingrediente: 'Merluza', alergeno: 'Pescado'},
        {ingrediente: 'Calamares', alergeno: 'Moluscos'},
        {ingrediente: 'Pulpo', alergeno: 'Moluscos'},
        {ingrediente: 'Claras de huevo', alergeno: 'Huevos'},
        {ingrediente: 'Queso Fresco Batido', alergeno: 'Lácteos'},
        {ingrediente: 'Yogur Griego', alergeno: 'Lácteos'},
        {ingrediente: 'Tofu Firme', alergeno: 'Soja'},
        {ingrediente: 'Soja Texturizada', alergeno: 'Soja'},
        {ingrediente: 'Edamame', alergeno: 'Soja'},
        {ingrediente: 'Avena', alergeno: 'Gluten'},
        {ingrediente: 'Pasta de Trigo Integral', alergeno: 'Gluten'},
        {ingrediente: 'Almendras', alergeno: 'Frutos de cáscara'},
        {ingrediente: 'Crema de Cacahuete', alergeno: 'Cacahuetes'},
        {ingrediente: 'Apio', alergeno: 'Apio'},
        {ingrediente: 'Salsa de Soja', alergeno: 'Soja'},
        {ingrediente: 'Salsa de Soja', alergeno: 'Gluten'},
        {ingrediente: 'Mostaza Antigua', alergeno: 'Mostaza'},
        {ingrediente: 'Semillas de Sésamo', alergeno: 'Granos de sésamo'}
    ] AS rel
    MATCH (i:Ingredient {name: rel.ingrediente})
    MATCH (a:Allergen {name: rel.alergeno})
    MERGE (i)-[:CONTAINS_ALLERGEN]->(a);

    // 5. Crear Recetas Base
    UNWIND [
        {id: 'r1', name: 'Pollo con Arroz', desc: 'Plato básico para ganar masa muscular'},
        {id: 'r2', name: 'Batido de Proteínas con Leche', desc: 'Batido para volumen'},
        {id: 'r3', name: 'Sandwich de Pollo', desc: 'Sandwich clásico'},
        {id: 'r4', name: 'Salmón con Arroz y Nueces', desc: 'Plato rico en omega 3'},
        {id: 'r5', name: 'Avena Nocturna Proteica', desc: 'Desayuno alto en fibra y proteínas. Preparar la noche anterior.'},
        {id: 'r6', name: 'Ensalada de Garbanzos y Tomate', desc: 'Fácil, fresca y rápida, con buena fuente de fibra.'},
        {id: 'r7', name: 'Tofu Salteado al Sésamo', desc: 'Opción vegana alta en proteína.'},
        {id: 'r8', name: 'Tortilla de Claras y Espinacas', desc: 'Corte puro de proteína para déficit calórico.'},
        {id: 'r9', name: 'Pasta Boloñesa Fit', desc: 'Carbohidratos pre-entreno con ternera magra.'},
        {id: 'r10', name: 'Merluza al Horno con Patatas', desc: 'Cena ligera y saciante.'},
        {id: 'r11', name: 'Ensalada Fresca de Atún', desc: 'Comida rápida alta en proteína.'},
        {id: 'r12', name: 'Batido Calórico de Cacahuete', desc: 'Bomba de calorías limpias para fase de volumen.'},
        {id: 'r13', name: 'Fajitas de Pavo', desc: 'Rápido y versátil.'},
        {id: 'r14', name: 'Arroz con Gambas y Ajo', desc: 'Excelente perfil de macronutrientes, muy bajo en grasa.'},
        {id: 'r15', name: 'Yogur Griego con Almendras y Arándanos', desc: 'Snack rico en antioxidantes y grasas saludables.'},
        {id: 'r16', name: 'Salteado de Garbanzos y Espinacas', desc: 'Hierro, fibra y proteína vegetal.'},
        {id: 'r17', name: 'Poke Bowl de Salmón', desc: 'Grasas saludables y alto volumen.'},
        {id: 'r18', name: 'Lentejas Estofadas Fit', desc: 'Plato de cuchara tradicional sin grasas añadidas.'},
        {id: 'r19', name: 'Ensalada Caprese con Queso Batido', desc: 'Versión ligera de la clásica italiana.'},
        {id: 'r20', name: 'Hamburguesa de Ternera al Plato', desc: 'Hamburguesa sin pan para dietas bajas en carbohidratos.'},
        {id: 'r21', name: 'Pudding de Chía y Fresa', desc: 'Postre o desayuno rico en omega 3 vegetal.'},
        {id: 'r22', name: 'Pollo al Curry con Yogur', desc: 'Estilo indio, usando yogur en lugar de nata.'},
        {id: 'r23', name: 'Calamares a la Plancha', desc: 'Proteína pura, ideal para definición.'},
        {id: 'r24', name: 'Puré de Calabacín Alto en Proteína', desc: 'Puré ligero enriquecido con claras.'},
        {id: 'r25', name: 'Tostada de Aguacate y Huevo', desc: 'Desayuno estrella para el balance hormonal.'},
        {id: 'r26', name: 'Boniato Asado con Pollo', desc: 'Carbohidratos de asimilación lenta.'},
        {id: 'r27', name: 'Sopa Depurativa de Apio', desc: 'Sopa de muy bajas calorías para saciedad.'},
        {id: 'r28', name: 'Ensalada de Quinoa y Pimientos', desc: 'Comida de tupper perfecta, perfil de aminoácidos completo.'},
        {id: 'r29', name: 'Pechuga a la Plancha con Brócoli', desc: 'El clásico de los culturistas de la vieja escuela.'},
        {id: 'r30', name: 'Revuelto de Champiñones', desc: 'Cena rápida con mucha fibra.'},
        {id: 'r31', name: 'Batido Verde Detox', desc: 'Vitaminas líquidas, sin proteína añadida.'},
        {id: 'r32', name: 'Merluza con Costra de Almendras', desc: 'Pescado con extra de grasas buenas y textura.'},
        {id: 'r33', name: 'Macarrones con Soja Texturizada', desc: 'Alternativa vegana a la boloñesa tradicional.'},
        {id: 'r34', name: 'Ensalada de Pulpo y Patata', desc: 'Inspiración gallega con macros inmejorables.'}
    ] AS rec
    CREATE (:Recipe {id: rec.id, name: rec.name, description: rec.desc});

    // 6. Vincular Recetas con Ingredientes (Cantidades)
    UNWIND [
        {id: 'r1', ing: 'Pechuga de Pollo', g: 200}, {id: 'r1', ing: 'Arroz Blanco', g: 150},
        {id: 'r2', ing: 'Leche Entera', g: 300}, {id: 'r2', ing: 'Proteina en polvo', g: 30},
        {id: 'r3', ing: 'Pan de Trigo', g: 100}, {id: 'r3', ing: 'Pechuga de Pollo', g: 100},
        {id: 'r4', ing: 'Salmón', g: 200}, {id: 'r4', ing: 'Arroz Blanco', g: 100}, {id: 'r4', ing: 'Nueces', g: 30},
        {id: 'r5', ing: 'Avena', g: 60}, {id: 'r5', ing: 'Leche Entera', g: 200}, {id: 'r5', ing: 'Proteina en polvo', g: 25}, {id: 'r5', ing: 'Semillas de Chía', g: 10},
        {id: 'r6', ing: 'Garbanzos (cocidos)', g: 200}, {id: 'r6', ing: 'Tomate', g: 100}, {id: 'r6', ing: 'Cebolla', g: 50}, {id: 'r6', ing: 'Aceite de Oliva Virgen', g: 10},
        {id: 'r7', ing: 'Tofu Firme', g: 150}, {id: 'r7', ing: 'Brócoli', g: 100}, {id: 'r7', ing: 'Salsa de Soja', g: 15}, {id: 'r7', ing: 'Semillas de Sésamo', g: 5},
        {id: 'r8', ing: 'Claras de huevo', g: 200}, {id: 'r8', ing: 'Huevo de gallina', g: 50}, {id: 'r8', ing: 'Espinacas', g: 80},
        {id: 'r9', ing: 'Pasta de Trigo Integral', g: 80}, {id: 'r9', ing: 'Ternera Magra', g: 150}, {id: 'r9', ing: 'Tomate', g: 150},
        {id: 'r10', ing: 'Merluza', g: 250}, {id: 'r10', ing: 'Patata (cruda)', g: 200}, {id: 'r10', ing: 'Aceite de Oliva Virgen', g: 5},
        {id: 'r11', ing: 'Atún al natural', g: 150}, {id: 'r11', ing: 'Lechuga', g: 100}, {id: 'r11', ing: 'Tomate', g: 100}, {id: 'r11', ing: 'Maíz dulce', g: 50},
        {id: 'r12', ing: 'Leche Entera', g: 300}, {id: 'r12', ing: 'Plátano', g: 120}, {id: 'r12', ing: 'Crema de Cacahuete', g: 30}, {id: 'r12', ing: 'Avena', g: 50},
        {id: 'r13', ing: 'Pechuga de Pavo', g: 150}, {id: 'r13', ing: 'Pimiento Rojo', g: 100}, {id: 'r13', ing: 'Cebolla', g: 50}, {id: 'r13', ing: 'Tortitas de Maíz', g: 60},
        {id: 'r14', ing: 'Arroz Blanco', g: 80}, {id: 'r14', ing: 'Gambas', g: 150}, {id: 'r14', ing: 'Ajo', g: 10},
        {id: 'r15', ing: 'Yogur Griego', g: 200}, {id: 'r15', ing: 'Almendras', g: 20}, {id: 'r15', ing: 'Arándanos', g: 50},
        {id: 'r16', ing: 'Garbanzos (cocidos)', g: 200}, {id: 'r16', ing: 'Espinacas', g: 100}, {id: 'r16', ing: 'Ajo', g: 5}, {id: 'r16', ing: 'Aceite de Oliva Virgen', g: 10},
        {id: 'r17', ing: 'Salmón', g: 150}, {id: 'r17', ing: 'Arroz Blanco', g: 80}, {id: 'r17', ing: 'Aguacate', g: 50}, {id: 'r17', ing: 'Salsa de Soja', g: 15},
        {id: 'r18', ing: 'Lentejas (cocidas)', g: 250}, {id: 'r18', ing: 'Zanahoria', g: 100}, {id: 'r18', ing: 'Patata (cruda)', g: 100}, {id: 'r18', ing: 'Cebolla', g: 50},
        {id: 'r19', ing: 'Tomate', g: 200}, {id: 'r19', ing: 'Queso Fresco Batido', g: 100}, {id: 'r19', ing: 'Aceite de Oliva Virgen', g: 15},
        {id: 'r20', ing: 'Ternera Magra', g: 200}, {id: 'r20', ing: 'Lechuga', g: 50}, {id: 'r20', ing: 'Tomate', g: 50},
        {id: 'r21', ing: 'Leche Entera', g: 150}, {id: 'r21', ing: 'Semillas de Chía', g: 30}, {id: 'r21', ing: 'Fresa', g: 100},
        {id: 'r22', ing: 'Pechuga de Pollo', g: 200}, {id: 'r22', ing: 'Arroz Blanco', g: 80}, {id: 'r22', ing: 'Yogur Griego', g: 100},
        {id: 'r23', ing: 'Calamares', g: 250}, {id: 'r23', ing: 'Ajo', g: 10}, {id: 'r23', ing: 'Limón', g: 20},
        {id: 'r24', ing: 'Calabacín', g: 300}, {id: 'r24', ing: 'Patata (cruda)', g: 100}, {id: 'r24', ing: 'Claras de huevo', g: 100},
        {id: 'r25', ing: 'Pan de Trigo', g: 60}, {id: 'r25', ing: 'Aguacate', g: 50}, {id: 'r25', ing: 'Huevo de gallina', g: 100},
        {id: 'r26', ing: 'Boniato (crudo)', g: 250}, {id: 'r26', ing: 'Pechuga de Pollo', g: 150}, {id: 'r26', ing: 'Aceite de Oliva Virgen', g: 5},
        {id: 'r27', ing: 'Apio', g: 150}, {id: 'r27', ing: 'Zanahoria', g: 100}, {id: 'r27', ing: 'Cebolla', g: 100},
        {id: 'r28', ing: 'Quinoa (cruda)', g: 80}, {id: 'r28', ing: 'Pimiento Rojo', g: 100}, {id: 'r28', ing: 'Tomate', g: 50}, {id: 'r28', ing: 'Zanahoria', g: 50},
        {id: 'r29', ing: 'Pechuga de Pollo', g: 200}, {id: 'r29', ing: 'Brócoli', g: 200}, {id: 'r29', ing: 'Aceite de Oliva Virgen', g: 10},
        {id: 'r30', ing: 'Huevo de gallina', g: 150}, {id: 'r30', ing: 'Champiñones', g: 150}, {id: 'r30', ing: 'Ajo', g: 5},
        {id: 'r31', ing: 'Manzana', g: 100}, {id: 'r31', ing: 'Espinacas', g: 50}, {id: 'r31', ing: 'Apio', g: 50}, {id: 'r31', ing: 'Limón', g: 20},
        {id: 'r32', ing: 'Merluza', g: 200}, {id: 'r32', ing: 'Almendras', g: 20}, {id: 'r32', ing: 'Limón', g: 10},
        {id: 'r33', ing: 'Pasta de Trigo Integral', g: 80}, {id: 'r33', ing: 'Soja Texturizada', g: 50}, {id: 'r33', ing: 'Tomate', g: 150},
        {id: 'r34', ing: 'Pulpo', g: 200}, {id: 'r34', ing: 'Patata (cruda)', g: 150}, {id: 'r34', ing: 'Aceite de Oliva Virgen', g: 15}
    ] AS rel
    MATCH (r:Recipe {id: rel.id})
    MATCH (i:Ingredient {name: rel.ing})
    MERGE (r)-[:CONTAINS_INGREDIENT {grams: rel.g}]->(i);

    // 7. Crear Tipos de Dieta y Reglas de Exclusión Dinámicas
    CREATE (vegan:DietType {name: 'Vegana'})
    CREATE (vegetarian:DietType {name: 'Vegetariana'})
    CREATE (carnivore:DietType {name: 'Carnivora'})
    CREATE (mediterranean:DietType {name: 'Mediterranea'});

    // Reglas Vegana
    MATCH (vegan:DietType {name: 'Vegana'})
    MATCH (i_animal:Ingredient {origen: 'animal'})
    MERGE (vegan)-[:EXCLUDES]->(i_animal);

    // Reglas Vegetariana
    MATCH (vegetarian:DietType {name: 'Vegetariana'})
    MATCH (i_animal_veg:Ingredient {origen: 'animal'})
    WHERE NOT i_animal_veg.categoria IN ['huevos', 'lacteos', 'miel']
    MERGE (vegetarian)-[:EXCLUDES]->(i_animal_veg);

    // Reglas Carnivora
    MATCH (carnivore:DietType {name: 'Carnivora'})
    MATCH (i_vegetal:Ingredient {origen: 'vegetal'})
    MERGE (carnivore)-[:EXCLUDES]->(i_vegetal);

    // Nodos estáticos de Nutrientes
    CREATE (:Nutrient {name: 'Proteínas'})
    CREATE (:Nutrient {name: 'Carbohidratos'})
    CREATE (:Nutrient {name: 'Grasas'});
    """

    async with driver.session() as session:
        await session.run(query_clear)

        # 1. Crear Admin y Alérgenos
        for q in query_admin_and_allergens.split(';'):
            q = q.strip()
            if q:
                await session.run(q)

        # 2. Crear los 40 usuarios con biometría hardcodeada
        await session.run(query_create_users, users=HARDCODED_USERS)

        # 3. Vincular las intolerancias de los usuarios
        await session.run(query_link_intolerances, users=HARDCODED_USERS)

        # 4. Crear ingredientes, recetas, tipos de dieta y reglas
        for q in query_graph_content.split(';'):
            q = q.strip()
            if q:
                await session.run(q)

        logger.info("Base de datos de prueba creada y poblada correctamente con datos hardcodeados.")
