import { createStore } from "vuex";
import axiosCom from "@/components/axios"

const store = createStore({
  state: {
    djangoClientId: import.meta.env.VITE_DJANGO_CLIENT_ID,
    user: {
      isLoggedIn: false,
      name: 'Please login',
    },
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    conversations: [],
    messages: [],
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
    },
    setMessage(state, messages) {
      state.messages = messages;
    },
    addMessage(state, message) {
      state.messages.push(message);
    },
    setConversationList(state, convs) {
      state.conversations = convs;
    },
    setConversation(state, {idx, conv}) {
      state.conversations[idx] = conv;
    },
    
  },
  actions: {
    login({ commit }, userName) {
      commit('loginUser', userName);
    },
    
    logout({ commit }) {
      commit('logoutUser');
    },

    async fetchMessagesList({ commit }) {
      try {
        const res = await axiosCom.get('/chatbot/conversations/list/');
        console.log(res.data);
        commit('setConversationList', res.data);
      } catch (err) {
        console.log('Error fetching conversations:', err);
      }
    },

    async fetchMessages({ commit }, {conversationId}) {
      try {
        const res = await axiosCom.get('/chatbot/conversations/' + conversationId + '/messages/')
        // console.log(res.data)
        commit('setMessage', res.data)
      } catch (err) {
        console.log('Error fetching conversation:', err)
      }
    },

    async sendMessage({ commit}, {conversationId, inputReq, isGraduateFlag}) {
      try {
        const res = await axiosCom.post('/chatbot/conversations/' + conversationId + '/messages/create/', {
          content: inputReq,
          isGraduate: isGraduateFlag,
          is_from_user: true,
          conversation: conversationId,
        });
        // console.log(res.data);
        commit('addMessage', res.data);
      } catch (err) {
        console.log('Error sending message:', err);
      }
    }
  },
  getters: {
    isLoggedIn: state => state.user.isLoggedIn,
    userName: state => state.user.name,
    djangoClientId: state => state.djangoClientId,
  },
});

export default store;