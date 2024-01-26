<template>
  <div class="container">
    <router-view />
  </div>
</template>

<style>
.container::-webkit-scrollbar {
  display: none;
}

/* Optional: Add vendor prefixes for other browsers */
.container {
  scrollbar-width: none; /* Firefox */
}
</style>
<script setup>
  //
</script>
