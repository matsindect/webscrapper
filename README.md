# AI News Scraper with Flask and MongoDB

A web scraper that collects AI-related news articles from TechCrunch and provides a REST API to access the data. Includes a dashboard for browsing and searching articles.

## Features

- **Automated Scraping**: Regularly scrapes TechCrunch's AI section for new articles
- **MongoDB Storage**: Stores articles in MongoDB Atlas (cloud database)
- **REST API**: Provides endpoints to access, search, and manage articles
- **Web Dashboard**: Interactive UI to browse and search articles
- **Scheduled Updates**: Automatically refreshes data every 24 hours

## Technologies Used

- Python 3
- Flask (web framework)
- BeautifulSoup (web scraping)
- MongoDB Atlas (database)
- Requests (HTTP client)
- Schedule (task scheduling)

## API Endpoints

- `GET /` - Dashboard homepage
- `GET /articles` - Get all articles (with optional limit and offset)
- `GET /articles/<title>` - Get a specific article by title
- `DELETE /articles/<title>` - Delete an article by title
- `GET /search?q=<query>` - Search articles by keyword

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-news-scraper.git
   cd ai-news-scraper

2. Install the required dependencies:
    ```bash
    pip install --user requests beautifulsoup4 flask schedule pymongo certifi

3. Set up your MongoDB Atlas:

- Create a free cluster on MongoDB Atlas
- Get your connection string
- Replace the MONGO_URI in the script with your actual connection string

4. Run the application:
    ```bash
    python app.py

5. Access the dashboard at http://localhost:5000

## Configuration
You can modify these variables in the script:

- SCRAPE_URL: URL to scrape (default: TechCrunch AI section)

- USER_AGENT: User agent for HTTP requests

- MONGO_URI: Your MongoDB Atlas connection string

## Project Structure

- app.py: Main application file containing:

  - Web scraping functionality

  - Flask API endpoints

  - Dashboard HTML/CSS/JS

  - MongoDB integration

  - Scheduling system
 
## ScreenShort
![Screenshot 2025-03-31 at 6 24 20 PM](https://github.com/user-attachments/assets/d475f31a-dbd8-4e0e-a575-23155aeb1dc2)


## License
This project is licensed under the MIT License - see the LICENSE file for details.

