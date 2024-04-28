from playwright.sync_api import sync_playwright, ElementHandle, Locator
from urllib import request
from string import printable
from requests import get
from typing import List, Literal
from interfaces import ISource
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

    def get_date_post(self, index) -> str:
        list_date = self.page.locator("//div[@data-mcomponent='MContainer' and @data-type='vscroller' and @class='m']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m bg-s3 displayed']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m' and @data-actual-height='43']//span[@class='f5']").all()
        date = list_date[index].inner_text()
        return date

    def download_image(self, src, source: ISource, index) -> None:
        with open(f"D:/python/download_data/image/{source['username']}/image({index}).jpg", "wb") as f:
            f.write(get(src).content)
            self.page.wait_for_timeout(3000)
    
    def download_content(self, content, source:ISource) -> None: 
        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a", encoding='utf8') as f:
            json.dump(content, f,  ensure_ascii=False)
            f.write(",")

    def get_content_post(self, source: ISource) -> None:
        mkdir(f"D:/python/download_data/content/{source['username']}")
        mkdir(f"D:/python/download_data/image/{source['username']}")

        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a") as f:
            f.write("[")

        self.scroll(source)

        list_container = self.get_all_container()

        for single_container in list_container:
            index_container = list_container.index(single_container)

            js_code = f"document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='ImageArea']/img[@class='img contain' and @data-type='image']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
            image_element = single_container.evaluate(js_code)
            if image_element is not None:
                js_code = f"document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='ImageArea']/img[@class='img contain' and @data-type='image']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.getAttribute('src')"
                src_image = single_container.evaluate(js_code)
                #print(src_image)
                self.download_image(src_image, source, index_container)

            if single_container.text_content().find("See translation") == -1:
                box = single_container.bounding_box()
                self.page.evaluate(f'document.documentElement.scrollTop+={box["height"]}')
                continue

            #print("Date: ", self.get_date_post(index_container-1), "\n")

            if single_container.text_content().find("See more") != -1: 
                post = single_container.get_by_role("link")
                post.click(timeout=60000)
                self.page.wait_for_timeout(2000)
                self.download_content(post.text_content(), source)
                #print(post.text_content(), "\n")
            else:
                self.download_content(single_container.text_content(), source)
                #print(single_container.text_content(), "\n") 
            
            box = single_container.bounding_box()
            self.page.evaluate(f'document.documentElement.scrollTop+={box["height"]}')
        
        with open(f"D:/python/download_data/content/{source['username']}/content.json", "a") as f:
            f.write("]")

    def get_all_container(self) -> List[Locator]:
        return self.page.locator("//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[@data-mcomponent='MContainer' and @data-type='container']").all()
        #return self.page.locator("//div[@data-mcomponent='MContainer' and @data-type='vscroller' and @class='m']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m bg-s3 displayed']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m']/div[@data-mcomponent='MContainer' and @data-type='container' and @class='m' and @role='link']").all()

    def scroll(self, source: ISource) -> None:
        self.page.goto(f"https://m.facebook.com/{source['username']}")
        print("[DEBUG] scrolling ...")
        for _ in range(10):
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

