import datetime
import sys
import os
from flask import Flask, request, redirect, jsonify

# To handle the package imports when running a file directly or as part of a package.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from models import url_db, lock
    from utils import generate_short_code, is_valid_url
else:
    from .models import url_db, lock
    from .utils import generate_short_code, is_valid_url


app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """A simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    }), 200

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Endpoint to shorten a URL."""
    if not request.json or 'url' not in request.json:
        return jsonify({"error": "URL is required"}), 400

    original_url = request.json['url']

    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL provided"}), 400

    with lock:
        # TO avoid creating a new code if the URL already exists.
        for short_code, data in url_db.items():
            if data['original_url'] == original_url:
                return jsonify({"short_code": short_code}), 200

        # To generate a new, unique short code.
        short_code = generate_short_code()
        while short_code in url_db:
            short_code = generate_short_code()

        url_db[short_code] = {
            "original_url": original_url,
            # Store timestamp in UTC with timezone info
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "clicks": 0
        }

        host = request.host_url.rstrip('/')
        short_url = f"{host}/{short_code}"
        return jsonify({
             "short_code": short_code,
            "short_url": short_url
        }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    """Redirects to the original URL and tracks the click."""
    with lock:
        if short_code in url_db:
            url_data = url_db[short_code]
            url_data['clicks'] += 1
            return redirect(url_data['original_url'])
        else:
            return jsonify({"error": "Short code not found"}), 404

@app.route('/api/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    """Returns analytics for a given short code."""
    with lock:
        if short_code in url_db:
            # Returning a copy to prevent direct modification of the database
            data = url_db[short_code]
            return jsonify({
                 "original_url": data["original_url"],
                 "clicks": data["clicks"],
                 "created_at": data["created_at"]
            })
        
        else:
            return jsonify({"error": "Short code not found"}), 404

if __name__ == '__main__':
    # For running the app for local development
    app.run(debug=True)
