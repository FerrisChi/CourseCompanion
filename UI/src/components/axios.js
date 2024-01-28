// axios.js

import axios from 'axios';

const axiosCom = axios.create({
  baseURL: 'https://127.0.0.1:1234',
  withCredentials: true,  // for cookies
  // Other configuration options like headers, timeouts, etc.
});

// Interceptors (if needed)
// For example, to handle authentication or manipulate requests globally

// interceptor for oauth is handled in LoginDialog.vue
// axiosCom.interceptors.response.use(
//   response => {
//       // Check if the response contains a new access token
//       console.log('new access token intercepted from axios.js')
//       const newAccessToken = response.data.newAccessToken;
//       if (newAccessToken) {
//           localStorage.setItem('accessToken', newAccessToken);
//       }
//       return response;
//   },
//   error => {
//       // Handle errors
//       return Promise.reject(error);
//   }
// );

// axiosCom.interceptors.request.use(
//   config => {
//       const token = localStorage.getItem('accessToken');
//       if (token) {
//           config.headers.Authorization = `Bearer ${token}`;
//       }
//       return config;
//   },
//   error => {
//       return Promise.reject(error);
//   }
// );



export default axiosCom;
