<script setup>
import { ref, watch, onMounted, defineProps } from "vue";
import botIcon from '@/assets/cap-logo.svg';
import userIcon from '@/assets/person-icon.png';

const props = defineProps(["conversation"]);
const chatWindow = ref(null);

onMounted(() => {
  scrollToEnd();
});

watch(() => props.conversation.messages, () => {
  scrollToEnd();
});

function scrollToEnd() {
  const element = chatWindow.value;
  if (element) {
    element.scrollTop = element.scrollHeight;
  }
}
</script>

<script>
export default {
  methods: {
    containsArray(message) {
      try {
        const parsedArray = JSON.parse(message.message);
        return Array.isArray(parsedArray);
      } catch (error) {
        return false; // Handle the case when the string is not valid JSON
      }
    },
  },
};
</script>

<template>
  <div v-if="conversation.messages" ref="chatWindow" class="chat-window">
    <v-container>
      <v-row>
        <v-col v-for="(message, index) in conversation.messages" :key="index" cols="12">
          <div :class="['bubble', message.is_bot ? 'bot-bubble' : 'user-bubble']">
            <div class="header">
              <v-img class="icon" :src="message.is_bot ? botIcon : userIcon" width="40" height="40"></v-img>
              <div class="content">
                <div class="user-info">
                  <span class="user-type">{{ message.is_bot ? 'CampusCompanion' : 'Student' }}</span>
                </div>
                <div>
              <div v-if="containsArray(message)">
                <table>
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Name</th>
                      <th>Score</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in JSON.parse(message.message)" :key="index">
                      <td>{{ item.code }}</td>
                      <td>{{ item.name }}</td>
                      <td>{{ item.score }}</td>
                      <td>{{ item.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text">{{ message.message }}</div>
            </div>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <div style="height: 200px; overflow-y: auto;"></div>
  </div>
</template>

<style scoped>
.icon {
  align-self: flex-start;
}

.content {
  display: flex;
  flex-direction: column;
}

.user-info {
  margin-left: 10px;
}

.user-type {
  font-weight: bold;
  margin-right: 5px;
  color: #ffffff; /* Set text color to white */
}

.text {
  margin-top: 4px;
  margin-bottom: 4px;
  margin-left: 10px;
  color: #ffffff;
  word-wrap: break-word; 
  width:600px;
}

.header {
  display: flex;
  align-items: center;
}

.bubble {
  display: flex;
  margin: 0 auto; /* Center horizontally */
  margin-bottom: -8px; /* Adjusted margin to make bubbles closer together */
  overflow: hidden;
  position: relative;
  transition: transform 0.2s ease-in-out; /* Smooth transition effect */
  width: 700px; /* Limit the maximum width */
  align-self: center;
}

.bubble:hover {
  transform: scale(1.02); /* Scale up on hover for a subtle effect */
}

.bot-bubble, .user-bubble {
  background-color: #a1a0a0;
  border-radius: 15px;
  padding: 10px;
  max-width: 70%;
  margin-bottom: 10px;
  align-self: flex-start; /* Align bubbles on the left */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle box shadow */
  position: relative;
}

.bot-bubble {
  background-color: #2196F3;
  color: #fff;
}

.user-bubble .icon {
  filter: brightness(0) invert(1);
}

.user-bubble::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-right: 2px solid transparent; /* Transparent border initially */
  animation: typing 1s infinite; /* Typing animation */
}

@keyframes typing {
  0% {
    border-color: transparent; /* Transparent at the beginning */
  }
  50% {
    border-color: #a1a0a0; /* Color when halfway through */
  }
  100% {
    border-color: transparent; /* Transparent at the end */
  }
}

.chat-window {
  width: 70vw;
  justify-self: center;
}

table {
  width: calc(100% - 20px);
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  
  padding: 8px;
  text-align: left;
}

th {
  background-color: #1870b8;
}

.bubble table {
  margin: 10px 0;
}

.bubble table tr {
 background-color: #7ab4f5;
}

.bubble table tr:nth-child(even) {
  background-color: #1870b8; /* Light gray background for alternating rows */
}
</style>
