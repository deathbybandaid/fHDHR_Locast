from gevent.pywsgi import WSGIServer
from flask import Flask, request, session
import threading
import uuid

from .pages import fHDHR_Pages
from .files import fHDHR_Files
from .brython import fHDHR_Brython
from .rmg import fHDHR_RMG
from .api import fHDHR_API


fHDHR_web_VERSION = "v0.8.1-beta"


class fHDHR_HTTP_Server():
    app = None

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.template_folder = fhdhr.config.internal["paths"]["www_templates_dir"]

        self.fhdhr.logger.info("Loading Flask.")

        self.fhdhr.app = Flask("fHDHR", template_folder=self.template_folder)
        self.instance_id = str(uuid.uuid4())

        # Allow Internal API Usage
        self.fhdhr.app.testing = True
        self.fhdhr.api.client = self.fhdhr.app.test_client()

        # Set Secret Key For Sessions
        self.fhdhr.app.secret_key = self.fhdhr.config.dict["fhdhr"]["friendlyname"]

        self.route_list = {}

        self.endpoints_obj = {}
        self.endpoints_obj["pages"] = fHDHR_Pages(fhdhr)
        self.endpoints_obj["files"] = fHDHR_Files(fhdhr)
        self.endpoints_obj["brython"] = fHDHR_Brython(fhdhr)
        self.endpoints_obj["rmg"] = fHDHR_RMG(fhdhr)
        self.endpoints_obj["api"] = fHDHR_API(fhdhr)

        self.selfadd_web_plugins()
        for endpoint_type in list(self.endpoints_obj.keys()):
            self.fhdhr.logger.info("Loading HTTP %s Endpoints." % endpoint_type)
            self.add_endpoints(endpoint_type)

        self.fhdhr.app.before_request(self.before_request)
        self.fhdhr.app.after_request(self.after_request)
        self.fhdhr.app.before_first_request(self.before_first_request)

        self.fhdhr.threads["flask"] = threading.Thread(target=self.run)

    def selfadd_web_plugins(self):
        for plugin_name in list(self.fhdhr.plugins.plugins.keys()):
            if self.fhdhr.plugins.plugins[plugin_name].type == "web":
                method = self.fhdhr.plugins.plugins[plugin_name].name.lower()
                plugin_utils = self.fhdhr.plugins.plugins[plugin_name].plugin_utils
                print(self.fhdhr.plugins.plugins[plugin_name].plugin_name)
                self.endpoints_obj[method] = self.fhdhr.plugins.plugins[plugin_name].Plugin_OBJ(self.fhdhr, plugin_utils)

    def start(self):
        self.fhdhr.logger.info("Flask HTTP Thread Starting")
        self.fhdhr.threads["flask"].start()

    def stop(self):
        self.fhdhr.logger.info("Flask HTTP Thread Stopping")
        self.http.stop()

    def before_first_request(self):
        self.fhdhr.logger.info("HTTP Server Online.")

    def before_request(self):

        session["session_id"] = str(uuid.uuid4())
        session["instance_id"] = self.instance_id
        session["route_list"] = self.route_list

        session["is_internal_api"] = self.detect_internal_api(request)
        if session["is_internal_api"]:
            self.fhdhr.logger.debug("Client is using internal API call.")

        session["is_mobile"] = self.detect_mobile(request)
        if session["is_mobile"]:
            self.fhdhr.logger.debug("Client is a mobile device.")

        session["is_plexmediaserver"] = self.detect_plexmediaserver(request)
        if session["is_plexmediaserver"]:
            self.fhdhr.logger.debug("Client is a Plex Media Server.")

        session["deviceauth"] = self.detect_plexmediaserver(request)

        session["tuner_used"] = None

        session["restart"] = False

        self.fhdhr.logger.debug("Client %s requested %s Opening" % (request.method, request.path))

    def after_request(self, response):

        # Close Tuner if it was in use, and did not close already
        # if session["tuner_used"] is not None:
        #    tuner = self.fhdhr.device.tuners.tuners[str(session["tuner_used"])]
        #    if tuner.tuner_lock.locked():
        #        self.fhdhr.logger.info("Shutting down Tuner #%s after Request." % session["tuner_used"])
        #        tuner.close()

        self.fhdhr.logger.debug("Client %s requested %s Closing" % (request.method, request.path))
        if not session["restart"]:
            return response
        else:
            return self.stop()

    def detect_internal_api(self, request):
        user_agent = request.headers.get('User-Agent')
        if not user_agent:
            return False
        elif str(user_agent).lower().startswith("fhdhr"):
            return True
        else:
            return False

    def detect_deviceauth(self, request):
        return request.args.get('DeviceAuth', default=None, type=str)

    def detect_mobile(self, request):
        user_agent = request.headers.get('User-Agent')
        phones = ["iphone", "android", "blackberry"]
        if not user_agent:
            return False
        elif any(phone in user_agent.lower() for phone in phones):
            return True
        else:
            return False

    def detect_plexmediaserver(self, request):
        user_agent = request.headers.get('User-Agent')
        if not user_agent:
            return False
        elif str(user_agent).lower().startswith("plexmediaserver"):
            return True
        else:
            return False

    def add_endpoints(self, index_name):

        item_list = [x for x in dir(self.endpoints_obj[index_name]) if self.isapath(x)]
        endpoint_main = self.endpoints_obj[index_name]
        endpoint_main.fhdhr.version  # dummy line
        for item in item_list:
            endpoints = eval("endpoint_main.%s.%s" % (item, "endpoints"))
            if isinstance(endpoints, str):
                endpoints = [endpoints]
            handler = eval("endpoint_main.%s" % item)
            endpoint_name = eval("endpoint_main.%s.%s" % (item, "endpoint_name"))

            try:
                endpoint_methods = eval("endpoint_main.%s.%s" % (item, "endpoint_methods"))
            except AttributeError:
                endpoint_methods = ['GET']

            try:
                endpoint_access_level = eval("endpoint_main.%s.%s" % (item, "endpoint_access_level"))
            except AttributeError:
                endpoint_access_level = 0

            try:
                pretty_name = eval("endpoint_main.%s.%s" % (item, "pretty_name"))
            except AttributeError:
                pretty_name = endpoint_name

            try:
                endpoint_category = eval("endpoint_main.%s.%s" % (item, "endpoint_category"))
            except AttributeError:
                endpoint_category = index_name

            try:
                endpoint_default_parameters = eval("endpoint_main.%s.%s" % (item, "endpoint_default_parameters"))
            except AttributeError:
                endpoint_default_parameters = {}

            self.fhdhr.logger.debug("Adding endpoint %s available at %s with %s methods." % (endpoint_name, ",".join(endpoints), ",".join(endpoint_methods)))

            if endpoint_category not in list(self.route_list.keys()):
                self.route_list[endpoint_category] = {}

            if endpoint_name not in list(self.route_list[endpoint_category].keys()):
                self.route_list[endpoint_category][endpoint_name] = {}
            self.route_list[endpoint_category][endpoint_name]["name"] = endpoint_name
            self.route_list[endpoint_category][endpoint_name]["endpoints"] = endpoints
            self.route_list[endpoint_category][endpoint_name]["endpoint_methods"] = endpoint_methods
            self.route_list[endpoint_category][endpoint_name]["endpoint_access_level"] = endpoint_access_level
            self.route_list[endpoint_category][endpoint_name]["endpoint_default_parameters"] = endpoint_default_parameters
            self.route_list[endpoint_category][endpoint_name]["pretty_name"] = pretty_name

            for endpoint in endpoints:
                self.add_endpoint(endpoint=endpoint,
                                  endpoint_name=endpoint_name,
                                  handler=handler,
                                  methods=endpoint_methods)

    def isapath(self, item):
        not_a_page_list = ["fhdhr", "plugin_utils"]
        if item in not_a_page_list:
            return False
        elif item.startswith("__") and item.endswith("__"):
            return False
        else:
            return True

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET']):
        self.fhdhr.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods)

    def run(self):

        self.http = WSGIServer(self.fhdhr.api.address_tuple,
                               self.fhdhr.app.wsgi_app,
                               log=self.fhdhr.logger.logger,
                               error_log=self.fhdhr.logger.logger)
        try:
            self.http.serve_forever()
            self.stop()
        except AttributeError:
            self.fhdhr.logger.info("HTTP Server Offline")
