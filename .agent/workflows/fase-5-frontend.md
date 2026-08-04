---
description: Frontend Angular (Signals, Onboarding, Chat SSE)
---

Fase 5: Frontend Angular
Objetivo

Desarrollar la aplicación cliente en Angular con arquitectura reactiva, flujo de onboarding interactivo y chat en tiempo real.
Instrucciones para el Agente

    Inicializa la app Angular en frontend/angular-app/ utilizando Standalone Components, Angular Signals y RxJS.

    Implementa los módulos y vistas principales:

        Autenticación: Pantallas de Login y Registro con AuthGuard e Interceptor JWT.

        Wizard de Onboarding: Formulario por pasos (Metas de peso, Parámetros biométricos basales, Pantalla de resultado IMC/TMB y Selección de intolerancias).

        Chat Conversacional: Interfaz de chat que consume el flujo SSE (EventSource / fetch asíncrono) actualizando la UI de manera continua mediante Signals.

        Fichas de Recetas: Componente visual para mostrar fichas de comida con gráficos/badges del desglose calórico y macros (proteínas, grasas, carbohidratos).

    Configura pruebas unitarias con Jasmine/Jest y pruebas End-to-End (E2E) con Playwright.

Criterios de Verificación

    Comprobación del flujo e2e en navegador: Registro -> Onboarding -> Visualización de IMC -> Interacción con el Chat en streaming.