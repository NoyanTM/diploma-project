import httpx
from fake_useragent import FakeUserAgent
from bs4 import BeautifulSoup

from src.etl_pipeline.schemas import LanguageTypePublic


def get_response_publicreg(url: str, language: LanguageTypePublic = LanguageTypePublic.RUSSIAN, user_agent: str = None, timeout: float = 10.0, params: dict = None):
    timeout_config = httpx.Timeout(timeout)
    random_user_agent = FakeUserAgent().random
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": user_agent if user_agent is not None else random_user_agent,
        'referer': url,
        'referrer-policy':'same-origin'
    }
    
    with httpx.Client(headers=headers, timeout=timeout_config) as client:
        initial_request = client.get(url=url, params=params)
        csrf_headers_token = initial_request.cookies["csrftoken"] # initial_request.headers["Set-Cookie"]
        
        soup = BeautifulSoup(markup=initial_request.text, features="lxml")
        csrf_html_token = soup.find("div", attrs={"class": "header-content"}).find("form").find('input', {'name': 'csrfmiddlewaretoken'}).get("value")

        form_data = {
            "csrfmiddlewaretoken": csrf_html_token,
            "next": "/",
            "language": language,
        }
        
        cookies = {
            "csrftoken": csrf_headers_token
        }
        
        i18_request = client.post(url="https://publicreg.myafsa.com/i18n/setlang/", data=form_data, cookies=cookies)
        next_request = client.get(url=url, cookies=cookies, params=params)
    
    return next_request.text


# TODO: handling try except, handling retries for in range, remake to async def, 
# remake to OOP approach - like general HTTPXClient class
# need to set reed timeout to None
"""
httpcore.ReadTimeout: The read operation timed out
The above exception was the direct cause of the following exception:
"""
def get_response_main(url: str, response_type: str, user_agent: str = None, timeout: float = 30.0, params: dict = None): # 10.0 retries: int = 5, cooldown: int = 5
    timeout_config = httpx.Timeout(timeout)
    random_user_agent = FakeUserAgent().random
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": user_agent if user_agent is not None else random_user_agent,
    }
    
    with httpx.Client(headers=headers, timeout=timeout_config) as client:
        # try:
        response = client.get(url=url, params=params)
        # except httpx.HTTPError as e:
        #     print(e) # raise e
    
    if response_type == "html":
        return response.text
    
    if response_type == "json":
        return response.json()
