<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-card>
      <v-card-title class="headline">Login</v-card-title>
      <v-card-text>
        <v-text-field
          label="Username"
          v-model="username"
        ></v-text-field>
        <v-text-field
          label="Email"
          v-model="email"
        ></v-text-field>
        <form>
        <v-text-field
          label="Password"
          v-model="password"
          :rules="[rules.required]"
          type="password"
          placeholder="your password"
          autocomplete="off"
        ></v-text-field>
        </form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="login">Login</v-btn>
        <v-btn color="secondary" text @click="loginWithGoogle">Login with Google</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axiosCom from "@/components/axios";
import { useStore } from 'vuex';

const store = useStore();

const props = defineProps({
  openDialog: Boolean
});

const dialog = ref(props.openDialog);
const username = ref('');
const password = ref('');
const email = ref('');
const client_id = ref('');

const rules = {
  required: value => !!value || 'Required.',
};

const emit = defineEmits(['update:openDialog', 'login']);

watch(() => props.openDialog, (newVal) => {
  dialog.value = newVal;
});

const login = async () => {
  // You can add more login logic here

  // REST CALL
  try {
    console.log(`Logging Django in with ${username.value} at ${email.value} and ${password.value}`);

    console.log(`Client ID: ${store.getters.djangoClientId}`);

    const response = await axiosCom.post('/users/login/', {
      username: username.value,
      email: email.value,
      password: password.value,
      client_id: store.getters.djangoClientId
    }, {
      withCredentials: true
    });
    
    const {access_token, refresh_token} = response.data;
    console.log(`Access token: ${access_token}`);
    console.log(`Refresh token: ${refresh_token}`);

    store.commit('loginUser', username.value)
    store.commit('setTokens', {access_token, refresh_token});

    axiosCom.interceptors.request.use(config => {
      config.headers.Authorization = `Bearer ${access_token}`;
      return config;
    });

  } catch (err) {
    error.value = err.message;
    console.log(error.value);
  }
  emit('update:openDialog', false);
};

const loginWithGoogle = async () => {

}

</script>
