import streamlit as st
from google import genai
from google.genai import types

# 웹페이지 기본 설정
st.set_page_config(page_title="글로벌 성명학 마스터 - 작명 집사", page_icon="📜", layout="centered")

st.title("📜 글로벌 성명학 마스터")
st.write("사주 오행의 균형을 맞추고, 외국인도 발음하기 좋은 세련된 한글·영문 이름을 제안합니다.")

# API 키 불러오기 (배포 시 Secrets에 등록된 키를 자동으로 사용)
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.info("관리자 설정: 사이드바에 Gemini API 키를 입력하거나 Streamlit Secrets에 등록해 주세요.")
    st.stop()

# 성명학 시스템 지침 정의
SYSTEM_INSTRUCTIONS = """
# 역할 및 목적
당신은 정통 성명학과 현대적 감각을 겸비한 전문 작명 에이전트 '글로벌 성명학 마스터'입니다. 
의뢰인의 사주팔자(생년월일시)와 성씨를 바탕으로 부족한 오행을 보완하고 길한 수리를 구성하는 정통 원칙을 지키면서, 외국인도 발음하기 쉽고 영어 이름처럼 자연스럽게 불릴 수 있는 세련된 이름을 제안하고 해설합니다.

## 작명 및 분석 핵심 기준
1. 자원오행 (사주 용신·희신 보완): 사주 오행 분포를 분석해 부족한 기운을 보강하는 대법원 인명용 한자 선정.
2. 발음오행 (초성 상생): 훈민정음 통용 발음오행 기준 성과 이름 초성 흐름이 상생을 이루도록 구성.
3. 음양 조화 및 수리오행 (81수리): 강희자전 원획수 기준 짝수/홀수 조화 및 원·형·이·정 4격 모두 길수 배합.
4. 글로벌 호환성: 영어권에서도 발음하기 쉽고 세련된 어감 (부정적 영단어 연상 배제, 통용 영문 스펠링 명시).
5. 실용성: 대법원 전산 등록 인명용 한자만 사용.

## 출력 양식
[추천 1] 한글 이름 (한자) | 영문 표기: [영문 스펠링]
1. 이름의 의미와 글로벌 감각
- 한자 뜻: 글자별 의미 및 상서로운 조합
- 글로벌 활용성: 외국인 발음 용이성 및 영문 친화성
2. 성명학적 분석
- 자원오행: 보완 오행 및 부합성
- 발음오행: 초성 상생 흐름
- 음양 조화: 성씨 포함 음양 배합
- 수리 4격 (원/형/이/정격 각 획수 및 길수 해설)
(총 3개의 이름을 위 양식으로 추천)
"""

# 사용자 입력 폼
with st.form("naming_form"):
    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input("성씨 (한자 포함)", placeholder="예: 김 (金)")
        gender = st.selectbox("성별", ["남아", "여아"])
    with col2:
        calendar_type = st.selectbox("양력/음력", ["양력", "음력"])
        birth_date = st.date_input("생년월일")
        
    birth_time = st.text_input("태어난 시간", placeholder="예: 오전 10시 30분 또는 사시(巳時)")
    preference = st.text_input("선호 스타일 (선택)", placeholder="예: 부드러운 느낌, 영문 Ryan 느낌 선호")
    
    submitted = st.form_submit_button("작명 결과 확인하기", use_container_width=True)

# 버튼 클릭 시 실행
if submitted:
    if not last_name or not birth_time:
        st.warning("성씨와 태어난 시간을 모두 입력해 주세요.")
    else:
        with st.spinner("사주 분석 및 글로벌 감각의 길격 이름을 도출하고 있습니다..."):
            client = genai.Client(api_key=api_key)
            user_prompt = f"""
            - 성씨: {last_name}
            - 성별: {gender}
            - 생년월일: {calendar_type} {birth_date.strftime('%Y년 %m월 %d일')}
            - 태어난 시간: {birth_time}
            - 선호 스타일: {preference if preference else '없음'}
            위 조건에 맞추어 최고 길격의 글로벌 호환 한글·영문 이름을 작명해 주세요.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    temperature=0.2,
                )
            )
            st.markdown("---")
            st.markdown(response.text)