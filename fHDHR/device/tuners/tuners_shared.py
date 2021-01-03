

class Tuners_Shared():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def get_stream_info(self, stream_args):

        stream_args["channelUri"] = self.channels.get_channel_stream(str(stream_args["channel"]))
        if not stream_args["channelUri"]:
            stream_args["true_content_type"] = "video/mpeg"
            stream_args["content_type"] = "video/mpeg"

        elif stream_args["channelUri"].startswith("udp://"):
            stream_args["true_content_type"] = "video/mpeg"
            stream_args["content_type"] = "video/mpeg"
        else:

            channelUri_headers = self.fhdhr.web.session.head(stream_args["channelUri"]).headers
            stream_args["true_content_type"] = channelUri_headers['Content-Type']

            if stream_args["true_content_type"].startswith(tuple(["application/", "text/"])):
                stream_args["content_type"] = "video/mpeg"
            else:
                stream_args["content_type"] = stream_args["true_content_type"]

        return stream_args
