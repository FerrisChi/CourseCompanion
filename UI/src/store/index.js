import { createStore } from "vuex";
import axiosCom from "@/components/axios"

const store = createStore({
  state: {
    djangoClientId: import.meta.env.VITE_DJANGO_CLIENT_ID,
    user: {
      isLoggedIn: false,
      name: 'Please login',
    },
    accessToken: sessionStorage.getItem('accessToken'),
    refreshToken: sessionStorage.getItem('refreshToken'),
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
      state.accessToken = null;
      state.refreshToken = null;
      sessionStorage.removeItem('accessToken');
      sessionStorage.removeItem('refreshToken');
    },
    setTokens(state, { accessToken, refreshToken }) {
      state.accessToken = accessToken;
      state.refreshToken = refreshToken;
      sessionStorage.setItem('accessToken', accessToken);
      sessionStorage.setItem('refreshToken', refreshToken);
    },
    setMessage(state, messages) {
      state.messages = messages;
    },
    addMessage(state, message) {
      state.messages.push(message);
    },
    addConversation(state, conversation) {
      state.conversations.push(conversation);
    },
    setConversationList(state, convs) {
      state.conversations = convs;
    },
    setConversation(state, {index, conversation}) {
      state.conversations[index] = conversation;
    },
    deleteConversation(state, index) {
      state.conversations.splice(index, 1);
    },
  },
  actions: {
    login({ commit }, userName) {
      commit('loginUser', userName);
    },
    
    logout({ commit }) {
      commit('logoutUser');
    },

    async fetchConversationList({ commit }) {
      try {
        const res = await axiosCom.get('/chatbot/conversations/list/');
        // console.log(res.data);
        commit('setConversationList', res.data);
      } catch (err) {
        console.log('Error fetching conversations:', err);
      }
    },

    async fetchMessages({ commit }, conversationId) {
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
    },
  },
  getters: {
    isLoggedIn: state => state.user.isLoggedIn,
    userName: state => state.user.name,
    djangoClientId: state => state.djangoClientId,
  },
});

export default store;