import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, request, jsonify
import schedule
import time
import threading
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

# Configuration
SCRAPE_URL = "https://techcrunch.com/category/artificial-intelligence/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Replace with your MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://matsindect:mXORYTECjLPXLynP@ac-imvs0hq-shard-00-00.qlxm23k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client.ai_news_scrapper
articles_collection = db.articles


#    Stores the scraped article data in the MongoDB database.
#    This function checks if an article with the same URL already exists in the database.
#    If it does not exist, the article data is inserted into the database.
#    Parameters:
#        article_data (dict): A dictionary containing the article data to be stored.
#    Returns:
#        bool: True if the article was successfully stored, False if it already exists.
#    Note: The function assumes that the MongoDB connection and database have been properly set up.
#    Raises:
#        pymongo.errors.PyMongoError: If there is an error during the database operation.
#    Example:
#        article_data = {
#            "title": "AI News Title",
#            "url": "https://example.com/ai-news",
#            "content": "This is the content of the AI news article.",
#            "author": "John Doe",
#            "published_date": "2023-10-01",
#            "scraped_date": "2023-10-01 12:00:00"
#        }
def store_article(article_data):
    # Check if article already exists by URL
    existing = articles_collection.find_one({"url": article_data["url"]})
    if not existing:
        articles_collection.insert_one(article_data)
        return True
    return False



#    Scrapes AI-related news articles from a specified URL and processes the data.

#    This function fetches the HTML content of a webpage, parses it to extract
#    articles, and processes each article to retrieve details such as title, URL,
#   author, publication date, and content. The extracted data is then stored in a
#   database if it is not already present.

#    Steps:
#    1. Sends an HTTP GET request to the target URL with appropriate headers.
#    2. Parses the HTML response using BeautifulSoup.
#    3. Extracts a list of articles based on specific HTML structure and class names.
#    4. Processes up to 10 articles, extracting relevant details for each.
#    5. Logs the scraping process and handles errors gracefully.

#    Note:
#    - The function assumes the presence of global variables `USER_AGENT` and
#        `SCRAPE_URL` for the user-agent string and the target URL, respectively.
#    - The `store_article` function is used to save the extracted article data.

#    Raises:
#            Exception: If there is an error during the scraping process or while
#            processing individual articles.

#    Returns:
#            None

def scrape_ai_news():
    
    print(f"Starting scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = requests.get(SCRAPE_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', class_='wp-block-post')
        length = len(articles)
        # Log the number of articles found
        print(length)
        print("\n===== SCRAPING NEW ARTICLES =====\n")

        for article in articles[:10]:  # Limiting to 10 articles for simplicity
            try:
                # Extract article data
                title_tag = article.find(['h2', 'h3'])
                if not title_tag:
                    continue

                title = title_tag.text.strip()

                link_tag = title_tag.find('a') or article.find('a', href=True)
                if not link_tag:
                    continue

                url = link_tag.get('href')
                if not url or not url.startswith('http'):
                    continue

                # Extract author and date if available
                author = None
                author_tag = article.find('a', class_='loop-card__author')
                if author_tag:
                    author = author_tag.text.strip()

                # Extract publication date
                # Note: The date format may vary, adjust the parsing as needed
                # Here we assume the date is in a <time> tag with a 'datetime' attribute
                # This may need to be adjusted based on the actual HTML structure
                date = None
                date_tag = article.find('time')
                if date_tag and date_tag.has_attr('datetime'):
                    date = date_tag['datetime'].strip()

                # Get article content (could fetch the full article page but simplified here)
                content = ""
                excerpt = article.find(['p', 'div'], class_=['excerpt', 'post-excerpt', 'entry-content'])
                if excerpt:
                    content = excerpt.text.strip()

                # Print article info as we go
                print(f"Found: {title}")
                print(f"URL: {url}")
                # Store in database if not already present
                store_article({
                    "title": title,
                    "url": url,
                    "content": content,
                    "author": author,
                    "published_date": date,
                    "scraped_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })


            except Exception as e:
                print(f"Error processing article: {e}")
                continue
        print(f"Scrape completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Scraping failed: {e}")



#    Generates the HTML content for the AI News Dashboard web application.

#    The function returns a multi-page HTML template with the following features:
#   - A responsive sidebar navigation menu with sections for Introduction, API Documentation, and Search Articles.
#    - A main content area that dynamically displays content based on the selected section.
#    - A search functionality to query AI-related news articles.
#    - API documentation with details about available endpoints.
#    - A demonstration video and a link to the GitHub repository for the project.

#    Returns:
#        str: A string containing the complete HTML structure and embedded CSS/JavaScript for the dashboard.
#    Note: The HTML includes inline CSS for styling and JavaScript for interactivity.
# Flask API
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI News Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary-color: #4a6bff;
                --secondary-color: #f8f9fa;
                --text-color: #333;
                --sidebar-width: 250px;
                --header-height: 60px;
                --border-radius: 8px;
                --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition-speed: 0.3s;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            body {
                background-color: #f5f7fb;
                color: var(--text-color);
                overflow-x: hidden;
            }
            video {
                width: 80%;
                max-width: 950px;
                border: 2px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            /* Layout */
            .dashboard {
                display: flex;
                min-height: 100vh;
            }

            /* Sidebar */
            .sidebar {
                width: var(--sidebar-width);
                background-color: white;
                box-shadow: var(--box-shadow);
                transition: transform var(--transition-speed);
                z-index: 100;
            }

            .sidebar-header {
                height: var(--header-height);
                display: flex;
                align-items: center;
                padding: 0 20px;
                border-bottom: 1px solid #eee;
            }

            .sidebar-header h2 {
                color: var(--primary-color);
                font-size: 1.5rem;
            }

            .sidebar-menu {
                padding: 20px 0;
            }

            .menu-item {
                padding: 12px 20px;
                cursor: pointer;
                border-left: 4px solid transparent;
                transition: all var(--transition-speed);
                display: flex;
                align-items: center;
            }

            .menu-item:hover {
                background-color: rgba(74, 107, 255, 0.1);
                border-left-color: var(--primary-color);
            }

            .menu-item.active {
                background-color: rgba(74, 107, 255, 0.15);
                border-left-color: var(--primary-color);
                font-weight: 600;
            }

            .menu-icon {
                margin-right: 10px;
                color: var(--primary-color);
            }

            /* Content area */
            .content {
                flex-grow: 1;
                padding: 20px;
                transition: all var(--transition-speed);
            }

            .content-header {
                margin-bottom: 20px;
                animation: fadeIn 0.5s ease;
            }

            /* Search section */
            .search-container {
                margin: 20px 0;
                animation: slideUp 0.5s ease;
            }

            .input-group {
                display: flex;
                box-shadow: var(--box-shadow);
                border-radius: var(--border-radius);
                overflow: hidden;
                background-color: white;
                transition: all var(--transition-speed);
            }

            .input-group:focus-within {
                box-shadow: 0 0 0 3px rgba(74, 107, 255, 0.3);
            }

            input[type="text"] {
                flex-grow: 1;
                padding: 12px 15px;
                border: none;
                font-size: 16px;
                outline: none;
            }

            button {
                padding: 12px 20px;
                background-color: var(--primary-color);
                color: white;
                border: none;
                cursor: pointer;
                transition: background-color var(--transition-speed);
                font-weight: 600;
            }

            button:hover {
                background-color: #3a59e0;
            }

            /* Article cards */
            .results {
                margin-top: 20px;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                animation: fadeIn 0.5s ease;
            }

            .article {
                background-color: white;
                border-radius: var(--border-radius);
                padding: 20px;
                box-shadow: var(--box-shadow);
                transition: transform var(--transition-speed), box-shadow var(--transition-speed);
            }

            .article:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }

            .article h3 {
                margin-bottom: 10px;
                color: var(--primary-color);
            }

            .article p {
                margin: 10px 0;
                color: #666;
            }

            .article a {
                display: inline-block;
                margin-top: 10px;
                color: var(--primary-color);
                text-decoration: none;
                font-weight: 600;
                position: relative;
            }

            .article a::after {
                content: '';
                position: absolute;
                width: 0;
                height: 2px;
                bottom: -2px;
                left: 0;
                background-color: var(--primary-color);
                transition: width var(--transition-speed);
            }

            .article a:hover::after {
                width: 100%;
            }

            /* API Documentation */
            .api-docs {
                background-color: white;
                border-radius: var(--border-radius);
                padding: 20px;
                box-shadow: var(--box-shadow);
                animation: fadeIn 0.5s ease;
            }

            .api-endpoint {
                margin-bottom: 15px;
                padding: 15px;
                border-left: 4px solid var(--primary-color);
                background-color: var(--secondary-color);
                border-radius: 0 var(--border-radius) var(--border-radius) 0;
                transition: transform var(--transition-speed);
            }

            .api-endpoint:hover {
                transform: translateX(5px);
            }

            /* Mobile responsiveness */
            .hamburger {
                display: none;
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: var(--primary-color);
                position: fixed;
                top: 15px;
                right: 15px;
                z-index: 200;
            }

            @media (max-width: 768px) {
                .sidebar {
                    position: fixed;
                    top: 0;
                    left: 0;
                    height: 100%;
                    transform: translateX(-100%);
                }

                .sidebar.active {
                    transform: translateX(0);
                }

                .hamburger {
                    display: block;
                }

                .content {
                    margin-left: 0;
                }

                .results {
                    grid-template-columns: 1fr;
                }
            }

            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            .page {
                display: none;
                animation: fadeIn 0.5s ease;
            }

            .page.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <button class="hamburger" onclick="toggleSidebar()">☰</button>

        <div class="dashboard">
            <!-- Sidebar Navigation -->
            <div class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <h2>AI News Dashboard</h2>
                </div>
                <div class="sidebar-menu">
                    <div class="menu-item active" onclick="showPage('intro-page')">
                        <span class="menu-icon">📚</span>
                        Introduction
                    </div>
                    <div class="menu-item" onclick="showPage('api-page')">
                        <span class="menu-icon">🔌</span>
                        API Documentation
                    </div>
                    <div class="menu-item" onclick="showPage('search-page')">
                        <span class="menu-icon">🔍</span>
                        Search Articles
                    </div>
                </div>
            </div>

            <!-- Main Content Area -->
            <div class="content">
                <!-- Introduction Page -->
                <div class="page active" id="intro-page">
                    <div class="content-header">
                        <h1>Welcome to the AI News Dashboard</h1>
                    </div>
                    <div class="api-docs">
                        <p>This dashboard provides access to a collection of AI-related news articles that are automatically scraped from TechCrunch website. You can search for specific key words, browse the latest articles, and access the data through our API.</p>
                        <p>Use the navigation menu on the left to explore different sections of the dashboard:</p>
                        <ul style="padding-left: 20px; margin: 15px 0;">
                            <li><strong>API Documentation</strong> - Learn how to use our API endpoints</li>
                            <li><strong>Search Articles</strong> - Find articles based on keywords</li>
                        </ul>
                        <p>The scraper automatically collects new articles every 24 hrs, ensuring you always have access to the latest AI news.</p>

                        <div class="content">
                            <p>My github Repos:</p>
                            <a href="https://github.com/matsindect/webscrapper/tree/main" target="_blank"> AI news scrapper repository</a>
                        </div>
                        <div class="content">
                            <h2>Demostration</h2>
                             <video controls>
                                <source src="https://github.com/user-attachments/assets/1975eedd-3ab0-4e8e-8b9f-0633c2e0946c" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                    </div>
                </div>

                <!-- API Documentation Page -->
                <div class="page" id="api-page">
                    <div class="content-header">
                        <h1>API Documentation</h1>
                    </div>
                    <div class="api-docs">
                        <p>Our API provides several endpoints to access and manage the scraped AI news articles.</p>

                        <div class="api-endpoint">
                            <h3>GET /articles</h3>
                            <p>Retrieve a list of articles.</p>
                            <p><strong>Parameters:</strong></p>
                            <ul>
                                <li><code>limit</code> - Maximum number of articles to return (default: 10)</li>
                                <li><code>offset</code> - Number of articles to skip (default: 0)</li>
                            </ul>
                        </div>

                        <div class="api-endpoint">
                            <h3>GET /articles/&lt;string:title&gt;</h3>
                            <p>Retrieve a specific article by its title.</p>
                        </div>

                        <div class="api-endpoint">
                            <h3>DELETE /articles/&lt;string:title&gt;</h3>
                            <p>Delete a specific article by its title.</p>
                        </div>

                        <div class="api-endpoint">
                            <h3>GET /search</h3>
                            <p>Search for articles based on keywords in title or content.</p>
                            <p><strong>Parameters:</strong></p>
                            <ul>
                                <li><code>q</code> - Search query (required)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Search Page -->
                <div class="page" id="search-page">
                    <div class="content-header">
                        <h1>Search AI News Articles</h1>
                    </div>
                    <div class="search-container">
                        <div class="input-group">
                            <input type="text" id="search-box" placeholder="Enter keywords to search..." />
                            <button onclick="searchArticles()">Search</button>
                        </div>
                    </div>
                    <div id="results" class="results">
                        <!-- Results will appear here -->
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Toggle sidebar on mobile
            function toggleSidebar() {
                document.getElementById('sidebar').classList.toggle('active');
            }

            // Switch between pages
            function showPage(pageId) {
                // Hide all pages
                document.querySelectorAll('.page').forEach(page => {
                    page.classList.remove('active');
                });

                // Show selected page
                document.getElementById(pageId).classList.add('active');

                // Update active menu item
                document.querySelectorAll('.menu-item').forEach(item => {
                    item.classList.remove('active');
                });
                event.currentTarget.classList.add('active');

                // Close sidebar on mobile after selection
                if (window.innerWidth <= 768) {
                    document.getElementById('sidebar').classList.remove('active');
                }
            }

            // Search articles function
            async function searchArticles() {
                const query = document.getElementById('search-box').value;
                const resultsContainer = document.getElementById('results');
                resultsContainer.innerHTML = ''; // Clear previous results

                if (!query) {
                    resultsContainer.innerHTML = '<p>Please enter a search query.</p>';
                    return;
                }

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();

                    if (data.error) {
                        resultsContainer.innerHTML = `<p>${data.error}</p>`;
                        return;
                    }

                    if (data.results.length === 0) {
                        resultsContainer.innerHTML = '<p>No articles found.</p>';
                        return;
                    }

                    data.results.forEach(article => {
                        const articleDiv = document.createElement('div');
                        articleDiv.className = 'article';

                        // Format the published_date to a human-readable format
                        let publishedDate = 'Unknown';
                        if (article.published_date) {
                            try {
                                const date = new Date(article.published_date);
                                publishedDate = date.toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                });
                            } catch (e) {
                                publishedDate = article.published_date;
                            }
                        }

                        articleDiv.innerHTML = `
                            <h3>${article.title}</h3>
                            <p><strong>Author:</strong> ${article.author || 'Unknown'}</p>
                            <p><strong>Published:</strong> ${publishedDate}</p>
                            <p>${article.content || 'No content available.'}</p>
                            <a href="${article.url}" target="_blank">Read Full Article</a>
                        `;
                        resultsContainer.appendChild(articleDiv);
                    });
                } catch (error) {
                    resultsContainer.innerHTML = `<p>Error fetching articles: ${error.message}</p>`;
                }
            }

            // Add event listener for search box (Enter key)
            document.getElementById('search-box').addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    searchArticles();
                }
            });
        </script>
    </body>
    </html>
    '''


#    Fetches a list of articles from the database with optional pagination.

#    Query Parameters:
#        limit (int, optional): The maximum number of articles to return. Defaults to 10.
#        offset (int, optional): The number of articles to skip before starting to collect the result set. Defaults to 0.

#    Returns:
#        flask.Response: A JSON response containing:
#            - count (int): The number of articles returned.
#            - articles (list): A list of articles, each represented as a dictionary with no "_id" field.

# Get all articles
@app.route('/articles', methods=['GET'])
def get_articles():

    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    articles = list(articles_collection.find(
        {},
        {"_id": 0}
    ).sort("scraped_date", -1).skip(offset).limit(limit))

    return jsonify({
        'count': len(articles),
        'articles': articles
    })

# Endpoint to get a single article by title
#    Fetches a single article from the database based on its title.
#    URL Parameters:
#        title (str): The title of the article to retrieve.

#    Returns:
#        flask.Response: A JSON response containing the article data if found, or an error message if not found.
#    Note: The article data is returned without the "_id" field.

@app.route('/articles/<string:title>', methods=['GET'])
def get_article_by_title(title):
    article = articles_collection.find_one({"title": title}, {"_id": 0})
    if article:
        return jsonify(article)
    else:
        return jsonify({'error': 'Article not found'}), 404

# Endpoint to delete an article by title
#    Deletes a specific article from the database based on its title.
#    URL Parameters:
#        title (str): The title of the article to delete.
#    Returns:
#        flask.Response: A JSON response indicating success or failure.
#    Note: The article is deleted from the database if found, and a success message is returned.
#    If the article is not found, an error message is returned with a 404 status code.

@app.route('/articles/<string:title>', methods=['DELETE'])
def delete_article_by_title(title):
    result = articles_collection.delete_one({"title": title})
    if result.deleted_count > 0:
        return jsonify({'message': 'Article deleted successfully'})
    else:
        return jsonify({'error': 'Article not found'}), 404

# Search articles by title or content
#    Searches for articles in the database based on a query string.
#    Query Parameters:
#        q (str): The search query string. This parameter is required.
#    Returns:
#        flask.Response: A JSON response containing:
#            - count (int): The number of articles matching the search query.
#            - query (str): The search query string.
#            - results (list): A list of articles matching the search query, each represented as a dictionary with no "_id" field.
#    Note: The search is case-insensitive and matches articles based on the title or content fields.

@app.route('/search', methods=['GET'])
def search_articles():
    query = request.args.get('q', default='', type=str)

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    # Text search
    results = list(articles_collection.find(
        {"$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}}
        ]},
        {"_id": 0}
    ).sort("scraped_date", -1))

    return jsonify({
        'count': len(results),
        'query': query,
        'results': results
    })

# Scheduler function
#    This function runs indefinitely, checking for scheduled tasks to execute.
#    It uses the `schedule` library to run pending tasks every second.
#    The function is designed to be run in a separate thread to avoid blocking the main application.

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main entry point
if __name__ == "__main__":

    # Run initial scrape
    scrape_ai_news()

    # Schedule scraping to run every 24 hours
    schedule.every(24).hours.do(scrape_ai_news)

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)