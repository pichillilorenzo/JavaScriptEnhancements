import sublime, sublime_plugin
import webbrowser, os
from urllib.parse import urlencode
from ..libs import javaScriptEnhancements
from ..libs import util

# Carbon language mapping
LANGUAGE_MAPPING = {
    'Auto': 'auto',
    'Apache': 'text/apache',
    'Shell-Unix-Generic': 'application/x-sh',
    'Plain text': 'text',
    'C': 'text/x-csrc',
    'C++': 'text/x-c++src',
    'C#': 'text/x-csharp',
    'Clojure': 'clojure',
    'Cobol': 'cobol',
    'CoffeeScript': 'coffeescript',
    'Crystal': 'crystal',
    'CSS': 'css',
    'D': 'd',
    'Dart': 'dart',
    'Diff': 'text/x-diff',
    'Django': 'django',
    'Docker': 'dockerfile',
    'Elixir': 'elixir',
    'Elm': 'elm',
    'Erlang': 'erlang',
    'Fortran': 'fortran',
    'F#': 'mllike',
    'OCaml': 'mllike',
    'GraphQL': 'graphql',
    'Go': 'go',
    'Groovy': 'groovy',
    'Handlebars': 'handlebars',
    'Haskell': 'haskell',
    'Haxe': 'haxe',
    'HTML': 'htmlmixed',
    'Java': 'text/x-java',
    'JavaScript': 'javascript',
    'JavaScript (Babel)': 'javascript',
    'JavaScriptNext': 'javascript',
    'JSON': 'application/json',
    'JSON (Sublime)': 'application/json',
    'JSX': 'jsx',
    'Julia': 'julia',
    'Kotlin': 'text/x-kotlin',
    'Lisp': 'commonlisp',
    'Lua': 'lua',
    'Markdown': 'markdown',
    'Mathematica': 'mathematica',
    'MySQL': 'text/x-mysql',
    'NGINX': 'nginx',
    'Nim': 'nimrod',
    'Objective-C': 'text/x-objectivec',
    'Pascal': 'pascal',
    'Perl': 'perl',
    'PHP': 'text/x-php',
    'PowerShell': 'powershell',
    'Python': 'python',
    'R': 'r',
    'Ruby': 'ruby',
    'Rust': 'rust',
    'Sass': 'sass',
    'Scala': 'text/x-scala',
    'Smalltalk': 'smalltalk',
    'SQL': 'sql',
    'Swift': 'swift',
    'TCL': 'tcl',
    'TypeScript': 'application/typescript',
    'VB.NET': 'vb',
    'Verilog': 'verilog',
    'VHDL': 'vhdl',
    'Vue': 'vue',
    'XML': 'xml',
    'YAML': 'yaml'
}

class JavascriptEnhancementsCarbonCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        view = self.view
        whitespace = ""
        body = ""
        code = ""

        if view.sel()[0].begin() != view.sel()[0].end():
            whitespace = util.convert_tabs_using_tab_size(view, util.get_whitespace_from_line_begin(view, view.sel()[0]))
            body = view.substr(view.sel()[0])
        else:
            body = view.substr(sublime.Region(0, view.size()))

        body = util.convert_tabs_using_tab_size(view, body.strip())

        # Put only about 3400 characters on the URL string. More than that won't work (in that case use https://carbon.now.sh directly).
        body = body[0:3400]
        
        for line in body.splitlines():
            line = line.rstrip()
            index_start = len(whitespace) if code else 0
            code += line[index_start:] + "\n"

        carbon_url = 'https://carbon.now.sh/?'
        language = javaScriptEnhancements.get('carbon_language')

        if not language:
            syntax = os.path.splitext(os.path.basename(view.settings().get("syntax")))[0]
            if syntax in LANGUAGE_MAPPING:
                language = LANGUAGE_MAPPING[syntax]
            else:
                language = 'auto'

        query = {
            'bg'  : javaScriptEnhancements.get('carbon_background_color'),
            't'   : javaScriptEnhancements.get('carbon_theme'),
            'l'   : language,
            'ds'  : javaScriptEnhancements.get('carbon_drop_shadow'),
            'wc'  : javaScriptEnhancements.get('carbon_window_controls'),
            'wa'  : javaScriptEnhancements.get('carbon_width_adjustment'),
            'pv'  : javaScriptEnhancements.get('carbon_padding_vertical'),
            'ph'  : javaScriptEnhancements.get('carbon_padding_horizontal'),
            'ln'  : javaScriptEnhancements.get('carbon_line_numbers'),
            'code': code
        }

        webbrowser.open(carbon_url + urlencode(query))

