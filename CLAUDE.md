# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python microservice that polls Environment Canada's weather RSS feed for Moncton, NB and outputs data to stdout or Redis. Designed to run as a systemd service.

## Commands

```bash
# Run once and print to console
python weather_poller.py

# Run continuously, writing to Redis every 10 minutes
python weather_poller.py -r -k weather -f 600

# Test WeatherGetter module directly
python WeatherGetter.py
```

## Dependencies

Requires Python 3.7+ and Redis server (if using `-r` flag). Install packages in a venv:
```bash
pip install -r requirements.txt
```

## Architecture

- **weather_poller.py**: Entry point with CLI argument parsing. Contains `Controller` class that manages update cycles and timestamp comparison to avoid redundant writes.
- **WeatherGetter.py**: Fetches and parses Environment Canada XML feed using BeautifulSoup. Extracts warnings, current conditions, and forecasts.

Data flow: `WeatherGetter` fetches XML → `Controller` checks if data is newer than last update → writes to Redis keys `{keyname}.lastUpdated`, `{keyname}.warnings`, `{keyname}.condition` or prints to stdout.
