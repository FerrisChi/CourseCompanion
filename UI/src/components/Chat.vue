<template>
  <v-container class="fill-height">
    <v-responsive class="align-center text-center">
      <div class="chat-container">
        <div class="welcome-message" :class="{ 'bot-bubble': true }">
          <div class="text-body-2 font-weight-light mb-n1 white-text">Welcome to</div>
          <h1 class="text-h2 font-weight-bold white-text">CampusCompanion</h1>
        </div>
        <chatWindow :conversation="conversation" />
      </div>
      <div class="py-14" />
    </v-responsive>
    <v-text-field v-model="newMessageText" color="primary" label="Chat" variant="filled" class="chat-input"
      @keydown.enter="sendMessage"
      :append-inner-icon="newMessageText ? 'mdi-send' : 'mdi-microphone'"
      clear-icon="mdi-close-circle"
      clearable
      @click:append-inner="sendMessage">
      <template #append>
        <v-row align="center" class="slider">
          <v-col class="text-right">
            <span>Undergraduate</span>
          </v-col>
          <v-col>
            <v-switch v-model="isGraduate" color="primary"></v-switch>
          </v-col>
          <v-col>
            <span>Graduate</span>
          </v-col>
        </v-row>
      </template>
    </v-text-field>
  </v-container>
</template>

<style scoped>
.align-center {
  align-items: center;
}

.slider {
  padding-left: 100px;
  margin-top:-10px;
  display: flex;
  flex-direction:row;
}

.text-center {
  text-align: center;
}

.fill-height {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.welcome-message {
  background-color: #a1a0a0;
  border-radius: 15px;
  padding: 10px;
  margin-bottom: 10px;
  position: sticky;
  top: 0;
  z-index: 2;
}

.chat-input {
  width: 70vw;
  margin: auto;
  position: absolute;
  left: 50%;
  transform: translateX(calc(-35vw + 100px));
  bottom: 10px;
  z-index: 1;
}

.chat-window {
  overflow-y: auto;
  flex-grow: 1;
  max-height: 70vh
}

/* Hide scrollbar for Chrome, Safari, and Opera */
.chat-window::-webkit-scrollbar {
  width: 0;
}


.message-container:hover .timestamp {
  opacity: 1;
  /* Show timestamp on hover */
}

.white-text {
  color: #fff;
  /* Set text color to white */
}

.scale-enter-active,
.scale-leave-active {
  transform: scale(1);
  transition: transform 0.2s;
}

.scale-enter,
.scale-leave-to {
  transform: scale(0.8);
}
</style>

<script setup>
import chatWindow from "./ChatWindow.vue";
import { ref } from "vue";
import axiosCom from "@/components/axios"
import { useEventBus } from "@/eventBus";

const newMessageText = ref("");
const conversation = ref({
  messages: [
    { is_bot: true, message: "Hi there! How can I assist you today with course recommendations?" },
  ],
});
const error = ref(null);
const isGraduate = ref(false);

const sendMessage = async () => {
  const  message = {
    is_bot: false,
    message: newMessageText.value.trim()
  };

  if (message.message !== "") {
     conversation.value.messages = [
      ...conversation.value.messages,
      message,
    ];

    // REST CALL
    newMessageText.value = "";
    try {
      console.log(message.message)
      // wait for axios to return
      let inputReq = message.message;
      if (conversation.value.messages.length === 2) {
        const level = isGraduate.value ? "graduate" : "undergraduate";
        inputReq = inputReq + ". I am doing a " + level + " degree";
      }

      const response = await axiosCom.post('/chatbot/chat/', {
        message: inputReq,
        isGraduate: isGraduate.value
      }, {
        withCredentials: true
      });
      console.log(response.data.message)
      const botMessage = {
        is_bot: true,
        message: response.data.message,
      };
      conversation.value.messages = [
      ...conversation.value.messages,
      botMessage,
    ];
    } catch (err) {
      error.value = err.message;
      console.log(error.value);
    }
  }
};

const bus = useEventBus();
bus.$on("reset-conversation", () => {
  // Logic to reset the conversation in chat.vue
  conversation.value.messages = [
    { is_bot: true, message: "Hi there! How can I assist you today with Course Recommendations?" }
  ];
  error.value = null;
  newMessageText.value = "";
  isGraduate.value = false;

});
</script>
