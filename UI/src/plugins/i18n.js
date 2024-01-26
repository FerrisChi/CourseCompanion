import { createI18n } from 'vue-i18n'

import en from '../lang/en.json'
import zh from '../lang/zh.json'
import fr from '../lang/fr.json'
import ru from '../lang/ru.json'

const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages: {
        en,
        zh,
        fr,
        ru,
    }
})

export const locales = [
    {code: 'en', name: 'English'},
    {code: 'zh', name: '中文'},
    {code: 'fr', name: 'Français'},
    {code: 'ru', name: 'русский'},
]

export default i18n