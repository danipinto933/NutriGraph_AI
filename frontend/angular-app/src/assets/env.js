(function (window) {
  window.__env = window.__env || {};

  // Environment variables for local development
  window.__env.apiUrl = 'http://localhost:8000/api/v1';
  window.__env.graphApiUrl = 'http://localhost:8001/api/v1';
  window.__env.chatApiUrl = 'http://localhost:8002/api/v1';
})(this);
