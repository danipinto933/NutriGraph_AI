(function (window) {
  window.__env = window.__env || {};

  // Plantilla de variables de entorno inyectadas en tiempo de ejecución por Render / Docker
  window.__env.apiUrl = '${API_URL}';
  window.__env.graphApiUrl = '${GRAPH_API_URL}';
  window.__env.chatApiUrl = '${CHAT_API_URL}';
})(this);
