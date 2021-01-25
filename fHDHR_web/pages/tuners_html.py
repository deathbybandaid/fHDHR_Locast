from flask import request, render_template, session

from fHDHR.tools import humanized_filesize


class Tuners_HTML():
    endpoints = ["/tuners", "/tuners.html"]
    endpoint_name = "page_streams_html"
    endpoint_access_level = 0
    pretty_name = "Tuners"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        tuner_list = []
        tuner_status = self.fhdhr.device.tuners.status()
        tuner_scanning = 0
        for tuner in list(tuner_status.keys()):
            if tuner_status[tuner]["status"] == "Scanning":
                tuner_scanning += 1

            tuner_dict = {
                          "number": str(tuner),
                          "status": str(tuner_status[tuner]["status"]),
                          "origin": "N/A",
                          "channel_number": "N/A",
                          "method": "N/A",
                          "running_time": "N/A",
                          "downloaded": "N/A",
                          }

            if tuner_status[tuner]["status"] in ["Active", "Acquired", "Scanning"]:
                tuner_dict["origin"] = tuner_status[tuner]["origin"]
                tuner_dict["channel_number"] = tuner_status[tuner]["channel"] or "N/A"
                tuner_dict["running_time"] = str(tuner_status[tuner]["running_time"])

            if tuner_status[tuner]["status"] in "Active":
                tuner_dict["method"] = tuner_status[tuner]["method"]
                tuner_dict["downloaded"] = humanized_filesize(tuner_status[tuner]["downloaded"])

            tuner_list.append(tuner_dict)

        return render_template('tuners.html', request=request, session=session, fhdhr=self.fhdhr, tuner_list=tuner_list, tuner_scanning=tuner_scanning)
