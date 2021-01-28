from flask import request, redirect, abort, Response
import urllib.parse


class RMG_Devices_DeviceKey_Media():
    endpoints = ["/rmg/devices/<devicekey>/media/<channel>"]
    endpoint_name = "rmg_devices_devicekey_media"
    endpoint_methods = ["GET"]

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, devicekey, channel, *args):
        return self.get(devicekey, channel, *args)

    def get(self, devicekey, channel, *args):

        param = request.args.get('method', default=None, type=str)
        self.fhdhr.logger.debug("param:%s" % param)

        if not devicekey.startswith(self.fhdhr.config.dict["main"]["uuid"]):
            response = Response("Not Found", status=404)
            response.headers["X-fHDHR-Error"] = "801 - Unknown devicekey"
            self.fhdhr.logger.error(response.headers["X-fHDHR-Error"])
            abort(response)

        method = self.fhdhr.config.dict["streaming"]["method"]
        redirect_url = "/api/tuners?method=%s" % (method)

        origin = devicekey.split(self.fhdhr.config.dict["main"]["uuid"])[-1]
        redirect_url += "&origin=%s" % (origin)

        if str(channel).startswith('id://'):
            channel = str(channel).replace('id://', '')
        redirect_url += "&channel=%s" % (channel)

        redirect_url += "&accessed=%s" % urllib.parse.quote(request.url)

        return redirect(redirect_url)
