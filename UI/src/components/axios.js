// axios.js

import axios from 'axios';

const axiosCom = axios.create({
  baseURL: 'http://127.0.0.1:1234',
  // Other configuration options like headers, timeouts, etc.
});

// Interceptors (if needed)
// For example, to handle authentication or manipulate requests globally
// instance.interceptors.request.use(...);
// instance.interceptors.response.use(...);

export default axiosCom;
