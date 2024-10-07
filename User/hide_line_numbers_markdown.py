import sublime
import sublime_plugin

class HideLineNumbersAndDisableAutocompleteForMarkdown(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.file_name().endswith('.md'):
            settings = view.settings()
            settings.set('line_numbers', False)
            settings.set('auto_complete', False)

# Este plugin se activará cada vez que se abra un archivo