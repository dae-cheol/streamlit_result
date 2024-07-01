import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import json
import http.client
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import requests as req
from bs4 import BeautifulSoup as bs
import streamlit.components.v1 as components

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
    st.title('Google Looker Studio Dashboard')
    components.html(
        """
        <iframe width="600" height="450" src="https://lookerstudio.google.com/embed/reporting/32a1a98f-786d-42ba-90ab-bea6585be308/page/p_hs7gfm0lid" frameborder="0" style="border:0" allowfullscreen sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
        """,
        height=450,
        width=600
    )
    
    st.sidebar.title("페이지 선택")
    pages = {
        "채권보고서 조회": page1,
        "뉴스 조회": page2,
        "카테고리 및 시각화": page3,
        "Hawkish & Dovish Dictionary 조회": page4
    }
    page = st.sidebar.radio("이동할 페이지를 선택하세요:", list(pages.keys()))
    pages[page]()

def page1():
    st.header("채권보고서 조회")
    
    # 데이터 로드
    call_report_url_df = pd.read_csv('call_reports_url.csv')
    
    # 날짜 형식 변환
    call_report_url_df['date'] = pd.to_datetime(call_report_url_df['date'])
    
    # 콜금리 데이터 필터링
    st.subheader("채권분석보고서 조회")
    min_date_report = st.date_input("조회 시작일", value=pd.to_datetime("2024-06-01").date(), key="min_date_report")
    max_date_report = st.date_input("조회 종료일", value=pd.to_datetime("2024-06-30").date(), key="max_date_report")
    min_date_report = pd.to_datetime(min_date_report)
    max_date_report = pd.to_datetime(max_date_report)
    filtered_report_url_df = call_report_url_df[(call_report_url_df['date'] >= min_date_report) & (call_report_url_df['date'] <= max_date_report)]
    filtered_report_url_df['date'] = filtered_report_url_df['date'].dt.strftime('%Y-%m-%d')
    st.write("조회된 채권분석보고서", filtered_report_url_df)
    
    st.title('클로바 스튜디오 API를 통한 보고서 요약')

    host = 'clovastudio.apigw.ntruss.com'
    api_key = 'NTA0MjU2MWZlZTcxNDJiY/PqfTH5O1AzhVvQ19bbilzDPeuewv+MtBurhirpz3XR'
    api_key_primary_val = 'xxTvHdu8492TCdtCPLcwa5DnT0aANd5KWdU7vc1B'
    request_id = 'ee0a6cbf-92be-4f25-ba41-a02579768e7f'

    completion_executor = CompletionExecutor(host, api_key, api_key_primary_val, request_id)

    # PDF URL 입력 받기
    pdf_url = st.text_input('요약할 PDF URL 입력:', 'https://stock.pstatic.net/stock-research/debenture/21/20240614_debenture_417971000.pdf')

    # PDF에서 텍스트 추출
    if pdf_url:
        txt = extract_text_from_pdf(pdf_url)
    else:
        txt = ""

    # 텍스트 입력 받기
    user_input = st.text_area('직접 텍스트 입력:', txt)

    dct = {
        "texts": [user_input],
        "segMinSize": 300,
        "includeAiFilters": True,
        "autoSentenceSplitter": True,
        "segCount": -1,
        "segMaxSize": 1000
    }

    request_data = json.dumps(dct, ensure_ascii=False)

    if st.button('요약 생성'):
        response_text = completion_executor.execute(request_data)
        st.text_area('요약 결과', response_text)

def page2():
    st.header("뉴스 조회")
    
    # 데이터 로드
    call_news_df = pd.read_csv('call_news.csv')
    
    # 날짜 형식 변환
    call_news_df['date'] = pd.to_datetime(call_news_df['date'])
    
    st.subheader("뉴스 조회")
    min_date_news = st.date_input("조회 시작일", value=pd.to_datetime("2024-03-01").date(), key="min_date_news")
    max_date_news = st.date_input("조회 종료일", value=pd.to_datetime("2024-03-31").date(), key="max_date_news")
    min_date_news = pd.to_datetime(min_date_news)
    max_date_news = pd.to_datetime(max_date_news)
    filtered_call_news_df = call_news_df[(call_news_df['date'] >= min_date_news) & (call_news_df['date'] <= max_date_news)]
    filtered_call_news_df['date'] = filtered_call_news_df['date'].dt.strftime('%Y-%m-%d')
    
    st.write("조회된 뉴스", filtered_call_news_df)
    
    st.title('클로바 스튜디오 API를 통한 뉴스 제목 요약')

    host = 'clovastudio.apigw.ntruss.com'
    api_key = 'NTA0MjU2MWZlZTcxNDJiY/PqfTH5O1AzhVvQ19bbilzDPeuewv+MtBurhirpz3XR'
    api_key_primary_val = 'xxTvHdu8492TCdtCPLcwa5DnT0aANd5KWdU7vc1B'
    request_id = 'ee0a6cbf-92be-4f25-ba41-a02579768e7f'

    completion_executor = CompletionExecutor(host, api_key, api_key_primary_val, request_id)

    # 뉴스 제목 입력 받기
    news_title = st.text_input('요약할 뉴스 제목 입력:', 'SC제일은행, 최고 4.0% 금리 파킹통장 출시')

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
            title_ = soup.select_one("h2#title_area").text
            if title_ == news_title:
                break
            else:
                continue

    content = soup.select_one('#dic_area') 
    txt = content.text

    # 텍스트 입력 받기
    user_input = st.text_area('직접 텍스트 입력:', txt)

    dct = {
        "texts": [user_input],
        "segMinSize": 300,
        "includeAiFilters": True,
        "autoSentenceSplitter": True,
        "segCount": -1,
        "segMaxSize": 1000
    }

    request_data = json.dumps(dct, ensure_ascii=False)

    if st.button('요약 생성'):
        response_text = completion_executor.execute(request_data)
        st.text_area('요약 결과', response_text)

def page3():
    st.header("카테고리 및 시각화")
    
    # 데이터 로드
    tone_rate_df = pd.read_csv('어조금리분석.csv')
    
    # 날짜 형식 변환
    tone_rate_df['date'] = pd.to_datetime(tone_rate_df['date'], format='%Y-%m-%d')
    
    # 날짜 흐름에 따른 doc_tone과 base_rate의 상관관계 산점도
    st.header('date에 따른 doc_tone과 base_rate의 상관관계 산점도')
    fig = px.scatter(tone_rate_df, x='doc_tone', y='base_rate', color='date', title='문서 어조와 기준 금리의 상관관계')
    st.plotly_chart(fig, use_container_width=True)
    
    # Min-Max 스케일링
    scaler = MinMaxScaler()
    tone_rate_df[['doc_tone', 'base_rate']] = scaler.fit_transform(tone_rate_df[['doc_tone', 'base_rate']])
    
    st.header('date에 따른 doc_tone과 base_rate 선 그래프')
    tone_rate_df = tone_rate_df.sort_values(by='date')
    tone_rate_df.set_index('date', inplace=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tone_rate_df.index, y=tone_rate_df['doc_tone'], mode='lines', name='문서 어조', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=tone_rate_df.index, y=tone_rate_df['base_rate'], mode='lines', name='기준 금리', line=dict(color='red')))
    
    fig.update_layout(title='문서 어조와 기준 금리의 시간에 따른 변화', xaxis_title='날짜', yaxis_title='값')
    st.plotly_chart(fig, use_container_width=True)

def page4():
    st.header("Hawkish & Dovish Dictionary 조회")
    
    # 카테고리 별 데이터 시각화
    raw_df = pd.read_csv('raw_극성사전.csv')
    categories = raw_df['category'].unique()
    st.write(f"카테고리 유니크 값: {', '.join(categories)}")
    
    fig = px.histogram(raw_df, x='category', color='category', title='카테고리 분포')
    st.plotly_chart(fig, use_container_width=True)
    
    # 데이터 로드
    hawk_df = pd.read_csv("hawk2.csv")
    dove_df = pd.read_csv("dove2.csv")
    
    hawk_df['polarity_score'] = hawk_df['polarity_score'].round(3)
    dove_df['polarity_score'] = dove_df['polarity_score'].round(3)
    
    # Hawkish Dictionary
    st.subheader("Hawkish Dictionary")
    min_hawk_score = hawk_df["polarity_score"].min()
    max_hawk_score = hawk_df["polarity_score"].max()
    hawk_score_range = st.slider("확인하고 싶은 극성점수의 범주를 설정하세요:", min_value=min_hawk_score, max_value=max_hawk_score, value=(min_hawk_score, max_hawk_score), step=0.1)
    filtered_hawk_df = hawk_df[(hawk_df["polarity_score"] >= hawk_score_range[0]) & (hawk_df["polarity_score"] <= hawk_score_range[1])]
    
    if not filtered_hawk_df.empty:
        st.write(f"극성점수가 {hawk_score_range[0]}과 {hawk_score_range[1]} 사이에 있는 단어는 다음과 같습니다.")
        st.dataframe(filtered_hawk_df)
    else:
        st.write("선택된 범주 내의 극성점수에 해당하는 단어가 없습니다.")
    
    # Dovish Dictionary
    st.subheader("Dovish Dictionary")
    min_dove_score = dove_df["polarity_score"].min()
    max_dove_score = dove_df["polarity_score"].max()
    dove_score_range = st.slider("확인하고 싶은 극성점수의 범주를 설정하세요:", min_value=min_dove_score, max_value=max_dove_score, value=(min_dove_score, max_dove_score), step=0.1)
    filtered_dove_df = dove_df[(dove_df["polarity_score"] >= dove_score_range[0]) & (dove_df["polarity_score"] <= dove_score_range[1])]
    
    if not filtered_dove_df.empty:
        st.write(f"극성점수가 {dove_score_range[0]}과 {dove_score_range[1]} 사이에 있는 단어는 다음과 같습니다.")
        st.dataframe(filtered_dove_df)
    else:
        st.write("선택된 범주 내의 극성점수에 해당하는 단어가 없습니다.")

if __name__ == "__main__":
    main()
