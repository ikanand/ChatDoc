# Flask-Based Web Application for Chat and File Serving

This project is a Flask-based web application that provides a chat interface with an AI assistant on your uploded documents and securely serves uploaded files. The assistant supports Markdown, file links with proper permissions, and additional features.

---

## Features

- Chat with an AI-powered assistant in a responsive web interface.
- Securely serve user-uploaded files through Flask routes.
- Markdown-supported chat, including links that open in new tabs.
- Easy setup and deployment instructions.
- Customizable and extensible.

---

## Installation and Setup

### Prerequisites

1. Install Python (version 3.13.3 or later). Download it from [python.org](https://www.python.org).
2. Ensure `pip` is installed (Python's package manager).

---

### Step 1: Clone the Repository

Clone the repository to your local system using `git`:
```bash
git clone [[https://github.com/ikanand/ChatDoc.git]()](https://github.com/ikanand/ChatDoc.git)
OR
directly downalod the zip file and extract on your machine.
cd ChatDoc
```

---

### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment to isolate dependencies:

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### On Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

Install the required Python packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

### Step 4: Run the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## Usage Instructions

1. Navigate to `http://127.0.0.1:5000` in your browser.
2. Interact with the AI assistant in the chat interface.
3. Upload files by following the file-serving instructions in the app.
4. Use the "New Conversation" button to start a fresh chat session.
5. Navigate to `http://127.0.0.1:5000/collections` for vector based search.

---

## Project Structure

```plaintext
/project
    /uploads        # Directory for storing uploaded files
    /templates      # HTML templates (e.g., for the chat interface)
    /static         # Static files (e.g., CSS, JavaScript)
    app.py          # Main Flask application code
    requirements.txt # List of required Python packages
    README.md       # Instructions and setup details
    .gitignore       # Rules for excluding unwanted files in the Git repository
```

- **`uploads/`**: Stores user-uploaded files served by the application.
- **`templates/`**: Contains Jinja2 templates for the user interface.
- **`static/`**: Includes CSS, JavaScript, and other static assets.
- **`app.py`**: The main Python file for the application logic.
- **`requirements.txt`**: Lists all required dependencies with version numbers.
- **`README.md`**: This file, providing setup instructions and project details.

---

## Markdown Support and Links

The chat interface supports Markdown for rendering links and other rich text. Links that open in new tabs include the `target="_blank"` attribute for better usability.

Example Markdown Link:
```markdown
<a href="http://127.0.0.1:5000/uploads/LLM.pdf" target="_blank" rel="noopener noreferrer">LLM.pdf</a>
```

---



## Author Information

Created by **Anand K**
