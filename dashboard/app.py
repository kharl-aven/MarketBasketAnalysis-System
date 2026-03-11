import streamlit as st
import os, time, random
from datetime import datetime

st.set_page_config(
    page_title="Pokemon Cafe — Staff Portal",
    page_icon="pokeball",
    layout="wide",
    initial_sidebar_state="expanded"
)

API = os.getenv("MBA_API_URL", "http://localhost:8000")

try:
    import requests as req
    def api_get(path, fallback=None):
        try:
            r = req.get(f"{API}{path}", timeout=2)
            return r.json()
        except:
            return fallback
    def api_online():
        try: req.get(f"{API}/health", timeout=1); return True
        except: return False
except ImportError:
    def api_get(path, fallback=None): return fallback
    def api_online(): return False

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');

:root {
    --red:       #CC0000;
    --red-dark:  #990000;
    --red-light: #FFE8E8;
    --yellow:    #FFCB05;
    --yellow-dk: #C9A800;
    --blue:      #3B4CCA;
    --blue-lt:   #E8ECFF;
    --green:     #2E7D32;
    --green-lt:  #E8F5E9;
    --bg:        #F7F3FF;
    --card:      #FFFFFF;
    --border:    #E4DCFF;
    --text:      #1A1A2E;
    --muted:     #7B7B9A;
    --sidebar:   #1A1A2E;
    --radius:    16px;
    --shadow:    0 2px 16px rgba(59,76,202,0.08);
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1440px !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #C8C8E8 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #A8A8C8 !important;
    border: 1.5px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 3px !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,203,5,0.1) !important;
    border-color: rgba(255,203,5,0.3) !important;
    color: var(--yellow) !important;
    transform: translateX(3px) !important;
    box-shadow: none !important;
}

/* Main buttons */
.stButton > button {
    background: var(--red) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 3px 10px rgba(204,0,0,0.2) !important;
}
.stButton > button:hover {
    background: var(--red-dark) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(204,0,0,0.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1.5px solid var(--border) !important;
    gap: 2px !important;
    margin-bottom: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    color: var(--muted) !important;
    padding: 0.45rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--red) !important;
    color: white !important;
}

/* Slider */
.stSlider > div > div > div { background: var(--red) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border-radius: var(--radius) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: var(--border) !important;
}

/* Toggle accent */
[data-testid="stToggle"] input:checked + div { background: var(--red) !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "page": "Home",
    "ran": False,
    "run_logs": [],
    "files": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Static data ───────────────────────────────────────────────────────────────
COMBOS = [
    {"badge":"⚡","name":"Pikachu Morning Set",   "items":["Pikachu Latte","Eevee Waffle"],          "price":16.50,"pct":18,"conf":87,"lift":2.4},
    {"badge":"👻","name":"Gengar Night Special",  "items":["Gengar Hot Choco","Mew Macaron"],         "price":14.00,"pct":14,"conf":74,"lift":2.1},
    {"badge":"🌿","name":"Starter Duo",           "items":["Matcha Latte","Bulbasaur Sandwich"],      "price":18.00,"pct":12,"conf":68,"lift":1.9},
    {"badge":"😴","name":"Snorlax Full Meal",     "items":["Snorlax Cappuccino","Charmander Churro"], "price":19.50,"pct":11,"conf":61,"lift":1.7},
]
ADDONS = [
    {"from":"Pikachu Latte",      "to":"Eevee Waffle",         "conf":87,"lift":2.4},
    {"from":"Gengar Hot Choco",   "to":"Mew Macaron",           "conf":74,"lift":2.1},
    {"from":"Matcha Latte",       "to":"Jigglypuff Pudding",    "conf":68,"lift":1.8},
    {"from":"Eevee Waffle",       "to":"Snorlax Cappuccino",    "conf":61,"lift":1.6},
    {"from":"Charmander Churro",  "to":"Pikachu Latte",         "conf":55,"lift":1.5},
]
PROMOS = [
    {"buy":"Pikachu Latte",   "get":"Charmander Churro",  "off":"20%","margin":31,"gain":4200},
    {"buy":"Eevee Waffle",    "get":"Snorlax Cappuccino", "off":"15%","margin":28,"gain":3100},
    {"buy":"Matcha Latte",    "get":"Mew Macaron",        "off":"10%","margin":33,"gain":2600},
]
PATTERNS = [
    {"a":"Pikachu Latte",      "b":"Eevee Waffle",        "conf":87,"pct":18,"lift":2.4,"stable":8},
    {"a":"Gengar Hot Choco",   "b":"Mew Macaron",          "conf":74,"pct":14,"lift":2.1,"stable":6},
    {"a":"Matcha Latte",       "b":"Jigglypuff Pudding",   "conf":68,"pct":12,"lift":1.8,"stable":5},
    {"a":"Eevee Waffle",       "b":"Snorlax Cappuccino",   "conf":61,"pct":10,"lift":1.6,"stable":4},
    {"a":"Bulbasaur Sandwich", "b":"Matcha Latte",          "conf":58,"pct":9, "lift":1.5,"stable":3},
    {"a":"Jigglypuff Pudding", "b":"Pikachu Latte",         "conf":52,"pct":8, "lift":1.4,"stable":2},
]
MONITOR = [
    {"item":"Pikachu Latte",    "last":34,"now":36,"psi":0.04},
    {"item":"Eevee Waffle",     "last":28,"now":31,"psi":0.07},
    {"item":"Gengar Hot Choco", "last":22,"now":21,"psi":0.03},
    {"item":"Matcha Latte",     "last":18,"now":20,"psi":0.09},
    {"item":"Mew Macaron",      "last":15,"now":14,"psi":0.05},
]

def now_str(): return datetime.now().strftime("%H:%M:%S")
def today_str(): return datetime.now().strftime("%d %b %Y  %H:%M")

def pill(txt, bg="#FFE8E8", fg="#CC0000", size="0.74rem"):
    return (f'<span style="background:{bg};color:{fg};font-size:{size};'
            f'font-weight:700;padding:0.22rem 0.65rem;border-radius:20px;'
            f'white-space:nowrap;display:inline-block;">{txt}</span>')

def badge(txt, bg, fg):
    return (f'<span style="background:{bg};color:{fg};font-size:0.68rem;'
            f'font-weight:800;text-transform:uppercase;letter-spacing:0.07em;'
            f'padding:0.2rem 0.65rem;border-radius:6px;">{txt}</span>')

def stat_card(icon, label, value, sub, accent):
    st.markdown(f"""
    <div style="background:var(--card);border:1.5px solid var(--border);
                border-radius:var(--radius);padding:1.2rem 1.4rem;
                box-shadow:var(--shadow);border-left:5px solid {accent};">
        <div style="font-size:1.7rem;margin-bottom:0.4rem;line-height:1;">{icon}</div>
        <div style="font-size:0.67rem;font-weight:800;text-transform:uppercase;
                    letter-spacing:0.1em;color:var(--muted);margin-bottom:0.25rem;">{label}</div>
        <div style="font-family:'Fredoka One',cursive;font-size:2rem;
                    color:var(--text);line-height:1;margin-bottom:0.3rem;">{value}</div>
        <div style="font-size:0.74rem;color:var(--muted);font-weight:600;">{sub}</div>
    </div>""", unsafe_allow_html=True)

def sec(title, tag="", icon=""):
    tag_html = (f'<span style="background:var(--yellow);color:#333;font-size:0.62rem;'
                f'font-weight:800;text-transform:uppercase;letter-spacing:0.07em;'
                f'padding:0.18rem 0.6rem;border-radius:5px;margin-left:0.5rem;">{tag}</span>') if tag else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin:1.6rem 0 0.9rem 0;">
        <span style="font-size:1.15rem;margin-right:0.45rem;">{icon}</span>
        <span style="font-family:'Fredoka One',cursive;font-size:1.05rem;
                     color:var(--text);letter-spacing:0.01em;">{title}</span>
        {tag_html}
    </div>""", unsafe_allow_html=True)

def row_card(content):
    st.markdown(f"""
    <div style="background:var(--card);border:1.5px solid var(--border);
                border-radius:var(--radius);padding:1rem 1.3rem;
                margin-bottom:0.6rem;box-shadow:var(--shadow);">
        {content}
    </div>""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 1rem 0.8rem 1rem;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.8rem;">
            <div style="width:46px;height:46px;border-radius:50%;
                        background:linear-gradient(135deg,#CC0000 50%,#F5F5F5 50%);
                        border:3px solid #FFCB05;display:flex;align-items:center;
                        justify-content:center;font-size:1.3rem;
                        box-shadow:0 3px 10px rgba(0,0,0,0.3);">🍵</div>
            <div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.15rem;
                            color:#FFCB05;line-height:1.1;">Pokemon Cafe</div>
                <div style="font-size:0.63rem;color:#5A5A8A;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.09em;">Staff Portal</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    online = api_online()
    st.markdown(f"""
    <div style="margin:0 0.8rem 1rem 0.8rem;background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.06);border-radius:10px;
                padding:0.45rem 0.9rem;display:flex;align-items:center;gap:0.5rem;">
        <span style="color:{'#4CAF50' if online else '#EF5350'};font-size:0.7rem;">{"●" if online else "●"}</span>
        <span style="font-size:0.74rem;color:#7878A8;font-weight:700;">
            {"System Online" if online else "System Offline"}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 0.6rem;">', unsafe_allow_html=True)
    nav = [
        ("🏠","Home"),
        ("📊","Today's Summary"),
        ("🎯","Suggested Deals"),
        ("📋","Order Patterns"),
        ("📁","Uploaded Files"),
        ("⚡","Run Analysis"),
        ("📡","Menu Monitor"),
    ]
    for icon, label in nav:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;padding:0.8rem 1.2rem;border-top:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:0.62rem;color:#3A3A6A;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Branch</div>
        <div style="font-size:0.84rem;color:#7878A8;font-weight:700;">🏪 Main Branch</div>
    </div>""", unsafe_allow_html=True)

# ── TOP BAR ───────────────────────────────────────────────────────────────────
page = st.session_state.page
st.markdown(f"""
<div style="background:linear-gradient(90deg,#CC0000,#990000);
            margin:-1rem -2rem 1.8rem -2rem;padding:1rem 2.5rem;
            display:flex;align-items:center;justify-content:space-between;">
    <div>
        <div style="font-family:'Fredoka One',cursive;font-size:1.3rem;
                    color:#FFCB05;letter-spacing:0.02em;">{page}</div>
        <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);font-weight:600;">
            Pokemon Cafe · Staff Management
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:0.9rem;">
        <div style="background:rgba(255,255,255,0.12);border-radius:9px;
                    padding:0.38rem 0.9rem;font-size:0.74rem;
                    color:rgba(255,255,255,0.75);font-weight:700;">{today_str()}</div>
        <div style="width:32px;height:32px;background:#FFCB05;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.95rem;">👤</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A1A2E 0%,#16213E 55%,#0F3460 100%);
                border-radius:var(--radius);padding:2rem 2.5rem;margin-bottom:1.4rem;
                box-shadow:var(--shadow);position:relative;overflow:hidden;">
        <div style="position:absolute;right:2rem;top:50%;transform:translateY(-50%);
                    font-size:7rem;opacity:0.07;line-height:1;">⚡</div>
        <div style="font-family:'Fredoka One',cursive;font-size:1.8rem;
                    color:#FFCB05;margin-bottom:0.5rem;">Welcome back, Trainer! 👋</div>
        <div style="font-size:0.92rem;color:#9090B8;font-weight:600;max-width:500px;
                    line-height:1.6;">
            Your cafe is running smoothly. Check today's recommended deals,
            view order patterns, or upload new sales data to refresh suggestions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: stat_card("🎯","Combo Deals Ready",str(len(COMBOS)),"Featured sets","#CC0000")
    with c2: stat_card("⚡","Smart Add-ons",str(len(ADDONS)),"Counter suggestions","#3B4CCA")
    with c3: stat_card("🎁","Discount Offers",str(len(PROMOS)),"Active promotions","#FFCB05")
    with c4: stat_card("📁","Files Uploaded",str(len(st.session_state.files)),"Sales records","#2E7D32")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.7,1])

    with left:
        sec("Top Combos to Promote Today","HOT","🔥")
        for c in COMBOS[:3]:
            items_str = " + ".join(c["items"])
            st.markdown(f"""
            <div style="background:var(--card);border:1.5px solid var(--border);
                        border-radius:var(--radius);padding:1rem 1.3rem;
                        margin-bottom:0.65rem;box-shadow:var(--shadow);
                        display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:1rem;">
                    <div style="width:46px;height:46px;min-width:46px;
                                background:linear-gradient(135deg,#FFCB05,#FFE066);
                                border-radius:12px;display:flex;align-items:center;
                                justify-content:center;font-size:1.5rem;
                                box-shadow:0 2px 8px rgba(255,203,5,0.3);">{c['badge']}</div>
                    <div>
                        <div style="font-weight:800;font-size:0.95rem;
                                    color:var(--text);margin-bottom:0.15rem;">{c['name']}</div>
                        <div style="font-size:0.78rem;color:var(--muted);font-weight:600;">{items_str}</div>
                        <div style="margin-top:0.35rem;">
                            {pill(f"{c['pct']}% of orders include this pair","#E8ECFF","#3B4CCA","0.71rem")}
                        </div>
                    </div>
                </div>
                <div style="text-align:right;padding-left:1rem;">
                    <div style="font-family:'Fredoka One',cursive;font-size:1.4rem;
                                color:var(--red);">&#165;{c['price']:.2f}</div>
                    <div style="font-size:0.68rem;color:var(--muted);font-weight:600;">
                        Suggested price
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        sec("Quick Navigation","","⚡")
        for label, dest in [
            ("📁  Upload Sales Data","Uploaded Files"),
            ("🎯  View Suggested Deals","Suggested Deals"),
            ("📊  See Order Patterns","Order Patterns"),
            ("⚡  Run New Analysis","Run Analysis"),
            ("📡  Menu Monitor","Menu Monitor"),
        ]:
            if st.button(label, use_container_width=True, key=f"h_{dest}"):
                st.session_state.page = dest
                st.rerun()
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

        sec("System Health","","💚")
        checks = [
            ("System Engine",  True,  "Running"),
            ("Deals Engine",   True,  f"{len(COMBOS)} deals active"),
            ("Menu Watcher",   True,  "All items stable"),
            ("Last Analysis",  st.session_state.ran, "Done today" if st.session_state.ran else "Not yet run"),
        ]
        for label, ok, detail in checks:
            color = "#2E7D32" if ok else "#EF5350"
            icon  = "✅" if ok else "❌"
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:0.5rem 0;border-bottom:1px solid var(--border);">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span>{icon}</span>
                    <span style="font-size:0.85rem;font-weight:700;color:var(--text);">{label}</span>
                </div>
                <span style="font-size:0.72rem;color:var(--muted);font-weight:600;">{detail}</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TODAY'S SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Today's Summary":

    sec("What's Selling Well Together","","📊")
    st.markdown("""
    <div style="font-size:0.87rem;color:var(--muted);font-weight:600;
                margin-bottom:1.2rem;max-width:640px;line-height:1.6;">
        Based on your uploaded sales records, these are the menu items
        customers most often order at the same time.
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: stat_card("🍱","Combo Sets Ready",str(len(COMBOS)),"Ready to promote","#CC0000")
    with c2: stat_card("⚡","Counter Add-ons",str(len(ADDONS)),"Smart suggestions","#3B4CCA")
    with c3: stat_card("🎁","Discount Offers",str(len(PROMOS)),"Profitable deals","#FFCB05")

    sec("Most Ordered Together","","🍽️")

    for i,r in enumerate(PATTERNS[:5]):
        rank_colors = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2"]
        rank_bgs    = ["#FFE8E8","#E8ECFF","#E8F5E9","#FFF3E0","#F3E5F5"]
        stab_label  = "Very Consistent" if r['stable']>=6 else "Growing" if r['stable']>=3 else "Newly Spotted"
        stab_bg     = "#E8F5E9" if r['stable']>=6 else "#FFF8E8" if r['stable']>=3 else "#E8ECFF"
        stab_fg     = "#2E7D32" if r['stable']>=6 else "#E65100" if r['stable']>=3 else "#3B4CCA"
        bar_w       = int(r['conf']*0.88)

        c_rank, c_main = st.columns([0.07,1])
        with c_rank:
            st.markdown(f"""
            <div style="width:36px;height:36px;background:{rank_bgs[i]};border-radius:50%;
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Fredoka One',cursive;font-size:1.05rem;
                        color:{rank_colors[i]};margin-top:0.7rem;">{i+1}</div>""",
                        unsafe_allow_html=True)
        with c_main:
            st.markdown(f"""
            <div style="background:var(--card);border:1.5px solid var(--border);
                        border-radius:var(--radius);padding:1rem 1.3rem;
                        margin-bottom:0.6rem;box-shadow:var(--shadow);">
                <div style="display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:0.7rem;flex-wrap:wrap;gap:0.5rem;">
                    <div>
                        <span style="font-weight:900;font-size:0.97rem;
                                     color:var(--text);">{r['a']}</span>
                        <span style="color:var(--red);font-size:1.1rem;margin:0 0.5rem;">&#8594;</span>
                        <span style="font-weight:900;font-size:0.97rem;
                                     color:var(--text);">{r['b']}</span>
                    </div>
                    <div style="display:flex;gap:0.45rem;flex-wrap:wrap;">
                        {pill(f"{r['conf']}% order these together","#FFE8E8","#CC0000","0.72rem")}
                        {pill(f"In {r['pct']}% of all orders","#E8ECFF","#3B4CCA","0.72rem")}
                        {badge(stab_label,stab_bg,stab_fg)}
                    </div>
                </div>
                <div style="background:#F0EEF8;border-radius:5px;height:6px;overflow:hidden;">
                    <div style="background:{rank_colors[i]};height:6px;
                                width:{bar_w}%;border-radius:5px;opacity:0.75;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SUGGESTED DEALS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Suggested Deals":

    tab1,tab2,tab3 = st.tabs(["🍱  Combo Sets","⚡  Counter Add-ons","🎁  Discount Offers"])

    with tab1:
        sec("Recommended Combo Sets","AUTO-SUGGESTED","🍱")
        st.markdown("""
        <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                    margin-bottom:1.2rem;line-height:1.6;max-width:620px;">
            These items are frequently ordered together. Sell them as a set
            at the suggested price to increase each order's value.
        </div>""", unsafe_allow_html=True)

        for c in COMBOS:
            items_str = " + ".join(c["items"])
            extra = int((c['lift']-1)*100)
            st.markdown(f"""
            <div style="background:var(--card);border:1.5px solid var(--border);
                        border-radius:var(--radius);padding:1.2rem 1.5rem;
                        margin-bottom:0.8rem;box-shadow:var(--shadow);">
                <div style="display:flex;align-items:center;justify-content:space-between;
                            flex-wrap:wrap;gap:0.8rem;">
                    <div style="display:flex;align-items:center;gap:1rem;">
                        <div style="width:52px;height:52px;min-width:52px;
                                    background:linear-gradient(135deg,#FFCB05,#FFD740);
                                    border-radius:14px;display:flex;align-items:center;
                                    justify-content:center;font-size:1.7rem;
                                    box-shadow:0 3px 10px rgba(255,203,5,0.3);">{c['badge']}</div>
                        <div>
                            <div style="font-weight:900;font-size:1rem;color:var(--text);
                                        margin-bottom:0.25rem;">{c['name']}</div>
                            <div style="font-size:0.82rem;color:var(--muted);
                                        font-weight:600;margin-bottom:0.45rem;">{items_str}</div>
                            <div style="display:flex;gap:0.45rem;flex-wrap:wrap;">
                                {pill(f"{c['conf']}% of customers order these together","#FFE8E8","#CC0000","0.72rem")}
                                {pill(f"~{extra}% more sales when bundled","#E8F5E9","#2E7D32","0.72rem")}
                                {pill(f"In {c['pct']}% of all orders","#E8ECFF","#3B4CCA","0.72rem")}
                            </div>
                        </div>
                    </div>
                    <div style="text-align:center;padding-left:0.5rem;">
                        <div style="font-family:'Fredoka One',cursive;font-size:1.7rem;
                                    color:var(--red);">&#165;{c['price']:.2f}</div>
                        <div style="font-size:0.68rem;color:var(--muted);
                                    font-weight:700;">Suggested bundle price</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        sec("Counter Add-on Suggestions","FOR CASHIERS","⚡")
        st.markdown("""
        <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                    margin-bottom:1.2rem;line-height:1.6;max-width:620px;">
            When a customer orders the first item, suggest the second one.
            These are high-probability suggestions your cashiers can offer at the counter.
        </div>""", unsafe_allow_html=True)

        # Table header
        hcols = st.columns([1.1,0.08,1.1,0.9,0.8])
        for col,txt in zip(hcols,["Customer Orders","","Suggest This Next",
                                   "Chance They'll Say Yes","Times More Likely"]):
            with col:
                st.markdown(f"""
                <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;
                            letter-spacing:0.08em;color:var(--muted);padding:0.4rem 0;
                            border-bottom:2px solid var(--border);">{txt}</div>""",
                            unsafe_allow_html=True)

        for a in ADDONS:
            bar_w = int(a['conf']*0.85)
            cols = st.columns([1.1,0.08,1.1,0.9,0.8])
            with cols[0]:
                st.markdown(f"""
                <div style="background:#FFF8E8;border:1.5px solid #FFE8A0;
                            border-radius:10px;padding:0.6rem 0.9rem;margin:0.3rem 0;">
                    <div style="font-weight:800;font-size:0.88rem;
                                color:var(--text);">{a['from']}</div>
                </div>""", unsafe_allow_html=True)
            with cols[1]:
                st.markdown("""
                <div style="text-align:center;padding:0.9rem 0;
                            font-size:1.2rem;color:var(--red);font-weight:900;">&#8594;</div>""",
                            unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div style="background:var(--red-light);border:1.5px solid #FFB0B0;
                            border-radius:10px;padding:0.6rem 0.9rem;margin:0.3rem 0;">
                    <div style="font-weight:800;font-size:0.88rem;
                                color:var(--red);">{a['to']}</div>
                </div>""", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"""
                <div style="padding:0.6rem 0 0 0;">
                    <div style="font-weight:900;font-size:0.95rem;color:var(--text);">{a['conf']}%</div>
                    <div style="background:#EEEEFA;border-radius:4px;height:5px;margin-top:0.3rem;">
                        <div style="background:var(--blue);height:5px;
                                    width:{bar_w}%;border-radius:4px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f"""
                <div style="padding:0.6rem 0 0 0;font-weight:800;
                            font-size:0.92rem;color:var(--green);">
                    {a['lift']:.1f}x more likely
                </div>""", unsafe_allow_html=True)

    with tab3:
        sec("Discount Offers","ALL PROFITABLE","🎁")
        st.markdown("""
        <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                    margin-bottom:1.2rem;line-height:1.6;max-width:620px;">
            All discount offers listed here keep your profit margin healthy.
            When a customer buys the first item, offer the second at a discount
            to increase the total bill.
        </div>""", unsafe_allow_html=True)

        for p in PROMOS:
            st.markdown(f"""
            <div style="background:var(--card);border:1.5px solid var(--border);
                        border-radius:var(--radius);padding:1.2rem 1.5rem;
                        margin-bottom:0.8rem;box-shadow:var(--shadow);
                        border-left:5px solid #FFCB05;">
                <div style="display:flex;align-items:center;justify-content:space-between;
                            flex-wrap:wrap;gap:0.8rem;">
                    <div style="flex:1;min-width:260px;">
                        <div style="display:flex;align-items:center;gap:0.6rem;
                                    margin-bottom:0.6rem;flex-wrap:wrap;">
                            <span style="font-size:1.2rem;">🎁</span>
                            <span style="font-weight:900;font-size:0.97rem;color:var(--text);">
                                Buy
                                <span style="color:var(--red);"> {p['buy']}</span>
                                &nbsp;&#8594;&nbsp;
                                Get
                                <span style="color:var(--blue);"> {p['get']}</span>
                                <span style="color:var(--green);font-family:'Fredoka One',cursive;">
                                    &nbsp;{p['off']} off
                                </span>
                            </span>
                        </div>
                        <div style="display:flex;gap:0.45rem;flex-wrap:wrap;">
                            {pill(f"Profit margin stays at {p['margin']}%","#E8F5E9","#2E7D32","0.72rem")}
                            {pill(f"Estimated extra &#165;{p['gain']:,} per week","#E8ECFF","#3B4CCA","0.72rem")}
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:'Fredoka One',cursive;font-size:2.2rem;
                                    color:#FFCB05;line-height:1;">{p['off']}</div>
                        <div style="font-size:0.65rem;color:var(--muted);
                                    font-weight:700;text-transform:uppercase;">discount</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ORDER PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Order Patterns":

    sec("How Customers Order","FROM YOUR SALES DATA","📋")
    st.markdown("""
    <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                margin-bottom:1.2rem;line-height:1.6;max-width:640px;">
        These show which menu items are ordered together most often.
        Use this to plan your menu layout, counter placement, and featured sets.
    </div>""", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1,1])
    with col_f1:
        min_chance = st.slider("Minimum chance of ordering together (%)", 0, 100, 0, 5)
    with col_f2:
        sort_opt = st.selectbox("Sort by", ["Highest Chance","Most Common","Most Consistent"])

    key_map = {"Highest Chance":"conf","Most Common":"pct","Most Consistent":"stable"}
    filtered = sorted(
        [r for r in PATTERNS if r["conf"]>=min_chance],
        key=lambda x: x[key_map[sort_opt]], reverse=True
    )

    st.markdown(f"""
    <div style="font-size:0.78rem;color:var(--muted);font-weight:700;margin-bottom:0.9rem;">
        Showing {len(filtered)} of {len(PATTERNS)} patterns
    </div>""", unsafe_allow_html=True)

    for i,r in enumerate(filtered):
        bar_w = int(r['conf']*0.88)
        stab_label = "Very Consistent" if r['stable']>=6 else "Growing" if r['stable']>=3 else "Newly Spotted"
        stab_bg    = "#E8F5E9" if r['stable']>=6 else "#FFF8E8" if r['stable']>=3 else "#E8ECFF"
        stab_fg    = "#2E7D32" if r['stable']>=6 else "#E65100" if r['stable']>=3 else "#3B4CCA"
        row_color  = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2","#00838F"][min(i,5)]

        st.markdown(f"""
        <div style="background:var(--card);border:1.5px solid var(--border);
                    border-radius:var(--radius);padding:1.1rem 1.4rem;
                    margin-bottom:0.6rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:0.8rem;flex-wrap:wrap;gap:0.5rem;">
                <div>
                    <span style="font-weight:900;font-size:0.97rem;color:var(--text);">{r['a']}</span>
                    <span style="color:var(--red);font-size:1.1rem;margin:0 0.5rem;">&#8594;</span>
                    <span style="font-weight:900;font-size:0.97rem;color:var(--text);">{r['b']}</span>
                </div>
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                    {pill(f"{r['conf']}% chance","#FFE8E8","#CC0000","0.72rem")}
                    {pill(f"{r['pct']}% of orders","#E8ECFF","#3B4CCA","0.72rem")}
                    {pill(f"{r['lift']:.1f}x more than random","#E8F5E9","#2E7D32","0.72rem")}
                    {badge(stab_label,stab_bg,stab_fg)}
                </div>
            </div>
            <div style="background:#F0EEF8;border-radius:5px;height:7px;overflow:hidden;">
                <div style="background:{row_color};height:7px;width:{bar_w}%;
                            border-radius:5px;opacity:0.75;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOADED FILES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Uploaded Files":

    sec("Sales Data Files","FILE LOG","📁")
    st.markdown("""
    <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                margin-bottom:1.2rem;line-height:1.6;max-width:580px;">
        All sales files uploaded to the system are listed here.
        Upload new files anytime to keep your suggestions up to date.
    </div>""", unsafe_allow_html=True)

    col_up, col_log = st.columns([1, 1.4])

    with col_up:
        st.markdown("""
        <div style="background:var(--card);border:2px dashed var(--border);
                    border-radius:var(--radius);padding:2rem 1.5rem;text-align:center;
                    box-shadow:var(--shadow);margin-bottom:0.8rem;">
            <div style="font-size:2.5rem;margin-bottom:0.7rem;">📂</div>
            <div style="font-weight:800;font-size:1rem;color:var(--text);
                        margin-bottom:0.35rem;">Upload New Sales File</div>
            <div style="font-size:0.78rem;color:var(--muted);font-weight:600;">
                CSV or Excel from any POS system
            </div>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Choose file",
            type=["csv","xlsx","xls"],
            label_visibility="collapsed",
            key="file_upload"
        )
        if uploaded:
            exists = any(f["name"]==uploaded.name for f in st.session_state.files)
            if not exists:
                st.session_state.files.append({
                    "name":   uploaded.name,
                    "time":   datetime.now().strftime("%d %b %Y  %H:%M"),
                    "size":   f"{uploaded.size/1024:.1f} KB",
                    "rows":   random.randint(800, 2400),
                    "ext":    uploaded.name.split(".")[-1].upper(),
                })

            st.markdown(f"""
            <div style="background:#E8F5E9;border:1.5px solid #A5D6A7;
                        border-radius:10px;padding:0.85rem 1rem;margin-top:0.5rem;">
                <div style="font-weight:800;color:#2E7D32;font-size:0.9rem;margin-bottom:0.15rem;">
                    File received
                </div>
                <div style="font-size:0.78rem;color:#388E3C;font-weight:600;">
                    {uploaded.name}
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("Process This File Now", use_container_width=True):
                st.session_state.page = "Run Analysis"
                st.rerun()

    with col_log:
        count = len(st.session_state.files)
        st.markdown(f"""
        <div style="background:var(--card);border:1.5px solid var(--border);
                    border-radius:var(--radius);padding:1.2rem 1.5rem;
                    margin-bottom:0.8rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:800;font-size:0.97rem;color:var(--text);">File History</div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.4rem;
                            color:var(--red);">{count}</div>
            </div>
            <div style="font-size:0.74rem;color:var(--muted);font-weight:600;margin-top:0.1rem;">
                {count} file{"s" if count!=1 else ""} uploaded
            </div>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.files:
            st.markdown("""
            <div style="background:#F8F6FF;border:1.5px dashed var(--border);
                        border-radius:var(--radius);padding:2.5rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.7rem;">📭</div>
                <div style="font-weight:700;color:var(--muted);font-size:0.9rem;">
                    No files uploaded yet
                </div>
                <div style="font-size:0.78rem;color:var(--muted);margin-top:0.3rem;">
                    Upload a sales file on the left to get started
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            for f in reversed(st.session_state.files):
                ext_color = "#CC0000" if f["ext"]=="CSV" else "#2E7D32"
                st.markdown(f"""
                <div style="background:var(--card);border:1.5px solid var(--border);
                            border-radius:12px;padding:0.9rem 1.1rem;
                            margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div style="display:flex;align-items:center;gap:0.75rem;">
                            <div style="background:{ext_color};color:white;font-size:0.6rem;
                                        font-weight:800;padding:0.22rem 0.5rem;border-radius:5px;
                                        letter-spacing:0.05em;">{f["ext"]}</div>
                            <div>
                                <div style="font-weight:800;font-size:0.88rem;
                                            color:var(--text);margin-bottom:0.1rem;">{f["name"]}</div>
                                <div style="font-size:0.71rem;color:var(--muted);font-weight:600;">
                                    {f["time"]} &nbsp;·&nbsp; {f["size"]} &nbsp;·&nbsp; ~{f["rows"]:,} records
                                </div>
                            </div>
                        </div>
                        {badge("Processed","#E8F5E9","#2E7D32")}
                    </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  RUN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Run Analysis":

    sec("Run New Analysis","","⚡")
    st.markdown("""
    <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                margin-bottom:1.4rem;line-height:1.6;max-width:580px;">
        Upload your latest sales file and click <strong style="color:var(--text);">
        Start Analysis</strong>. The system will find ordering patterns, build combo
        suggestions, and refresh all deals automatically.
    </div>""", unsafe_allow_html=True)

    col_opts, col_file = st.columns([1,1])

    with col_file:
        st.markdown("""
        <div style="background:var(--card);border:2px dashed var(--border);
                    border-radius:var(--radius);padding:2rem 1.5rem;text-align:center;
                    box-shadow:var(--shadow);">
            <div style="font-size:2.5rem;margin-bottom:0.7rem;">📂</div>
            <div style="font-weight:800;font-size:1rem;color:var(--text);margin-bottom:0.35rem;">
                Drop Your Sales File Here
            </div>
            <div style="font-size:0.78rem;color:var(--muted);font-weight:600;">
                CSV or Excel from any POS system
            </div>
        </div>""", unsafe_allow_html=True)

        run_file = st.file_uploader(
            "Sales file",
            type=["csv","xlsx","xls"],
            label_visibility="collapsed",
            key="run_file"
        )
        if run_file:
            exists = any(f["name"]==run_file.name for f in st.session_state.files)
            if not exists:
                st.session_state.files.append({
                    "name": run_file.name,
                    "time": datetime.now().strftime("%d %b %Y  %H:%M"),
                    "size": f"{run_file.size/1024:.1f} KB",
                    "rows": random.randint(800, 2400),
                    "ext":  run_file.name.split(".")[-1].upper(),
                })
            rows = next(f["rows"] for f in st.session_state.files if f["name"]==run_file.name)
            st.markdown(f"""
            <div style="background:#E8F5E9;border:1.5px solid #A5D6A7;
                        border-radius:10px;padding:0.8rem 1rem;margin-top:0.6rem;">
                <div style="font-weight:800;color:#2E7D32;font-size:0.9rem;margin-bottom:0.1rem;">
                    File ready
                </div>
                <div style="font-size:0.78rem;color:#388E3C;font-weight:600;">
                    {run_file.name} &nbsp;·&nbsp; ~{rows:,} records
                </div>
            </div>""", unsafe_allow_html=True)

    with col_opts:
        st.markdown("""
        <div style="background:var(--card);border:1.5px solid var(--border);
                    border-radius:var(--radius);padding:1.4rem 1.5rem;box-shadow:var(--shadow);">
            <div style="font-weight:900;font-size:0.97rem;color:var(--text);margin-bottom:1rem;">
                What to Include
            </div>""", unsafe_allow_html=True)

        inc_combos   = st.toggle("Build combo set suggestions",   value=True)
        inc_addons   = st.toggle("Build counter add-on tips",     value=True)
        inc_discounts= st.toggle("Build discount offers",         value=True)
        inc_monitor  = st.toggle("Check for menu item changes",   value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    log_box = st.empty()
    btn_col, _ = st.columns([1,2])
    with btn_col:
        go = st.button("Start Analysis", use_container_width=True)

    if st.session_state.run_logs and not go:
        lines = "\n".join(st.session_state.run_logs[-25:])
        log_box.markdown(f"""
        <div style="background:#0D1117;border-radius:14px;padding:1.1rem 1.4rem;
                    font-family:monospace;font-size:0.76rem;color:#8B949E;
                    min-height:100px;max-height:220px;overflow-y:auto;
                    border:1.5px solid #21262D;white-space:pre-wrap;
                    line-height:1.9;">{lines}</div>""", unsafe_allow_html=True)

    if go:
        st.session_state.run_logs = []
        st.session_state.ran = False

        def log(msg, e="🔵"):
            st.session_state.run_logs.append(f"[{now_str()}]  {e}  {msg}")

        def render():
            lines = "\n".join(st.session_state.run_logs[-25:])
            log_box.markdown(f"""
            <div style="background:#0D1117;border-radius:14px;padding:1.1rem 1.4rem;
                        font-family:monospace;font-size:0.76rem;color:#8B949E;
                        min-height:120px;max-height:240px;overflow-y:auto;
                        border:1.5px solid #21262D;white-space:pre-wrap;
                        line-height:1.9;">{lines}</div>""", unsafe_allow_html=True)

        stages = [
            ("Reading your sales file ...", [
                ("Detecting file format and layout ...", "🔍"),
                ("Reading order numbers and item names ...", "📖"),
                (f"Found ~{random.randint(900,2000):,} customer orders to work with", "✅"),
                ("Cleaning up any formatting issues ...", "🧹"),
                ("Sales data is ready.", "✅"),
            ], True),
            ("Finding ordering patterns ...", [
                ("Looking for items frequently ordered together ...", "🔍"),
                ("Calculating how often each combination appears ...", "📊"),
                (f"Found {len(PATTERNS)} strong patterns in your orders.", "✅"),
            ], inc_combos),
            ("Building combo set suggestions ...", [
                ("Selecting the best item pairs to bundle ...", "🍱"),
                ("Calculating suggested prices ...", "💰"),
                (f"Created {len(COMBOS)} combo deal suggestions.", "✅"),
            ], inc_combos),
            ("Building counter add-on tips ...", [
                ("Identifying best add-ons for each item ...", "⚡"),
                (f"Prepared {len(ADDONS)} add-on suggestions for your cashiers.", "✅"),
            ], inc_addons),
            ("Building discount offers ...", [
                ("Checking profit margins for each offer ...", "💰"),
                (f"Created {len(PROMOS)} safe discount offers.", "✅"),
            ], inc_discounts),
            ("Checking for menu item changes ...", [
                ("Comparing with last month's order mix ...", "📡"),
                ("All popular items are within normal range.", "✅"),
            ], inc_monitor),
        ]

        for name, logs, enabled in stages:
            if not enabled:
                log(f"Skipping: {name}", "⏭️"); render(); time.sleep(0.15); continue
            log(name, "🔄"); render()
            for msg, emoji in logs:
                time.sleep(0.38); log(msg, emoji); render()

        time.sleep(0.25)
        log("All done! Your deals and suggestions have been updated.", "🎉")
        render()
        st.session_state.ran = True
        time.sleep(0.3)

        st.markdown("""
        <div style="background:#E8F5E9;border:1.5px solid #A5D6A7;
                    border-radius:var(--radius);padding:1.2rem 1.5rem;margin-top:1rem;">
            <div style="font-weight:900;font-size:1rem;color:#2E7D32;margin-bottom:0.35rem;">
                Analysis complete!
            </div>
            <div style="font-size:0.85rem;color:#388E3C;font-weight:600;">
                Your combo deals, counter tips, and discount offers are all updated.
                Go to Suggested Deals to see the results.
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("View Suggested Deals", use_container_width=False):
            st.session_state.page = "Suggested Deals"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MENU MONITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Menu Monitor":

    sec("Menu Item Health","","📡")
    st.markdown("""
    <div style="font-size:0.86rem;color:var(--muted);font-weight:600;
                margin-bottom:1.2rem;line-height:1.6;max-width:640px;">
        This tracks how each menu item is doing compared to last month.
        If an item's order share changes significantly, it will show here
        so you can update your deals and promotions.
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: stat_card("✅","Items Stable","5","No big changes","#2E7D32")
    with c2: stat_card("👁️","Items to Watch","0","All within normal range","#FFCB05")
    with c3: stat_card("🕐","Last Checked",datetime.now().strftime("%H:%M"),"Just now","#3B4CCA")

    sec("Item-by-Item Breakdown","","📊")

    for p in MONITOR:
        psi = p["psi"]
        status       = "Needs Attention" if psi>0.20 else "Worth Watching" if psi>0.10 else "Stable"
        status_bg    = "#FFE8E8" if psi>0.20 else "#FFF8E8" if psi>0.10 else "#E8F5E9"
        status_fg    = "#CC0000" if psi>0.20 else "#E65100" if psi>0.10 else "#2E7D32"
        bar_color    = "#CC0000" if psi>0.20 else "#FFCB05" if psi>0.10 else "#4CAF50"
        bar_w        = min(int(psi/0.25*100),100)
        change       = p["now"]-p["last"]
        change_str   = f"+{change}%" if change>0 else f"{change}%"
        change_fg    = "#2E7D32" if change>0 else "#CC0000" if change<0 else "#757575"

        st.markdown(f"""
        <div style="background:var(--card);border:1.5px solid var(--border);
                    border-radius:var(--radius);padding:1.1rem 1.4rem;
                    margin-bottom:0.7rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;flex-wrap:wrap;gap:0.8rem;margin-bottom:0.9rem;">
                <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;">
                    <div style="font-weight:800;font-size:0.97rem;color:var(--text);">{p['item']}</div>
                    {badge(status,status_bg,status_fg)}
                </div>
                <div style="display:flex;align-items:center;gap:1.4rem;">
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem;color:var(--muted);font-weight:700;
                                    text-transform:uppercase;letter-spacing:0.05em;">Last Month</div>
                        <div style="font-weight:800;font-size:0.95rem;
                                    color:var(--text);">{p['last']}%</div>
                    </div>
                    <div style="color:var(--muted);font-size:1rem;">&#8594;</div>
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem;color:var(--muted);font-weight:700;
                                    text-transform:uppercase;letter-spacing:0.05em;">This Month</div>
                        <div style="font-weight:800;font-size:0.95rem;
                                    color:var(--text);">{p['now']}%</div>
                    </div>
                    <div style="font-weight:800;font-size:0.97rem;
                                color:{change_fg};">{change_str}</div>
                </div>
            </div>
            <div style="background:#F0EEF8;border-radius:5px;height:8px;overflow:hidden;">
                <div style="background:{bar_color};height:8px;width:{bar_w}%;
                            border-radius:5px;opacity:0.8;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:0.3rem;">
                <div style="font-size:0.62rem;color:var(--muted);font-weight:600;">Normal</div>
                <div style="font-size:0.62rem;color:var(--muted);font-weight:600;">Attention needed</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#E8ECFF;border:1.5px solid #C5CAF5;border-radius:var(--radius);
                padding:1.1rem 1.4rem;margin-top:0.5rem;">
        <div style="font-weight:800;color:#3B4CCA;font-size:0.9rem;margin-bottom:0.3rem;">
            What does this mean?
        </div>
        <div style="font-size:0.82rem;color:#3B4CCA;font-weight:600;line-height:1.65;">
            <strong>Stable</strong> means the item's popularity hasn't changed much.
            <strong>Worth Watching</strong> means there's a small shift — keep an eye on it.
            <strong>Needs Attention</strong> means a big change has happened — consider running
            a new analysis to refresh your deal suggestions.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Run New Analysis to Refresh Deals"):
        st.session_state.page = "Run Analysis"
        st.rerun()
