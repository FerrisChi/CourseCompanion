<!-- MainComponent.vue -->
<template>
  <v-card>
    <v-layout>
      <v-navigation-drawer v-model="drawer" :rail="rail" permanent @click="rail = false">
        <v-list density="compact" nav>
          <v-list-item prepend-icon="mdi-restart" title="New Conversation" value="new_conv" @click="resetConversation">
            <template v-slot:append>
              <v-btn variant="text" icon="mdi-chevron-left" @click.stop="rail = !rail"></v-btn>
            </template>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="uploadModal = true" prepend-icon="mdi-upload" title="Upload Transcript"
            value="account"></v-list-item>
        </v-list>
      </v-navigation-drawer>
      <v-main style="height: calc(100vh - 65px)">


        <v-dialog v-model="uploadModal" max-width="500">
          <v-card>
            <v-card-title>Upload Transcript</v-card-title>
            <v-file-input v-model="selectedFile" :rules="rules" accept="application/pdf" placeholder="Upload Transcript"
              prepend-icon="mdi-upload" label="Upload PDF Transcript"></v-file-input>
            <v-card-actions>
              <v-btn @click="uploadModal = false">Close</v-btn>
              <v-spacer></v-spacer>
              <v-btn @click="submitFile">Upload</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-main>
    </v-layout>
  </v-card>
</template>

<script>
import axiosCom from "@/components/axios"
import { useEventBus } from "@/eventBus";
export default {
  data() {
    return {
      drawer: true,
      rail: true,
      uploadModal: false,
      selectedFile: null,
      rules: [
        // required: value => !!value || 'File is required',
        // sizeLimit: value => (!value || value.size < 2000000) || 'File size should be less than 2MB', // Example size limit rule
        // Add more rules as needed
      ],
    };
  },
  methods: {
    submitFile() {
      if (!this.selectedFile) {
        alert("Please select a file first.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile[0]);

      // Example of sending the file to a server endpoint
      // Replace with your actual upload logic
      axiosCom.post('/chatbot/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(res => {
          console.log("File uploaded successfully", res.data);
          this.uploadModal = false;
        })
        .catch(err => {
          console.error("Error uploading file", err);
        });
    },
    resetConversation() {
      const bus = useEventBus();
      bus.$emit("reset-conversation");
      this.selectedFile = null;
      axiosCom.post('/chatbot/reset')
        .then(res => {
          console.log("Conversation reset successfully", res.data);
        })
        .catch(err => {
          console.error("Error resetting conversation", err);
        });
    }
  }
};
</script>
