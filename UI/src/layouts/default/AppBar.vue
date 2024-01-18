<template>
  <v-app>
    <v-app-bar flat class="container">
      <div class="logo-and-title">
        <v-img class="logo" width="60" src="@/assets/Robot.png" />
        <span class="title">CampusCompanion</span>
      </div>
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
</script>
