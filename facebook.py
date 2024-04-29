from playwright.sync_api import sync_playwright, ElementHandle, Locator
from urllib import request
from string import printable
from requests import get
from typing import List, Literal
from interfaces import ISource
import jscode 
from os import getenv, mkdir, path
from shutil import rmtree
import json
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env


class FacebookFetch:
    def __init__(self) -> None:
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=not 0, channel="chrome", args=["--window-position=0,0"])
            self.context = self.browser.new_context(**p.devices["iPhone 13"])
            self.page = self.context.new_page()

            #self.generate_cookie()
            self.load_cookie()
            for source in self.get_sources_list("facebook_page"):
                print("=" * 10 + f" {source['name']} " + "=" * 10)
                self.fetch_page(source)

    def get_sources_list(self, source_type: Literal["facebook_page"]) -> List[ISource]:
        with open(f"D:/python/sources.json", "r") as sources_file:
            sources = json.load(sources_file)
        return [source for source in sources if source["source_type"] == source_type]

    def fetch_page(self, source: ISource) -> None:
        self.get_content_post(source)
        return

    def download_image(self, src, source: ISource, index) -> str:
        with open(f"D:/python/download_data/image/{source['username']}/image({index}).jpg", "wb") as f:
            f.write(get(src).content)
            self.page.wait_for_timeout(3000)
            return f"image({index}).jpg"
    
    def download_video(self, src, source:ISource, index) -> str:
            print("\t[*] Downloading video")
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
            href  = btn_download_2.get_attribute('href')
            if href:
                request.urlretrieve(href, f"D:/python/download_data/video/{source['username']}/video({index}).mp4")
            self.context.pages[1].wait_for_timeout(3000)
            self.context.pages[1].close()   
            print("\t[*] Video was downloaded inside download folder")
            return f"video({index}).mp4"
    
    def download_post_data(self, content, source:ISource) -> None: 
        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a", encoding='utf8') as f:
            json.dump(content, f,  ensure_ascii=False)
            f.write(",")

    def get_content_post(self, source: ISource) -> None:
        mkdir(f"D:/python/download_data/content/{source['username']}")
        mkdir(f"D:/python/download_data/image/{source['username']}")
        mkdir(f"D:/python/download_data/video/{source['username']}")

        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a") as f:
            f.write("[")

        data_post = {
            "date": " ",
            "engagement": " ",
            "content": " ",
            "image": [""],
            "video": [""]
        }
        
        count = 0

        self.scroll(source)

        list_container = self.get_all_container()

        for single_container in list_container:
            if count == 3:
                self.download_post_data(data_post, source)
                count = 0
                data_post = {
                    "date": " ",
                    "engagement": " ",
                    "content": " ",
                    "image": [""],
                    "video": [""]
                }

            index_container = list_container.index(single_container) + 1

            #check whether element has image or not
            js_code = jscode.getImageElement(index_container)
            image_element = single_container.evaluate(js_code) #return array image element
            if len(image_element) != 0:
                js_code = jscode.getAttributeElement(index_container, 'src', 'image')
                src_image = single_container.evaluate(js_code)
                for src in src_image:
                    #print(index_container, ": ", src, "\n")
                    self.download_image(src, source, index_container)

            #check whether element has video or not
            js_code = jscode.getVideoElement(index_container)
            video_element = single_container.evaluate(js_code)
            if len(video_element) != 0:
                js_code = jscode.getAttributeElement(index_container, 'data-video-id', 'video')
                id_video = single_container.evaluate(js_code) #id_video is id video array
                for id in id_video:
                    src_video = "https://www.facebook.com/video.php/?video_id=" + id
                    # print(index_container, ": ", src_video, "\n")
                    self.download_video(src_video, source, index_container)
                

            # scrape text content
            js_code = jscode.getContentElement(index_container)
            content_element = self.page.evaluate(js_code)
            if content_element is not None:
                if single_container.text_content().find("See more") != -1: 
                    post = single_container.locator("//div[@role='link']")
                    post.click(timeout=60000)
                    self.page.wait_for_timeout(2000)
                    data_post["content"] = post.text_content()
                    #print("content: ", post.text_content())
                    count += 1
                else:
                    data_post["content"] = single_container.text_content()
                    count += 1
                    #print("content: ", single_container.text_content())

            #scrap post's date
            date = ""
            js_code = jscode.getDateElement(index_container)
            date_element = single_container.evaluate(js_code)
            if date_element:
                js_code = jscode.getAttributeElement(index_container, '', 'date')
                date = single_container.evaluate(js_code)
                # print(date, "\n")
                data_post["date"] = date
                count += 1
            
            #scrap like, commnent, share number
            post_engagement = ""
            if single_container.get_attribute("class") == "m displayed":
                    post_engagement = single_container.text_content()
                    # print(post_engagement, "\n")
                    data_post["engagement"] = post_engagement
                    count += 1

            #scroll 
            box = single_container.bounding_box()
            if box is not None:
                self.page.evaluate(f'document.documentElement.scrollTop+={box["height"]}')
        
        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a") as f:
            f.write("{ }")
            f.write("]")

    def get_all_container(self) -> List[Locator]:
        return self.page.locator("//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div").all()

    def scroll(self, source: ISource) -> None:
        self.page.goto(f"https://m.facebook.com/{source['username']}")
        print("[DEBUG] scrolling ...")
        for _ in range(int(getenv("FETCH_TOTAL_SCROLL"))):
            self.page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
            self.page.wait_for_timeout(2000)

        self.page.evaluate("document.documentElement.scrollTop=0")

    def generate_cookie(self) -> None:
        self.page.goto("https://www.facebook.com/login/")
        self.page.fill("//input[@id='m_login_email']", getenv("EMAIL"))
        self.page.fill("//input[@id='m_login_password']", getenv("PASSWORD"))
        self.page.click("//button[@name='login']")
        self.page.wait_for_load_state("networkidle")

        cookies = self.page.context.cookies()
        with open(f"D:/python/sessions/facebook-cookies.json", "w") as f:
            json.dump(cookies, f)
        input("[*] press any key to continue")
        exit()

    def load_cookie(self) -> None:
        file_path = f"D:/python/sessions/facebook-cookies.json"
        if not path.exists(file_path):
            print("[-] Not found facebook.json")
            print("[-] Generate using `generate_cookie()`")
            exit()

        self.page.goto("https://m.facebook.com/login")
        with open(file_path, "r") as f:
            cookies = json.loads(f.read())
            self.context.add_cookies(cookies)

