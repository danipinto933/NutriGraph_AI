---
description: Microservicio AI Agent Service (GraphRAG, Tool Calling, Streaming SSE)
---

Fase 4: Microservicio ai-agent-service
Objetivo

Construir el agente conversacional personalizado con GraphRAG, invocación de herramientas (Tool Calling), memoria en Redis y respuestas en streaming.
Instrucciones para el Agente

    Crea la estructura en services/ai-agent-service/.

    Configura el orquestador de LLM (LangChain / LlamaIndex).

    Implementa herramientas (Tools) explícitas para que el agente consulte al nutrition-graph-service en lugar de deducir valores nutricionales:

        buscar_receta_por_macros

        verificar_compatibilidad_alimento

        obtener_desglose_receta

    Configura Redis para guardar el historial conversacional por sesión (session_id).

    Implementa el endpoint en streaming: POST /api/v1/chat/stream utilizando StreamingResponse de FastAPI con Server-Sent Events (SSE).

    Crea el Dockerfile y añade tests con pytest.

Criterios de Verificación

    Prueba del endpoint SSE comprobando el envío de chunks de texto en formato text/event-stream.

    Test de invocación de herramientas para confirmar que el LLM consulta el servicio de grafos antes de responder.