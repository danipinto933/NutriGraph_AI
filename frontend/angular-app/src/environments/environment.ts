const isBrowser = typeof window !== 'undefined';
const browserEnv = (isBrowser && (window as any).__env) || {};
const isLocalhost = isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const defaultApiUrl = isLocalhost ? 'http://localhost:8000/api/v1' : '';
const defaultGraphUrl = isLocalhost ? 'http://localhost:8001/api/v1' : '';
const defaultChatUrl = isLocalhost ? 'http://localhost:8002/api/v1' : '';

const apiUrl = browserEnv.apiUrl || defaultApiUrl;
const graphApiUrl = browserEnv.graphApiUrl || defaultGraphUrl;
const chatApiUrl = browserEnv.chatApiUrl || defaultChatUrl;

if (isBrowser && !isLocalhost && (!apiUrl || apiUrl.includes('localhost'))) {
  console.warn(
    '[NutriGraph AI] ALERTA DE CONFIGURACIÓN DE RENDER:\n' +
    'La aplicación se está ejecutando en ' + window.location.origin + ' pero API_URL no está configurada o apunta a localhost.\n' +
    'Debes configurar la variable de entorno API_URL en el Dashboard de Render con la URL pública HTTPS de tu microservicio backend.'
  );
}

export const environment = {
  production: false,
  apiUrl,
  graphApiUrl,
  chatApiUrl
};
