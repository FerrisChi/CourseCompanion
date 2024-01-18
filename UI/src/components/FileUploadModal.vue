<!-- FileUploadModal.vue -->
<template>
    <v-dialog v-model="uploadModal" max-width="500">
      <v-card>
        <v-card-title>Upload Transcript</v-card-title>
        <!-- Add your file upload form or component here -->
        <v-card-actions>
          <v-btn @click="closeUploadModal">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>
  
  <script>
  export default {
    props: {
      value: Boolean,
    },
    computed: {
      uploadModal: {
        get() {
          return this.value;
        },
        set(value) {
          this.$emit("input", value);
        },
      },
    },
    methods: {
      closeUploadModal() {
        this.uploadModal = false;
        this.$emit("close");
      },
    },
  };
  </script>
  