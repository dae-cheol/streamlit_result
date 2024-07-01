import streamlit as st
import requests as req
from bs4 import BeautifulSoup as bs
import json
import http.client
import requests
from io import BytesIO
from PyPDF2 import PdfReader

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/api-tools/summarization/v2/bb446bd461784e9bb68694dc4efb66c3', completion_request.encode('utf-8'), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['text']
        else:
            return 'Error'

def extract_text_from_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        with BytesIO(response.content) as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
    else:
        return None

def main():
    st.title('Text Summarization From News Title with Clova Studio API')

    host = 'clovastudio.apigw.ntruss.com'
    api_key = 'NTA0MjU2MWZlZTcxNDJiY/PqfTH5O1AzhVvQ19bbilzDPeuewv+MtBurhirpz3XR'
    api_key_primary_val = 'xxTvHdu8492TCdtCPLcwa5DnT0aANd5KWdU7vc1B'
    request_id = 'ee0a6cbf-92be-4f25-ba41-a02579768e7f'

    completion_executor = CompletionExecutor(host, api_key, api_key_primary_val, request_id)

    # NEWS TITLE 입력 받기
    news_title = st.text_input('Enter NEWS TITLE to summarize:', 'SC제일은행, 최고 4.0% 금리 파킹통장 출시')

    # 텍스트 추출
    url = f"https://search.naver.com/search.naver?where=news&query={news_title}&sort=1&sm=tab_smr&nso=so:dd,p:all,a:all"
    res = req.get(url)
    soup = bs(res.text, "html.parser")

    news = soup.select('div.info_group a.info')
    link = 0
    for i in news:
        if 'n.news.naver.com' in i['href']:
            link = i['href']
            res = req.get(link)
            soup = bs(res.text, "html.parser")
            #title_ = soup.select_one("#title_area > span")
            title_ = soup.select_one("h2#title_area").text
            if title_ == news_title:
                break
            else :
                continue

        

    content = soup.select_one('#dic_area') 
    txt = content.text

    # 텍스트 입력 받기
    user_input = st.text_area('Or enter your own text to summarize:', txt)

    dct = {
        "texts": [user_input],
        "segMinSize": 300,
        "includeAiFilters": True,
        "autoSentenceSplitter": True,
        "segCount": -1,
        "segMaxSize": 1000
    }

    request_data = json.dumps(dct, ensure_ascii=False)

    if st.button('Generate Summary'):
        response_text = completion_executor.execute(request_data)
        st.text_area('Summary', response_text)

if __name__ == '__main__':
    main()
