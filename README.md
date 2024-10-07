# Simple YouTube video downloader

## Structure

```
youtube-downloader
├── backend
│   ├── downloader
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── downloaderapp
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
├── frontend
│   ├── src
│   │   ├── App.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── logo.svg
│   │   ├── views
│   │   │   ├── YoutubeDownloader.js
│   ├── README.md
│   ├── package.json
│   ├── public

```

## How it works

The youtube downloader is a simple web application that allows users to download youtube videos. The application is built using Django and React. The backend is a Django application that handles the downloading of videos using restframework and yt-dlp library while the frontend is a React application that displays input fields and a button to initiate the download process.

## Installation

### Backend

1. Clone the repository
2. Create a virtual environment
3. Install the requirements
4. Run the migrations
5. Run the server

### Frontend

1. Clone the repository
2. Install the dependencies
3. Run the application

## Built with love by Mr T

More developments coming soon...
