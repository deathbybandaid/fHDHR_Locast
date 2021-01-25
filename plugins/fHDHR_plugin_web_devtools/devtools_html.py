from flask import request, render_template_string, session
import pathlib
from io import StringIO


class DevTools_HTML():
    endpoints = ["/devtools", "/devtools.html"]
    endpoint_name = "devtools_html"
    endpoint_access_level = 2
    pretty_name = "Dev Tools"
    endpoint_category = "pages"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.template_file = pathlib.Path(plugin_utils.config.dict["plugin_web_paths"][plugin_utils.namespace]["path"]).joinpath('devtools.html')
        self.template = StringIO()
        self.template.write(open(self.template_file).read())

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr)
