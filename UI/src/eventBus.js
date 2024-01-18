import { reactive, readonly } from 'vue';

const state = reactive({});

export const eventBus = {
  $on: (event, callback) => {
    if (!state[event]) state[event] = [];
    state[event].push(callback);
  },
  $emit: (event, payload) => {
    if (state[event]) {
      state[event].forEach(callback => callback(payload));
    }
  }
};

export const useEventBus = () => {
  return readonly(eventBus);
};
