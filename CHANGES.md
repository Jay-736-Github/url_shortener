## Overview  
This document outlines the development process, design choices, and improvements made while building the URL Shortener service.

## Development Process

### Initial Scaffolding  
The initial code was created to meet all the core functional requirements in a single script. This included the three main endpoints, in-memory data storage, and basic utility functions.

### Code Structuring  
Based on the project's file structure, the single script was refactored into a organized architecture:

- `app/main.py`: Contains all Flask routes and application logic.
- `app/models.py`: Manages the in-memory database (`url_db`) and the `threading.Lock` for thread safety.
- `app/utils.py`: Includes helper functions for URL validation and short code generation.
- `tests/test_basic.py`: Contains all unit tests using `pytest`.

### Debugging Path Issues  
Encountered and resolved a `ModuleNotFoundError` by updating the Python `sys.path` in `app/main.py` and `tests/test_basic.py`. This standard approach ensures that the application can be run directly and that tests can locate the app module from the root directory.

### Refinement and Finalization  
The final stage involved refining the code based on best practices.

## Key Improvements

### API Response Enhancement  
The `POST /api/shorten` endpoint was updated to return not only the `short_code` but also the full `short_url` (e.g., `http://127.0.0.1:5000/abc123`). This will provides a better experience for the API consumer.

### Timezone Correction  
Addressed a `DeprecationWarning` by changing `datetime.utcnow()` to the timezone-aware `datetime.now(datetime.timezone.utc)`. This ensures timestamps are handled correctly according to modern Python standards.

### Explicit Stats Response  
The `GET /api/stats/<short_code>` endpoint was modified to return an explicitly defined JSON object. This creates a more stable API contract and prevents accidentally leaking internal data structures.

## AI Usage

### Tool Used  
Google's Gemini Pro.

### Usage  
- **Initial Code Generation**: Provided the initial implementation based on the project requirements.  
- **Debugging**: Helped diagnose and provide solutions for `ModuleNotFoundError` and `DeprecationWarning`.  
- **Code Review**: Offered suggestions for improving the API response and overall code quality, which were incorporated into the final version.
