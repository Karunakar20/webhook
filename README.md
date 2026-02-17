# Webhook Delivery System - Full Stack Application

This is the frontend application for the Webhook Delivery System. It allows users to view webhook events, check details, retry failed events, and trigger new events manually.

## Features
- **Event Dashboard**: View a list of all webhook events with their status (Success, Failed, Pending and Delivered).
- **Event Details**: Click on any event to see full details including payload, headers, and metadata.
- **Retry Mechanism**: Manually retry failed events with a single click.
- **Create Event**: Trigger a new webhook event by supplying a JSON payload and API Key.
- **Auto-Refresh**: The event list automatically refreshes every 5 seconds.

### Prerequisites
- Node.js (v18 or higher)
- npm (v9 or higher)
- python

### Installation
1.  Clone the repository:
    ```bash
    git clone <repo_url>
    ```
### Setup for backend
1.  Navigate to the project directory
     ```bash
    cd webhook/backend
    ```
2.  Create virtual environment (.venv)
     ```bash
    python3 -m venv .venv
    ```
3.  Activate Virtual Environment
      ```bash
    source .venv/bin/activate
    ```
4.  Install dependencies:
       ```bash
    pip install -r requirements.txt
    ```
5.  Create Migration Files
      ```bash
    python manage.py makemigrations
    ```
6.  Apply Migrations to Database
      ```bash
    python manage.py migrate
    ```
7.  Intilaize intigrations
      ```bash
    python integrations_intializer.py
    ```
8.  Run worker
      ```bash
    python run_worker.py
    ```
9.  Start the development server (In new terminal)
      ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

### Setup for frontend
1.  Navigate to the project directory
     ```bash
    cd webhook/frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to `http://localhost:5173`.

### Backend Configuration
The application expects a backend service running at `http://192.168.0.135:8000`.
- The frontend uses a proxy configuration in `vite.config.js` to forward requests starting with `/api` to the backend.
- If your backend URL changes, update the `target` in `vite.config.js`.

## API Integration
The frontend interacts with the following backend endpoints:
-   `GET /api/webhook/?cmd=get`: Fetches the list of webhook events.
-   `GET /api/webhook/?cmd=get&id={id}`: Fetches details for a specific event.
-   `POST /api/webhook/?cmd=retry_event`: Retries a failed event. (Body: `{"id": "..."}`)
-   `POST /api/webhook/?cmd=create_event`: Creates a new event. (Headers: `X-API-Key`, Body: `{"payload": ...}`)

## Usage Guide
1.  **Viewing Events**: The main page displays a list of recent webhook events.
2.  ** inspecting Details**: Click on an item in the list to reveal the payload and other details in the right panel.
3.  **Retrying Failures**: If an event status is "Failed", a "Retry Event" button will appear in the details panel.
4.  **Creating Events**:
    -   Click the "Create Event" button in the header.
    -   Enter your Integration API Key.
    -   Enter the JSON payload (e.g., `{"payload": {"id": "123", "data": "test"}}`).
    -   Click "Create".

## Technologies Used
-   **React**: UI Library
-   **Vite**: Build tool and dev server
-   **CSS**: Custom styling (no external frameworks used)
