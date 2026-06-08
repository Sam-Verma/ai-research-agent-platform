// API Configuration - dynamically uses the current host
export const getApiBaseUrl = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = window.location.port ? `:${window.location.port}` : '';
  
  // If accessed via frontend port (like 5173 in dev), use port 8000 for backend
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//127.0.0.1:8000`;
  }
  
  // For network access, use the same hostname but with backend port
  return `${protocol}//${hostname}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();
