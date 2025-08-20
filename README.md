# Grammar Checker Pro

This is a web-based application that allows users to check their text for grammar, punctuation, and style errors. It provides AI-powered suggestions to help improve writing.

## Features

*   **Advanced Grammar Checking:** Identifies a wide range of grammatical errors, including subject-verb agreement, tense usage, and more.
*   **Punctuation Correction:** Catches mistakes with commas, apostrophes, and other punctuation marks.
*   **Style Improvements:** Offers suggestions for improving word choice, reducing wordiness, and avoiding common stylistic pitfalls.
*   **Dynamic Results:** The interface dynamically updates to show a list of identified issues and a fully corrected version of the text.
*   **Text Statistics:** Provides real-time counts for characters and words.
*   **Example Text:** Includes a button to load example text to demonstrate the checker's capabilities.
*   **Clear and Modern UI:** A clean, responsive interface for a seamless user experience.

## Installation and Setup

Follow these steps to set up and run the application on your server.

### Prerequisites

*   Python 3.6+
*   `pip` (Python package installer)

### Step-by-Step Instructions

1.  **Clone the Repository:**
    First, get the code onto your local machine or server. If using git, you would clone it:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment (Recommended):**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Install the required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    **Note:** The first time you run the application, the `language-tool-python` library may need to download language model files. An internet connection is required for this initial setup.

4.  **Run the Application (Development):**
    For development purposes, you can use the built-in Flask development server.
    ```bash
    flask run
    ```
    The application will be accessible at `http://127.0.0.1:5000`.

5.  **Running in Production (Recommended):**
    For a production environment, it is recommended to use a production-ready WSGI server like Gunicorn or uWSGI.

    **Example with Gunicorn:**
    a. Install Gunicorn:
    ```bash
    pip install gunicorn
    ```
    b. Run the application with Gunicorn:
    ```bash
    gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    ```
    This command starts Gunicorn with 4 worker processes, making the application available on port 8000 of your server's IP address.

### Accessing the Application

Once the server is running, open your web browser and navigate to your server's IP address and the port you configured (e.g., `http://your-server-ip:8000`).
