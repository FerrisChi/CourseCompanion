<template>
  <v-dialog v-model="loginDialog" persistent max-width="500px">
    <v-container fluid>
      <v-card>
        <v-card-title class="headline">
          <v-container>
            <v-row>
              <div>{{$t('logIn')}}</div>
              <v-spacer></v-spacer>
              <v-btn @click="signupDialog = true; loginDialog = false" variant="text" color="primary">Don't have an account? Sign up</v-btn>
            </v-row>
          </v-container>
        </v-card-title>
        
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
          <v-btn color="blue" text @click="closeDialog">Close</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="login">{{$t('logIn')}}</v-btn>
          <v-btn color="secondary" text @click="loginWithGoogle">{{$t('logInWithGoogle')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
  </v-dialog>

  <v-dialog v-model="signupDialog" persistent max-width="500px">
    <v-container fluid>
      <v-row>
        <v-col
            sm="9"
            offset-sm="1"
            md="6"
            offset-md="3"
        >
          <v-card>
            <v-card-title class="headline">
              <div>{{$t('Create your account')}}</div>
            </v-card-title>
            <v-card-text>
              <v-form ref="signUpForm">
                <v-text-field
                    v-model="formData.username"
                    :rules="formRules.username"
                    :error-messages="fieldErrors.username"
                    :label="$t('username')"
                    @update:modelValue="handleFieldUpdate('username')"
                    clearable
                ></v-text-field>

                <v-text-field
                    v-model="formData.email"
                    :rules="formRules.email"
                    :error-messages="fieldErrors.email"
                    :label="$t('email')"
                    @update:modelValue="handleFieldUpdate('email')"
                    clearable
                ></v-text-field>

                <v-text-field
                    v-model="formData.password1"
                    :rules="formRules.password1"
                    :error-messages="fieldErrors.password1"
                    :label="$t('password')"
                    @update:modelValue="handleFieldUpdate('password1')"
                    clearable
                ></v-text-field>

                <v-text-field
                    v-model="formData.password2"
                    :rules="formRules.password2"
                    :error-messages="fieldErrors.password2"
                    :label="$t('confirmPassword')"
                    @update:modelValue="handleFieldUpdate('password2')"
                    clearable
                ></v-text-field>

<!--                <v-text-field-->
<!--                    v-model="formData.code"-->
<!--                    :rules="formRules.code"-->
<!--                    :label="$t('invitation code')"-->
<!--                    variant="underlined"-->
<!--                    @keyup.enter="submit"-->
<!--                    clearable-->
<!--                ></v-text-field>-->

              </v-form>

              <div v-if="errorMsg" class="text-red">{{ errorMsg }}</div>

              <div
                  class="mt-5 d-flex justify-space-between"
              >
                <v-btn
                    @click="loginDialog = true; signupDialog = false"
                    variant="text"
                    color="primary"
                >{{$t('Sign in instead')}}</v-btn>

                <v-btn
                    color="primary"
                    :loading="submitting"
                    @click="submit"
                >{{$t('signUp')}}</v-btn>
              </div>

            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axiosCom from "@/components/axios";
import { useStore } from 'vuex';
import { useI18n } from 'vue-i18n';

const store = useStore();
const { t } = useI18n();

const props = defineProps({
  openDialog: Boolean
});

const loginDialog = ref(props.openDialog);
const signupDialog = ref(false);
const username = ref('');
const password = ref('');
const email = ref('');
const client_id = ref('');

const formData = ref({
  username: '',
  email: '',
  password1: '',
  password2: '',
  code:'',
})

const fieldErrors = ref({
  username: '',
  email: '',
  password1: '',
  password2: '',
  code:'',
})
const submitting = ref(false)
const errorMsg = ref(null)
const signUpForm = ref(null)

const formRules = ref({
  username: [
    v => !!v || t('Please enter your username'),
    v => v.length >= 4 || t('Username must be at least 4 characters')
  ],
  email: [
    v => !!v || t('Please enter your e-mail address'),
    v => /.+@.+\..+/.test(v) || t('E-mail address must be valid')
  ],
  password1: [
    v => !!v || t('Please enter your password'),
    v => v.length >= 8 || t('Password must be at least 8 characters')
  ],
  password2: [
    v => !!v || t('Please confirm your password'),
    v => v.length >= 8 || t('Password must be at least 8 characters'),
    v => v === formData.value.password1 || t('Confirm password must match password')
  ],
  code: [
    v => !!v || t('Please enter your code'),
  ],
})


const rules = {
  required: value => !!value || 'Required.',
};

const emit = defineEmits(['update:openDialog']);

const closeDialog = () => {
  emit('update:openDialog', false);
};

watch(() => props.openDialog, (newVal) => {
  loginDialog.value = newVal;
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
    
    store.dispatch('fetchConversationList')
    emit('update:openDialog', false);
  } catch (err) {
    errorMsg.value = err.message;
    console.log(errorMsg.value);
  }
};

const loginWithGoogle = async () => {

}

const handleFieldUpdate = (field) => {
  fieldErrors.value[field] = ''
}

const submit = async () => {
  errorMsg.value = null
  const { valid } = await signUpForm.value.validate()
  if (valid) {
    submitting.value = true

    try {
      const res = await axiosCom.post('/users/register/', {
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password1,
        code: formData.value.code,
      })

      store.commit('loginUser', res.data['username'])
      store.commit('setTokens', {access_token: res.data['access_token'], refresh_token: res.data['refresh_token']});

      axiosCom.interceptors.request.use(config => {
        config.headers.Authorization = `Bearer ${res.data['access_token']}`;
        return config;
      });
      signupDialog.value = false
    } catch (err) {
      console.log(err)
      if (err.response.status === 400) {
        for (const key in formData.value) {
          if (err.response.data[key]) {
            fieldErrors.value[key] = t(err.response.data[key][0])
          }
        }
        if (err.response.data.non_field_errors) {
          errorMsg.value = t(err.response.data.non_field_errors[0])
        }
      } else {
        if (err.response.data.detail) {
          errorMsg.value = t(err.response.data.detail)
        } else {
          errorMsg.value = 'Something went wrong. Please try again.'
        }
      }
    }
      // navigateTo('/account/onboarding?email_verification_required='+data.value.email_verification_required)

    submitting.value = false
  }
}
</script>
