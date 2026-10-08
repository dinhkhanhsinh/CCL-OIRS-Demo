import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from model import (
    SCENARIOS,
    equal_allocation,
    qos_aware_allocation,
    evaluate,
    scenario_explanation,
)
from asset_data import ASSETS

st.set_page_config(
    page_title="Smart OIRS Allocation Demo",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        [data-testid="stDeployButton"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {max-width: 1540px; padding-top: 1.1rem; padding-bottom: 2rem;}
        html, body, [class*="css"] {font-size: 18px;}
        h1 {font-size: 2.2rem !important;}
        h2 {font-size: 1.85rem !important;}
        h3 {font-size: 1.48rem !important;}
        h4 {font-size: 1.20rem !important;}
        p, li, div, label {font-size: 1rem;}

        .hero {padding: 1.35rem 1.5rem; border: 1px solid rgba(120,120,120,0.18); border-radius: 22px; margin-bottom: 1rem; background: linear-gradient(120deg, rgba(68,124,201,0.12), rgba(111,87,193,0.08));}
        .hero-title {font-size: 2.2rem; font-weight: 800; margin-bottom: 0.3rem; letter-spacing: -0.03em;}
        .hero-subtitle {font-size: 1.12rem; opacity: 0.84; margin-bottom: 0;}

        .step-card {border: 1px solid rgba(120,120,120,0.18); border-radius: 18px; padding: 1rem 1.1rem; min-height: 118px; background: rgba(255,255,255,0.72);}
        .step-card.blue {background: linear-gradient(180deg, rgba(68,124,201,0.07), rgba(255,255,255,0.84));}
        .step-card.green {background: linear-gradient(180deg, rgba(34,197,94,0.07), rgba(255,255,255,0.84));}
        .step-card.orange {background: linear-gradient(180deg, rgba(245,158,11,0.08), rgba(255,255,255,0.84));}
        .step-number {font-size: 0.82rem; font-weight: 700; opacity: 0.58; text-transform: uppercase; letter-spacing: 0.06em;}
        .step-title {font-size: 1.08rem; font-weight: 760; margin-top: 0.2rem;}
        .step-text {font-size: 0.96rem; opacity: 0.74; margin-top: 0.2rem; line-height: 1.45;}

        .section-kicker {font-size: 0.86rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; opacity: 0.58; margin-bottom: 0.12rem;}
        .section-band {padding: 0.4rem 0.8rem; border-radius: 999px; display: inline-block; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.35rem;}
        .band-blue {background: rgba(68,124,201,0.12); color: #1D4ED8;}
        .band-green {background: rgba(34,197,94,0.12); color: #047857;}

        .info-card {border: 1px solid rgba(120,120,120,0.18); border-left: 5px solid #4f46e5; border-radius: 16px; padding: 1.05rem 1.1rem; background: rgba(255,255,255,0.74); height: 100%;}
        .info-card.green {border-left-color: #10b981;}
        .scenario-highlight {border: 1px solid rgba(16,185,129,0.20); border-left: 6px solid #10b981; border-radius: 18px; padding: 1.05rem 1.1rem; background: linear-gradient(180deg, rgba(16,185,129,0.08), rgba(255,255,255,0.95)); box-shadow: 0 10px 24px rgba(16,185,129,0.08);}
        .scenario-pill {display:inline-block; padding:0.28rem 0.72rem; border-radius:999px; background: rgba(16,185,129,0.14); color:#047857; font-weight:800; font-size:0.92rem; margin-bottom:0.55rem;}
        .info-card h4 {margin: 0 0 0.5rem 0; font-size: 1.08rem;}
        .info-card p {margin: 0; line-height: 1.62; opacity: 0.84; font-size: 1rem;}

        .method-card {border: 1px solid rgba(120,120,120,0.18); border-top: 6px solid #2563eb; border-radius: 18px; padding: 1.15rem 1.25rem 1.05rem 1.25rem; background: linear-gradient(180deg, rgba(68,124,201,0.05), rgba(255,255,255,0.9));}
        .method-card.green {border-top-color: #10b981; background: linear-gradient(180deg, rgba(16,185,129,0.06), rgba(255,255,255,0.9));}
        .method-title {font-size: 1.18rem; font-weight: 780; margin-bottom: 0.6rem;}
        .big-number {font-size: 2.55rem; font-weight: 830; line-height: 1.0; margin-bottom: 0.32rem; color: #111827;}
        .small-note {font-size: 0.98rem; opacity: 0.7;}
        .rate-text {font-size: 1.08rem; font-weight: 700; margin-top: 0.7rem;}

        .takeaway {border-left: 5px solid #4f46e5; border-radius: 10px; padding: 0.95rem 1.05rem; background: rgba(79,70,229,0.055); margin: 0.6rem 0 0.7rem 0; font-size: 1rem; line-height: 1.55;}
        .uav-card {border: 1px solid rgba(120,120,120,0.18); border-radius: 18px; padding: 1rem 0.9rem; text-align: center; background: rgba(255,255,255,0.88); min-height: 245px; box-shadow: 0 8px 18px rgba(15,23,42,0.04);}
        .uav-icon {width: 54px; height: auto; margin-bottom: 0.35rem;}
        .uav-name {font-weight: 800; font-size: 1.14rem; margin-bottom: 0.30rem; color: #111827;}
        .uav-meta {font-size: 0.97rem; opacity: 0.82; line-height: 1.58;}
        .status-row {margin-top: 0.55rem; display: flex; justify-content: center; gap: 0.35rem; flex-wrap: wrap;}
        .status-label {font-size: 0.90rem; color: #475569; font-weight: 700;}
        .status-badge {display:inline-block; padding: 0.22rem 0.56rem; border-radius: 999px; font-size: 0.88rem; font-weight: 800;}
        .pass-badge {background: rgba(16,185,129,0.14); color: #047857; border: 1px solid rgba(16,185,129,0.24);}
        .fail-badge {background: rgba(239,68,68,0.12); color: #B91C1C; border: 1px solid rgba(239,68,68,0.22);}
        .ok {color: #047857; font-weight: 800;}
        .bad {color: #B91C1C; font-weight: 800;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(120,120,120,0.18);}
        [data-testid="stSidebar"] .block-container {padding-top: 1.3rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

JP = {
    "Balanced links": "バランスの取れたリンク",
    "One weak UAV": "1機のUAVのリンクが弱い場合",
    "Different QoS demands": "QoS要求が異なる場合",
}


def channel_visual_level(ch):
    if ch < 0.040:
        return "weak", "#B91C1C", "#FEE2E2", "#FCA5A5"
    if ch < 0.075:
        return "medium", "#B45309", "#FEF3C7", "#FCD34D"
    return "good", "#1D4ED8", "#DBEAFE", "#93C5FD"


def scenario_reason_lines(name):
    data = {
        "Balanced links": [
            "UAV 1: clear path, medium distance / UAV1: 良好な光路・中距離",
            "UAV 2: slightly longer distance / UAV2: やや長い距離",
            "UAV 3: better alignment / UAV3: アライメントがやや良い",
            "UAV 4: clear path / UAV4: 良好な光路",
        ],
        "One weak UAV": [
            "UAV 1: clear path / UAV1: 良好な光路",
            "UAV 2: slightly longer distance / UAV2: やや長い距離",
            "UAV 3: longer distance + cloud loss / UAV3: 長距離＋雲減衰",
            "UAV 4: clear path / UAV4: 良好な光路",
        ],
        "Different QoS demands": [
            "UAV 1: relatively stable link / UAV1: 比較的安定",
            "UAV 2: weaker path / UAV2: やや弱い光路",
            "UAV 3: moderate attenuation / UAV3: やや大きい減衰",
            "UAV 4: stable link / UAV4: 安定したリンク",
        ],
    }
    return data[name]


def scenario_mapping_text(name):
    if name == "Balanced links":
        return "Channel differences are mainly caused by small distance or alignment differences. / チャネル差は主に距離やアライメントの小さな違いによって生じます。"
    if name == "One weak UAV":
        return "UAV 3 has a longer FSO path and cloud-related loss, so its channel becomes much weaker. / UAV3はFSO距離が長く、雲減衰もあるため、チャネルが大きく弱くなります。"
    return "Here, the link quality changes moderately, while the QoS targets also differ across UAVs. / このシナリオではリンク品質に差があり、QoS要求も異なります。"

with st.sidebar:
    st.markdown("## 🎛️ Visitor Controls / 操作パネル")
    st.caption("Change only these two controls and watch the network respond. / この2つだけを変えて、結果の変化を見てみましょう。")
    scenario_name = st.radio(
        "1 · Network scenario / シナリオ",
        list(SCENARIOS.keys()),
        index=1,
        format_func=lambda x: f"{x} / {JP.get(x, x)}",
        help="Choose how link conditions or QoS requirements differ among the UAVs.",
    )
    total_blocks = st.slider(
        "2 · Available OIRS blocks / 利用可能なOIRSブロック数",
        min_value=24,
        max_value=100,
        value=48,
        step=4,
        help="This is the total OIRS resource that must be shared among all UAVs.",
    )

uavs = SCENARIOS[scenario_name]
equal = equal_allocation(uavs, total_blocks)
qos = qos_aware_allocation(uavs, total_blocks)
eval_equal = evaluate(uavs, equal)
eval_qos = evaluate(uavs, qos)


def make_network_html(uavs, total_blocks, scenario_name):
    W, H = 990, 590
    gs_x, gs_y = 24, 316
    hap_x, hap_y = 560, 68
    oirs_x, oirs_y = 595, 120
    uav_positions = [(350, 300), (510, 318), (680, 318), (840, 300)]
    service_positions = [(345, 443), (505, 460), (675, 460), (835, 443)]
    uav_service_mid = [(388, 420), (548, 437), (718, 437), (878, 420)]

    def beam_line(x1, y1, x2, y2, color='#ef4444', width=5, dash='12 10', duration='2.2s', marker_end='url(#arrow-red)', opacity='0.95'):
        return f'''
        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"
              stroke-linecap="round" opacity="{opacity}" stroke-dasharray="{dash}" marker-end="{marker_end}">
          <animate attributeName="stroke-dashoffset" from="0" to="-44" dur="{duration}" repeatCount="indefinite" />
        </line>
        '''

    def glow_pulse(cx, cy, color='#ef4444', r=5, dur='2s'):
        return f'''
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="0.35">
          <animate attributeName="r" values="{r};{r+10};{r}" dur="{dur}" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.35;0.08;0.35" dur="{dur}" repeatCount="indefinite" />
        </circle>
        '''

    beam_parts = []
    beam_parts.append(beam_line(gs_x+122, gs_y+70, oirs_x+10, oirs_y+36, color='#ef4444', width=4.2, dash='9 8', duration='2.2s'))
    beam_parts.append(glow_pulse(245, 300, '#ef4444', r=4, dur='2.0s'))
    beam_parts.append(glow_pulse(420, 220, '#ef4444', r=4, dur='2.3s'))

    # short connector from HAP to OIRS to make them visually attached
    connector = '<line x1="650" y1="128" x2="650" y2="160" stroke="#64748B" stroke-width="3" opacity="0.55" />'

    for i, (ux, uy) in enumerate(uav_positions):
        level, line_color, _, _ = channel_visual_level(uavs[i].channel_factor)
        if level == "weak":
            width = 2.9
            pulse_color = '#ef4444'
            marker = 'url(#arrow-red)'
        elif level == "medium":
            width = 3.2
            pulse_color = '#f59e0b'
            marker = 'url(#arrow-orange)'
            line_color = '#f59e0b'
        else:
            width = 3.5
            pulse_color = '#60a5fa'
            marker = 'url(#arrow-blue)'
            line_color = '#2563eb'
        beam_parts.append(beam_line(oirs_x+60, oirs_y+78, ux+42, uy+22, color=line_color, width=width, dash='10 8', duration=f'{2.0 + i*0.25}s', marker_end=marker))
        midx = int((oirs_x+60 + ux+42) / 2)
        midy = int((oirs_y+78 + uy+22) / 2)
        beam_parts.append(glow_pulse(midx, midy, pulse_color, r=4, dur=f'{1.8 + i*0.18}s'))

    # UAV to users light communication lines
    service_link_parts = []
    for (ux, uy), (mx, my) in zip(uav_positions, uav_service_mid):
        service_link_parts.append(beam_line(ux+42, uy+58, mx, my, color='#22c55e', width=2.2, dash='5 6', duration='2.6s', marker_end='url(#arrow-green)', opacity='0.72'))

    if scenario_name == "One weak UAV":
        cloud_elems = f'''
      <image href="{ASSETS['cloud']}" x="642" y="218" width="122" height="74" opacity="0.82" />
      <text x="705" y="212" text-anchor="middle" font-size="12.5" fill="#6B7280">Cloud loss / 雲減衰</text>
      <text x="315" y="262" text-anchor="middle" font-size="14" font-weight="700" fill="#dc2626">FSO uplink</text>
      <text x="730" y="296" text-anchor="middle" font-size="14" font-weight="700" fill="#B91C1C">Weak FSO link</text>
    '''
    elif scenario_name == "Balanced links":
        cloud_elems = f'''
      <text x="315" y="262" text-anchor="middle" font-size="14" font-weight="700" fill="#2563eb">FSO uplink</text>
      <text x="758" y="288" text-anchor="middle" font-size="14" font-weight="700" fill="#2563eb">FSO links</text>
    '''
    else:
        cloud_elems = f'''
      <image href="{ASSETS['cloud']}" x="470" y="208" width="104" height="64" opacity="0.58" />
      <text x="522" y="203" text-anchor="middle" font-size="12.5" fill="#6B7280">Mild loss / 軽い減衰</text>
      <text x="315" y="262" text-anchor="middle" font-size="14" font-weight="700" fill="#dc2626">FSO uplink</text>
      <text x="754" y="288" text-anchor="middle" font-size="14" font-weight="700" fill="#b45309">Different link quality</text>
    '''

    service_groups = []
    for (sx, sy) in service_positions:
        service_groups.append(f'''
        <g opacity="0.66">
          <ellipse cx="{sx+20}" cy="{sy+58}" rx="83" ry="24" fill="#DCFCE7" opacity="0.67" stroke="#86EFAC" stroke-width="1.6"/>
          <image href="{ASSETS['house1']}" x="{sx-35}" y="{sy+6}" width="36" height="36" />
          <image href="{ASSETS['house2']}" x="{sx+7}" y="{sy+0}" width="42" height="42" />
          <image href="{ASSETS['tree']}" x="{sx-64}" y="{sy+12}" width="28" height="36" opacity="0.9"/>
          <image href="{ASSETS['tree']}" x="{sx+46}" y="{sy+12}" width="26" height="33" opacity="0.9"/>
          <image href="{ASSETS['person']}" x="{sx-5}" y="{sy+20}" width="18" height="30" />
          <image href="{ASSETS['wifi']}" x="{sx-9}" y="{sy+7}" width="20" height="20" opacity="0.65"/>
        </g>
        ''')
    service_groups.append(f'''
      <image href="{ASSETS['car']}" x="555" y="505" width="36" height="25" opacity="0.78"/>
      <text x="650" y="565" text-anchor="middle" font-size="16" fill="#374151">Service area / サービスエリア</text>
    ''')

    uav_labels = []
    for idx, ((ux, uy), u) in enumerate(zip(uav_positions, uavs), start=1):
        level, text_color, bg_color, stroke_color = channel_visual_level(u.channel_factor)
        tag = 'WEAK' if level == 'weak' else ('MEDIUM' if level == 'medium' else 'GOOD')
        uav_labels.append(f'''
        <g>
          <image href="{ASSETS['uav']}" x="{ux}" y="{uy}" width="84" height="54" />
          <text x="{ux+42}" y="{uy+63}" text-anchor="middle" font-size="19" font-weight="700" fill="#111827">UAV {idx}</text>
          <rect x="{ux-8}" y="{uy+69}" width="100" height="18" rx="9" fill="{bg_color}" stroke="{stroke_color}" stroke-width="1" opacity="0.96" />
          <text x="{ux+42}" y="{uy+82}" text-anchor="middle" font-size="13.5" font-weight="700" fill="{text_color}">Channel: {u.channel_factor:.3f}</text>
          <rect x="{ux-29}" y="{uy+91}" width="142" height="18" rx="9" fill="#DCFCE7" opacity="0.96" />
          <text x="{ux+42}" y="{uy+104}" text-anchor="middle" font-size="13.2" font-weight="700" fill="#047857">QoS target: {u.qos_requirement:.1f} Gbps</text>
          <text x="{ux+42}" y="{uy+121}" text-anchor="middle" font-size="11.8" font-weight="700" fill="{text_color}">{tag}</text>
        </g>
        ''')

    html = f'''
    <div style="border:1px solid rgba(120,120,120,0.18);border-radius:20px;background:linear-gradient(180deg,rgba(96,165,250,0.06),rgba(240,249,255,0.82));padding:14px;font-family:Arial,Helvetica,sans-serif;">
      <div style="text-align:center;font-size:24px;font-weight:800;margin-bottom:4px;">Limited OIRS resource / 利用可能なOIRS資源: {total_blocks} blocks</div>
      <div style="text-align:center;font-size:16px;opacity:0.72;margin-bottom:8px;">Conceptual system overview for Open Lab / オープンラボ向けシステム全体図</div>
      <svg viewBox="0 0 {W} {H}" width="100%" height="545" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bggrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#F8FBFF"/>
            <stop offset="100%" stop-color="#F3F8FC"/>
          </linearGradient>
          <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
          </marker>
          <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#22c55e" />
          </marker>
          <marker id="arrow-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
          </marker>
          <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
          </marker>
          <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <rect x="0" y="0" width="{W}" height="{H}" rx="22" fill="url(#bggrad)" />

        <text x="495" y="34" text-anchor="middle" font-size="18" font-weight="700" fill="#1F2937">HAP-assisted Optical IRS Aerial Network / HAP支援型光IRS空中ネットワーク</text>

        <image href="{ASSETS['gs']}" x="{gs_x}" y="{gs_y}" width="150" height="188" />
        <text x="{gs_x+72}" y="{gs_y+201}" text-anchor="middle" font-size="22" font-weight="700" fill="#111827">Optical Ground Station</text>
        <text x="{gs_x+72}" y="{gs_y+223}" text-anchor="middle" font-size="16" fill="#374151">OGS / 光地上局</text>

        <image href="{ASSETS['hap']}" x="{hap_x}" y="{hap_y}" width="205" height="104" />
        {connector}
        <image href="{ASSETS['oirs']}" x="{oirs_x}" y="{oirs_y}" width="118" height="108" filter="url(#softGlow)" />
        <text x="{hap_x+128}" y="{hap_y+8}" text-anchor="middle" font-size="18" font-weight="700" fill="#111827">HAP</text>
        <text x="{oirs_x+58}" y="{oirs_y+120}" text-anchor="middle" font-size="17" font-weight="700" fill="#111827">Optical IRS / 光IRS</text>
        <text x="{oirs_x+58}" y="{oirs_y+139}" text-anchor="middle" font-size="14" fill="#6B7280">Mirror array / ミラーアレイ</text>

        {''.join(beam_parts)}
        {''.join(service_link_parts)}
        {cloud_elems}

        {''.join(uav_labels)}
        {''.join(service_groups)}
      </svg>
    </div>
    '''
    return html


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🛰️ Smart Optical IRS Allocation for Multi-UAV Networks</div>
        <div class="hero-subtitle">
            Explore how a limited OIRS resource can be shared among UAVs with different link conditions and QoS needs. / 限られたOIRS資源を、リンク状態やQoS要求が異なる複数のUAVにどのように割り当てるかを可視化します。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown('<div class="step-card blue"><div class="step-number">Step 1</div><div class="step-title">🎯 Choose a scenario / シナリオ選択</div><div class="step-text">Balanced links, one weak UAV, or different QoS demands. / 3つの条件から選択します。</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="step-card green"><div class="step-number">Step 2</div><div class="step-title">🎚️ Change OIRS resources / OIRS資源変更</div><div class="step-text">Move the slider and see how limited resources affect the network. / ブロック数を変えて影響を確認します。</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="step-card orange"><div class="step-number">Step 3</div><div class="step-title">⚖️ Compare two strategies / 2方式を比較</div><div class="step-text">Equal allocation versus QoS-aware allocation. / 均等分配とQoS重視分配を比較します。</div></div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-band band-blue">Big picture / 全体像</div>', unsafe_allow_html=True)
st.markdown("## One OIRS, multiple UAV links / 1つのOIRSで複数UAVリンクを支援")
left, right = st.columns([1.65, 1], gap="large")
with left:
    components.html(make_network_html(uavs, total_blocks, scenario_name), height=625, scrolling=False)
with right:
    st.markdown(f'''<div class="info-card"><h4>💡 The research question / 研究課題</h4><p>A HAP-mounted Optical IRS supports several UAV links, but the total OIRS resource is limited. Should every UAV receive the same amount, or should the allocation adapt to each UAV's link condition and QoS requirement?<br><br>HAP搭載型光IRSは複数のUAVリンクを支援しますが、利用できるOIRS資源は限られています。各UAVに均等に割り当てるべきか、それともリンク状態やQoS要求に応じて柔軟に割り当てるべきかを考えます。</p></div>''', unsafe_allow_html=True)
    st.write("")
    bullets = ''.join([f'<li>{x}</li>' for x in scenario_reason_lines(scenario_name)])
    st.markdown(f'''<div class="scenario-highlight"><div class="scenario-pill">Current scenario / 現在のシナリオ</div><h4 style="margin:0 0 0.45rem 0;">🧪 {scenario_name} / {JP.get(scenario_name, scenario_name)}</h4><p style="margin:0 0 0.55rem 0; line-height:1.62; opacity:0.86;">{scenario_explanation(scenario_name)}</p><p style="margin:0 0 0.45rem 0; line-height:1.58; opacity:0.9;"><b>Why do the channels differ?</b> / <b>なぜチャネルが違うのか？</b><br>{scenario_mapping_text(scenario_name)}</p><ul style="margin:0.2rem 0 0 1.05rem; padding:0; line-height:1.5;">{bullets}</ul><p style="margin:0.55rem 0 0 0; color:#B91C1C; font-weight:700;">Red highlight = weak channel / 赤色ハイライト = 弱いチャネル</p></div>''', unsafe_allow_html=True)

st.markdown('<div class="section-band band-green">Compare / 比較</div>', unsafe_allow_html=True)
st.markdown("## Equal allocation vs. QoS-aware allocation / 均等分配とQoS重視分配")
eq_col, arrow_col, qa_col = st.columns([1, 0.18, 1])
with eq_col:
    st.markdown(f'''<div class="method-card"><div class="method-title">Equal Allocation / 均等分配</div><div class="big-number">{eval_equal['num_satisfied']} / {len(uavs)}</div><div class="small-note">UAVs satisfy QoS / QoS達成UAV数</div><div class="rate-text">{eval_equal['total_rate']:.2f} normalized total rate / 正規化総レート</div></div>''', unsafe_allow_html=True)
with arrow_col:
    st.markdown("<div style='text-align:center; font-size:2.4rem; font-weight:800; padding-top:2.5rem; color:#334155;'>→</div>", unsafe_allow_html=True)
with qa_col:
    st.markdown(f'''<div class="method-card green"><div class="method-title">QoS-Aware Allocation / QoS重視分配</div><div class="big-number">{eval_qos['num_satisfied']} / {len(uavs)}</div><div class="small-note">UAVs satisfy QoS / QoS達成UAV数</div><div class="rate-text">{eval_qos['total_rate']:.2f} normalized total rate / 正規化総レート</div></div>''', unsafe_allow_html=True)

st.write("")
allocation_df = pd.DataFrame({
    "UAV": [f"UAV {i+1}" for i in range(len(uavs))] * 2,
    "OIRS blocks": equal + qos,
    "Method": ["Equal Allocation"] * len(uavs) + ["QoS-Aware Allocation"] * len(uavs),
})
bar = px.bar(
    allocation_df,
    x="UAV",
    y="OIRS blocks",
    color="Method",
    barmode="group",
    text="OIRS blocks",
    color_discrete_map={
        "Equal Allocation": "#2563EB",
        "QoS-Aware Allocation": "#10B981",
    },
)
bar.update_traces(textposition="outside", textfont_size=16)
bar.update_layout(
    height=450,
    margin=dict(l=12, r=12, t=30, b=10),
    legend_title_text="",
    xaxis_title="",
    yaxis_title="Allocated OIRS blocks / 割り当てブロック数",
    font=dict(size=17),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.75)",
    legend=dict(font=dict(size=16)),
    xaxis=dict(tickfont=dict(size=16)),
    yaxis=dict(tickfont=dict(size=15), gridcolor="rgba(148,163,184,0.25)"),
)
st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

st.markdown("### What happens to each UAV? / 各UAVの結果")
reason_lines = scenario_reason_lines(scenario_name)
uav_cols = st.columns(len(uavs))
for idx, (col, u) in enumerate(zip(uav_cols, uavs), start=1):
    eq_ok = eval_equal["satisfied"][idx-1]
    qa_ok = eval_qos["satisfied"][idx-1]
    eq_class = "pass-badge" if eq_ok else "fail-badge"
    qa_class = "pass-badge" if qa_ok else "fail-badge"
    eq_text = "✓ Pass" if eq_ok else "✕ Fail"
    qa_text = "✓ Pass" if qa_ok else "✕ Fail"
    _, text_color, bg_color, stroke_color = channel_visual_level(u.channel_factor)
    with col:
        st.markdown(
            f'''<div class="uav-card"><img src="{ASSETS['uav']}" class="uav-icon" alt="uav icon" /><div class="uav-name">UAV {idx}</div><div class="uav-meta"><span style="display:inline-block;padding:0.2rem 0.55rem;border-radius:999px;background:{bg_color};color:{text_color};border:1px solid {stroke_color};font-weight:800;">Channel: {u.channel_factor:.3f}</span><br><span style="display:inline-block;margin-top:0.42rem;">QoS target: <b>{u.qos_requirement:.1f} Gbps</b></span><br><span style="display:inline-block;margin-top:0.42rem;font-size:0.88rem;color:{text_color};font-weight:700;">{reason_lines[idx-1]}</span></div><div class="status-row"><span class="status-label">Equal</span><span class="status-badge {eq_class}">{eq_text}</span></div><div class="status-row"><span class="status-label">QoS-aware</span><span class="status-badge {qa_class}">{qa_text}</span></div></div>''',
            unsafe_allow_html=True,
        )

st.write("")
if eval_qos["num_satisfied"] > eval_equal["num_satisfied"]:
    takeaway = f"With the same {total_blocks} OIRS blocks, QoS-aware allocation increases the number of satisfied UAVs from {eval_equal['num_satisfied']} to {eval_qos['num_satisfied']}. / 同じ{total_blocks}ブロックでも、QoS重視分配はQoS達成UAV数を{eval_equal['num_satisfied']}から{eval_qos['num_satisfied']}へ増やします。"
elif eval_qos["num_satisfied"] == eval_equal["num_satisfied"] and eval_qos["num_satisfied"] == len(uavs):
    takeaway = "Both strategies satisfy all UAVs in this setting. Try reducing the available OIRS blocks or switching to a more difficult scenario. / この条件では両方式とも全UAVがQoSを達成しています。OIRSブロック数を減らすか、より厳しいシナリオに変更してみてください。"
else:
    takeaway = "In this setting, both strategies satisfy the same number of UAVs. Change the scenario or resource budget to explore when adaptive allocation becomes useful. / この条件では両方式の達成数は同じです。シナリオや資源量を変更して違いを見てみましょう。"

st.markdown(f'''<div class="takeaway"><b>✨ Key takeaway / ポイント</b><br>{takeaway}</div>''', unsafe_allow_html=True)
with st.expander("🎤 30-second explanation for visitors / 来場者向け30秒説明"):
    st.markdown("**We have one Optical IRS with limited resources, but several UAVs need support. Equal allocation gives every UAV the same number of OIRS blocks. Our QoS-aware approach instead considers each UAV's link condition and service requirement. Try changing the scenario or the total OIRS resource and see how the allocation changes. Red channel labels show weak links caused by distance or weather loss.**\n\n**限られた光IRS資源を、複数のUAVにどう配分するかを示すデモです。均等分配では全UAVに同じ数のブロックを与えますが、QoS重視分配ではリンク状態やQoS要求を考慮して配分します。シナリオやブロック数を変えて違いを見てください。**")
with st.expander("🔬 Technical note / 技術メモ"):
    st.markdown("This Open Lab version uses a **simplified educational model** to visualize the allocation idea. The displayed rate values are simplified educational outputs and are **not numerical results from the paper/thesis**.\n\nFor a publication-faithful version, replace the simplified model in `model.py` with the exact channel/rate equations, or load precomputed results exported from the original simulation code.\n\nこのオープンラボ版は、割り当ての考え方を分かりやすく示すための**簡易教育モデル**です。表示されるレート値は正規化されたものであり、**論文や学位論文の数値結果そのものではありません**。")

st.caption("CCL Open Lab 2026 · Interactive educational demo inspired by QoS-aware OIRS resource allocation for HAP-assisted multi-UAV networks. / CCLオープンラボ2026向けインタラクティブ教育デモ")
