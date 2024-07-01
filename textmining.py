import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler


def main():
    st.title("논문 프로젝트 페이지")
    pages = {
        "채권보고서 및 뉴스 조회": page1,
        "카테고리 및 시각화": page2,
        "Hawkish & Dovish Dictionary 조회": page3
    }
    
    st.sidebar.title("페이지 선택")
    page = st.sidebar.radio("이동할 페이지를 선택하세요:", list(pages.keys()))
    
    pages[page]()

def page1():
    st.header("채권보고서 및 뉴스 조회")
    
    # 데이터 로드
    call_report_url_df = pd.read_csv('call_reports_url.csv')
    call_news_df = pd.read_csv('call_news.csv')
    
    # 날짜 형식 변환
    call_report_url_df['date'] = pd.to_datetime(call_report_url_df['date'])
    call_news_df['date'] = pd.to_datetime(call_news_df['date'])
    
    # 콜금리 데이터 필터링
    st.subheader("채권분석보고서 조회")
    min_date_report = st.date_input("조회 시작일", value=pd.to_datetime("2024-06-01").date(), key="min_date_report")
    max_date_report = st.date_input("조회 종료일", value=pd.to_datetime("2024-06-30").date(), key="max_date_report")
    min_date_report = pd.to_datetime(min_date_report)
    max_date_report = pd.to_datetime(max_date_report)
    filtered_report_url_df = call_report_url_df[(call_report_url_df['date'] >= min_date_report) & (call_report_url_df['date'] <= max_date_report)]
    filtered_report_url_df['date'] = filtered_report_url_df['date'].dt.strftime('%Y-%m-%d')
    st.write("조회된 채권분석보고서", filtered_report_url_df)
    
    st.subheader("뉴스 조회")
    min_date_news = st.date_input("조회 시작일", value=pd.to_datetime("2024-03-01").date(), key="min_date_news")
    max_date_news = st.date_input("조회 종료일", value=pd.to_datetime("2024-03-31").date(), key="max_date_news")
    min_date_news = pd.to_datetime(min_date_news)
    max_date_news = pd.to_datetime(max_date_news)
    filtered_call_news_df = call_news_df[(call_news_df['date'] >= min_date_news) & (call_news_df['date'] <= max_date_news)]
    filtered_call_news_df['date'] = filtered_call_news_df['date'].dt.strftime('%Y-%m-%d')
    
    st.write("조회된 뉴스", filtered_call_news_df)

def page2():
    st.header("카테고리 및 시각화")
    
    # 데이터 로드

    tone_rate_df = pd.read_csv('어조금리분석.csv')
    
    # 날짜 형식 변환
    tone_rate_df['date'] = pd.to_datetime(tone_rate_df['date'], format='%Y-%m-%d')
    

    
    # 날짜 흐름에 따른 doc_tone과 base_rate의 상관관계 산점도
    st.header('date에 따른 doc_tone과 base_rate의 상관관계 산점도')
    fig = px.scatter(tone_rate_df, x='doc_tone', y='base_rate', color='date', title='Doc Tone vs Base Rate')
    st.plotly_chart(fig, use_container_width=True)
    
    # Min-Max 스케일링
    scaler = MinMaxScaler()
    tone_rate_df[['doc_tone', 'base_rate']] = scaler.fit_transform(tone_rate_df[['doc_tone', 'base_rate']])
    
    st.header('date에 따른 doc_tone과 base_rate 선 그래프')
    tone_rate_df = tone_rate_df.sort_values(by='date')
    tone_rate_df.set_index('date', inplace=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tone_rate_df.index, y=tone_rate_df['doc_tone'], mode='lines', name='doc_tone', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=tone_rate_df.index, y=tone_rate_df['base_rate'], mode='lines', name='base_rate', line=dict(color='red')))
    
    fig.update_layout(title='Doc Tone and Base Rate Over Time', xaxis_title='Date', yaxis_title='Value')
    st.plotly_chart(fig, use_container_width=True)

def page3():
    st.header("Hawkish & Dovish Dictionary 조회")
        # 카테고리 별 데이터 시각화
    raw_df = pd.read_csv('raw_극성사전.csv')
    categories = raw_df['category'].unique()
    st.write(f"카테고리 유니크 값: {', '.join(categories)}")
    
    fig = px.histogram(raw_df, x='category', color='category', title='Category Distribution')
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
