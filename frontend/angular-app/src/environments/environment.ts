const isBrowser = typeof window !== 'undefined';
const browserEnv = (isBrowser && (window as any).__env) || {};
const isLocalhost = isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const defaultApiUrl = isLocalhost ? 'http://localhost:8000/api/v1' : 'https://user-auth-service-a6cx.onrender.com/api/v1';
const defaultGraphUrl = isLocalhost ? 'http://localhost:8001/api/v1' : 'https://nutrition-graph-service.onrender.com/api/v1';
const defaultChatUrl = isLocalhost ? 'http://localhost:8002/api/v1' : 'https://ai-agent-service-tvtg.onrender.com/api/v1';

const apiUrl = browserEnv.apiUrl || defaultApiUrl;
const graphApiUrl = browserEnv.graphApiUrl || defaultGraphUrl;
const chatApiUrl = browserEnv.chatApiUrl || defaultChatUrl;

export const environment = {
  production: !isLocalhost,
  apiUrl,
  graphApiUrl,
  chatApiUrl
};
