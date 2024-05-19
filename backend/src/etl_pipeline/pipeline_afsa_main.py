import re
import json
import json
import time
from pathlib import Path
from unicodedata import normalize

from dateutil.parser import parse
from tqdm import tqdm
from bs4 import BeautifulSoup, ResultSet, Tag
from pydantic import AnyUrl

from src.etl_pipeline.httpx import get_response_main
from src.etl_pipeline.schemas import language_dict
from src.etl_pipeline.utils import normalize_tag
from src.chats.llm import LLMService

base_url = "https://afsa.aifc.kz/api/search"
subdomains_list = ["", "court", "authority", "afsa", "iac", "tech", "bcpd", "gfc", "expatcentre", "aol", "itrp"] # "" - aifc


def get_api_json():
    for key, value in tqdm(language_dict.items(), position=0, desc=f"Language"):
        Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/").mkdir(parents=True, exist_ok=True)
        for subdomain in tqdm(subdomains_list, position=1, desc="Subdomain", leave=False):
            params = {
                "lang": key.value,
                "siteUrl": subdomain,
            }
            response = get_response_main(url=base_url, response_type="json", params=params)
            with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/{subdomain if subdomain else 'aifc'}.json", "w", encoding="utf-8") as file:
                json_object = json.dumps(response, indent=4, ensure_ascii=False)
                file.write(json_object)


# TODO: тут можно было пойти от обратно и не делать редактирование множества json а объединить их все в одного большого со всеми языками и со всеми категориями как keys
# TODO: compare amount of module (news, events, pages) between different languages 
# TODO: compare aifc.json with all jsons within some language in order to understand that is a "god json" with all elements maybe
def transform_and_compare_json_files():
    for key, value in tqdm(language_dict.items(), position=0, desc="Language"):
        files = list(Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/").glob(pattern="*.json"))
        for file in tqdm(files, position=1, desc="File", leave=False):
            json_data = json.loads(file.read_text(encoding="utf-8"))        
            if file.name == "aifc.json":
                data_list = []
                data_set = set()
                for data in json_data:
                    if data["site"] == 1:
                        data.pop("site_url")
                        data.pop("site")
                        if data["id"] not in data_set:
                            data_list.append(data)
                            data_set.add(data["id"])
                with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/aifc.json", "w", encoding="utf-8") as file:
                    json_object = json.dumps(data_list, indent=4, ensure_ascii=False)
                    file.write(json_object)
            else:
                data_list = []
                data_set = set()
                for data in json_data:
                    data.pop("site_url")
                    data.pop("site")
                    if data["id"] not in data_set:
                        data_list.append(data)
                        data_set.add(data["id"])
                with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/{file.name}", "w", encoding="utf-8") as file:
                    json_object = json.dumps(data_list, indent=4, ensure_ascii=False)
                    file.write(json_object)  


def group_json_files():
    for key, value in tqdm(language_dict.items(), position=0, desc="Language"):
        files = list(Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/").glob(pattern="*.json")) 
        
        news_list = []
        events_list = []
        pages_list = []
        Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/news/").mkdir(parents=True, exist_ok=True)
        Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/events/").mkdir(parents=True, exist_ok=True)
        Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/pages/").mkdir(parents=True, exist_ok=True)
        
        for file in tqdm(files, position=1, desc="File", leave=False):
            json_data = json.loads(file.read_text(encoding="utf-8"))
            for data in json_data:
                data.update({"group": str(file.name.replace(".json", ""))})                        
                if data["module"] == "news":
                    news_list.append(data)
                if data["module"] == "events":
                    events_list.append(data)
                if data["module"] == "pages":
                    pages_list.append(data)
                
        with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/news/news.json", "w", encoding="utf-8") as file:
                json_object = json.dumps(news_list, indent=4, ensure_ascii=False)
                file.write(json_object)
        with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/events/events.json", "w", encoding="utf-8") as file:
                json_object = json.dumps(events_list, indent=4, ensure_ascii=False)
                file.write(json_object)
        with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/pages/pages.json", "w", encoding="utf-8") as file:
                json_object = json.dumps(pages_list, indent=4, ensure_ascii=False)
                file.write(json_object)


def get_news_data():
    for key, value in tqdm(language_dict.items(), position=0, desc=f"Language"):
        directories = ["events", "news", "pages"]
        for directory in directories:
            Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/{directory}/html").mkdir(parents=True, exist_ok=True)
            Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/{directory}/image").mkdir(parents=True, exist_ok=True)
            Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/{directory}/txt/").mkdir(parents=True, exist_ok=True)
            # also need pdf, csv, excel, transcript, etc. # html / clean txt, images, transcript, audio (if video with link)

    values = ["en"] # "ru", "kk"
    for value in values:
        with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/news/news.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
        files = list(Path(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/").glob(pattern="*.json"))
        file_names = [file.stem for file in files if file.stem is not None] # if file.stem
        for idx, name in enumerate(tqdm(file_names, position=1, desc="Group", leave=False)):
            filtered_list = []
            for data in json_data:
                if data["group"] == name:
                    if data["url"] and data["url"] is not AnyUrl:
                        if name == "aifc":
                            url = f"https://aifc.kz/{value}/news/{data['url']}/"
                        else:
                            url = f"https://{name}.aifc.kz/{value}/news/{data['url']}/"
                        filtered_data = {
                            "id": int(data["id"]),
                            "title": str(data["name"]),
                            "url": str(url),
                            "endpoint": str(data['url']),
                        }
                        filtered_list.append(filtered_data)
            for data in tqdm(filtered_list, desc="Url", leave=False):
                response_html = get_response_main(url=data["url"], response_type="html")
                # time.sleep(5)
                
                with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/news/html/{name}_{data['id']}.html", "w", encoding="utf-8") as file:
                    file.write(response_html)
                
                soup = BeautifulSoup(markup=response_html, features="lxml")
                document_data = soup.select("div.col-12.col-lg-7") # div, p, li, a
                
                for document in document_data:                    
                    title = document.select_one("div[class=article-title]").text.strip()
                    datetime = parse(document.select_one("div.article-head.mt-2 > div[class=time]").getText(strip=True)).isoformat()
                    image_link = document.select_one("div[class=article-main-image] img")["src"]
                    # additional_links - all hrefs
                    # "description": , if it is not None or != ""
                    
                    for tag in document.select("div.article-title, div.article-head.mt-2, div.mt-4, div.article-main-image"): 
                        tag.decompose() # tag.extract
                    
                    page_content = normalize("NFKD", document.text.strip())
                    page_content_stripped = re.sub(r"\s\s+", " ", page_content)
                    # lines = content.split("\n") 
                    # stripped_lines = [line.strip() for line in lines] 
                    # non_empty_lines = [line for line in stripped_lines if line] 
                    # cleaned_content = " ".join(non_empty_lines) 
                    
                    with open(f"./src/etl_pipeline/extracted_data/afsa_main/{value}/news/txt/{name}_{data['id']}.txt", "w", encoding="utf-8") as file:
                        file.write(page_content_stripped)
                    
                    metadata = {
                        "source": data["url"],
                        "id": data["id"],
                        "site": name,
                        "category": "news",
                        "title": title, # data["title"]
                        "created_at": datetime,
                        "language": value,
                    }
                    
                    LLMService.upload_langchain_document(
                        page_content=page_content_stripped,
                        metadata=metadata,
                    )
                
                time.sleep(2)


def main():
    # get_api_json()
    # transform_and_compare_json_files()
    # group_json_files()
    get_news_data()
    # get_events_data() # parse every "events" of specific language and site_url
    # get_pages_data() # find out way to parse "pages" because they can be in any form + find out how to use "parent"
    
    
if __name__ == "__main__":
    main()
