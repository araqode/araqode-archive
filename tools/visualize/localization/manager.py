import importlib

class LocalizationManager:
    """
    Language options.
    """
    def __init__(self, fall_back):
        """
        Initialize the LocalizationManager.

        Args:
            fall_back: Fallback localization.
        """
        self.available = {
            'english/india': lambda : importlib.import_module('tools.visualize.localization.english.india'),
        }
        self.current_locale = None
        self.fall_back = fall_back

    def load_locale(self, language: str):
        """
        Load a specific localization.

        Args:
            language (str): Localization language.
        """
        self.current_locale = self.available.get(language, lambda: self.fall_back)()
    
    def __getattr__(self, key: str):
        """
        Retrieve the attribute from the current locale, falling back to the default if not found.

        Args:
            key (str)   : Attribute key.
        
        Returns:
            str         : Locale string corresponding to the key.
        """
        if self.current_locale and hasattr(self.current_locale, key):
            return getattr(self.current_locale, key)
        if hasattr(self.fall_back, key):
            return getattr(self.fall_back, key)
        return f"nolocale[{key}]"