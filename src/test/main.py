from facebook_scraper_vn.facebook_scraper import FacebookScraper

def main():
    scraper = FacebookScraper("", "")
    scraper.generate_cookie()
    scraper.load_cookie()
    scraper.fetch_page(["hustconfession"], 5)

if __name__ == "__main__":
    main()