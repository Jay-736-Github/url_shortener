import sys
import os
import pytest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.models import url_db

@pytest.fixture
def client():
    """A test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
       # clear db before each test to start fresh
        url_db.clear()
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_shorten_url_success(client):
    """Test successful URL shortening and the new response format."""
    response = client.post('/api/shorten',
                           data=json.dumps({"url": "https://www.google.com"}),
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data
    assert 'short_url' in data # new field that returns full URL
    assert len(data['short_code']) == 6
    # short_url should end with the same code
    assert data['short_url'].endswith(data['short_code'])


def test_redirect_success(client):
    """Test successful redirection and click tracking."""
    # first create a short URL
    post_response = client.post('/api/shorten',
                                data=json.dumps({"url": "https://www.example.com"}),
                                content_type='application/json')
    short_code = post_response.get_json()['short_code']

    # then hit that short URL and expect redirect
    redirect_response = client.get(f'/{short_code}')
    assert redirect_response.status_code == 302
    assert redirect_response.location == "https://www.example.com"

    # to check if clicks are being tracked
    assert url_db[short_code]['clicks'] == 1

def test_get_stats_success(client):
    """Test the analytics endpoint."""
    post_response = client.post('/api/shorten',
                                data=json.dumps({"url": "https://www.python.org"}),
                                content_type='application/json')
    short_code = post_response.get_json()['short_code']

    # Increment clicks
    client.get(f'/{short_code}')
    client.get(f'/{short_code}')

    # Get stats
    stats_response = client.get(f'/api/stats/{short_code}')
    assert stats_response.status_code == 200
    data = stats_response.get_json()
    assert data['original_url'] == "https://www.python.org"
    assert data['clicks'] == 2
    assert 'created_at' in data

def test_short_code_not_found_redirect(client):
    """Test 404 error for a non-existent short code on redirect."""
    response = client.get('/noexist')
    assert response.status_code == 404

def test_short_code_not_found_stats(client):
    """Test 404 error for a non-existent short code on stats."""
    response = client.get('/api/stats/noexist')
    assert response.status_code == 404

def test_invalid_url_submission(client):
    """Test submitting an invalid URL."""
    response = client.post('/api/shorten',
                           data=json.dumps({"url": "this-is-not-a-url"}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Invalid URL provided"

def test_missing_url_payload(client):
    """Test request with missing 'url' key."""
    response = client.post('/api/shorten',
                           data=json.dumps({"other_key": "some_value"}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "URL is required"
