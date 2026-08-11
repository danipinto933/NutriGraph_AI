(function (window) {
  window.__env = window.__env || {};

  var isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

  // Configuración de URLs de la API para desarrollo local y producción (Render)
  window.__env.apiUrl = window.__env.apiUrl || (isLocal ? 'http://localhost:8000/api/v1' : 'https://user-auth-service-a6cx.onrender.com/api/v1');
  window.__env.graphApiUrl = window.__env.graphApiUrl || (isLocal ? 'http://localhost:8001/api/v1' : 'https://nutrition-graph-service.onrender.com/api/v1');
  window.__env.chatApiUrl = window.__env.chatApiUrl || (isLocal ? 'http://localhost:8002/api/v1' : 'https://ai-agent-service-tvtg.onrender.com/api/v1');
})(this);
