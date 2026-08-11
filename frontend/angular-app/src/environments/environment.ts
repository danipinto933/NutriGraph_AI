const isBrowser = typeof window !== 'undefined';
const browserEnv = (isBrowser && (window as any).__env) || {};
const isLocalhost = isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const apiUrl = browserEnv.apiUrl || 'http://localhost:8000/api/v1';
const graphApiUrl = browserEnv.graphApiUrl || 'http://localhost:8001/api/v1';
const chatApiUrl = browserEnv.chatApiUrl || 'http://localhost:8002/api/v1';

if (isBrowser && !isLocalhost && apiUrl.includes('localhost')) {
  console.warn(
    '[NutriGraph AI] ALERTA DE CONFIGURACIÓN DE RENDER:\n' +
    'La aplicación se está ejecutando en ' + window.location.origin + ' pero API_URL apunta a ' + apiUrl + '.\n' +
    'Debes configurar la variable de entorno API_URL en el Dashboard de Render con la URL pública HTTPS de tu microservicio backend.'
  );
}

export const environment = {
  production: false,
  apiUrl,
  graphApiUrl,
  chatApiUrl
};
