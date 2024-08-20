from playwright.sync_api import sync_playwright, Locator
from urllib import request
from requests import get
from typing import List
import facebook_scraper_vn._jscode as _jscode
import facebook_scraper_vn._utils as _utils
from os import mkdir, path
import json
import pathlib


class FacebookScraper:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.current_dir_path = pathlib.Path().resolve()

        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=not 0, channel="chrome", args=["--window-position=0,0"])
        self.context = self.browser.new_context(**self.p.devices["iPhone 13"])
        self.page = self.context.new_page()

    def fetch_page(self, facebook_pages: List, fetch_total_scroll: int) -> None:
        for page in facebook_pages:
            self._get_content_post(page, fetch_total_scroll)
        self.p.stop()

    def _download_image(self, src, page, index, index_image) -> str:
        with open(f"{self.current_dir_path}\dowload_data\image\{page}\image({index})({index_image}).jpg", "wb") as f:
            f.write(get(src).content)
            self.page.wait_for_timeout(3000)
            return f"image({index})({index_image}).jpg"
    
    def _download_video(self, src, page, index, index_video) -> str:
            self.context.new_page()
            self.context.pages[1].goto("https://fdownloader.net/en")
            input = self.context.pages[1].get_by_placeholder("Enter the Facebook video link here")
            input.wait_for()
            input.fill(src)
            btn_download_1 = self.context.pages[1].locator("//button[@class='btn-red']")
            btn_download_1.wait_for()
            btn_download_1.click()
            self.context.pages[1].wait_for_timeout(5000)
            btn_download_2 = self.context.pages[1].locator("//a[@class='button is-success is-small download-link-fb']").first
            btn_download_2.wait_for()
            href = btn_download_2.get_attribute('href')
            if href:
                request.urlretrieve(href, f"{self.current_dir_path}\dowload_data\\video\{page}\\video({index})({index_video}).mp4")
            self.context.pages[1].wait_for_timeout(3000)
            self.context.pages[1].close()   
            return f"video({index})({index_video}).mp4"
    
    def _download_post_data(self, content, page) -> None: 
        with open(f"{self.current_dir_path}\dowload_data\content\{page}\content.json", "a", encoding='utf8') as f:
            json.dump(content, f,  ensure_ascii=False)
            f.write(",")

    def _get_content_post(self, page, fetch_total_scroll) -> None:
        print("[RUN] scraping ...")
        mkdir(f"{self.current_dir_path}\dowload_data")

        mkdir(f"{self.current_dir_path}\dowload_data\content")
        mkdir(f"{self.current_dir_path}\dowload_data\image")
        mkdir(f"{self.current_dir_path}\dowload_data\\video")
        
        mkdir(f"{self.current_dir_path}\dowload_data\content\{page}")
        mkdir(f"{self.current_dir_path}\dowload_data\image\{page}")
        mkdir(f"{self.current_dir_path}\dowload_data\\video\{page}")

        with open(f"{self.current_dir_path}\dowload_data\content\{page}\content.json", "a+") as f:
            f.write("[")

        data_post = {
            "date": " ",
            "post_engagement": [], #like, cmt, share
            "content": " ",
            "image": [""],
            "video": [""]
        }
        check_flags = {
            "has_date": False,
            "has_post_engagement": False
        }
        self._scroll(page, fetch_total_scroll)

        list_container = self._get_all_container()
        for single_container in list_container:
            if check_flags["has_date"] and check_flags["has_post_engagement"]:
                self._download_post_data(data_post, page)
                
                check_flags = {
                   "has_date": False,
                   "has_post_engagement": False
                }

                data_post = {
                    "date": " ",
                    "post_engagement": [],
                    "content": " ",
                    "image": [""],
                    "video": [""]
                }

            index_container = list_container.index(single_container) + 1

            #scrap post's date
            date = ""
            js_code = _jscode.getDateElement(index_container)
            date_element = single_container.evaluate(js_code)
            if date_element:
                js_code = _jscode.getAttributeElement(index_container, '', 'date')
                date = single_container.evaluate(js_code)
                data_post["date"] = _utils.formatDateString(date)
                check_flags["has_date"] = True
                self._scroll_over_container(single_container)
                continue

            #scrape image
            js_code = _jscode.getImageElement(index_container)
            image_element = single_container.evaluate(js_code) 
            if len(image_element) != 0:
                js_code = _jscode.getAttributeElement(index_container, 'src', 'image')
                src_image = single_container.evaluate(js_code)
                for src in src_image:
                    index_image = src_image.index(src)
                    file_name = self._download_image(src, page, index_container, index_image)
                    data_post["image"].append(file_name)

            #scrape video 
            js_code = _jscode.getVideoElement(index_container)
            video_element = single_container.evaluate(js_code)
            if len(video_element) != 0:
                js_code = _jscode.getAttributeElement(index_container, 'data-video-id', 'video')
                id_video = single_container.evaluate(js_code) 
                for id in id_video:
                    index_video = id_video.index(id)
                    src_video = "https://www.facebook.com/video.php/?video_id=" + id
                    file_name = self._download_video(src_video, page, index_container, index_video)
                    data_post["video"].append(file_name)

            # scrape text content
            js_code = _jscode.getContentElement(index_container)
            content_element = self.page.evaluate(js_code)
            if content_element is not None: 
                data_post["content"] = single_container.text_content()
            
            #scrap like, commnent, share number
            post_engagement = ""
            if single_container.get_attribute("class") == "m displayed":
                    post_engagement = single_container.text_content()
                    data_post["post_engagement"] = _utils.extractString(post_engagement)
                    check_flags["has_post_engagement"] = True

            #scroll 
            self._scroll_over_container(single_container)
        
        with open(f"{self.current_dir_path}\dowload_data\content\{page}\content.json", "a") as f:
            f.write("{ }")
            f.write("]")
        print("[DONE] scraping was done!")

    def _scroll_over_container(self, single_container: Locator):
        #scroll 
            box = single_container.bounding_box()
            if box is not None:
                self.page.evaluate(f'document.documentElement.scrollTop+={box["height"]}')

    def _get_all_container(self) -> List[Locator]:
        return self.page.locator("//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div").all()

    def _scroll(self, page, fetch_total_scroll) -> None:
        self.page.goto(f"https://m.facebook.com/{page}")
        for _ in range(fetch_total_scroll):
            self.page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
            self.page.wait_for_timeout(2000)

        self.page.evaluate("document.documentElement.scrollTop=0")

    def generate_cookie(self, saved_cookie_location="facebook_cookies.json") -> None:
        self.page.goto("https://m.facebook.com/login/")
        self.page.fill("//input[@id='m_login_email']", self.email)
        self.page.fill("//input[@id='m_login_password']", self.password)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

        cookies = self.page.context.cookies()
        with open(saved_cookie_location, "w") as f:
            json.dump(cookies, f)
        input("[*]Generate cookie successfully! Press any key to continue...")
        exit()

    def load_cookie(self, saved_cookie_location="facebook_cookies.json") -> None:
        file_path = saved_cookie_location
        if not path.exists(file_path):
            print("[-] Not found facebook.json")
            print("[-] Generate using `generate_cookie()`")
            exit()

        self.page.goto("https://m.facebook.com/login")
        with open(file_path, "r") as f:
            cookies = json.loads(f.read())
            self.context.add_cookies(cookies)

