# Global Travel Photo Generator

This project allows users to search for a location on a map, upload a photo, and generate a travel photo at that location using AI.

## Demo
<video src="demo.mp4" controls width="640">
  您的浏览器不支持 HTML5 视频播放。
</video>

## Prerequisites

- Node.js
- Python 3.8+
- Docker & Docker Compose (for containerized deployment)

## Setup

1.  **Backend Setup**:
    ```bash
    cd backend
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    
    pip install fastapi uvicorn requests python-multipart
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

## Running the Application (Development)

1.  **Start Backend**:
    ```bash
    cd backend
    # Activate venv if not already activated
    uvicorn main:app --reload
    ```
    The backend runs on `http://localhost:8000`.

2.  **Start Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```
    The frontend runs on `http://localhost:5173`.
    Note: The frontend is configured to proxy `/api` requests to `http://localhost:8000`.

## Running with Docker Compose

1.  Make sure Docker Desktop is running.
2.  Run the following command in the project root:
    ```bash
    docker-compose up --build
    ```
3.  Open `http://localhost` in your browser.
    - Frontend is served on port 80.
    - Backend is accessible via internal network, and exposed on port 8000 (optional).

## Usage

1.  Open the frontend URL in your browser.
2.  Use the search bar to find a location.
3.  Click on a location from the search results.
4.  The map will center on the location and a modal will appear.
5.  Upload a photo of yourself.
6.  Select the aspect ratio (Portrait or Landscape).
7.  Click "Generate Travel Photo".
8.  Wait for the generation to complete.
9.  Preview and download the generated photo.
