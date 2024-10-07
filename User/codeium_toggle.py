import sublime
import sublime_plugin
from Codeium.login import CodeiumSettings

class CodeiumToggleCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        # Toggle the Codeium enable setting
        CodeiumSettings.enable = not CodeiumSettings.enable
        
        # Save the settings
        sublime.save_settings("Codeium.sublime-settings")
        
        # Provide feedback to the user
        status = "habilitado" if CodeiumSettings.enable else "deshabilitado"
        sublime.status_message(f"Codeium {status}")
        print(f"Codeium {status}")

class CodeiumStatusListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        self.update_status(view)
    
    def on_modified_async(self, view):
        self.update_status(view)
    
    def update_status(self, view):
        if CodeiumSettings.enable:
            view.set_status('codeium', 'Codeium: Activo')
        else:
            view.erase_status('codeium')