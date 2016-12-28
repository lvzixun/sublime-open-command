import re
import os
import socket
import sublime, sublime_plugin


def get_settings():
    ret = sublime.load_settings("sublime-open-command.sublime-settings")
    return ret


# 远程打开UI
class OpenComplexByRemoteui(sublime_plugin.TextCommand):
    def __init__(self, arg):
        sublime_plugin.TextCommand.__init__(self, arg)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, msg):
        settings = get_settings()
        host = settings.get("remote_config")["host"]
        port = settings.get("remote_config")["port"]
        self.sock.sendto(bytes(msg, "utf-8"), (host, port))

    def run(self, edit):
        cur_word = self.view.substr(self.view.word(self.view.sel()[0]))
        cmd = "hydrarnan:%s" % cur_word
        self.send_message(cmd)



# 本地进行匹配打开UI
class OpenComplexByLocalui(sublime_plugin.TextCommand):
    default_regex = re.compile(r"^\s*--\s*file:\s*(.+)$")

    def __init__(self, arg):
        sublime_plugin.TextCommand.__init__(self, arg)
        self.drive = []
        self.settings = get_settings()
        self.rawres_path = self.settings.get("rawres_path")

        open_config_list = self.settings.get("open_config", []) or []
        for entry in open_config_list:
            exe = entry["exe"]
            regex = entry["regex"]
            use_current_path = 'use_current_path' in entry and entry["use_current_path"] or False
            self.drive.append({"exe": exe, "regex": re.compile(regex), "use_current_path":use_current_path})


    def match_open(self, cur_line_str):
        file_name = self.view.file_name()
        cur_dir = os.path.dirname(file_name)
        for entry in self.drive:
            ret = entry["regex"].search(cur_line_str)
            if ret != None:
                exe_path = entry["exe"]
                cur_path = entry["use_current_path"] and cur_dir or self.rawres_path
                target_path = os.path.join(cur_path, ret.group(1))
                return [exe_path, target_path]
        
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

