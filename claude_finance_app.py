import streamlit as st
import anthropic
import json
import time
from datetime import datetime, timedelta
import math

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Claude AI · Finance Professionals",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Styling ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --burnt-orange: #C94F0C;
    --deep-black: #0D0D0D;
    --off-white: #F2EDE4;
    --warm-gray: #8C8378;
    --card-bg: #1A1A1A;
    --border: #2E2E2E;
    --green: #1DB954;
    --purple: #9B59B6;
    --teal: #1ABC9C;
    --gold: #F39C12;
    --red: #E74C3C;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--deep-black);
    color: var(--off-white);
}
.stApp { background: var(--deep-black); }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown { padding: 0.2rem 0; }

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a0800 0%, #0D0D0D 40%, #0a1a0a 100%);
    border: 1px solid var(--burnt-orange);
    border-radius: 16px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(201,79,12,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    color: var(--off-white);
    line-height: 1.1;
    margin: 0;
}
.hero-title span { color: var(--burnt-orange); }
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--warm-gray);
    margin-top: 0.8rem;
    font-weight: 300;
    letter-spacing: 0.02em;
}
.hero-badge {
    display: inline-block;
    background: rgba(201,79,12,0.2);
    border: 1px solid var(--burnt-orange);
    color: var(--burnt-orange);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    margin-top: 1.2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Module Cards ── */
.module-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.module-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.module-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.module-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
}
.module-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.module-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--off-white);
    margin-bottom: 0.3rem;
}
.module-desc { font-size: 0.8rem; color: var(--warm-gray); line-height: 1.5; }

/* ── Section Headers ── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--off-white);
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-header .accent { color: var(--burnt-orange); }

/* ── Prompt Cards ── */
.prompt-card {
    background: #141414;
    border: 1px solid var(--border);
    border-left: 3px solid var(--burnt-orange);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
}
.prompt-card:hover {
    background: #1e1e1e;
    border-left-color: var(--accent, var(--burnt-orange));
}
.prompt-title { font-weight: 600; font-size: 0.9rem; color: var(--off-white); }
.prompt-preview { font-size: 0.78rem; color: var(--warm-gray); margin-top: 0.25rem; }

/* ── AI Output ── */
.ai-output-container {
    background: #0F1A0F;
    border: 1px solid #1e3a1e;
    border-radius: 12px;
    padding: 1.75rem;
    margin-top: 1.5rem;
    position: relative;
}
.ai-output-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: var(--green);
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.ai-output-header::before {
    content: '●';
    color: var(--green);
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── DCF Calculator ── */
.dcf-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}
.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.8rem;
    font-weight: 500;
    color: var(--teal);
}
.metric-label { font-size: 0.78rem; color: var(--warm-gray); margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Streamlit overrides ── */
.stButton > button {
    background: var(--burnt-orange) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #a83d08 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(201,79,12,0.4) !important;
}
.stTextArea textarea {
    background: #141414 !important;
    border: 1px solid var(--border) !important;
    color: var(--off-white) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #141414 !important;
    border: 1px solid var(--border) !important;
    color: var(--off-white) !important;
    border-radius: 8px !important;
}
.stSlider [data-testid="stSlider"] { color: var(--burnt-orange); }
div[data-testid="stExpander"] {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: var(--warm-gray);
}
.stTabs [aria-selected="true"] {
    color: var(--burnt-orange) !important;
    border-bottom-color: var(--burnt-orange) !important;
}
.stSuccess { background: rgba(29,185,84,0.1) !important; border: 1px solid rgba(29,185,84,0.3) !important; }
.stInfo { background: rgba(26,188,156,0.1) !important; border: 1px solid rgba(26,188,156,0.3) !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Data: Prompts Library ────────────────────────────────────────────────────
MODULES = {
    "equity_research": {
        "name": "Equity Research",
        "name_zh": "股票研究",
        "icon": "📈",
        "color": "#F39C12",
        "desc": "Institutional-grade equity analysis, buy/sell ratings, price targets",
        "prompts": [
            {
                "title": "Initiation of Coverage Report",
                "title_zh": "首次覆蓋報告",
                "template": """You are a senior equity research analyst at a top-tier investment bank. Write an institutional-grade Initiation of Coverage report for {ticker} ({company_name}).

Structure:
1. **Investment Thesis** (3 key catalysts)
2. **Rating & Price Target** (12-month)
3. **Business Overview** (competitive positioning, moat analysis)
4. **Financial Analysis** (Revenue/EBITDA trends, margins)
5. **Valuation** (EV/EBITDA, P/E vs peers)
6. **Key Risks** (bull/base/bear scenarios)
7. **Conclusion**

Ticker: {ticker}
Company: {company_name}
Sector: {sector}
Current Price: ${current_price}

Write in Goldman Sachs research style. Be specific with numbers and catalysts."""
            },
            {
                "title": "Earnings Preview Analysis",
                "title_zh": "業績前瞻分析",
                "template": """You are a buy-side equity analyst. Write an earnings preview for {ticker} ahead of their Q{quarter} {year} earnings report.

Include:
1. **Consensus Estimates** vs your estimates
2. **Key Metrics to Watch** (revenue, margins, guidance)
3. **Bull/Bear Scenarios**
4. **Options Implied Move** analysis
5. **Historical Earnings Reaction** patterns
6. **Positioning Recommendation** (pre-earnings trade setup)

Company: {company_name} ({ticker})
Quarter: Q{quarter} {year}
Street EPS Est: ${eps_est}

Format as an actionable trading note."""
            },
            {
                "title": "Peer Comparison Analysis",
                "title_zh": "同業比較分析",
                "template": """Create an institutional peer comparison analysis for {ticker} vs its competitors.

Include:
1. **Comparable Universe** (5-7 peers)
2. **Valuation Multiples Table** (EV/Revenue, EV/EBITDA, P/E, P/B, PEG)
3. **Growth Metrics** (Revenue CAGR, EPS growth)
4. **Profitability** (Gross/EBITDA/Net margins)
5. **Return Metrics** (ROE, ROIC, FCF yield)
6. **Relative Valuation Assessment**
7. **Premium/Discount Justification**

Primary Stock: {ticker} ({company_name})
Sector: {sector}

Present as if writing for a portfolio manager."""
            },
            {
                "title": "Sum-of-the-Parts Valuation",
                "title_zh": "分部估值",
                "template": """Perform a Sum-of-the-Parts (SOTP) valuation analysis for {ticker}.

Structure:
1. **Business Segment Breakdown** (revenue & EBITDA per segment)
2. **Segment-Specific Multiples** (justify each multiple vs pure-play peers)
3. **SOTP Valuation Table** (EV per segment → Total EV → Equity Value → Per Share)
4. **Conglomerate Discount/Premium Analysis**
5. **Sensitivity Table** (±1x multiple)
6. **Implied Upside/Downside** from current price

Company: {company_name} ({ticker})
Current Market Cap: ${market_cap}B
Current Price: ${current_price}"""
            },
        ]
    },
    "dcf_valuation": {
        "name": "DCF Valuation",
        "name_zh": "DCF估值",
        "icon": "💰",
        "color": "#1ABC9C",
        "desc": "Discounted cash flow models, WACC, terminal value analysis",
        "prompts": [
            {
                "title": "Full DCF Model Buildout",
                "title_zh": "完整DCF模型",
                "template": """Build a comprehensive DCF valuation model for {company_name} ({ticker}).

Provide:
1. **Assumptions Summary** (revenue growth, EBITDA margin, capex/sales, NWC%)
2. **5-Year FCF Projection Table** (Revenue → EBIT → NOPAT → FCF)
3. **WACC Calculation** (cost of equity via CAPM, cost of debt, capital structure)
4. **Terminal Value** (Gordon Growth + Exit Multiple methods)
5. **Enterprise Value Bridge** (EV → Net Debt → Equity Value → Per Share)
6. **Sensitivity Analysis** (WACC vs Terminal Growth Rate matrix)
7. **Bear/Base/Bull** scenario values

Sector: {sector}
LTM Revenue: ${revenue}M
LTM EBITDA Margin: {ebitda_margin}%
Current Price: ${current_price}
Shares Outstanding: {shares}M"""
            },
            {
                "title": "WACC Calculation Deep Dive",
                "title_zh": "WACC深度計算",
                "template": """Calculate and justify the WACC for {company_name} ({ticker}).

Provide step-by-step:
1. **Cost of Equity** (Risk-free rate + Beta × ERP + size/country premium)
2. **Beta Analysis** (raw, levered, unlevered, re-levered vs target structure)
3. **Cost of Debt** (yield-to-maturity, tax shield)
4. **Capital Structure** (market value weights)
5. **Final WACC** with sensitivity to ±0.5% on each input
6. **Peer WACC Benchmarking**
7. **Football Field Chart** (implied ranges from DCF, comps, precedents)

Company: {company_name} ({ticker})
Market Cap: ${market_cap}B
Total Debt: ${total_debt}B
Tax Rate: {tax_rate}%
Credit Rating: {credit_rating}"""
            },
        ]
    },
    "fixed_income": {
        "name": "Fixed Income",
        "name_zh": "固定收益",
        "icon": "📊",
        "color": "#9B59B6",
        "desc": "Bond analysis, yield curves, credit spreads, duration risk",
        "prompts": [
            {
                "title": "Credit Analysis Report",
                "title_zh": "信用分析報告",
                "template": """Write an institutional credit analysis report for {issuer} bonds.

Include:
1. **Credit Summary** (rating, outlook, key credit metrics)
2. **Business Risk Assessment** (competitive position, sector dynamics)
3. **Financial Risk Profile** (leverage, coverage ratios, liquidity)
4. **Debt Structure Analysis** (maturity profile, covenants, security)
5. **Rating Agency Scorecard** (Moody's/S&P framework)
6. **Relative Value** (spread vs peers, Z-spread, OAS)
7. **Investment Recommendation** (Overweight/Neutral/Underweight)

Issuer: {issuer}
Bond: {bond_description}
Current Rating: {rating}
Current Spread: {spread}bps over Treasury
Maturity: {maturity}"""
            },
            {
                "title": "Yield Curve Analysis",
                "title_zh": "收益率曲線分析",
                "template": """Provide an institutional-grade yield curve analysis and rate outlook.

Cover:
1. **Current Curve Shape** (normal/flat/inverted analysis)
2. **Key Rate Levels** (2Y, 5Y, 10Y, 30Y) and recent moves
3. **2s10s Spread** historical context and recession implications
4. **Fed Policy Outlook** (dots plot, forward guidance interpretation)
5. **Duration Positioning** recommendation (short/neutral/long)
6. **Sector Allocation** (Treasuries vs IG vs HY vs EM)
7. **Rates Trade Ideas** (specific curve trades, roll-down strategies)

Analysis Date: {date}
10Y Treasury: {ten_year}%
2Y Treasury: {two_year}%
Fed Funds Target: {fed_funds}%"""
            },
        ]
    },
    "portfolio_strategy": {
        "name": "Portfolio Strategy",
        "name_zh": "組合策略",
        "icon": "🥧",
        "color": "#1DB954",
        "desc": "Asset allocation, risk management, factor exposure, rebalancing",
        "prompts": [
            {
                "title": "Portfolio Construction Framework",
                "title_zh": "組合構建框架",
                "template": """Design an institutional portfolio construction framework for {portfolio_type}.

Provide:
1. **Investment Policy Statement** (objectives, constraints, time horizon)
2. **Strategic Asset Allocation** (equity/fixed income/alternatives/cash)
3. **Factor Tilts** (value, momentum, quality, low-vol) with rationale
4. **Geographic Allocation** (US/International/EM weights)
5. **Sector Overweights/Underweights** vs benchmark
6. **Risk Budget** (tracking error, VaR, max drawdown limits)
7. **Rebalancing Rules** (calendar vs threshold triggers)
8. **Expected Return & Risk** (5-year Sharpe ratio target)

Portfolio Type: {portfolio_type}
AUM: ${aum}M
Benchmark: {benchmark}
Risk Tolerance: {risk_level}"""
            },
            {
                "title": "Risk Attribution Analysis",
                "title_zh": "風險歸因分析",
                "template": """Perform a comprehensive risk attribution analysis for the portfolio.

Analyze:
1. **Total Portfolio VaR** (95% and 99% confidence, 1-day and 10-day)
2. **Factor Risk Decomposition** (market, sector, style factors)
3. **Correlation Matrix** insights and concentration risk
4. **Stress Test Results** (2008 GFC, 2020 COVID, 2022 Rate Shock)
5. **Tail Risk Metrics** (CVaR, max drawdown, Sortino ratio)
6. **Position-Level Risk Contribution**
7. **Hedging Recommendations** (options, futures, correlation trades)

Portfolio Holdings: {holdings_description}
Portfolio Beta: {beta}
Current VIX: {vix}"""
            },
        ]
    },
    "earnings_analysis": {
        "name": "Earnings Analysis",
        "name_zh": "業績分析",
        "icon": "🔍",
        "color": "#E74C3C",
        "desc": "Earnings quality, beat/miss analysis, guidance interpretation",
        "prompts": [
            {
                "title": "Earnings Quality Deep Dive",
                "title_zh": "業績質量深度分析",
                "template": """Analyze the earnings quality for {company_name} ({ticker}) most recent quarter.

Examine:
1. **Revenue Quality** (organic vs acquisitions, one-time items, channel stuffing signs)
2. **Margin Analysis** (gross/EBIT/net trends, mix shift, pricing power)
3. **Cash Conversion** (net income vs FCF, accruals ratio)
4. **Balance Sheet Changes** (receivables, inventory, payables—warning signs?)
5. **Non-GAAP Adjustments** critique (what's being excluded and why)
6. **Guidance Analysis** (conservative/aggressive vs history, credibility score)
7. **Management Commentary** key phrases and tone analysis
8. **Overall Quality Score** (1-10) with investment implication

Company: {company_name} ({ticker})
Reported EPS: ${reported_eps} vs Est ${est_eps}
Revenue: ${revenue}M vs Est ${est_revenue}M
YoY Revenue Growth: {revenue_growth}%"""
            },
            {
                "title": "Post-Earnings Trade Setup",
                "title_zh": "業績後交易設置",
                "template": """Design a post-earnings trading strategy for {ticker} after their results.

Include:
1. **Reaction Assessment** (beat/miss magnitude, guidance delta)
2. **Price Action Analysis** (gap fill risk, support/resistance levels)
3. **Options Strategy** (if IV crush favors spreads vs directional)
4. **Momentum Signal** (continuation vs mean reversion probability)
5. **Fundamental Re-rating** (has the story changed?)
6. **Entry/Exit Parameters** (specific price levels, stop losses, targets)
7. **Position Sizing** recommendation
8. **Timeline** (1-day, 1-week, 1-month expected move)

Ticker: {ticker}
Earnings Result: {result_description}
Pre-earnings Price: ${pre_price}
Post-earnings Price: ${post_price}
IV Rank: {iv_rank}%"""
            },
        ]
    },
    "investment_banking": {
        "name": "Investment Banking",
        "name_zh": "投資銀行",
        "icon": "🏛️",
        "color": "#C94F0C",
        "desc": "M&A analysis, LBO modeling, pitch books, deal structuring",
        "prompts": [
            {
                "title": "M&A Deal Analysis",
                "title_zh": "併購交易分析",
                "template": """Analyze the M&A transaction between {acquirer} acquiring {target}.

Provide:
1. **Strategic Rationale** (synergies, market position, capabilities acquired)
2. **Valuation Analysis** (deal multiples vs precedent transactions and trading comps)
3. **Synergy Quantification** (revenue synergies, cost synergies, timeline)
4. **Accretion/Dilution Analysis** (EPS impact Year 1, Year 2, Year 3)
5. **Deal Financing** (cash/stock/debt mix, pro forma leverage)
6. **Risk Assessment** (integration, regulatory, cultural, overpayment risk)
7. **Shareholder Value Assessment** (acquirer and target perspectives)
8. **Recommendation** for each party's shareholders

Acquirer: {acquirer}
Target: {target}
Deal Value: ${deal_value}B
Premium Paid: {premium}%
Deal Structure: {structure}"""
            },
            {
                "title": "LBO Model Framework",
                "title_zh": "LBO模型框架",
                "template": """Build an LBO analysis framework for a private equity acquisition of {company_name}.

Structure:
1. **Purchase Price** (entry multiple and rationale)
2. **Sources & Uses Table** (debt tranches, equity check, fees)
3. **Debt Structure** (senior secured, mezzanine, PIK terms)
4. **Operating Projections** (revenue growth, EBITDA margin expansion levers)
5. **Debt Paydown Schedule** (free cash flow sweep, covenant compliance)
6. **Exit Analysis** (Year 3/4/5 at various exit multiples)
7. **Returns Analysis** (IRR and MoM at each exit scenario)
8. **Key Value Creation Levers** for the PE sponsor

Target: {company_name}
LTM EBITDA: ${ebitda}M
Entry Multiple: {entry_multiple}x EBITDA
Target Hold Period: {hold_period} years
Target IRR: {target_irr}%"""
            },
        ]
    }
}

# ─── Helper: Call Claude API ──────────────────────────────────────────────────
def call_claude(prompt: str, system: str = "") -> str:
    """Call Anthropic API with streaming."""
    client = anthropic.Anthropic(api_key=st.session_state.get("api_key", ""))
    
    messages = [{"role": "user", "content": prompt}]
    sys_prompt = system or "You are an elite Wall Street analyst with 20+ years of experience at Goldman Sachs, Morgan Stanley, and Bridgewater. Provide institutional-grade financial analysis with specific numbers, actionable insights, and professional formatting. Use markdown with headers, tables, and bullet points."
    
    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=sys_prompt,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            yield text

# ─── DCF Calculator ───────────────────────────────────────────────────────────
def calculate_dcf(revenue, revenue_growth, ebitda_margin, tax_rate, capex_pct, 
                  wacc, terminal_growth, net_debt, shares_out, years=5):
    """Simple DCF calculator."""
    fcfs = []
    rev = revenue
    for i in range(years):
        rev = rev * (1 + revenue_growth / 100)
        ebitda = rev * (ebitda_margin / 100)
        ebit = ebitda * 0.85  # approximate D&A
        nopat = ebit * (1 - tax_rate / 100)
        capex = rev * (capex_pct / 100)
        fcf = nopat - capex + (ebitda - ebit)  # + D&A
        fcfs.append(fcf)
    
    # PV of FCFs
    pv_fcfs = sum(fcf / (1 + wacc/100)**i for i, fcf in enumerate(fcfs, 1))
    
    # Terminal Value (Gordon Growth)
    terminal_fcf = fcfs[-1] * (1 + terminal_growth/100)
    tv = terminal_fcf / (wacc/100 - terminal_growth/100)
    pv_tv = tv / (1 + wacc/100)**years
    
    enterprise_value = pv_fcfs + pv_tv
    equity_value = enterprise_value - net_debt
    price_per_share = equity_value / shares_out if shares_out > 0 else 0
    
    return {
        "pv_fcfs": pv_fcfs,
        "pv_tv": pv_tv,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "price_per_share": price_per_share,
        "fcfs": fcfs,
        "tv_pct": pv_tv / enterprise_value * 100 if enterprise_value > 0 else 0
    }

# ─── Session State Init ───────────────────────────────────────────────────────
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "active_module" not in st.session_state:
    st.session_state.active_module = "equity_research"
if "ai_output" not in st.session_state:
    st.session_state.ai_output = ""
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem;'>
        <div style='font-family: Playfair Display, serif; font-size: 1.4rem; font-weight: 900; color: #F2EDE4;'>
            Claude <span style='color: #C94F0C;'>Finance</span>
        </div>
        <div style='font-size: 0.75rem; color: #8C8378; margin-top: 0.25rem;'>Institutional AI Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language Toggle
    lang = st.radio("Language / 語言", ["EN", "繁中"], horizontal=True, key="lang_select")
    st.session_state.lang = lang
    
    st.divider()
    
    # API Key
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="sk-ant-..."
    )
    if api_key:
        st.session_state.api_key = api_key
        st.success("✓ API Key set" if lang == "EN" else "✓ API Key 已設定")
    
    st.divider()
    
    # Module Navigation
    st.markdown("<div style='font-size:0.75rem; color:#8C8378; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem;'>MODULES</div>", unsafe_allow_html=True)
    
    for key, mod in MODULES.items():
        label = f"{mod['icon']} {mod['name']}" if lang == "EN" else f"{mod['icon']} {mod['name_zh']}"
        is_active = st.session_state.active_module == key
        if st.button(label, key=f"nav_{key}", use_container_width=True, 
                     type="primary" if is_active else "secondary"):
            st.session_state.active_module = key
            st.session_state.ai_output = ""
            st.rerun()
    
    st.divider()
    st.markdown("<div style='font-size:0.75rem; color:#8C8378; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem;'>TOOLS</div>", unsafe_allow_html=True)
    
    if st.button("🧮 DCF Calculator", use_container_width=True):
        st.session_state.active_module = "dcf_calculator"
        st.rerun()

# ─── Main Content ─────────────────────────────────────────────────────────────

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Claude <span>AI</span> for<br>Finance Professionals</div>
    <div class="hero-subtitle">120+ Institutional-Grade Prompts · Financial Models · AI-Powered Analysis</div>
    <div class="hero-badge">🏦 Wall Street Grade</div>
</div>
""", unsafe_allow_html=True)

# ─── DCF Calculator Module ────────────────────────────────────────────────────
if st.session_state.active_module == "dcf_calculator":
    st.markdown('<div class="section-header">🧮 <span class="accent">DCF</span> Valuation Calculator</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Operating Assumptions")
        revenue = st.number_input("LTM Revenue ($M)", value=10000, step=100)
        revenue_growth = st.slider("Revenue Growth (%)", 0.0, 30.0, 8.0, 0.5)
        ebitda_margin = st.slider("EBITDA Margin (%)", 5.0, 50.0, 25.0, 0.5)
        capex_pct = st.slider("CapEx % of Revenue", 1.0, 20.0, 5.0, 0.5)
        tax_rate = st.slider("Tax Rate (%)", 10.0, 35.0, 21.0, 0.5)
    
    with col2:
        st.markdown("##### Valuation Parameters")
        wacc = st.slider("WACC (%)", 5.0, 15.0, 9.0, 0.25)
        terminal_growth = st.slider("Terminal Growth Rate (%)", 1.0, 4.0, 2.5, 0.25)
        net_debt = st.number_input("Net Debt ($M) — negative = net cash", value=2000, step=100)
        shares_out = st.number_input("Shares Outstanding (M)", value=500, step=10)
        current_price = st.number_input("Current Stock Price ($)", value=150.0, step=1.0)
    
    if st.button("⚡ Run DCF Model", use_container_width=True):
        results = calculate_dcf(revenue, revenue_growth, ebitda_margin, tax_rate,
                                capex_pct, wacc, terminal_growth, net_debt, shares_out)
        
        implied = results["price_per_share"]
        updown = ((implied - current_price) / current_price * 100) if current_price > 0 else 0
        color = "#1DB954" if updown > 0 else "#E74C3C"
        
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:#1ABC9C">${results['enterprise_value']:,.0f}M</div>
                <div class="metric-label">Enterprise Value</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:#1ABC9C">${results['equity_value']:,.0f}M</div>
                <div class="metric-label">Equity Value</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{color}">${implied:,.2f}</div>
                <div class="metric-label">Implied Share Price</div></div>""", unsafe_allow_html=True)
        with c4:
            arrow = "▲" if updown > 0 else "▼"
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{color}">{arrow} {abs(updown):.1f}%</div>
                <div class="metric-label">Upside / Downside</div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='margin-top:1rem; background:#141414; border:1px solid #2E2E2E; border-radius:10px; padding:1.25rem;'>
            <div style='font-size:0.8rem; color:#8C8378; margin-bottom:0.5rem;'>VALUE BRIDGE SUMMARY</div>
            <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; font-family: DM Mono, monospace; font-size:0.85rem;'>
                <div><span style='color:#8C8378;'>PV of FCFs:</span> <span style='color:#F2EDE4;'>${results['pv_fcfs']:,.0f}M</span></div>
                <div><span style='color:#8C8378;'>PV Terminal Value:</span> <span style='color:#F2EDE4;'>${results['pv_tv']:,.0f}M</span></div>
                <div><span style='color:#8C8378;'>TV as % of EV:</span> <span style='color:#F39C12;'>{results['tv_pct']:.1f}%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sensitivity Table
        st.markdown("##### 📊 Sensitivity: Implied Price vs WACC & Terminal Growth")
        wacc_range = [wacc - 1, wacc - 0.5, wacc, wacc + 0.5, wacc + 1]
        tg_range = [terminal_growth - 0.5, terminal_growth, terminal_growth + 0.5]
        
        import pandas as pd
        rows = {}
        for tg in tg_range:
            row = {}
            for w in wacc_range:
                r = calculate_dcf(revenue, revenue_growth, ebitda_margin, tax_rate,
                                  capex_pct, w, tg, net_debt, shares_out)
                row[f"WACC {w:.1f}%"] = f"${r['price_per_share']:,.2f}"
            rows[f"TGR {tg:.1f}%"] = row
        
        df = pd.DataFrame(rows).T
        st.dataframe(df, use_container_width=True)

# ─── Finance Module Pages ─────────────────────────────────────────────────────
else:
    mod_key = st.session_state.active_module
    if mod_key not in MODULES:
        mod_key = "equity_research"
    
    mod = MODULES[mod_key]
    lang = st.session_state.lang
    mod_name = mod['name'] if lang == "EN" else mod['name_zh']
    
    st.markdown(f'<div class="section-header">{mod["icon"]} <span class="accent">{mod_name}</span></div>', unsafe_allow_html=True)
    
    # Prompt Selector
    prompt_titles = [p['title'] if lang == 'EN' else p['title_zh'] for p in mod['prompts']]
    selected_idx = st.selectbox(
        "Select Analysis Template" if lang == "EN" else "選擇分析模板",
        range(len(prompt_titles)),
        format_func=lambda i: f"📄 {prompt_titles[i]}"
    )
    
    selected_prompt = mod['prompts'][selected_idx]
    template = selected_prompt['template']
    
    # Extract variables from template
    import re
    variables = list(set(re.findall(r'\{(\w+)\}', template)))
    
    st.markdown("---")
    col_form, col_preview = st.columns([1, 1])
    
    with col_form:
        st.markdown(f"##### {'Fill in Parameters' if lang == 'EN' else '填寫參數'}")
        
        var_defaults = {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "sector": "Technology",
            "current_price": "175.00",
            "quarter": "2",
            "year": "2025",
            "eps_est": "1.45",
            "market_cap": "2.8",
            "total_debt": "95",
            "tax_rate": "21",
            "credit_rating": "Aaa",
            "revenue": "385,000",
            "ebitda_margin": "32",
            "shares": "15,500",
            "portfolio_type": "Balanced Growth",
            "aum": "500",
            "benchmark": "S&P 500",
            "risk_level": "Moderate",
            "holdings_description": "60% Equity, 30% Fixed Income, 10% Alternatives",
            "beta": "1.05",
            "vix": "18",
            "issuer": "Apple Inc.",
            "bond_description": "3.850% Notes due 2043",
            "rating": "Aaa",
            "spread": "85",
            "maturity": "2043",
            "date": datetime.now().strftime("%B %d, %Y"),
            "ten_year": "4.35",
            "two_year": "4.85",
            "fed_funds": "5.25-5.50",
            "reported_eps": "1.53",
            "est_eps": "1.45",
            "est_revenue": "119,000",
            "revenue_growth": "5.1",
            "result_description": "Beat EPS by $0.08, revenue inline, guidance raised",
            "pre_price": "170.00",
            "post_price": "178.50",
            "iv_rank": "45",
            "acquirer": "Microsoft Corp.",
            "target": "GitHub",
            "deal_value": "7.5",
            "premium": "34",
            "structure": "All-cash",
            "ebitda": "450",
            "entry_multiple": "12",
            "hold_period": "5",
            "target_irr": "25",
            "terminal_growth": "2.5",
            "wacc": "9.0",
            "net_debt": "2000",
        }
        
        user_inputs = {}
        for var in sorted(variables):
            default = var_defaults.get(var, "")
            user_inputs[var] = st.text_input(
                var.replace("_", " ").title(),
                value=default,
                key=f"input_{var}"
            )
    
    with col_preview:
        st.markdown(f"##### {'Prompt Preview' if lang == 'EN' else '提示詞預覽'}")
        filled = template
        for k, v in user_inputs.items():
            filled = filled.replace(f"{{{k}}}", v if v else f"[{k}]")
        st.text_area("", value=filled, height=300, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Custom prompt option
    with st.expander("✏️ " + ("Custom Prompt Override" if lang == "EN" else "自定義提示詞")):
        custom_prompt = st.text_area(
            "Override the prompt entirely:" if lang == "EN" else "完全覆蓋提示詞：",
            height=150
        )
    
    btn_label = "⚡ Generate AI Analysis" if lang == "EN" else "⚡ 生成 AI 分析"
    
    if st.button(btn_label, use_container_width=True):
        if not st.session_state.api_key:
            st.error("Please enter your Anthropic API Key in the sidebar." if lang == "EN" else "請在側欄輸入 Anthropic API Key。")
        else:
            final_prompt = custom_prompt if custom_prompt.strip() else filled
            
            st.markdown(f"""
            <div class="ai-output-container">
                <div class="ai-output-header">CLAUDE AI · INSTITUTIONAL ANALYSIS</div>
            """, unsafe_allow_html=True)
            
            output_placeholder = st.empty()
            full_text = ""
            
            try:
                for chunk in call_claude(final_prompt):
                    full_text += chunk
                    output_placeholder.markdown(full_text)
                
                st.session_state.ai_output = full_text
                
            except Exception as e:
                st.error(f"API Error: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Show saved output
    if st.session_state.ai_output and not st.button:
        st.markdown(f"""
        <div class="ai-output-container">
            <div class="ai-output-header">CLAUDE AI · LAST OUTPUT</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#8C8378; font-size:0.75rem; padding: 1rem 0;'>
    Claude AI for Finance Professionals · Powered by Anthropic Claude · 
    <span style='color:#C94F0C;'>Institutional Grade Analysis</span>
</div>
""", unsafe_allow_html=True)
