---
description: Inicialización del Monorepo e Infraestructura Base con Docker
---

Fase 1: Estructura de Monorepo e Infraestructura Base
Objetivo

Configurar la raíz del proyecto NutriGraph AI y desplegar la pila de infraestructura base con Docker Compose.
Instrucciones para el Agente

    Crea la estructura de directorios del monorepo:

        config/traefik/

        config/consul/

        services/user-auth-service/

        services/nutrition-graph-service/

        services/ai-agent-service/

        frontend/angular-app/

    Genera el archivo docker-compose.yml en la raíz con los siguientes servicios:

        Traefik (v2.10): API Gateway en puerto 80 con dashboard en :8080.

        HashiCorp Consul: Discovery & Config Server en puerto :8500.

        Neo4j (5.x): Base de datos de grafos con plugin APOC habilitado en puertos :7474 (HTTP) y :7687 (Bolt).

        Redis 7: Caché en puerto :6379.

        Apache Kafka: Broker de eventos en modo KRaft (sin Zookeeper) en puerto :9092.

    Genera un archivo .env.example centralizado con todas las variables requeridas (credenciales Neo4j, secretos JWT, puertos, URLs de Redis y Kafka).

Criterios de Verificación

    Genera y muestra los comandos terminales para ejecutar docker-compose up -d.

    Indica las URLs para verificar visualmente Traefik Dashboard (:8080), Consul (:8500) y Neo4j Browser (:7474).