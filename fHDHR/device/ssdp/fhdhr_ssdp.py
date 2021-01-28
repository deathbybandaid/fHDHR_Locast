

class fHDHR_SSDP():

    def __init__(self, fhdhr, broadcast_ip, max_age):
        self.fhdhr = fhdhr

        self.ssdp_content = None

        self.broadcast_ip = broadcast_ip
        self.device_xml_path = '/api/device.xml'
        self.schema = "upnp:rootdevice"

        self.max_age = max_age

    def get(self):
        if self.ssdp_content:
            return self.ssdp_content.encode("utf-8")

        data = ''
        data_command = "NOTIFY * HTTP/1.1"

        data_dict = {
                    "HOST": "%s:%d" % ("239.255.255.250", 1900),
                    "NTS": "ssdp:alive",
                    "USN": 'uuid:%s::%s' % (self.fhdhr.config.dict["main"]["uuid"], self.schema),
                    "LOCATION": "%s%s" % (self.fhdhr.api.base, self.device_xml_path),
                    "EXT": '',
                    "SERVER": 'fHDHR/%s UPnP/1.0' % self.fhdhr.version,
                    "Cache-Control:max-age=": self.max_age,
                    "NT": self.schema,
                    }

        data += "%s\r\n" % data_command
        for data_key in list(data_dict.keys()):
            data += "%s:%s\r\n" % (data_key, data_dict[data_key])
        data += "\r\n"

        self.ssdp_content = data
        return data.encode("utf-8")
