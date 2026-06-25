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

    st.divider()
    st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#F3F4F6;margin-bottom:8px'>🥗 USDA 영양 API</div>", unsafe_allow_html=True)
    st.markdown('<span class="step-tag">STEP 3</span><span style="font-size:0.82rem"> USDA API Key (선택)</span>', unsafe_allow_html=True)
    usda_api_key = st.text_input("API Key", key="usda_api_key", placeholder="미입력 시 DEMO_KEY 사용")
    st.markdown("<div style='font-size:0.72rem;color:#9CA3AF;margin-top:4px'>DEMO_KEY: 시간 30회 · 일 1,000회 무료</div>", unsafe_allow_html=True)

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

# ── Row 4: BMI 분포 히스토그램 | 나이대별 체성분 ─────────────
col_l4, col_r4 = st.columns(2, gap="large")

with col_l4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">BMI 분포 히스토그램</div>', unsafe_allow_html=True)
    if "BMI" in filt.columns:
        bmi_df = filt[["BMI"]].dropna().copy()
        bmi_df["구간"] = bmi_df["BMI"].apply(
            lambda b: "저체중 (<18.5)" if b < 18.5
                 else ("정상 (18.5-25)" if b < 25
                 else ("과체중 (25-30)" if b < 30
                 else "비만 (≥30)"))
        )
        zone_order  = ["저체중 (<18.5)", "정상 (18.5-25)", "과체중 (25-30)", "비만 (≥30)"]
        zone_colors = ["#90CAF9", GRAY_400, "#E57373", RED]
        chart_bmi = alt.Chart(bmi_df).mark_bar(
            cornerRadiusTopLeft=5, cornerRadiusTopRight=5
        ).encode(
            x=alt.X("BMI:Q", bin=alt.Bin(step=1.0), title="BMI"),
            y=alt.Y("count():Q", title="인원 수"),
            color=alt.Color("구간:N",
                scale=alt.Scale(domain=zone_order, range=zone_colors),
                legend=alt.Legend(title="BMI 구간")),
            tooltip=["구간:N",
                     alt.Tooltip("BMI:Q", bin=alt.Bin(step=1.0), title="BMI 구간 시작"),
                     alt.Tooltip("count():Q", title="인원")],
        ).properties(height=260)
        st.altair_chart(base_chart(chart_bmi), use_container_width=True)
    else:
        st.info("BMI 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">나이대별 평균 체지방률 & 골격근량</div>', unsafe_allow_html=True)
    if {"나이", "체지방률(%)", "골격근량(kg)"}.issubset(filt.columns):
        age_df = filt[["나이", "체지방률(%)", "골격근량(kg)"]].dropna().copy()
        age_df["나이대"] = pd.cut(
            age_df["나이"],
            bins=[0, 30, 40, 50, 60, 200],
            labels=["20대", "30대", "40대", "50대", "60대+"],
            right=False,
        )
        age_agg = age_df.groupby("나이대", observed=True).agg(
            평균체지방률=("체지방률(%)", "mean"),
            평균골격근량=("골격근량(kg)", "mean"),
        ).reset_index()
        bars_age = alt.Chart(age_agg).mark_bar(
            cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=RED, opacity=0.85
        ).encode(
            x=alt.X("나이대:N", axis=alt.Axis(labelAngle=0), title=""),
            y=alt.Y("평균체지방률:Q", title="평균 체지방률 (%)"),
            tooltip=["나이대:N", alt.Tooltip("평균체지방률:Q", format=".1f", title="체지방률(%)")]
        )
        line_age = alt.Chart(age_agg).mark_line(
            point=alt.OverlayMarkDef(color=GRAY_900, size=60), color=GRAY_600, strokeWidth=2.5
        ).encode(
            x=alt.X("나이대:N", title=""),
            y=alt.Y("평균골격근량:Q", title="평균 골격근량 (kg)"),
            tooltip=["나이대:N", alt.Tooltip("평균골격근량:Q", format=".1f", title="골격근량(kg)")]
        )
        st.altair_chart(
            base_chart(
                alt.layer(bars_age, line_age).resolve_scale(y="independent").properties(height=260)
            ),
            use_container_width=True,
        )
    else:
        st.info("나이, 체지방률, 골격근량 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 5: 시계열 트렌드 ──────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">월별 평균 체성분 트렌드</div>', unsafe_allow_html=True)

if "측정일" in filt.columns and not filt["측정일"].isna().all():
    trend_cols = [c for c in ["체중(kg)", "체지방률(%)", "골격근량(kg)", "BMI"] if c in filt.columns]
    if trend_cols:
        sel_metric = st.selectbox("지표 선택", options=trend_cols, key="trend_metric")
        trend_df = filt[["측정일", "회원ID", sel_metric]].dropna().copy()
        trend_df["월"] = trend_df["측정일"].dt.to_period("M").astype(str)
        monthly = (
            trend_df.groupby("월")
            .agg(값=(sel_metric, "mean"), 측정인원=("회원ID", "count"))
            .reset_index()
            .sort_values("월")
        )
        area_trend = alt.Chart(monthly).mark_area(color=RED, opacity=0.08).encode(
            x=alt.X("월:N"),
            y=alt.Y("값:Q", scale=alt.Scale(zero=False)),
        )
        line_trend = alt.Chart(monthly).mark_line(
            point=alt.OverlayMarkDef(color=RED, size=65, filled=True),
            color=RED, strokeWidth=2.5,
        ).encode(
            x=alt.X("월:N", axis=alt.Axis(labelAngle=-30), title=""),
            y=alt.Y("값:Q", title=sel_metric, scale=alt.Scale(zero=False)),
            tooltip=["월:N",
                     alt.Tooltip("값:Q", format=".2f", title=sel_metric),
                     alt.Tooltip("측정인원:Q", title="측정 인원")],
        )
        st.altair_chart(
            base_chart(alt.layer(area_trend, line_trend).properties(height=220)),
            use_container_width=True,
        )
    else:
        st.info("체중, 체지방률, 골격근량, BMI 중 하나 이상의 컬럼이 필요합니다.")
else:
    st.info("측정일 컬럼이 필요합니다.")

st.markdown('</div>', unsafe_allow_html=True)

# ── 이탈 위험 회원 목록 ────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'<div class="section-title">⚠️ 이탈 위험 회원 목록</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-card">', unsafe_allow_html=True)

RISK_COLS = ["주운동빈도(회)", "만족도(5점)", "회원기간(개월)"]
if any(c in filt.columns for c in RISK_COLS):
    risk_df = filt.copy()
    risk_df["위험점수"] = 0
    if "주운동빈도(회)"  in risk_df.columns:
        risk_df["위험점수"] += (risk_df["주운동빈도(회)"]  <= 2).astype(int)
    if "만족도(5점)"     in risk_df.columns:
        risk_df["위험점수"] += (risk_df["만족도(5점)"]     <= 3.0).astype(int)
    if "회원기간(개월)"  in risk_df.columns:
        risk_df["위험점수"] += (risk_df["회원기간(개월)"]  <= 3).astype(int)

    at_risk = risk_df[risk_df["위험점수"] >= 2].copy()
    at_risk["위험등급"] = at_risk["위험점수"].map({2: "⚠️ 주의", 3: "🔴 고위험"})

    r1, r2, r3 = st.columns(3)
    total_r   = len(at_risk)
    high_r    = len(at_risk[at_risk["위험점수"] == 3])
    caution_r = len(at_risk[at_risk["위험점수"] == 2])

    r1.markdown(f"""<div class="kpi-card">
  <div class="kpi-label">이탈 위험 회원</div>
  <div class="kpi-value">{total_r} 명</div>
  <div class="kpi-sub">전체 {len(filt)}명 중 {total_r/len(filt)*100:.1f}%</div>
</div>""", unsafe_allow_html=True)
    r2.markdown(f"""<div class="kpi-card">
  <div class="kpi-label">🔴 고위험 (3점)</div>
  <div class="kpi-value">{high_r} 명</div>
  <div class="kpi-sub">즉각 관리 필요</div>
</div>""", unsafe_allow_html=True)
    r3.markdown(f"""<div class="kpi-card" style="border-top-color:#E57373">
  <div class="kpi-label">⚠️ 주의 (2점)</div>
  <div class="kpi-value">{caution_r} 명</div>
  <div class="kpi-sub">모니터링 권장</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if total_r == 0:
        st.success("✅ 이탈 위험 기준에 해당하는 회원이 없습니다.")
    else:
        show_risk_cols = [c for c in [
            "회원ID", "이름", "이용센터", "담당트레이너", "프로그램",
            "주운동빈도(회)", "만족도(5점)", "회원기간(개월)", "위험점수", "위험등급",
        ] if c in at_risk.columns]
        st.dataframe(
            at_risk[show_risk_cols].sort_values("위험점수", ascending=False).reset_index(drop=True),
            use_container_width=True,
            height=280,
            hide_index=True,
        )
        st.markdown(f"""<div style="font-size:0.78rem;color:{GRAY_400};margin-top:8px">
💡 판단 기준 — 주운동빈도 ≤ 2회, 만족도 ≤ 3.0점, 회원기간 ≤ 3개월 각 1점씩 합산 (2점 이상 위험 분류)
</div>""", unsafe_allow_html=True)
else:
    st.info("주운동빈도, 만족도, 회원기간 중 하나 이상의 컬럼이 필요합니다.")

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

# ── 영양 가이드 (USDA FoodData Central) ──────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🥗 목표 달성 영양 가이드 (USDA FoodData Central)</div>', unsafe_allow_html=True)

_usda_key = usda_api_key.strip() if usda_api_key.strip() else "DEMO_KEY"

@st.cache_data(ttl=86400)
def fetch_usda_food(query, api_key):
    resp = requests.get(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={
            "query": query,
            "api_key": api_key,
            "pageSize": 1,
            "dataType": "Foundation,SR Legacy",
        },
        timeout=8,
    )
    resp.raise_for_status()
    foods = resp.json().get("foods", [])
    if not foods:
        return None
    nutrients = {n["nutrientName"]: n["value"] for n in foods[0].get("foodNutrients", [])}
    return {
        "칼로리(kcal)": round(nutrients.get("Energy", 0)),
        "단백질(g)":    round(nutrients.get("Protein", 0), 1),
        "탄수화물(g)":  round(nutrients.get("Carbohydrate, by difference", 0), 1),
        "지방(g)":      round(nutrients.get("Total lipid (fat)", 0), 1),
    }

USDA_FOODS = [
    ("닭가슴살 100g",   "chicken breast raw"),
    ("고구마 100g",     "sweet potato baked"),
    ("계란 1개",        "egg hard boiled"),
    ("그릭요거트 100g", "greek yogurt plain nonfat"),
    ("현미밥 100g",     "brown rice cooked"),
]

food_rows = []
with st.spinner("USDA에서 영양 데이터를 불러오는 중..."):
    for label, query in USDA_FOODS:
        try:
            data = fetch_usda_food(query, _usda_key)
            if data:
                food_rows.append({"식품": label, **data})
        except Exception:
            pass

n_col1, n_col2 = st.columns([1, 2], gap="large")

with n_col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">회원 평균 권장 섭취량</div>', unsafe_allow_html=True)

    if "체중(kg)" in filt.columns:
        avg_weight = filt["체중(kg)"].mean()
        avg_height = filt["키(cm)"].mean()         if "키(cm)"         in filt.columns else 170.0
        avg_age    = filt["나이"].mean()            if "나이"           in filt.columns else 35.0
        avg_goal   = filt["목표체중(kg)"].mean()   if "목표체중(kg)"   in filt.columns else avg_weight
        avg_freq   = filt["주운동빈도(회)"].mean() if "주운동빈도(회)" in filt.columns else 3.0

        male_ratio = (filt["성별"] == "남").mean() if "성별" in filt.columns else 0.5
        bmr_m = 10 * avg_weight + 6.25 * avg_height - 5 * avg_age + 5
        bmr_f = 10 * avg_weight + 6.25 * avg_height - 5 * avg_age - 161
        bmr   = bmr_m * male_ratio + bmr_f * (1 - male_ratio)

        if avg_freq <= 1:   activity = 1.2
        elif avg_freq <= 3: activity = 1.375
        elif avg_freq <= 5: activity = 1.55
        else:               activity = 1.725

        tdee        = bmr * activity
        weight_diff = avg_goal - avg_weight
        if abs(weight_diff) <= 0.5:
            goal_cal = tdee
            cal_note = "현재 체중 유지"
        elif weight_diff < 0:
            goal_cal = tdee - 500
            cal_note = "500 kcal 감량 식단"
        else:
            goal_cal = tdee + 300
            cal_note = "300 kcal 증량 식단"

        protein_target = avg_weight * 1.6

        for lbl, val, note in [
            ("유지 칼로리", f"{tdee:.0f} kcal",          "TDEE 기준"),
            ("목표 칼로리", f"{goal_cal:.0f} kcal",       cal_note),
            ("권장 단백질", f"{protein_target:.0f} g/일", "체중 × 1.6 g"),
        ]:
            st.markdown(f"""
<div style="padding:12px 0;border-bottom:1px solid {GRAY_100}">
  <div style="color:{GRAY_400};font-size:0.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase">{lbl}</div>
  <div style="color:{GRAY_900};font-size:1.25rem;font-weight:800;margin:4px 0 2px">{val}</div>
  <div style="color:{RED};font-size:0.72rem;font-weight:600">{note}</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="font-size:0.72rem;color:{GRAY_400};margin-top:10px">
※ 필터 회원 평균 기준 · Mifflin-St Jeor 공식
</div>""", unsafe_allow_html=True)
    else:
        st.info("체중(kg) 컬럼이 필요합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

with n_col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">헬스 추천 식품 단백질 비교 (100g 기준)</div>', unsafe_allow_html=True)

    if food_rows:
        food_df = pd.DataFrame(food_rows).sort_values("단백질(g)", ascending=False).reset_index(drop=True)

        chart_food = alt.Chart(food_df).mark_bar(
            cornerRadiusTopLeft=6, cornerRadiusTopRight=6
        ).encode(
            y=alt.Y("식품:N", sort="-x", title="", axis=alt.Axis(labelFontSize=12)),
            x=alt.X("단백질(g):Q", title="단백질 (g)"),
            color=alt.Color("단백질(g):Q",
                scale=alt.Scale(range=[GRAY_400, RED]), legend=None),
            tooltip=[
                "식품:N",
                alt.Tooltip("칼로리(kcal):Q", title="칼로리"),
                alt.Tooltip("단백질(g):Q",    title="단백질(g)"),
                alt.Tooltip("탄수화물(g):Q",  title="탄수화물(g)"),
                alt.Tooltip("지방(g):Q",      title="지방(g)"),
            ],
        ).properties(height=180)
        st.altair_chart(base_chart(chart_food), use_container_width=True)
        st.dataframe(food_df, use_container_width=True, hide_index=True, height=200)
    else:
        st.warning("USDA에서 데이터를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.markdown('</div>', unsafe_allow_html=True)
