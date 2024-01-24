import { createStore } from "vuex";

const store = createStore({
  state: {
    djangoClientId: import.meta.env.VITE_DJANGO_CLIENT_ID,
    user: {
      isLoggedIn: false,
      name: 'Please login',
    },
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken')
  },
  mutations: {
    loginUser(state, userName) {
      state.user.isLoggedIn = true;
      state.user.name = userName;
    },
    logoutUser(state) {
      state.user.isLoggedIn = false;
      state.user.name = 'Please login';
    },
    setTokens(state, { accessToken, refreshToken }) {
      state.accessToken = accessToken;
      state.refreshToken = refreshToken;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    },
    clearTokens(state) {
      state.accessToken = null;
      state.refreshToken = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  },
  actions: {
    login({ commit }, userName) {
      // Implement login logic here, then commit
      commit('loginUser', userName);
    },
    logout({ commit }) {
      // Implement logout logic here, then commit
      commit('logoutUser');
    },
  },
  getters: {
    isLoggedIn: state => state.user.isLoggedIn,
    userName: state => state.user.name,
    djangoClientId: state => state.djangoClientId,
  },
});

export default store;