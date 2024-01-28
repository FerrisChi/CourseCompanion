<template>
  <v-app>
    <v-app-bar flat class="container">
      <div class="logo-and-title">
        <v-img class="logo" width="60" src="@/assets/Robot.png" />
        <span class="title">CampusCompanion</span>
      </div>

      <v-spacer></v-spacer>
      <!-- Display user name if logged in -->
      <span v-if="isLoggedIn">{{ userName }}</span>

      <!-- Conditional Button for Login/Logout -->
      <v-btn v-if="!isLoggedIn" @click="openLoginDialog" color="primary" variant="flat">Login</v-btn>
      <v-btn v-else @click="logout">Logout</v-btn>

      <!-- Login Dialog -->
      <login-dialog :open-dialog="loginDialog" @update:openDialog="loginDialog = $event"/>
    </v-app-bar>

    <default-view />
  </v-app>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
}

.logo-and-title {
  display: flex;
  align-items: center;
}

.logo {
  margin-right: 10px; /* Adjust spacing between logo and title */
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #000000; /* Set text color to white */
}
</style>

<script setup>
import DefaultView from './View.vue';

import { computed, ref } from 'vue';
import { useStore } from 'vuex';
import LoginDialog from '@/components/LoginDialog.vue';

const store = useStore();

// Computed properties for reactive Vuex state
const isLoggedIn = computed(() => store.getters.isLoggedIn);
const userName = computed(() => store.getters.userName);
const loginDialog = ref(false);

// Methods to dispatch Vuex actions
const openLoginDialog = () => {
  loginDialog.value = true;
  // store.dispatch('login', 'User123'); // Replace 'User123' with actual user name
};

const logout = () => {
  store.dispatch('logout');
};
</script>
