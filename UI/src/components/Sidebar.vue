<!-- MainComponent.vue -->
<template>
  <v-card>
    <v-layout>
      <v-navigation-drawer v-model="drawer" :rail="rail" permanent @click="rail = false" width=365>
        <v-list density="compact" nav>
          <v-list-item prepend-icon="mdi-restart" prepend title="New Conversation" value="new_conv" @click="createConversation">
            <template v-slot:append>
              <v-btn variant="text" icon="mdi-chevron-left" @click.stop="rail = !rail"></v-btn>
            </template>
          </v-list-item>
          <v-list-item @click="uploadModal = true" prepend-icon="mdi-upload" title="Upload Transcript"
            value="account"></v-list-item>
        </v-list>

        <v-divider></v-divider>

        <div class="px-2">
          <v-list>
            <v-list-item v-show="loadingConversations">
              <v-list-item-title class="d-flex justify-center">
                <v-progress-circular indeterminate></v-progress-circular>
              </v-list-item-title>
            </v-list-item>
          </v-list>

          <!-- show conversations with title -->
          <v-list nav>
            <template
                v-for="(conversation, cIdx) in conversations"
                :key="conversation.id"
            >
              <v-list-item
                  color="primary"
                  rounded="xl"
                  v-if="editingConversation && editingConversation.id === conversation.id"
              >
                <v-text-field
                    v-model="editingConversation.title"
                    :loading="editingConversation.updating"
                    variant="underlined"
                    append-icon="mdi-check"
                    hide-details
                    density="compact"
                    autofocus
                    @keyup.enter="updateConversationTitle(cIdx)"
                    @click:append="updateConversationTitle(cIdx)"
                ></v-text-field>
              </v-list-item>
              <v-hover
                  v-if="!editingConversation || editingConversation.id !== conversation.id"
                  v-slot="{ isHovering, props }"
              >
                <v-list-item
                    rounded="xl"
                    color="primary"
                    @click="loadConversations(conversation.id)"
                    v-bind="props"
                >
                  <v-list-item-title>{{ (conversation.title && conversation.title !== '') ? conversation.title : $t('defaultConversationTitle') }}</v-list-item-title>
                  <template v-slot:append>
                    <div
                        v-show="isHovering && conversation.id"
                    >
                      <v-btn
                          icon="mdi-pencil"
                          size="small"
                          variant="text"
                          @click.prevent="editConversation(cIdx)"
                      >
                      </v-btn>
                      <v-btn
                          icon="mdi-delete"
                          size="small"
                          variant="text"
                          :loading="deletingConversationIndex === cIdx"
                          @click.prevent="deleteConversation(cIdx)"
                      >
                      </v-btn>
                      <v-btn
                          icon="mdi-download"
                          size="small"
                          variant="text"
                          @click.prevent="exportConversation(cIdx)"
                      >
                      </v-btn>
                    </div>
                  </template>
                </v-list-item>
              </v-hover>
            </template>
          </v-list>
        </div>

        <!-- settings menu -->
        <template v-slot:append>
          <v-expansion-panels style="flex-direction: column;">
            <v-expansion-panel>
              <v-expansion-panel-title class="panelTitle" expand-icon="mdi-plus" collapse-icon="mdi-minus">
                    <v-icon color="primary">mdi-cog</v-icon>
                    <span>{{ $t("settingDraw") }}</span>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div class="px-1">
          
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

                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </template>
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
import { ref, computed } from "vue";
import { useStore } from "vuex";
import axiosCom from "@/components/axios"
import { useEventBus } from "@/eventBus";
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

const loadingConversations = ref(false)
const bus = useEventBus();


// for conversation list
const store = useStore()
const conversations = computed(() => store.state.conversations)
const editingConversation = ref(false)
const deletingConversationIndex = ref(false)

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

const createConversation = async () => {
  const res = await axiosCom.post('/chatbot/conversations/', {});
  store.commit('addConversation', res.data);
  loadConversations(res.data.id)
}

const loadConversations = async (conversationId) => {
  loadingConversations.value = true
  store.dispatch('fetchMessages', conversationId)
  loadingConversations.value = false
}


const feedback = () => {
  window.open('https://github.com/FerrisChi/CourseCompanion/issues', '_blank')
}

const editConversation = (index) => {
  editingConversation.value = conversations.value[index]
}

const updateConversationTitle = async (index) => {
  editingConversation.value.updating = true
  try {
    const res = await axiosCom.patch('/chatbot/conversations/' + editingConversation.value.id + '/', {
      title: editingConversation.value.title,
    });
    let conversation = res.data
    store.commit('setConversation', {index, conversation});
    editingConversation.value = false
  } catch (err) {
    console.error(err)
    editingConversation.value.updating = false
  }
}

const deleteConversation = async (index) => {
  deletingConversationIndex.value = index
  const deletingConversationId = conversations.value[index].id

  try {
    const res = await axiosCom.delete('/chatbot/conversations/'+deletingConversationId+'/', {})
    store.commit('deleteConversation', index)
  } catch(err) {    
    console.error(err)
  }
  deletingConversationIndex.value = false
}

const exportConversation = async (index) => {
  let conversation = conversations.value[index]
  let data = {}
  data.conversation_topic = conversation.title
  data.messages = []
  let messages = await loadMessage(conversation.id)
  for (let message of messages) {
    let msg = {}
    msg.role = message.is_bot ? "assistant" : "user"
    msg.content = message.message
    data.messages.push(msg)
  }
  let file_content = JSON.stringify(data)
  let file_name = `${conversation.title}_${new Date()}`.replace(/[\/\\:*?"<>]/g, "_")
  const element = document.createElement('a');
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(file_content),
  );
  element.setAttribute("download", file_name);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}
</script>
