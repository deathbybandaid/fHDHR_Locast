from flask import request, render_template_string, session
import urllib.parse
from simplejson.errors import JSONDecodeError
import pathlib
from io import StringIO


class Cluster_HTML():
    endpoints = ["/cluster", "/cluster.html"]
    endpoint_name = "page_cluster_html"
    endpoint_access_level = 1
    endpoint_category = "pages"
    pretty_name = "Cluster/SSDP"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.location_dict = {
                              "name": self.fhdhr.config.dict["fhdhr"]["friendlyname"],
                              "location": self.fhdhr.api.base,
                              "joined": "N/A",
                              "url_query": self.fhdhr.api.base_quoted
                              }

        self.template_file = pathlib.Path(plugin_utils.config.dict["plugin_web_paths"][plugin_utils.namespace]["path"]).joinpath('cluster.html')
        self.template = StringIO()
        self.template.write(open(self.template_file).read())

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        locations_list = []

        if self.fhdhr.config.dict["fhdhr"]["discovery_address"]:

            locations_list.append(self.location_dict)

            fhdhr_list = self.fhdhr.device.interfaces[self.plugin_utils.namespace].get_list()
            for location in list(fhdhr_list.keys()):

                if location in list(self.fhdhr.device.interfaces[self.plugin_utils.namespace].cluster().keys()):
                    location_name = self.fhdhr.device.interfaces[self.plugin_utils.namespace].cluster()[location]["name"]
                else:
                    try:
                        location_info_url = "%s/discover.json" % location
                        location_info_req = self.fhdhr.web.session.get(location_info_url)
                        location_info = location_info_req.json()
                        location_name = location_info["FriendlyName"]
                    except self.fhdhr.web.exceptions.ConnectionError:
                        self.fhdhr.logger.error("Unreachable: %s" % location)
                    except JSONDecodeError:
                        self.fhdhr.logger.error("Unreachable: %s" % location)
                location_dict = {
                                "name": location_name,
                                "location": location,
                                "joined": str(fhdhr_list[location]["Joined"]),
                                "url_query": urllib.parse.quote(location)
                                }
                locations_list.append(location_dict)

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr, locations_list=locations_list)
