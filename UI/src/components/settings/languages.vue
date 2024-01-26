<template>
  <v-dialog v-model="selectLanguageDialog">
    <template v-slot:activator="{ props }">
      <v-list-item
        v-bind="props"
        rounded="xl"
        prepend-icon="mdi-translate"
        :title="$t('language')"
      ></v-list-item>
    </template>
    <v-card>
      <v-toolbar>
        <v-btn icon @click="closeDialog">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{ $t('language') }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn variant="text" @click="closeDialog">Save</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-list>
        <v-list-item v-for="l in locales" :key="l.code" :title="l.name" :append-icon="radioIcon(l.code)"
          @click="updateLocale(l.code)">
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from "vue";
import { useI18n } from 'vue-i18n';
import { locales } from '@/plugins/i18n';

const selectLanguageDialog = ref(false);
const { locale } = useI18n();

const closeDialog = () => {
  selectLanguageDialog.value = false;
};

const updateLocale = (lang) => {
  locale.value = lang;
  closeDialog();
};

const radioIcon = (code) => {
  return code === locale.value ? 'mdi-checkbox-marked-circle' : 'mdi-checkbox-blank-circle';
};
</script>

<style scoped>
/* Your styles here */
</style>
