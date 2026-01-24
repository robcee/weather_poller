#!python


"""
weather_poller: retrieve, display or store weather data on stdout or Redis at {keyname}.warnings and {keyname}.condition.

version 0.1.0: initial version.
"""

__desc__ = """
weather_poller: retrieve, display or store weather data on stdout or Redis at {keyname}.lastUpdated {keyname}.warnings and {keyname}.condition.

USAGE: python weather_poller [-r|--redis -k|--key keyname] [-f|--frequency seconds] [-h|--help]

-r, --redis: (optional) log values to redis, otherwise stdout
-k, --key keyname: non-optional if using --redis. Key to store the document's contents in.
-f, --frequency: (optional) number of seconds between samples, if omitted, run once and exit.
"""

__author__ = "Rob Campbell"
__version__ = "0.1.0"
__license__ = "The Unlicense"

import argparse
import json
import socket
import redis
import urllib.request
import sched, time
import math
import subprocess
from datetime import datetime, timedelta, tzinfo, timezone
from dateutil import parser

from WeatherGetter import WeatherGetter

# Controller

class Controller:
    """I am a Controller class for the WeatherGetter. I know how to update the WeatherGetter and compare dates."""

    def __init__(self):
        self.wg = WeatherGetter()
        self.lastUpdated = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        self.updated = False
    
    def update(self):
        if self.wg.get_page():
            if self.wg.parse_weather():
                updated = True
                # print(f"Last Updated: {self.wg.get_last_updated()}")
            else:
                updated = False
                print("ERROR: No Weather Data!")
        
        return updated
    
    def compare_date_updated(self):
        """compare the controller's lastUpdated timestamp with timestamp from the WeatherGetter.
        If WeatherGetter's timestamp is more recent than controller's return True. Return False otherwise.
        """

        current = parser.parse(self.wg.get_last_updated())

        return self.lastUpdated < current

    def update_lastUpdated(self):
        self.lastUpdated = parser.parse(self.wg.get_last_updated())
    
# Globals

def write_to_redis(controller):
    key = args.key

    print(f"INFO: Controller Updated: {controller.lastUpdated}")
    if controller.update():
        if controller.compare_date_updated():
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.set(key + '.lastUpdated', controller.wg.get_last_updated())
            r.set(key + '.warnings', json.dumps(controller.wg.get_warnings()))
            r.set(key + '.condition', controller.wg.get_condition())
            r.set(key + '.forecasts', json.dumps(controller.wg.get_forecasts()))
            controller.update_lastUpdated()
            print("INFO: Redis write")
    else:
        print("ERROR: Error fetching data, unable to write.")


def write_to_console(controller):
    "probably no key = args.key"

    print(f"INFO: Controller Updated: {controller.lastUpdated}")
    if controller.update():
        if controller.compare_date_updated():
            print(f"Last Updated: {controller.wg.get_last_updated()}")
            print(f"Warnings:")
            for warning in controller.wg.get_warnings():
                print(f"  - {warning}")
            print(f"Condition: {controller.wg.get_condition()}")
            print(f"Forecasts:")
            for forecast in controller.wg.get_forecasts():
                print(f"  - {forecast}")
            controller.update_lastUpdated()
    else:
        print("ERROR: Error fetching data, no data to print")

# Main function

def main(args):
    """ Main entry point """

    freq = args.frequency
    scheduler = sched.scheduler()

    if args.redis:
        action = write_to_redis
    else:
        action = write_to_console

    print(f"INFO: weather_poller starting up, retrieving conditions for Moncton, storing on {args.key}")
    print(args)

    controller = Controller()

    # First one is free!
    action(controller)

    while freq > 0:
        # print("weather_poller, scheduler loop tick")
        scheduler.enter(freq, 1, action, {controller: controller})
        
        scheduler.run()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    argparser = argparse.ArgumentParser(usage=__desc__)

    # Optional argument flag which defaults to False
    argparser.add_argument("-r", "--redis", help="store values in redis", action="store_true")

    argparser.add_argument("-k", "--key", help="key name to store document's contents in", type=str, default="")

    # Optional argument which requires a parameter (eg. -d test)
    argparser.add_argument("-f", "--frequency", help="set frequency in seconds, if omitted, run once and exit", type=int, default=0)

    # Specify output of "--version"
    argparser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = argparser.parse_args()
    main(args)
