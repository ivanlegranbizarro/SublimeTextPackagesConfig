import sublime
import sublime_plugin

class CloseAllButActiveView(sublime_plugin.WindowCommand):
    def run(self):
        windows = sublime.windows()
        active_window = sublime.active_window()
        active_view_id = active_window.active_view().id()

        for window in windows:
            for view in window.views():
                if view.id() != active_view_id:
                    window.focus_view(view)
                    window.run_command("close")

        active_window.focus_view(active_window.active_view())