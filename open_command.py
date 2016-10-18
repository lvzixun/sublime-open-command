import re
import os
import sublime, sublime_plugin


def get_settings():
    ret = sublime.load_settings("open_command.sublime-settings")
    sublime.save_settings("open_command.sublime-settings")
    return ret


class OpenComplexFromUi(sublime_plugin.TextCommand):
    settings = get_settings()
    rawres_path = settings.get("rawres_path")
    default_regex = re.compile(r"^\s*--\s*file:\s*(.+)$")

    def __init__(self, arg):
        sublime_plugin.TextCommand.__init__(self, arg)
        self.drive = []
        open_config_list = self.settings.get("open_config", []) or []
        for entry in open_config_list:
            exe = entry["exe"]
            regex = entry["regex"]
            rg_exp = r"^\s*--\s*file:\s*({0})".format(regex)
            self.drive.append({"exe": exe, "regex": re.compile(rg_exp)})


    def match_open(self, cur_line_str):
        for entry in self.drive:
            ret = entry["regex"].search(cur_line_str)
            if ret != None:
                path = os.path.join(self.rawres_path, entry["exe"])
                return [path, ret.group(1)]
        
        ret = self.default_regex.search(cur_line_str)
        if ret != None:
            return [os.path.join(self.rawres_path, ret.group(1))]
        else:
            return None


    def run(self, edit):
        cur_line_str = self.view.substr(self.view.line(self.view.sel()[0]))
        ret = self.match_open(cur_line_str)
        if ret != None:
            command = " ".join(ret)
            print(command)
            os.popen(command)

