from .cluster_api import Cluster_API
from .cluster_html import Cluster_HTML


class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.cluster_api = Cluster_API(fhdhr, plugin_utils)
        self.cluster_html = Cluster_HTML(fhdhr, plugin_utils)
