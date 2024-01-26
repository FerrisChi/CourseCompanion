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
          <v-list-item @click="uploadModal = true" prepend-icon="mdi-upload" title="Upload Transcript"
            value="account"></v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-expansion-panels style="flex-direction: column;">
          <v-expansion-panel rounded="rounded-pill">
            <v-expansion-panel-title class="panelTitle" expand-icon="mdi-plus" collapse-icon="mdi-minus">
                  <!-- <svg-icon type="mdi" :path="settingspath"></svg-icon> -->
                  <v-icon>mdi-cog-outline</v-icon>
                  <span>{{ $t("settingDraw") }}</span>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="px-1">
                <v-list density="compact">
        
                  <v-dialog
                      v-model="clearConfirmDialog"
                      persistent
                  >
                    <template v-slot:activator="{ props }">
                      <v-list-item
                          v-bind="props"
                          rounded="xl"
                          prepend-icon="mdi-delete"
                          :title="$t('clearConversations')"
                      ></v-list-item>
                    </template>
                    <v-card>
                      <v-card-title class="text-h5">
                        Are you sure you want to delete all conversations?
                      </v-card-title>
                      <v-card-text>This will be a permanent deletion and cannot be retrieved once deleted. Please proceed with caution.</v-card-text>
                      <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            color="green-darken-1"
                            variant="text"
                            @click="clearConfirmDialog = false"
                            class="text-none"
                        >
                          Cancel deletion
                        </v-btn>
                        <v-btn
                            color="green-darken-1"
                            variant="text"
                            @click="clearConversations"
                            class="text-none"
                            

                            
                        >
                          Confirm deletion
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-dialog>

                  <!-- <v-list-item
                    rounded="xl"
                    prepend-icon="input"
                    :title="$t('importConversation')"
                    @click="openImportFileChooser()"
                  ></v-list-item> -->
        
                  <!-- <ApiKeyDialog
                      v-if="$settings.open_api_key_setting === 'True'"
                  /> -->
        
                  <!-- <ModelParameters/> -->
        
                  <!-- <v-menu
                  >
                    <template v-slot:activator="{ props }">
                      <v-list-item
                          v-bind="props"
                          rounded="xl"
                          :title="$t('themeMode')"
                      >
                        <template v-slot:prepend>
                          <v-icon
                              v-show="$colorMode.value === 'light'"
                              icon="light_mode"
                          ></v-icon>
                          <v-icon
                              v-show="$colorMode.value !== 'light'"
                              icon="dark_mode"
                          ></v-icon>
                        </template>
                      </v-list-item>
                    </template>
                    <v-list
                        bg-color="white"
                    >
                      <v-list-item
                          v-for="(theme, idx) in themes"
                          :key="idx"
                          @click="setTheme(theme.value)"
                      >
                        <v-list-item-title>{{ theme.title }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu> -->

                  <SettingsLanguages/>
        
                  <v-list-item
                      rounded="xl"
                      prepend-icon="mdi-help-circle"
                      :title="$t('feedback')"
                      @click="feedback"
                  ></v-list-item>

                </v-list>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
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

<style scoped>

.panelTitle > span {
  margin-left: 20px;
  text-align: center;
  vertical-align: middle; /* Align the text with the icon */
}


</style>

<script setup>
import { ref } from "vue";
import axiosCom from "@/components/axios"
import { useEventBus } from "@/eventBus";
import SvgIcon from '@jamescoyle/vue-icon'
import { mdiCogOutline } from '@mdi/js'
import SettingsLanguages from "@/components/settings/languages.vue"

const drawer = ref(true)
const rail = ref(true)
const uploadModal = ref(false)
const selectedFile = ref(null)
const rules = ref([
  // required: value => !!value || 'File is required',
  // sizeLimit: value => (!value || value.size < 2000000) || 'File size should be less than 2MB', // Example size limit rule
  // Add more rules as needed
])
const clearConfirmDialog = ref(false)
const colorMode = ref('light')
  // settingspath: mdiCogOutline,

const submitFile = () => {
  if (!selectedFile) {
    alert("Please select a file first.");
    return;
  }
  const formData = new FormData();
  formData.append("file", selectedFile[0]);

  // Example of sending the file to a server endpoint
  // Replace with your actual upload logic
  axiosCom.post('/chatbot/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
    .then(res => {
      console.log("File uploaded successfully", res.data);
      uploadModal = false;
    })
    .catch(err => {
      console.error("Error uploading file", err);
    });
}

const resetConversation = () => {
  const bus = useEventBus();
  bus.$emit("reset-conversation");
  selectedFile = null;
  axiosCom.post('/chatbot/reset')
    .then(res => {
      console.log("Conversation reset successfully", res.data);
    })
    .catch(err => {
      console.error("Error resetting conversation", err);
    });
}

const feedback = () => {
  window.open('https://github.com/FerrisChi/CourseCompanion/issues', '_blank')
}
</script>
