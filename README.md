# URL Shortener

A lightweight URL shortener API built with Flask and SQLite.

## Features
- POST `/shorten` — Create short URL
- GET `/<code>` — Redirect to original URL
- GET `/stats/<code>` — View URL statistics
- Custom short codes supported
- Click tracking

## API Usage

### Create short URL
```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

### Response
```json
{
    "short_url": "http://localhost:5000/a1b2c3d",
    "original_url": "https://example.com/very/long/url",
    "code": "a1b2c3d"
}
```

## Setup
```bash
pip install -r requirements.txt
python app.py
```

Server starts at `http://localhost:5000`
