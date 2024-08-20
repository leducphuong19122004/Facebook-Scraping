# facebook_scraper_vn version 0.0.1
facebook_scraper_vn is a python package for scraping facebook's page. It can get text content, date, image, video, post engagement's post.
> [!WARNING]
> This package is only developed for learning purposes
## Installation
```python
pip install facebook_scraper_vn
```
## Sample
Firstly, we need to create and save a facebook's cookie into a file called "facebook_cookies.json" in the current folder
```python
from facebook_scraper_vn.facebook_scraper import FacebookScraper

scraper = FacebookScraper("your facebook's email", "your facebook's password")
scraper.generate_cookie()
```
And when we had the cookie, we started to scrape
```python
from facebook_scraper_vn.facebook_scraper import FacebookScraper

SCROLL_NUMBER = 5

scraper = FacebookScraper("your facebook's email", "your facebook's password") 
# scraper.generate_cookie() # run this line if we dont have cookie
scraper.load_cookie()
facebook_pages = ["hustconfession"] # page's id list
scraper.fetch_page(facebook_pages, SCROLL_NUMBER)
```
> [!TIP]
> The higher "SCROLL_NUMBER" value, the more pages are scraped