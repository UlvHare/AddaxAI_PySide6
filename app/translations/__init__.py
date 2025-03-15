class TranslationManager:
    def __init__(self):
        self.languages = {
            'en': 'English',
            'es': 'Español',
            'ru': 'Русский'
        }
        self.current_language = 'en'
        self._translations = {}
        self._load_translations()

    def _load_translations(self):
        # Import all language modules
        from . import en, es, ru
        self._translations = {
            'en': en.TRANSLATIONS,
            'es': es.TRANSLATIONS,
            'ru': ru.TRANSLATIONS
        }

    def set_language(self, lang_code):
        if lang_code in self.languages:
            self.current_language = lang_code
            return True
        return False

    def get_text(self, key, *args):
        translation = self._translations.get(self.current_language, {}).get(key)
        if translation is None:
            # Fallback to English
            translation = self._translations.get('en', {}).get(key, key)

        # Format with args if provided
        if args:
            try:
                return translation.format(*args)
            except:
                return translation
        return translation

    def get_languages(self):
        return self.languages

    def get_current_language(self):
        return self.current_language

    def get_current_language_name(self):
        return self.languages.get(self.current_language, 'English')

    def get_next_language(self):
        language_codes = list(self.languages.keys())
        current_index = language_codes.index(self.current_language)
        next_index = (current_index + 1) % len(language_codes)
        return language_codes[next_index]

    def get_next_language_name(self):
        next_lang = self.get_next_language()
        return self.languages.get(next_lang, 'English')

# Create a global instance
translation_manager = TranslationManager()

# Helper function for easier access
def tr(key, *args):
    return translation_manager.get_text(key, *args)
