import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import requests

st.set_page_config(page_title="InBody 회원 분석 대시보드", layout="wide")

# ── 컬러 팔레트 ─────────────────────────────────────────────
RED       = "#D32F2F"
RED_DARK  = "#B71C1C"
RED_LIGHT = "#FFEBEE"
GRAY_900  = "#1F2937"
GRAY_600  = "#4B5563"
GRAY_400  = "#9CA3AF"
GRAY_100  = "#F3F4F6"
WHITE     = "#FFFFFF"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

*, body {{ font-family: 'Inter', sans-serif; }}

[data-testid="stAppViewContainer"] {{
    background: {GRAY_100};
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* 사이드바 — 다크 차콜 */
[data-testid="stSidebar"] {{
    background: {GRAY_900} !important;
}}
[data-testid="stSidebar"] * {{ color: #E5E7EB !important; }}
[data-testid="stSidebar"] .stMultiSelect > label {{ color: {GRAY_400} !important; font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; }}
[data-testid="stSidebar"] [data-baseweb="select"] {{
    background: #374151 !important;
    border: 1px solid #4B5563 !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] .stFileUploader {{
    background: #374151;
    border: 1.5px dashed #4B5563;
    border-radius: 10px;
    padding: 8px;
}}
[data-testid="stSidebar"] hr {{ border-color: #374151; }}

/* 헤더 배너 */
.header-banner {{
    background: {GRAY_900};
    border-radius: 14px;
    padding: 26px 36px;
    margin-bottom: 20px;
    border-left: 6px solid {RED};
    display: flex;
    align-items: center;
    gap: 20px;
}}
.header-banner h1 {{ color: {WHITE}; font-size: 2rem; font-weight: 800; margin: 0; }}
.header-banner p {{ color: {GRAY_400}; font-size: 0.9rem; margin: 6px 0 0; }}

/* KPI 카드 */
.kpi-card {{
    background: {WHITE};
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-top: 4px solid {RED};
    text-align: center;
}}
.kpi-label {{ color: {GRAY_400}; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; }}
.kpi-value {{ color: {GRAY_900}; font-size: 1.85rem; font-weight: 800; }}
.kpi-sub {{ color: {RED}; font-size: 0.78rem; margin-top: 6px; font-weight: 600; }}

/* 섹션 제목 */
.section-title {{
    font-size: 0.95rem;
    font-weight: 700;
    color: {GRAY_900};
    margin: 4px 0 14px;
    padding-left: 10px;
    border-left: 4px solid {RED};
    letter-spacing: 0.01em;
}}

/* 차트 래퍼 */
.chart-card {{
    background: {WHITE};
    border-radius: 12px;
    padding: 20px 20px 8px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    margin-bottom: 20px;
}}

/* 업로드 카드 */
.upload-card {{
    background: {WHITE};
    border-radius: 14px;
    padding: 32px 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 16px;
    text-align: center;
}}

/* 머지 배너 */
.merge-badge {{
    background: {RED_LIGHT};
    border-left: 4px solid {RED};
    border-radius: 8px;
    padding: 10px 18px;
    margin-bottom: 18px;
    font-size: 0.86rem;
    color: {RED_DARK};
    font-weight: 600;
}}

/* STEP 태그 */
.step-tag {{
    display: inline-block;
    background: {RED};
    color: white;
    border-radius: 5px;
    padding: 1px 8px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-right: 6px;
    vertical-align: middle;
}}
</style>
""", unsafe_allow_html=True)

# ── 헤더 ────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div style="font-size:2.8rem;line-height:1">💪</div>
  <div>
    <h1>InBody 회원 분석 대시보드</h1>
    <p>측정결과 + 회원관리 파일을 업로드하면 통합 분석이 시작됩니다</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 사이드바: 파일 업로드 ─────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:0.95rem;font-weight:700;color:#F3F4F6;margin-bottom:12px'>📂 파일 업로드</div>", unsafe_allow_html=True)
    st.markdown('<span class="step-tag">STEP 1</span><span style="font-size:0.82rem"> 측정결과 파일</span>', unsafe_allow_html=True)
    file_measurement = st.file_uploader("측정결과", type=["xlsx", "xls"], key="measurement", label_visibility="collapsed")
    st.markdown('<span class="step-tag">STEP 2</span><span style="font-size:0.82rem"> 회원관리 파일</span>', unsafe_allow_html=True)
    file_member = st.file_uploader("회원관리", type=["xlsx", "xls"], key="member", label_visibility="collapsed")

    if file_measurement and file_member:
        st.success("✅ 두 파일 업로드 완료")
        st.divider()
        st.markdown(f"<div style='font-size:0.95rem;font-weight:700;color:#F3F4F6;margin-bottom:10px'>🔽 필터</div>", unsafe_allow_html=True)

# ── 파일 미업로드 상태 ─────────────────────────────────────────
if not file_measurement or not file_member:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown(f"""
<div class="upload-card">
  <div style="font-size:3.5rem;margin-bottom:12px">📊</div>
  <div style="font-size:1.15rem;font-weight:800;color:{GRAY_900};margin-bottom:8px">두 파일을 업로드해 주세요</div>
  <div style="color:{GRAY_400};font-size:0.88rem;line-height:1.7">
    왼쪽 사이드바에서<br>
    <b style="color:{RED}">inbody_측정결과.xlsx</b> 와<br>
    <b style="color:{RED}">inbody_회원관리.xlsx</b> 를<br>
    각각 업로드하면 대시보드가 활성화됩니다
  </div>
  <hr style="border:none;border-top:1px solid {GRAY_100};margin:20px 0">
  <div style="display:flex;justify-content:space-around;text-align:center">
    <div>
      <div style="font-size:1.6rem">📋</div>
      <div style="font-size:0.78rem;color:{RED};font-weight:700;margin-top:4px">측정결과</div>
      <div style="font-size:0.72rem;color:{GRAY_400}">BMI·체지방·근육량</div>
    </div>
    <div style="display:flex;align-items:center;color:{GRAY_400};font-size:1.3rem;font-weight:300">+</div>
    <div>
      <div style="font-size:1.6rem">🗂️</div>
      <div style="font-size:0.78rem;color:{GRAY_600};font-weight:700;margin-top:4px">회원관리</div>
      <div style="font-size:0.72rem;color:{GRAY_400}">센터·프로그램·만족도</div>
    </div>
    <div style="display:flex;align-items:center;color:{GRAY_400};font-size:1.3rem;font-weight:300">=</div>
    <div>
      <div style="font-size:1.6rem">✨</div>
      <div style="font-size:0.78rem;color:{GRAY_900};font-weight:700;margin-top:4px">통합 분석</div>
      <div style="font-size:0.72rem;color:{GRAY_400}">인사이트 대시보드</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── 데이터 로드 & 머지 ────────────────────────────────────────
@st.cache_data
def load_and_merge(f1, f2):
    df_meas = pd.read_excel(f1)
    df_memb = pd.read_excel(f2)
    merged = pd.merge(df_meas, df_memb, on="회원ID", how="inner", suffixes=("_측정", "_관리"))
    for col in ["이름_측정", "이름_관리"]:
        if col in merged.columns:
            merged.rename(columns={col: "이름"}, inplace=True)
            break
    for col in ["성별_측정", "성별_관리"]:
        if col in merged.columns:
            merged.rename(columns={col: "성별"}, inplace=True)
            break
    if "측정일" in merged.columns:
        merged["측정일"] = pd.to_datetime(merged["측정일"], errors="coerce")
    if "등록일" in merged.columns:
        merged["등록일"] = pd.to_datetime(merged["등록일"], errors="coerce")
    return merged, df_meas, df_memb

try:
    df, df_meas, df_memb = load_and_merge(file_measurement, file_member)
except Exception as e:
    st.error(f"파일 로드 중 오류가 발생했습니다: {e}")
    st.stop()

merge_cnt = len(df)
meas_cnt  = len(df_meas)
memb_cnt  = len(df_memb)

if merge_cnt == 0:
    st.error("두 파일에서 매칭되는 회원ID가 없습니다. 파일을 확인해 주세요.")
    st.stop()

# ── 사이드바 필터 ─────────────────────────────────────────────
with st.sidebar:
    centers  = sorted(df["이용센터"].dropna().unique().tolist()) if "이용센터" in df.columns else []
    programs = sorted(df["프로그램"].dropna().unique().tolist()) if "프로그램" in df.columns else []
    genders  = sorted(df["성별"].dropna().unique().tolist())    if "성별"    in df.columns else []

    sel_center  = st.multiselect("이용센터",  options=centers,  default=centers)
    sel_program = st.multiselect("프로그램",  options=programs, default=programs)
    sel_gender  = st.multiselect("성별",      options=genders,  default=genders)

filt = df.copy()
if sel_center  and "이용센터" in filt.columns: filt = filt[filt["이용센터"].isin(sel_center)]
if sel_program and "프로그램" in filt.columns: filt = filt[filt["프로그램"].isin(sel_program)]
if sel_gender  and "성별"    in filt.columns: filt = filt[filt["성별"].isin(sel_gender)]

if len(filt) == 0:
    st.warning("선택한 필터 조건에 해당하는 회원이 없습니다.")
    st.stop()

# ── 머지 요약 배너 ─────────────────────────────────────────────
st.markdown(
    f'<div class="merge-badge">📎 머지 완료 — 측정결과 {meas_cnt}명 × 회원관리 {memb_cnt}명 → 공통 회원 <b>{merge_cnt}명</b> &nbsp;|&nbsp; 현재 필터 적용: <b>{len(filt)}명</b></div>',
    unsafe_allow_html=True,
)

# ── KPI 카드 ─────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "분석 회원 수",  f"{len(filt)} 명",                                                             "필터 적용 기준"),
    (k2, "평균 BMI",      f"{filt['BMI'].mean():.1f}"            if "BMI"         in filt.columns else "-", "정상범위 18.5~24.9"),
    (k3, "평균 체지방률", f"{filt['체지방률(%)'].mean():.1f} %"  if "체지방률(%)" in filt.columns else "-", "평균 측정값"),
    (k4, "평균 만족도",   f"{filt['만족도(5점)'].mean():.2f} / 5" if "만족도(5점)" in filt.columns else "-", "5점 만점"),
]
for col, label, value, sub in kpis:
    col.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 공통 차트 스타일 헬퍼 ─────────────────────────────────────
def base_chart(c):
    return c.configure_view(strokeWidth=0).configure_axis(
        grid=False, labelColor=GRAY_600, titleColor=GRAY_600,
        labelFontSize=11, titleFontSize=11,
    ).configure_legend(labelColor=GRAY_900, titleColor=GRAY_600, labelFontSize=11)

# ── Row 1: 센터별 지표 | 산점도 ──────────────────────────────
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">이용센터별 평균 체지방률 & 골격근량</div>', unsafe_allow_html=True)
    if {"이용센터","체지방률(%)","골격근량(kg)"}.issubset(filt.columns):
        agg = filt.groupby("이용센터").agg(
            평균체지방률=("체지방률(%)","mean"), 평균골격근량=("골격근량(kg)","mean")
        ).reset_index()
        bars = alt.Chart(agg).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=RED, opacity=0.88).encode(
            x=alt.X("이용센터:N", axis=alt.Axis(labelAngle=0), title=""),
            y=alt.Y("평균체지방률:Q", title="평균 체지방률 (%)"),
            tooltip=["이용센터:N", alt.Tooltip("평균체지방률:Q", format=".1f", title="체지방률(%)")]
        )
        line = alt.Chart(agg).mark_line(point=alt.OverlayMarkDef(color=GRAY_900, size=60), color=GRAY_600, strokeWidth=2.5).encode(
            x=alt.X("이용센터:N", title=""),
            y=alt.Y("평균골격근량:Q", title="평균 골격근량 (kg)"),
            tooltip=["이용센터:N", alt.Tooltip("평균골격근량:Q", format=".1f", title="골격근량(kg)")]
        )
        st.altair_chart(
            base_chart(alt.layer(bars, line).resolve_scale(y="independent").properties(height=280)),
            use_container_width=True
        )
    else:
        st.info("이용센터, 체지방률, 골격근량 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">체지방률 vs 골격근량 (성별 구분)</div>', unsafe_allow_html=True)
    if {"체지방률(%)","골격근량(kg)","성별"}.issubset(filt.columns):
        scatter = alt.Chart(filt).mark_circle(size=75, opacity=0.75).encode(
            x=alt.X("체지방률(%):Q", title="체지방률 (%)"),
            y=alt.Y("골격근량(kg):Q", title="골격근량 (kg)"),
            color=alt.Color("성별:N", scale=alt.Scale(domain=["남","여"], range=[RED, GRAY_400]),
                            legend=alt.Legend(title="성별")),
            tooltip=["이름:N","성별:N",
                     alt.Tooltip("체지방률(%):Q", format=".1f"),
                     alt.Tooltip("골격근량(kg):Q", format=".1f"),
                     "BMI:Q"],
        ).properties(height=280)
        st.altair_chart(
            scatter.configure_view(strokeWidth=0)
                   .configure_axis(grid=True, gridColor="#EEEEEE", labelColor=GRAY_600, titleColor=GRAY_600, labelFontSize=11, titleFontSize=11)
                   .configure_legend(labelColor=GRAY_900, titleColor=GRAY_600, labelFontSize=11),
            use_container_width=True
        )
    else:
        st.info("체지방률, 골격근량, 성별 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 2: 트레이너 만족도 | 목표 체중 달성 ──────────────────
col_l2, col_r2 = st.columns(2, gap="large")

with col_l2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">담당 트레이너별 평균 만족도</div>', unsafe_allow_html=True)
    if {"담당트레이너","만족도(5점)"}.issubset(filt.columns):
        t_agg = filt.groupby("담당트레이너").agg(
            평균만족도=("만족도(5점)","mean"), 회원수=("회원ID","count")
        ).reset_index().sort_values("평균만족도", ascending=False)
        chart_t = alt.Chart(t_agg).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("담당트레이너:N", sort="-y", axis=alt.Axis(labelAngle=0), title=""),
            y=alt.Y("평균만족도:Q", scale=alt.Scale(domain=[0,5]), title="평균 만족도"),
            color=alt.Color("평균만족도:Q",
                            scale=alt.Scale(domain=[t_agg["평균만족도"].min(), t_agg["평균만족도"].max()],
                                            range=[GRAY_400, RED]),
                            legend=None),
            tooltip=["담당트레이너:N", alt.Tooltip("평균만족도:Q", format=".2f"), "회원수:Q"],
        ).properties(height=260)
        st.altair_chart(base_chart(chart_t), use_container_width=True)
    else:
        st.info("담당트레이너, 만족도 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">목표 체중까지 남은 거리 (현재 − 목표)</div>', unsafe_allow_html=True)
    if {"체중(kg)","목표체중(kg)","이름"}.issubset(filt.columns):
        goal_df = filt[["이름","체중(kg)","목표체중(kg)"]].copy()
        goal_df["차이(kg)"] = (goal_df["체중(kg)"] - goal_df["목표체중(kg)"]).round(1)
        goal_df = goal_df.sort_values("차이(kg)", ascending=False).head(15)
        goal_df["상태"] = goal_df["차이(kg)"].apply(lambda x: "초과" if x > 0 else "달성")
        chart_g = alt.Chart(goal_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X("이름:N", sort=alt.EncodingSortField("차이(kg)", order="descending"),
                    axis=alt.Axis(labelAngle=-35), title=""),
            y=alt.Y("차이(kg):Q", title="현재 − 목표 (kg)"),
            color=alt.Color("상태:N",
                            scale=alt.Scale(domain=["초과","달성"], range=[RED, GRAY_400]),
                            legend=alt.Legend(title="상태")),
            tooltip=["이름:N",
                     alt.Tooltip("체중(kg):Q", format=".1f"),
                     alt.Tooltip("목표체중(kg):Q", format=".1f"),
                     alt.Tooltip("차이(kg):Q", format=".1f")],
        ).properties(height=260)
        st.altair_chart(base_chart(chart_g), use_container_width=True)
    else:
        st.info("체중(kg), 목표체중(kg), 이름 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 3: 내장지방 분포 | 프로그램별 현황 ───────────────────
col_l3, col_r3 = st.columns(2, gap="large")

with col_l3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">내장지방 레벨 분포</div>', unsafe_allow_html=True)
    if "내장지방레벨" in filt.columns:
        vf = filt["내장지방레벨"].value_counts().reset_index()
        vf.columns = ["레벨","인원"]
        vf = vf.sort_values("레벨")
        vf["위험도"] = vf["레벨"].apply(lambda x: "정상" if x <= 9 else ("경계" if x <= 12 else "위험"))
        chart_vf = alt.Chart(vf).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("레벨:O", title="내장지방 레벨", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("인원:Q", title="인원 수"),
            color=alt.Color("위험도:N",
                            scale=alt.Scale(domain=["정상","경계","위험"],
                                            range=[GRAY_400, "#E57373", RED]),
                            legend=alt.Legend(title="위험도")),
            tooltip=["레벨:O","인원:Q","위험도:N"],
        ).properties(height=240)
        st.altair_chart(base_chart(chart_vf), use_container_width=True)
    else:
        st.info("내장지방레벨 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">프로그램별 회원 수 & 평균 운동빈도</div>', unsafe_allow_html=True)
    if {"프로그램","주운동빈도(회)"}.issubset(filt.columns):
        p_agg = filt.groupby("프로그램").agg(
            회원수=("회원ID","count"), 평균운동빈도=("주운동빈도(회)","mean")
        ).reset_index().sort_values("회원수", ascending=False)
        bars_p = alt.Chart(p_agg).mark_bar(color=GRAY_600, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, opacity=0.85).encode(
            x=alt.X("프로그램:N", sort="-y", axis=alt.Axis(labelAngle=-20), title=""),
            y=alt.Y("회원수:Q", title="회원 수"),
            tooltip=["프로그램:N","회원수:Q",
                     alt.Tooltip("평균운동빈도:Q", format=".1f", title="평균 주운동빈도(회)")],
        )
        text_p = alt.Chart(p_agg).mark_text(dy=-9, color=RED, fontSize=11, fontWeight="bold").encode(
            x=alt.X("프로그램:N", sort="-y"),
            y=alt.Y("회원수:Q"),
            text=alt.Text("평균운동빈도:Q", format=".1f"),
        )
        st.altair_chart(
            base_chart(alt.layer(bars_p, text_p).properties(height=240)),
            use_container_width=True
        )
    else:
        st.info("프로그램, 주운동빈도 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 통합 데이터 테이블 ────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 통합 데이터 탐색</div>', unsafe_allow_html=True)

display_cols = [c for c in [
    "회원ID","이름","성별","나이","이용센터","프로그램","담당트레이너",
    "체중(kg)","BMI","체지방률(%)","골격근량(kg)","내장지방레벨",
    "목표체중(kg)","만족도(5점)","주운동빈도(회)","회원기간(개월)",
] if c in filt.columns]

st.dataframe(filt[display_cols].reset_index(drop=True), use_container_width=True, height=300, hide_index=True)

with st.expander("전체 컬럼 보기"):
    st.dataframe(filt.reset_index(drop=True), use_container_width=True, height=280, hide_index=True)

# ── 서울 날씨 (Open-Meteo) ────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🌡️ 서울 현재 날씨 (Open-Meteo)</div>', unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_seoul_weather():
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 37.5665,
            "longitude": 126.9780,
            "current_weather": True,
            "hourly": "temperature_2m",
            "timezone": "Asia/Seoul",
            "forecast_days": 1,
        },
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()

def weather_emoji(code):
    if code == 0:                        return "☀️"
    if code in (1, 2, 3):               return "⛅"
    if code in (45, 48):                 return "🌫️"
    if code in (51, 53, 55, 61, 63, 65): return "🌧️"
    if code in (71, 73, 75, 77):         return "🌨️"
    if code in (80, 81, 82):             return "🌦️"
    if code in (95, 96, 99):             return "⛈️"
    return "🌡️"

try:
    w         = fetch_seoul_weather()
    cur_temp  = w["current_weather"]["temperature"]
    wcode     = w["current_weather"]["weathercode"]
    h_times   = w["hourly"]["time"]
    h_temps   = w["hourly"]["temperature_2m"]
    today_str = h_times[0][:10]

    hour_labels = [t[11:16] for t in h_times if t.startswith(today_str)]
    hour_temps  = h_temps[:len(hour_labels)]

    w_col1, w_col2 = st.columns([1, 3], gap="large")

    with w_col1:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">서울 현재 기온</div>
  <div class="kpi-value">{weather_emoji(wcode)} {cur_temp}°C</div>
  <div class="kpi-sub">10분마다 자동 갱신</div>
</div>""", unsafe_allow_html=True)

    with w_col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">오늘 서울 시간별 기온</div>', unsafe_allow_html=True)
        weather_df = pd.DataFrame({"시간": hour_labels, "기온(°C)": hour_temps})
        line_w = alt.Chart(weather_df).mark_line(
            point=alt.OverlayMarkDef(color=RED, size=55),
            color=RED,
            strokeWidth=2.5,
        ).encode(
            x=alt.X("시간:N",
                    axis=alt.Axis(labelAngle=-45, values=hour_labels[::3]),
                    title=""),
            y=alt.Y("기온(°C):Q", title="기온 (°C)", scale=alt.Scale(zero=False)),
            tooltip=["시간:N", alt.Tooltip("기온(°C):Q", format=".1f", title="기온")],
        ).properties(height=200)
        st.altair_chart(base_chart(line_w), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.warning(f"날씨 정보를 불러올 수 없습니다: {e}")
