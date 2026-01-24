# weather_poller

Simple Python app (microservice) to read the Environment Canada weather XML file for the City of Moncton and write output to stdio or Redis server. It is intended to be run from systemd as a service, but it should also work under whatever scheduler or service manager you use.

requires a running Redis server, Python 3.7+, Redis-py, e.g., pip install redis.

see [requirements.txt](requirements.txt) for additional PyPi packages.

## running a test

You will need to ensure the packages listed in requirements.txt are installed.

```
beautifulsoup4==4.9.3
lxml==4.6.3
python-dateutil==2.8.1
redis==3.5.3
urllib3==1.26.4
```

Install them with pip [package_name]. I recommend using a [python venv](https://docs.python.org/3/library/venv.html) for this.

If you want to run this to try it out, `python weather_poller.py` from this directory will run once and exit, printing some output to the console. (note, you may have to run python3 if you don't have an alias or link for that on your system).

## installation as a systemd service

Assuming you are running this as `ubuntu` user, with a virtual environment setup under `~/.venvs/default/`, and your script is installed under `~/Projects/weather_poller`,
add the following to your `/etc/systemd/system` folder, name it something sensible like `weather_poller.service`:

```
[Unit]
Description=Weather Poller Service
After=redis-server.service

[Service]
Type=simple
User=ubuntu
ExecStart=/home/ubuntu/.venvs/default/bin/python /home/ubuntu/Projects/weather_poller/weather_poller.py -r -f 600 -k weather
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

After installation, run `sudo systemctl daemon-reload` to pick up the changes, then `sudo systemctl start weather_poller.service` (assuming that's the name you gave it).

You can be sure it's running by checking `sudo systemctl status weather_poller` and `sudo journalctl -e -u weather_poller` for details.

When satisfied that everything is working as intended, you can permanently install the temperature monitor by entering `sudo systemctl enable weather_poller`.

## Running More Than One Web Poller
Same as above, but give each poller service a unique description and filename. You will want to adjust the Key argument (-k) to be unique so you don't overwrite each poller's contents in redis.

## Redis Output Format

When running with the `-r` flag, the poller writes to the following Redis keys (where `{key}` is the value passed to `-k`):

| Key | Type | Description |
|-----|------|-------------|
| `{key}.lastUpdated` | string | ISO 8601 timestamp of when Environment Canada last updated the feed |
| `{key}.warnings` | JSON array | List of active weather warnings/watches (e.g., `["YELLOW WARNING - COLD, Moncton", "SPECIAL WEATHER STATEMENT, Moncton"]`) |
| `{key}.condition` | string | HTML-formatted current conditions including temperature, humidity, wind, etc. |
| `{key}.forecasts` | JSON array | List of forecast titles for upcoming days (e.g., `["Saturday: Sunny. High minus 15.", "Saturday night: Clear. Low minus 23."]`) |

Example reading from Redis:
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)
warnings = json.loads(r.get('weather.warnings'))
forecasts = json.loads(r.get('weather.forecasts'))
```

## License

Do what you want with this.
