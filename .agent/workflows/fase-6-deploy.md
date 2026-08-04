---
description: API Gateway, Observabilidad, Tracing y Kubernetes Manifests
---

Fase 6: Gateway, Observabilidad y Despliegue
Objetivo

Consolidar el enrutamiento centralizado en Traefik, agregar monitoreo/tracing y generar manifiestos de Kubernetes para producción.
Instrucciones para el Agente

    Configura en config/traefik/traefik.yml las reglas de enrutamiento dinámico:

        /api/v1/auth/* -> user-auth-service

        /api/v1/nutrition/* -> nutrition-graph-service

        /api/v1/chat/* -> ai-agent-service

    Añade instrumentación de observabilidad y tracing con OpenTelemetry en los microservicios FastAPI.

    Configura métricas expuestas para Prometheus y dashboard básico en Grafana.

    Genera el directorio k8s/ con los manifiestos de Kubernetes (o Helm Charts):

        Deployments, Services, ConfigMaps, Secrets, Ingress para cada servicio.

Criterios de Verificación

    Verificar la comunicación fluida del sistema a través de un único puerto mediante Traefik.

    Comprobar la existencia y validez sintáctica de los manifiestos YAML de Kubernetes.

¿Cómo utilizarlos en Antigravity IDE?

    En la raíz de tu proyecto, crea la carpeta .agent/workflows/.  

    Guarda cada uno de los 6 bloques anteriores en su archivo correspondiente (ejemplo: .agent/workflows/fase-1-infra.md).  

    Abre el panel de Antigravity en tu IDE y escribe /fase-1-infra para iniciar la construcción de la primera fase.