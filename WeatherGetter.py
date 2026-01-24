#!python

from urllib3 import PoolManager
from bs4 import BeautifulSoup

"""
WeatherGetter: retrieve, and store parsed XML data in a more comfortable interface.

version 0.1.0: initial version.
"""

__desc__ = """
Moncton.py: retrieve, and store parsed XML data in a more comfortable interface.

USAGE: from Moncton.py import WeatherGetter, or run it from the command line to
    display current conditions.
"""

class WeatherGetter:
    """A simple WeatherGetter class to fetch the weather for a given URL
    
    TODO: Refactor this into a generic WeatherGetter class.
    """

    moncton = 'https://weather.gc.ca/rss/city/nb-36_e.xml'

    def __init__(self):
        self.http = PoolManager()
        self.location = self.moncton # TODO generic
        self.weather = ''
        self.lastUpdated = ''
        self.warnings = ''
        self.condition = ''
        self.lastUpdated = ''
        self.forecasts = []
        self.notices = []

    def get_page(self):
        self.response = self.http.request('GET', self.location)
        if self.response.status == 200:
            self.weather = BeautifulSoup(self.response.data, "lxml-xml")
            return True

        return False
    
    def get_warning(self):
        """Return the text of the current weather warnings, otherwise empty string"""

        return self.warnings
    
    def get_condition(self):
        """Return the text of the current weather condition, otherwise empty string"""

        return self.condition
    
    def get_last_updated(self):
        return self.lastUpdated
   
    def parse_weather(self):
        """private method, used to parse weather page and extract current conditions and alerts"""

        if not self.weather:
            return False
        
        self.lastUpdated = self.weather.find("updated").get_text()

        entries = self.weather.find_all("entry")

        self.warnings = ''
        self.condition = ''
        self.forecasts = []
        self.notices = []

        for entry in entries:
            category = entry.find("category").get("term")
            if category == 'Warnings and Watches':
                self.warnings = entry.find("title").get_text()
                continue
            if category == 'Current Conditions':
                self.condition = entry.find("summary").get_text()
                continue
            if category == 'Weather Forecasts':
                self.forecasts.append(entry)
                continue
            if category == 'Notice':
                self.notices.append(entry)
                continue

            print(f"Unknown entry: {category}")
        
        return True

# Main function, primarily for testing.

def main(args):
    wg = WeatherGetter()
    if wg.get_page():
        if wg.parse_weather():
            print(f"Last Updated: {wg.get_last_updated()}")
            print(f"Warnings: {wg.get_warning()}")
            print(f"Current Conditions: {wg.get_condition()}")
        else:
            print("No Weather Data")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
