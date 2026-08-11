const browserEnv = (typeof window !== 'undefined' && (window as any).__env) || {};

export const environment = {
  production: false,
  apiUrl: browserEnv.apiUrl || 'http://localhost:8000/api/v1',       // User Auth Service
  graphApiUrl: browserEnv.graphApiUrl || 'http://localhost:8001/api/v1',  // Nutrition Graph Service
  chatApiUrl: browserEnv.chatApiUrl || 'http://localhost:8002/api/v1'    // AI Agent Service
};
