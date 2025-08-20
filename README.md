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

### Deploying with DirectAdmin

If your hosting provider uses the DirectAdmin control panel, you can follow these steps to deploy the application. These instructions assume DirectAdmin is using Phusion Passenger to serve Python applications.

1.  **Upload Your Files:**
    - Log in to your DirectAdmin account.
    - Use the **File Manager** to navigate to the directory where you want to store your application (e.g., `domains/yourdomain.com/private_html/grammar-checker`).
    - Upload all the application files and directories (`app.py`, `requirements.txt`, `static/`, `templates/`) to this location.

2.  **Set up the Python Application:**
    - Go back to the main DirectAdmin dashboard.
    - Under the **Extra Features** section, click on **Setup Python App**.
    - Click the **CREATE APP** button.
    - Configure the application:
        - **Python version:** Choose a recent version, like 3.8 or higher.
        - **Application Root:** Set this to the directory where you uploaded your files (e.g., `/home/youruser/domains/yourdomain.com/private_html/grammar-checker`).
        - **Application startup file:** Enter `app.py`. This is the main file for the Flask application.
        - **Application Entry Point:** Enter `app`. This is the name of the Flask object created in `app.py` (`app = Flask(__name__)`).
    - Click **CREATE**.

3.  **Install Dependencies:**
    - Once the application is created, the page will reload and show you details about your new app.
    - A command to install dependencies will be displayed. It will look like `pip install -r requirements.txt`. Click the **Run** button next to this command.
    - This will install Flask and `language-tool-python` inside the virtual environment created by DirectAdmin.

4.  **Restart the Application:**
    - At the top of the "Python App" page, click the **RESTART** button to apply your changes.

5.  **Access Your Application:**
    - Your application should now be live at your domain.

**Note:** The exact names and locations of buttons might vary slightly depending on your hosting provider's DirectAdmin theme and version.
