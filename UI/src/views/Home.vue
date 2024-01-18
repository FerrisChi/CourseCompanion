<template>
  <div class="container">
    <Sidebar/>
    <Chat/>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  overflow: hidden;
  height: 93vh;
  
}
</style>

<script>
  import Sidebar from '@/components/Sidebar.vue'
  import Chat from '@/components/Chat.vue'

  export default {
  components: {
    Sidebar,
    Chat,
  }
};
</script>