// axios.js

import axios from 'axios';

const axiosCom = axios.create({
  baseURL: 'https://127.0.0.1:1234',
  // Other configuration options like headers, timeouts, etc.
});

axiosCom.defaults.withCredentials = true;

// Interceptors (if needed)
// For example, to handle authentication or manipulate requests globally
// instance.interceptors.request.use(...);
// instance.interceptors.response.use(...);

export default axiosCom;
