import os
import sys
import argparse
import time
import threading

from fHDHR import fHDHR_VERSION, fHDHR_OBJ
import fHDHR.exceptions
import fHDHR.config
from fHDHR.db import fHDHRdb

ERR_CODE = 1
ERR_CODE_NO_RESTART = 2


if sys.version_info.major == 2 or sys.version_info < (3, 7):
    print('Error: fHDHR requires python 3.7+.')
    sys.exit(1)


def build_args_parser():
    """Build argument parser for fHDHR"""
    parser = argparse.ArgumentParser(description='fHDHR')
    parser.add_argument('-c', '--config', dest='cfg', type=str, required=True, help='configuration file to load.')
    return parser.parse_args()


def get_configuration(args, script_dir, origin, fHDHR_web):
    if not os.path.isfile(args.cfg):
        raise fHDHR.exceptions.ConfigurationNotFound(filename=args.cfg)
    return fHDHR.config.Config(args.cfg, script_dir, origin, fHDHR_web)


def run(settings, logger, db, script_dir, fHDHR_web, origin, alternative_epg):

    fhdhr = fHDHR_OBJ(settings, logger, db, origin, alternative_epg)
    fhdhrweb = fHDHR_web.fHDHR_HTTP_Server(fhdhr)

    try:

        fhdhr.logger.info("HTTP Server Starting")
        fhdhr_web = threading.Thread(target=fhdhrweb.run)
        fhdhr_web.start()

        if settings.dict["fhdhr"]["discovery_address"]:
            fhdhr.logger.info("SSDP Server Starting")
            fhdhr_ssdp = threading.Thread(target=fhdhr.device.ssdp.run)
            fhdhr_ssdp.start()

        if settings.dict["epg"]["method"]:
            fhdhr.logger.info("EPG Update Thread Starting")
            fhdhr_epg = threading.Thread(target=fhdhr.device.epg.run)
            fhdhr_epg.start()

        # Perform some actions now that HTTP Server is running
        fhdhr.logger.info("Waiting 3 seconds to send startup tasks trigger.")
        time.sleep(3)
        fhdhr.api.client.get("/api/startup_tasks", headers=fhdhr.api.headers)

        # wait forever
        while True:
            time.sleep(3600)

    except KeyboardInterrupt:
        return ERR_CODE_NO_RESTART

    return ERR_CODE


def start(args, script_dir, fHDHR_web, origin, alternative_epg):
    """Get Configuration for fHDHR and start"""

    try:
        settings = get_configuration(args, script_dir, origin, fHDHR_web)
    except fHDHR.exceptions.ConfigurationError as e:
        print(e)
        return ERR_CODE_NO_RESTART

    logger = settings.logging_setup()

    db = fHDHRdb(settings)

    return run(settings, logger, db, script_dir, fHDHR_web, origin, alternative_epg)


def main(script_dir, fHDHR_web, origin, alternative_epg):
    """fHDHR run script entry point"""

    print("Loading fHDHR %s" % fHDHR_VERSION)
    print("Loading fHDHR_web %s" % fHDHR_web.fHDHR_web_VERSION)
    print("Loading Origin Service: %s %s" % (origin.ORIGIN_NAME, origin.ORIGIN_VERSION))

    try:
        args = build_args_parser()
        return start(args, script_dir, fHDHR_web, origin, alternative_epg)
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return ERR_CODE


if __name__ == '__main__':
    main()
