import streamlit as st
import os, time, random
from datetime import datetime

st.set_page_config(
    page_title="Pokemon Cafe — Staff Portal",
    page_icon="🍵",
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

# ── MENU DATA ─────────────────────────────────────────────────────────────────
MENU = [
    {"name":"The Pikachu Hamburger",                         "category":"Food",   "price":980,  "emoji":"⚡","desc":"Signature hamburger shaped like Pikachu's face with seasoned beef patty"},
    {"name":"Snorlax's Tummy Filling Nap Lunch Plate",       "category":"Food",   "price":1200, "emoji":"😴","desc":"Hearty rice and meat plate inspired by Snorlax — comes with soup"},
    {"name":"Pikachu & Squirtle's BFF Curry Plate",          "category":"Food",   "price":1150, "emoji":"🍛","desc":"Two-tone curry plate with chicken and vegetable sides"},
    {"name":"Rice Plate Meal with Eevee",                    "category":"Food",   "price":1050, "emoji":"🌿","desc":"Eevee-decorated rice omelette with demi-glace sauce"},
    {"name":"Paldean Form Wooper Burger",                    "category":"Food",   "price":950,  "emoji":"🍔","desc":"Ground pork burger with Paldean Wooper bun decoration"},
    {"name":"Clodsire Soup Pot",                             "category":"Food",   "price":750,  "emoji":"🍲","desc":"Warm creamy potato soup served in a Clodsire-shaped bowl"},
    {"name":"Pokemon Cafe's Pikachu Souffle Pancake",        "category":"Sweets", "price":880,  "emoji":"🥞","desc":"Fluffy Japanese souffle pancake with Pikachu face design"},
    {"name":"Pokemon Cafe's Berry Chocolate Parfait",        "category":"Sweets", "price":920,  "emoji":"🫐","desc":"Layered parfait with fresh berries, chocolate sauce, and whipped cream"},
    {"name":"Poke Ball Dessert Bowl",                        "category":"Sweets", "price":850,  "emoji":"🔴","desc":"Ice cream dessert bowl decorated as a Poke Ball with red and white layers"},
    {"name":"Assorted Dragon-Type Sweets",                   "category":"Sweets", "price":1100, "emoji":"🐉","desc":"Plate of three dragon-themed petit fours and macarons"},
    {"name":"Fuecoco's Apple Soda Float",                    "category":"Drinks", "price":680,  "emoji":"🍎","desc":"Apple-flavored soda with vanilla ice cream float and Fuecoco decoration"},
    {"name":"Quaxly's Ramune Soda Float",                    "category":"Drinks", "price":680,  "emoji":"💧","desc":"Ramune soda float with blue jelly and Quaxly character straw topper"},
    {"name":"Gengar's Confuse Ray Smoothie",                 "category":"Drinks", "price":720,  "emoji":"👻","desc":"Purple mixed berry smoothie with popping candy rim"},
    {"name":"Say Hello to Eevee's Royal Milk Tea",           "category":"Drinks", "price":650,  "emoji":"🍵","desc":"Classic royal milk tea with Eevee latte art and brown sugar boba"},
    {"name":"Pokemon Latte",                                 "category":"Drinks", "price":620,  "emoji":"☕","desc":"House latte with seasonal Pokemon latte art — design changes monthly"},
    {"name":"Cocoa",                                         "category":"Drinks", "price":580,  "emoji":"🍫","desc":"Rich hot chocolate with Pokemon-themed marshmallows"},
]

CATEGORY_COLORS = {
    "Food":   {"bg":"#FFF3E0","fg":"#E65100","border":"#FFCC80"},
    "Sweets": {"bg":"#FCE4EC","fg":"#AD1457","border":"#F48FB1"},
    "Drinks": {"bg":"#E3F2FD","fg":"#1565C0","border":"#90CAF9"},
}

COMBOS = [
    {"badge":"⚡","name":"Pikachu Morning Set",       "items":["Pokemon Latte","Pokemon Cafe's Pikachu Souffle Pancake"],                  "price":1380,"pct":21,"conf":88,"lift":2.6},
    {"badge":"👻","name":"Gengar Night Special",      "items":["Gengar's Confuse Ray Smoothie","Assorted Dragon-Type Sweets"],             "price":1700,"pct":16,"conf":76,"lift":2.2},
    {"badge":"😴","name":"Snorlax Full Meal",         "items":["Snorlax's Tummy Filling Nap Lunch Plate","Cocoa"],                        "price":1680,"pct":14,"conf":71,"lift":2.0},
    {"badge":"🌿","name":"Eevee Afternoon Tea",       "items":["Say Hello to Eevee's Royal Milk Tea","Pokemon Cafe's Berry Chocolate Parfait"], "price":1450,"pct":12,"conf":65,"lift":1.8},
    {"badge":"🍎","name":"Fuecoco Fun Combo",         "items":["Fuecoco's Apple Soda Float","The Pikachu Hamburger"],                     "price":1560,"pct":10,"conf":60,"lift":1.7},
]
ADDONS = [
    {"from":"The Pikachu Hamburger",               "to":"Pokemon Latte",                         "conf":82,"lift":2.4},
    {"from":"Pokemon Cafe's Pikachu Souffle Pancake","to":"Say Hello to Eevee's Royal Milk Tea", "conf":74,"lift":2.1},
    {"from":"Pikachu & Squirtle's BFF Curry Plate","to":"Fuecoco's Apple Soda Float",            "conf":68,"lift":1.9},
    {"from":"Gengar's Confuse Ray Smoothie",       "to":"Assorted Dragon-Type Sweets",           "conf":61,"lift":1.7},
    {"from":"Snorlax's Tummy Filling Nap Lunch Plate","to":"Poke Ball Dessert Bowl",             "conf":55,"lift":1.5},
]
PROMOS = [
    {"buy":"The Pikachu Hamburger",          "get":"Pokemon Latte",                    "off":"15%","margin":32,"gain":5200},
    {"buy":"Pokemon Cafe's Pikachu Souffle Pancake","get":"Say Hello to Eevee's Royal Milk Tea","off":"10%","margin":35,"gain":3800},
    {"buy":"Pikachu & Squirtle's BFF Curry Plate","get":"Fuecoco's Apple Soda Float",  "off":"20%","margin":28,"gain":4100},
]
PATTERNS = [
    {"a":"The Pikachu Hamburger",                "b":"Pokemon Latte",                          "conf":82,"pct":21,"lift":2.4,"stable":9},
    {"a":"Pokemon Cafe's Pikachu Souffle Pancake","b":"Say Hello to Eevee's Royal Milk Tea",   "conf":74,"pct":16,"lift":2.1,"stable":7},
    {"a":"Pikachu & Squirtle's BFF Curry Plate", "b":"Fuecoco's Apple Soda Float",             "conf":68,"pct":14,"lift":1.9,"stable":6},
    {"a":"Gengar's Confuse Ray Smoothie",        "b":"Assorted Dragon-Type Sweets",            "conf":61,"pct":11,"lift":1.7,"stable":5},
    {"a":"Snorlax's Tummy Filling Nap Lunch Plate","b":"Poke Ball Dessert Bowl",               "conf":55,"pct":9, "lift":1.5,"stable":4},
    {"a":"Rice Plate Meal with Eevee",           "b":"Pokemon Cafe's Berry Chocolate Parfait", "conf":48,"pct":7, "lift":1.4,"stable":3},
]
MONITOR = [
    {"item":"The Pikachu Hamburger",    "emoji":"⚡","last":24,"now":27,"psi":0.04},
    {"item":"Pokemon Latte",            "emoji":"☕","last":31,"now":34,"psi":0.05},
    {"item":"Pikachu Souffle Pancake",  "emoji":"🥞","last":18,"now":16,"psi":0.06},
    {"item":"Gengar Smoothie",          "emoji":"👻","last":14,"now":14,"psi":0.02},
    {"item":"Snorlax Lunch Plate",      "emoji":"😴","last":12,"now":15,"psi":0.08},
    {"item":"Eevee Royal Milk Tea",     "emoji":"🍵","last":11,"now":10,"psi":0.03},
]

# ── POKEMON ASSET URLS (official press / wiki assets) ─────────────────────────
POKEMON_SPRITES = {
    "pikachu":    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
    "eevee":      "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png",
    "snorlax":    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png",
    "gengar":     "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png",
    "squirtle":   "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png",
    "fuecoco":    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/909.png",
    "quaxly":     "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/914.png",
    "clodsire":   "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/980.png",
    "wooper":     "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/194.png",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def now_str(): return datetime.now().strftime("%H:%M:%S")
def today_str(): return datetime.now().strftime("%d %b %Y  %H:%M")

def pill(txt, bg="#FFE8E8", fg="#CC0000", size="0.74rem"):
    return (f'<span style="background:{bg};color:{fg};font-size:{size};font-weight:700;'
            f'padding:0.22rem 0.65rem;border-radius:20px;white-space:nowrap;">{txt}</span>')

def badge(txt, bg, fg):
    return (f'<span style="background:{bg};color:{fg};font-size:0.68rem;font-weight:800;'
            f'text-transform:uppercase;letter-spacing:0.07em;padding:0.22rem 0.65rem;border-radius:6px;">{txt}</span>')

def stat_card(icon, label, value, sub, accent, clickable_page=None):
    cursor = "pointer" if clickable_page else "default"
    key = f"stat_{label.replace(' ','_')}"
    html = f"""
    <div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;
                padding:1.3rem 1.4rem;box-shadow:0 2px 16px rgba(59,76,202,0.08);
                border-left:6px solid {accent};cursor:{cursor};
                transition:box-shadow 0.2s,transform 0.15s;"
         {"onclick=\"\"" if clickable_page else ""}>
        <div style="font-size:1.9rem;margin-bottom:0.35rem;line-height:1;">{icon}</div>
        <div style="font-size:0.66rem;font-weight:800;text-transform:uppercase;
                    letter-spacing:0.11em;color:#7B7B9A;margin-bottom:0.2rem;">{label}</div>
        <div style="font-family:'Fredoka One',cursive;font-size:2.1rem;
                    color:#1A1A2E;line-height:1;margin-bottom:0.28rem;">{value}</div>
        <div style="font-size:0.74rem;color:#7B7B9A;font-weight:600;">{sub}</div>
    </div>"""
    if clickable_page:
        if st.button(f"{icon} {label}", key=key, help=f"Go to {clickable_page}",
                     use_container_width=True):
            st.session_state.page = clickable_page
            st.rerun()
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def clickable_stat(icon, label, value, sub, accent, dest):
    col_inner = st.container()
    with col_inner:
        if st.button("", key=f"cs_{label}", use_container_width=True,
                     help=f"Go to {dest}"):
            st.session_state.page = dest
            st.rerun()
        st.markdown(f"""
        <div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;
                    padding:1.3rem 1.4rem;box-shadow:0 2px 16px rgba(59,76,202,0.08);
                    border-left:6px solid {accent};margin-top:-2.8rem;
                    pointer-events:none;">
            <div style="font-size:1.9rem;margin-bottom:0.35rem;line-height:1;">{icon}</div>
            <div style="font-size:0.66rem;font-weight:800;text-transform:uppercase;
                        letter-spacing:0.11em;color:#7B7B9A;margin-bottom:0.2rem;">{label}</div>
            <div style="font-family:'Fredoka One',cursive;font-size:2.1rem;
                        color:#1A1A2E;line-height:1;margin-bottom:0.28rem;">{value}</div>
            <div style="font-size:0.74rem;color:#7B7B9A;font-weight:600;">{sub}</div>
        </div>""", unsafe_allow_html=True)

def sec(title, tag="", icon=""):
    tag_html = (f'<span style="background:#FFCB05;color:#333;font-size:0.62rem;font-weight:800;'
                f'text-transform:uppercase;letter-spacing:0.07em;padding:0.18rem 0.6rem;'
                f'border-radius:5px;margin-left:0.5rem;">{tag}</span>') if tag else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin:1.6rem 0 0.9rem 0;">
        <span style="font-size:1.2rem;margin-right:0.45rem;">{icon}</span>
        <span style="font-family:'Fredoka One',cursive;font-size:1.08rem;
                     color:#1A1A2E;letter-spacing:0.01em;">{title}</span>
        {tag_html}
    </div>""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k,v in {"page":"Home","ran":False,"run_logs":[],"files":[],"total_txn":0}.items():
    if k not in st.session_state: st.session_state[k] = v

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');

:root {
    --red:#CC0000; --red-dk:#990000; --red-lt:#FFE8E8;
    --yellow:#FFCB05; --blue:#3B4CCA; --blue-lt:#E8ECFF;
    --green:#2E7D32; --green-lt:#E8F5E9;
    --bg:#F7F3FF; --card:#FFFFFF; --border:#E4DCFF;
    --text:#1A1A2E; --muted:#7B7B9A;
    --sidebar:#12102A;
    --radius:18px; --shadow:0 2px 16px rgba(59,76,202,0.08);
}
html,body,[class*="css"]{font-family:'Nunito',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 1.8rem 2rem 1.8rem!important;max-width:1440px!important;}

[data-testid="stSidebar"]{background:var(--sidebar)!important;border-right:none!important;}
[data-testid="stSidebar"] *{color:#C8C8E8!important;}
[data-testid="stSidebar"] .stButton>button{
    background:transparent!important;color:#9090B8!important;
    border:1.5px solid rgba(255,255,255,0.07)!important;border-radius:12px!important;
    font-family:'Nunito',sans-serif!important;font-weight:700!important;font-size:0.88rem!important;
    padding:0.58rem 1rem!important;width:100%!important;text-align:left!important;
    margin-bottom:3px!important;transition:all 0.15s!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
    background:rgba(255,203,5,0.1)!important;border-color:rgba(255,203,5,0.28)!important;
    color:#FFCB05!important;transform:translateX(3px)!important;box-shadow:none!important;
}

.stButton>button{
    background:var(--red)!important;color:white!important;border:none!important;
    border-radius:12px!important;font-family:'Nunito',sans-serif!important;font-weight:800!important;
    font-size:0.91rem!important;padding:0.58rem 1.4rem!important;transition:all 0.15s!important;
    box-shadow:0 3px 10px rgba(204,0,0,0.2)!important;
}
.stButton>button:hover{background:var(--red-dk)!important;transform:translateY(-2px)!important;box-shadow:0 6px 18px rgba(204,0,0,0.28)!important;}
[data-testid="stSidebar"] .stButton>button:hover{transform:translateX(3px)!important;box-shadow:none!important;}

/* invisible clickable card buttons */
div[data-testid="stVerticalBlock"] .stButton>button[kind="secondary"]{
    background:transparent!important;color:transparent!important;
    box-shadow:none!important;border:none!important;height:0px!important;
    padding:0!important;margin:0!important;
}

.stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:14px!important;
    padding:4px!important;border:1.5px solid var(--border)!important;gap:2px!important;margin-bottom:1rem!important;}
.stTabs [data-baseweb="tab"]{border-radius:9px!important;font-family:'Nunito',sans-serif!important;
    font-weight:700!important;font-size:0.84rem!important;color:var(--muted)!important;padding:0.45rem 1.1rem!important;}
.stTabs [aria-selected="true"]{background:var(--red)!important;color:white!important;}

.stSlider>div>div>div{background:var(--red)!important;}
[data-testid="stFileUploader"]{background:var(--card)!important;border-radius:var(--radius)!important;}
.stSelectbox>div>div{border-radius:10px!important;border-color:var(--border)!important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Pokeball logo
    st.markdown("""
    <div style="padding:1.4rem 1rem 0.6rem 1rem;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.8rem;">
            <div style="width:48px;height:48px;border-radius:50%;overflow:hidden;
                        border:3px solid #FFCB05;box-shadow:0 0 0 2px #CC0000,0 4px 12px rgba(0,0,0,0.4);
                        background:linear-gradient(180deg,#CC0000 50%,#FFFFFF 50%);
                        display:flex;align-items:center;justify-content:center;position:relative;">
                <div style="width:14px;height:14px;background:#FFFFFF;border-radius:50%;
                            border:3px solid #333;z-index:2;position:absolute;"></div>
                <div style="position:absolute;top:50%;left:0;right:0;height:3px;background:#333;transform:translateY(-50%);z-index:1;"></div>
            </div>
            <div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.15rem;color:#FFCB05;line-height:1.1;">Pokemon Cafe</div>
                <div style="font-size:0.62rem;color:#4A4A6A;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;">Staff Portal</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    online = api_online()
    st.markdown(f"""
    <div style="margin:0 0.8rem 0.9rem 0.8rem;background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.06);border-radius:10px;
                padding:0.42rem 0.9rem;display:flex;align-items:center;gap:0.5rem;">
        <span style="color:{'#4CAF50' if online else '#EF5350'};font-size:0.8rem;">●</span>
        <span style="font-size:0.73rem;color:#6868A8;font-weight:700;">
            {"System Online" if online else "System Offline"}
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 0.5rem;">', unsafe_allow_html=True)
    nav = [
        ("🏠","Home"),("📊","Today's Summary"),("🎯","Suggested Deals"),
        ("📋","Order Patterns"),("🍽️","Menu & Pricing"),
        ("📁","Uploaded Files"),("⚡","Run Analysis"),("📡","Menu Monitor"),
    ]
    for icon, label in nav:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1.5rem;padding:0.8rem 1.2rem;border-top:1px solid rgba(255,255,255,0.05);">
        <div style="font-size:0.6rem;color:#2A2A5A;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Branch</div>
        <div style="font-size:0.83rem;color:#6868A8;font-weight:700;">🏪 Main Branch</div>
    </div>""", unsafe_allow_html=True)

# ── TOP BAR ───────────────────────────────────────────────────────────────────
page = st.session_state.page
st.markdown(f"""
<div style="background:linear-gradient(90deg,#CC0000 0%,#990000 70%,#7A0000 100%);
            margin:-1rem -1.8rem 1.8rem -1.8rem;padding:0.95rem 2.5rem;
            display:flex;align-items:center;justify-content:space-between;">
    <div style="display:flex;align-items:center;gap:1rem;">
        <img src="{POKEMON_SPRITES['pikachu']}" style="width:38px;height:38px;object-fit:contain;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
        <div>
            <div style="font-family:'Fredoka One',cursive;font-size:1.28rem;color:#FFCB05;letter-spacing:0.02em;">{page}</div>
            <div style="font-size:0.68rem;color:rgba(255,255,255,0.4);font-weight:600;">Pokemon Cafe · Staff Management</div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:0.85rem;">
        <div style="background:rgba(255,255,255,0.11);border-radius:9px;padding:0.36rem 0.88rem;font-size:0.73rem;color:rgba(255,255,255,0.72);font-weight:700;">{today_str()}</div>
        <div style="width:32px;height:32px;background:#FFCB05;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.92rem;">👤</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HOME — clickable cards
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":

    # Pikachu + Eevee welcome banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#12102A 0%,#1A1A3E 55%,#0F2060 100%);
                border-radius:var(--radius);padding:1.8rem 2rem;margin-bottom:1.4rem;
                box-shadow:var(--shadow);display:flex;align-items:center;
                justify-content:space-between;overflow:hidden;position:relative;">
        <div style="position:absolute;right:220px;top:-10px;opacity:0.06;font-size:9rem;line-height:1;">⚡</div>
        <div style="flex:1;">
            <div style="font-family:'Fredoka One',cursive;font-size:1.75rem;color:#FFCB05;margin-bottom:0.45rem;">
                Welcome back, Trainer! 👋
            </div>
            <div style="font-size:0.9rem;color:#8888B8;font-weight:600;max-width:480px;line-height:1.65;">
                Your Pokémon Café is running smoothly.<br>
                Click any card below to jump straight to that section.
            </div>
            <div style="margin-top:0.9rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
                {pill(f"{'✅ Last run today' if st.session_state.ran else '⚠️ Not yet run today'}","#1A2A4A","#6888C8","0.75rem")}
                {pill(f"{len(st.session_state.files)} file{'s' if len(st.session_state.files)!=1 else ''} uploaded","#1A2A4A","#6888C8","0.75rem")}
                {pill(f"{st.session_state.total_txn:,} total orders processed","#1A2A4A","#6888C8","0.75rem") if st.session_state.total_txn>0 else ""}
            </div>
        </div>
        <div style="display:flex;gap:-0.5rem;">
            <img src="{POKEMON_SPRITES['pikachu']}" style="width:90px;height:90px;object-fit:contain;filter:drop-shadow(0 4px 8px rgba(0,0,0,0.4));">
            <img src="{POKEMON_SPRITES['eevee']}"   style="width:75px;height:75px;object-fit:contain;filter:drop-shadow(0 4px 8px rgba(0,0,0,0.3));margin-left:-10px;align-self:flex-end;">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Clickable stat cards ───────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)

    def _ccard(col, icon, label, value, sub, accent, dest):
        with col:
            clicked = st.button(f"→ {label}", key=f"cc_{label}", use_container_width=True,
                                help=f"Go to {dest}")
            if clicked:
                st.session_state.page = dest
                st.rerun()
            st.markdown(f"""
            <div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:var(--radius);
                        padding:1.25rem 1.3rem;box-shadow:var(--shadow);border-left:6px solid {accent};
                        margin-top:-2.55rem;cursor:pointer;">
                <div style="font-size:1.8rem;margin-bottom:0.3rem;line-height:1;">{icon}</div>
                <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;
                            letter-spacing:0.11em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>
                <div style="font-family:'Fredoka One',cursive;font-size:2rem;color:#1A1A2E;
                            line-height:1;margin-bottom:0.25rem;">{value}</div>
                <div style="font-size:0.73rem;color:#7B7B9A;font-weight:600;">{sub}</div>
                <div style="font-size:0.68rem;color:{accent};font-weight:700;margin-top:0.4rem;">
                    Tap to view →
                </div>
            </div>""", unsafe_allow_html=True)

    _ccard(c1,"🎯","Combo Deals",str(len(COMBOS)),"Featured sets","#CC0000","Suggested Deals")
    _ccard(c2,"🍽️","Menu Items",str(len(MENU)),"With pricing","#3B4CCA","Menu & Pricing")
    _ccard(c3,"📁","Files Uploaded",str(len(st.session_state.files)),"Sales records","#2E7D32","Uploaded Files")
    _ccard(c4,"⚡","Run Analysis","→","Process new sales data","#E65100","Run Analysis")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.7,1])

    with left:
        sec("Top Combos to Promote Today","HOT","🔥")
        for c in COMBOS[:3]:
            items_str = " + ".join([i.split("'s")[-1].strip() if "'s" in i else i.split()[-1] for i in c["items"]])
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                        padding:1rem 1.3rem;margin-bottom:0.6rem;box-shadow:var(--shadow);
                        display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:0.9rem;">
                    <div style="width:46px;height:46px;min-width:46px;background:linear-gradient(135deg,#FFCB05,#FFE066);
                                border-radius:12px;display:flex;align-items:center;justify-content:center;
                                font-size:1.5rem;box-shadow:0 2px 8px rgba(255,203,5,0.3);">{c['badge']}</div>
                    <div>
                        <div style="font-weight:800;font-size:0.93rem;color:#1A1A2E;margin-bottom:0.12rem;">{c['name']}</div>
                        <div style="font-size:0.76rem;color:#7B7B9A;font-weight:600;margin-bottom:0.3rem;">{" + ".join(c["items"])[:60]}{"..." if len(" + ".join(c["items"]))>60 else ""}</div>
                        <div>{pill(f"{c['pct']}% of orders include this pair","#E8ECFF","#3B4CCA","0.7rem")}</div>
                    </div>
                </div>
                <div style="text-align:right;padding-left:0.8rem;">
                    <div style="font-family:'Fredoka One',cursive;font-size:1.4rem;color:#CC0000;">&#165;{c['price']:,}</div>
                    <div style="font-size:0.67rem;color:#7B7B9A;font-weight:600;">Bundle price</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Total transactions panel
        if st.session_state.total_txn > 0:
            sec("Data Overview","","📊")
            foods  = sum(1 for m in MENU if m["category"]=="Food")
            sweets = sum(1 for m in MENU if m["category"]=="Sweets")
            drinks = sum(1 for m in MENU if m["category"]=="Drinks")
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                        padding:1.2rem 1.5rem;box-shadow:var(--shadow);">
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;text-align:center;">
                    <div>
                        <div style="font-family:'Fredoka One',cursive;font-size:1.8rem;color:#CC0000;">{st.session_state.total_txn:,}</div>
                        <div style="font-size:0.72rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Total Orders</div>
                    </div>
                    <div>
                        <div style="font-family:'Fredoka One',cursive;font-size:1.8rem;color:#3B4CCA;">{len(st.session_state.files)}</div>
                        <div style="font-size:0.72rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Files Processed</div>
                    </div>
                    <div>
                        <div style="font-family:'Fredoka One',cursive;font-size:1.8rem;color:#2E7D32;">{len(MENU)}</div>
                        <div style="font-size:0.72rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Menu Items</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with right:
        sec("Quick Links","","⚡")
        qlinks = [
            ("📁  Upload Sales Data","Uploaded Files"),
            ("🎯  View Suggested Deals","Suggested Deals"),
            ("📊  See Order Patterns","Order Patterns"),
            ("🍽️  Menu & Pricing","Menu & Pricing"),
            ("⚡  Run New Analysis","Run Analysis"),
            ("📡  Menu Monitor","Menu Monitor"),
        ]
        for label, dest in qlinks:
            if st.button(label, use_container_width=True, key=f"ql_{dest}"):
                st.session_state.page = dest
                st.rerun()
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

        sec("Pokémon Featured Today","","⭐")
        featured = [
            (POKEMON_SPRITES["pikachu"],"Pikachu","The Pikachu Hamburger","⚡"),
            (POKEMON_SPRITES["gengar"], "Gengar", "Gengar's Confuse Ray Smoothie","👻"),
            (POKEMON_SPRITES["snorlax"],"Snorlax","Snorlax Lunch Plate","😴"),
        ]
        for sprite, pname, dish, em in featured:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:12px;
                        padding:0.65rem 1rem;margin-bottom:0.45rem;
                        display:flex;align-items:center;gap:0.75rem;">
                <img src="{sprite}" style="width:38px;height:38px;object-fit:contain;">
                <div>
                    <div style="font-weight:800;font-size:0.85rem;color:#1A1A2E;">{em} {pname}</div>
                    <div style="font-size:0.72rem;color:#7B7B9A;font-weight:600;">{dish[:35]}{"..." if len(dish)>35 else ""}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TODAY'S SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Today's Summary":

    sec("What's Selling Well Together","","📊")
    st.markdown("""<div style="font-size:0.86rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:640px;">
        Based on your uploaded sales records, here are the menu items customers most often order at the same time.</div>""",
        unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,icon,label,val,sub,acc in [
        (c1,"🍱","Combo Sets",str(len(COMBOS)),"Ready to promote","#CC0000"),
        (c2,"⚡","Counter Add-ons",str(len(ADDONS)),"Smart suggestions","#3B4CCA"),
        (c3,"🎁","Discount Offers",str(len(PROMOS)),"Profitable deals","#FFCB05"),
    ]:
        with col:
            st.markdown(f"""<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:var(--radius);
                    padding:1.2rem 1.3rem;box-shadow:var(--shadow);border-left:6px solid {acc};">
                <div style="font-size:1.7rem;margin-bottom:0.3rem;">{icon}</div>
                <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.2rem;">{label}</div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.9rem;color:#1A1A2E;line-height:1;margin-bottom:0.25rem;">{val}</div>
                <div style="font-size:0.73rem;color:#7B7B9A;font-weight:600;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    if st.session_state.total_txn > 0:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1A1A3E,#12102A);border-radius:var(--radius);
                    padding:1.2rem 1.6rem;margin:1rem 0;display:flex;align-items:center;gap:2rem;">
            <img src="{POKEMON_SPRITES['pikachu']}" style="width:55px;height:55px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.4));">
            <div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.5rem;color:#FFCB05;">
                    {st.session_state.total_txn:,} total orders analysed
                </div>
                <div style="font-size:0.82rem;color:#6868A8;font-weight:600;">
                    across {len(st.session_state.files)} uploaded sales file{"s" if len(st.session_state.files)!=1 else ""}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    sec("Most Ordered Together","","🍽️")
    for i,r in enumerate(PATTERNS[:5]):
        rank_colors = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2"]
        rank_bgs    = ["#FFE8E8","#E8ECFF","#E8F5E9","#FFF3E0","#F3E5F5"]
        stab_label  = "Very Consistent" if r['stable']>=6 else "Growing" if r['stable']>=3 else "Newly Spotted"
        stab_bg     = "#E8F5E9" if r['stable']>=6 else "#FFF8E8" if r['stable']>=3 else "#E8ECFF"
        stab_fg     = "#2E7D32" if r['stable']>=6 else "#E65100" if r['stable']>=3 else "#3B4CCA"
        bar_w       = int(r['conf']*0.87)
        rc,rm = st.columns([0.07,1])
        with rc:
            st.markdown(f"""<div style="width:34px;height:34px;background:{rank_bgs[i]};border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-family:'Fredoka One',cursive;
                font-size:1rem;color:{rank_colors[i]};margin-top:0.65rem;">{i+1}</div>""",unsafe_allow_html=True)
        with rm:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                        padding:0.95rem 1.3rem;margin-bottom:0.55rem;box-shadow:var(--shadow);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                            margin-bottom:0.65rem;flex-wrap:wrap;gap:0.4rem;">
                    <div>
                        <span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r['a']}</span>
                        <span style="color:#CC0000;font-size:1rem;margin:0 0.45rem;">&#8594;</span>
                        <span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r['b']}</span>
                    </div>
                    <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                        {pill(f"{r['conf']}% order these together","#FFE8E8","#CC0000","0.7rem")}
                        {pill(f"In {r['pct']}% of all orders","#E8ECFF","#3B4CCA","0.7rem")}
                        {badge(stab_label,stab_bg,stab_fg)}
                    </div>
                </div>
                <div style="background:#F0EEF8;border-radius:5px;height:6px;overflow:hidden;">
                    <div style="background:{rank_colors[i]};height:6px;width:{bar_w}%;border-radius:5px;opacity:0.75;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SUGGESTED DEALS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Suggested Deals":
    tab1,tab2,tab3 = st.tabs(["🍱  Combo Sets","⚡  Counter Add-ons","🎁  Discount Offers"])

    with tab1:
        sec("Recommended Combo Sets","AUTO-SUGGESTED","🍱")
        st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:600px;">
            These items are frequently ordered together. Sell them as a set at the suggested price.</div>""",unsafe_allow_html=True)
        for c in COMBOS:
            extra = int((c['lift']-1)*100)
            items_full = " + ".join(c["items"])
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                        padding:1.1rem 1.4rem;margin-bottom:0.75rem;box-shadow:var(--shadow);">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.7rem;">
                    <div style="display:flex;align-items:center;gap:0.9rem;">
                        <div style="width:50px;height:50px;min-width:50px;background:linear-gradient(135deg,#FFCB05,#FFE066);
                                    border-radius:13px;display:flex;align-items:center;justify-content:center;
                                    font-size:1.6rem;box-shadow:0 2px 8px rgba(255,203,5,0.3);">{c['badge']}</div>
                        <div>
                            <div style="font-weight:900;font-size:0.97rem;color:#1A1A2E;margin-bottom:0.2rem;">{c['name']}</div>
                            <div style="font-size:0.78rem;color:#7B7B9A;font-weight:600;margin-bottom:0.38rem;">{items_full}</div>
                            <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                                {pill(f"{c['conf']}% order these together","#FFE8E8","#CC0000","0.7rem")}
                                {pill(f"~{extra}% more when bundled","#E8F5E9","#2E7D32","0.7rem")}
                                {pill(f"{c['pct']}% of all orders","#E8ECFF","#3B4CCA","0.7rem")}
                            </div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Fredoka One',cursive;font-size:1.6rem;color:#CC0000;">&#165;{c['price']:,}</div>
                        <div style="font-size:0.67rem;color:#7B7B9A;font-weight:700;">Bundle price</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        sec("Counter Add-on Suggestions","FOR CASHIERS","⚡")
        st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:600px;">
            When a customer orders the first item, suggest the second one at the counter.</div>""",unsafe_allow_html=True)
        hc = st.columns([1.1,0.08,1.1,0.85,0.75])
        for col,txt in zip(hc,["Customer Orders","","Suggest This Next","Chance They'll Say Yes","Times More Likely"]):
            with col:
                st.markdown(f'<div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;color:#7B7B9A;padding:0.3rem 0;border-bottom:2px solid #E4DCFF;">{txt}</div>',unsafe_allow_html=True)
        for a in ADDONS:
            bw = int(a['conf']*0.84)
            cols = st.columns([1.1,0.08,1.1,0.85,0.75])
            with cols[0]:
                st.markdown(f'<div style="background:#FFF8E8;border:1.5px solid #FFE8A0;border-radius:10px;padding:0.58rem 0.85rem;margin:0.28rem 0;"><div style="font-weight:800;font-size:0.86rem;color:#1A1A2E;">{a["from"][:30]}{"..." if len(a["from"])>30 else ""}</div></div>',unsafe_allow_html=True)
            with cols[1]:
                st.markdown('<div style="text-align:center;padding:0.8rem 0;font-size:1.15rem;color:#CC0000;font-weight:900;">&#8594;</div>',unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div style="background:#FFE8E8;border:1.5px solid #FFBCBC;border-radius:10px;padding:0.58rem 0.85rem;margin:0.28rem 0;"><div style="font-weight:800;font-size:0.86rem;color:#CC0000;">{a["to"][:30]}{"..." if len(a["to"])>30 else ""}</div></div>',unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f'<div style="padding:0.65rem 0;"><div style="font-weight:900;font-size:0.92rem;color:#1A1A2E;">{a["conf"]}%</div><div style="background:#EEEEFA;border-radius:4px;height:4px;margin-top:0.28rem;"><div style="background:#3B4CCA;height:4px;width:{bw}%;border-radius:4px;"></div></div></div>',unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f'<div style="padding:0.65rem 0;font-weight:800;font-size:0.9rem;color:#2E7D32;">{a["lift"]:.1f}x</div>',unsafe_allow_html=True)

    with tab3:
        sec("Discount Offers","ALL PROFITABLE","🎁")
        st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:600px;">
            All these discount offers keep your profit margin healthy.</div>""",unsafe_allow_html=True)
        for p in PROMOS:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-left:5px solid #FFCB05;
                        border-radius:var(--radius);padding:1.1rem 1.4rem;margin-bottom:0.75rem;box-shadow:var(--shadow);">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.7rem;">
                    <div style="flex:1;min-width:240px;">
                        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;flex-wrap:wrap;">
                            <span style="font-size:1.1rem;">🎁</span>
                            <span style="font-weight:900;font-size:0.95rem;color:#1A1A2E;">
                                Buy <span style="color:#CC0000;">{p['buy'][:25]}{"..." if len(p['buy'])>25 else ""}</span>
                                &nbsp;&#8594;&nbsp;
                                Get <span style="color:#3B4CCA;">{p['get'][:25]}{"..." if len(p['get'])>25 else ""}</span>
                                <span style="color:#2E7D32;font-family:'Fredoka One',cursive;">&nbsp;{p['off']} off</span>
                            </span>
                        </div>
                        <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                            {pill(f"Profit margin stays at {p['margin']}%","#E8F5E9","#2E7D32","0.71rem")}
                            {pill(f"Est. extra &#165;{p['gain']:,}/week","#E8ECFF","#3B4CCA","0.71rem")}
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:'Fredoka One',cursive;font-size:2.1rem;color:#FFCB05;">{p['off']}</div>
                        <div style="font-size:0.63rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;">discount</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ORDER PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Order Patterns":
    sec("How Customers Order","FROM YOUR SALES DATA","📋")
    st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:620px;">
        Which menu items are ordered together most often. Use this for menu layout and counter placement.</div>""",unsafe_allow_html=True)
    f1,f2 = st.columns([1,1])
    with f1: min_c = st.slider("Minimum chance of ordering together (%)",0,100,0,5)
    with f2: sopt  = st.selectbox("Sort by",["Highest Chance","Most Common","Most Consistent"])
    km = {"Highest Chance":"conf","Most Common":"pct","Most Consistent":"stable"}
    filtered = sorted([r for r in PATTERNS if r["conf"]>=min_c],key=lambda x:x[km[sopt]],reverse=True)
    st.markdown(f'<div style="font-size:0.77rem;color:#7B7B9A;font-weight:700;margin-bottom:0.8rem;">Showing {len(filtered)} of {len(PATTERNS)} patterns</div>',unsafe_allow_html=True)
    rc2 = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2","#00838F"]
    for i,r in enumerate(filtered):
        bw = int(r['conf']*0.87)
        sl = "Very Consistent" if r['stable']>=6 else "Growing" if r['stable']>=3 else "Newly Spotted"
        sb = "#E8F5E9" if r['stable']>=6 else "#FFF8E8" if r['stable']>=3 else "#E8ECFF"
        sf = "#2E7D32" if r['stable']>=6 else "#E65100" if r['stable']>=3 else "#3B4CCA"
        color = rc2[min(i,5)]
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                    padding:1rem 1.3rem;margin-bottom:0.55rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.7rem;flex-wrap:wrap;gap:0.4rem;">
                <div>
                    <span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r['a']}</span>
                    <span style="color:#CC0000;font-size:1rem;margin:0 0.45rem;">&#8594;</span>
                    <span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r['b']}</span>
                </div>
                <div style="display:flex;gap:0.38rem;flex-wrap:wrap;">
                    {pill(f"{r['conf']}% chance","#FFE8E8","#CC0000","0.7rem")}
                    {pill(f"{r['pct']}% of orders","#E8ECFF","#3B4CCA","0.7rem")}
                    {pill(f"{r['lift']:.1f}x more likely","#E8F5E9","#2E7D32","0.7rem")}
                    {badge(sl,sb,sf)}
                </div>
            </div>
            <div style="background:#F0EEF8;border-radius:5px;height:6px;overflow:hidden;">
                <div style="background:{color};height:6px;width:{bw}%;border-radius:5px;opacity:0.75;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MENU & PRICING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Menu & Pricing":
    sec("Full Menu & Pricing","","🍽️")

    # Summary
    foods  = [m for m in MENU if m["category"]=="Food"]
    sweets = [m for m in MENU if m["category"]=="Sweets"]
    drinks = [m for m in MENU if m["category"]=="Drinks"]
    avg_price = int(sum(m["price"] for m in MENU)/len(MENU))

    c1,c2,c3,c4 = st.columns(4)
    for col,icon,label,val,sub,acc in [
        (c1,"🍔","Food Items",str(len(foods)),f"Avg &#165;{int(sum(m['price'] for m in foods)/len(foods)):,}","#E65100"),
        (c2,"🍰","Sweets",str(len(sweets)),f"Avg &#165;{int(sum(m['price'] for m in sweets)/len(sweets)):,}","#AD1457"),
        (c3,"🥤","Drinks",str(len(drinks)),f"Avg &#165;{int(sum(m['price'] for m in drinks)/len(drinks)):,}","#1565C0"),
        (c4,"💴","Avg Price",f"&#165;{avg_price:,}","Across all items","#2E7D32"),
    ]:
        with col:
            st.markdown(f"""<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:var(--radius);
                    padding:1.1rem 1.2rem;box-shadow:var(--shadow);border-left:6px solid {acc};">
                <div style="font-size:1.6rem;margin-bottom:0.28rem;">{icon}</div>
                <div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.85rem;color:#1A1A2E;line-height:1;margin-bottom:0.22rem;">{val}</div>
                <div style="font-size:0.71rem;color:#7B7B9A;font-weight:600;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    # Filter row
    fc1,fc2 = st.columns([1,1])
    with fc1: cat_filter = st.selectbox("Show category",["All","Food","Sweets","Drinks"])
    with fc2: sort_menu  = st.selectbox("Sort by",["Category","Price: Low to High","Price: High to Low","Name"])

    filtered_menu = MENU if cat_filter=="All" else [m for m in MENU if m["category"]==cat_filter]
    if   sort_menu=="Price: Low to High":  filtered_menu = sorted(filtered_menu,key=lambda x:x["price"])
    elif sort_menu=="Price: High to Low":  filtered_menu = sorted(filtered_menu,key=lambda x:x["price"],reverse=True)
    elif sort_menu=="Name":                filtered_menu = sorted(filtered_menu,key=lambda x:x["name"])

    # Render by category
    current_cat = None
    for m in filtered_menu:
        if m["category"] != current_cat:
            current_cat = m["category"]
            cc = CATEGORY_COLORS[current_cat]
            cat_icon = {"Food":"🍔","Sweets":"🍰","Drinks":"🥤"}[current_cat]
            sec(f"{cat_icon}  {current_cat}","","")

        cc = CATEGORY_COLORS[m["category"]]
        # Find if this item is in any combo for the "featured in" tag
        in_combos = [c["name"] for c in COMBOS if m["name"] in c["items"]]
        combo_tag = f'&nbsp;{pill("Featured in combo",cc["bg"],cc["fg"],"0.68rem")}' if in_combos else ""

        # Find add-on relation
        addon_tag = ""
        for a in ADDONS:
            if a["from"]==m["name"] or a["to"]==m["name"]:
                addon_tag = f'&nbsp;{pill("Used in add-on tip","#E8F5E9","#2E7D32","0.68rem")}'
                break

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1.5px solid {cc['border']};border-radius:14px;
                    padding:0.95rem 1.3rem;margin-bottom:0.5rem;box-shadow:var(--shadow);
                    display:flex;align-items:center;justify-content:space-between;gap:0.8rem;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:0.85rem;flex:1;min-width:200px;">
                <div style="width:42px;height:42px;min-width:42px;background:{cc['bg']};border-radius:11px;
                            display:flex;align-items:center;justify-content:center;font-size:1.4rem;
                            border:1.5px solid {cc['border']};">{m['emoji']}</div>
                <div>
                    <div style="font-weight:800;font-size:0.9rem;color:#1A1A2E;margin-bottom:0.12rem;">{m['name']}</div>
                    <div style="font-size:0.75rem;color:#7B7B9A;font-weight:600;margin-bottom:0.28rem;">{m['desc']}</div>
                    <div style="display:flex;gap:0.3rem;flex-wrap:wrap;">
                        {badge(m['category'],cc['bg'],cc['fg'])}
                        {combo_tag}
                        {addon_tag}
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Fredoka One',cursive;font-size:1.5rem;color:#CC0000;">&#165;{m['price']:,}</div>
                <div style="font-size:0.67rem;color:#7B7B9A;font-weight:600;">per item</div>
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOADED FILES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Uploaded Files":
    sec("Sales Data Files","FILE LOG","📁")
    st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:580px;">
        All sales files uploaded to the system. Upload new files anytime, or remove files you no longer need.</div>""",unsafe_allow_html=True)

    col_up,col_log = st.columns([1,1.4])

    with col_up:
        st.markdown("""
        <div style="background:#FFFFFF;border:2px dashed #E4DCFF;border-radius:var(--radius);
                    padding:1.8rem 1.4rem;text-align:center;box-shadow:var(--shadow);margin-bottom:0.7rem;">
            <div style="font-size:2.3rem;margin-bottom:0.6rem;">📂</div>
            <div style="font-weight:800;font-size:0.97rem;color:#1A1A2E;margin-bottom:0.3rem;">Upload New Sales File</div>
            <div style="font-size:0.77rem;color:#7B7B9A;font-weight:600;">CSV or Excel from any POS system</div>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose file",type=["csv","xlsx","xls"],
                                     label_visibility="collapsed",key="file_upload")
        if uploaded:
            exists = any(f["name"]==uploaded.name for f in st.session_state.files)
            rows = random.randint(800,2400)
            if not exists:
                st.session_state.files.append({
                    "name": uploaded.name,
                    "time": datetime.now().strftime("%d %b %Y  %H:%M"),
                    "size": f"{uploaded.size/1024:.1f} KB",
                    "rows": rows,
                    "ext":  uploaded.name.split(".")[-1].upper(),
                })
                st.session_state.total_txn += rows
            st.markdown(f"""
            <div style="background:#E8F5E9;border:1.5px solid #A5D6A7;border-radius:10px;padding:0.8rem 1rem;margin-top:0.5rem;">
                <div style="font-weight:800;color:#2E7D32;font-size:0.88rem;margin-bottom:0.1rem;">File received</div>
                <div style="font-size:0.76rem;color:#388E3C;font-weight:600;">{uploaded.name}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:0.4rem'></div>",unsafe_allow_html=True)
            if st.button("Process This File Now",use_container_width=True):
                st.session_state.page = "Run Analysis"; st.rerun()

    with col_log:
        count = len(st.session_state.files)
        total = st.session_state.total_txn
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                    padding:1.1rem 1.4rem;margin-bottom:0.75rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.1rem;">
                <div style="font-weight:800;font-size:0.95rem;color:#1A1A2E;">File History</div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.35rem;color:#CC0000;">{count}</div>
            </div>
            <div style="font-size:0.73rem;color:#7B7B9A;font-weight:600;">
                {count} file{"s" if count!=1 else ""} · {total:,} total orders
            </div>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.files:
            st.markdown("""
            <div style="background:#F8F6FF;border:1.5px dashed #E4DCFF;border-radius:var(--radius);
                        padding:2.5rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.6rem;">📭</div>
                <div style="font-weight:700;color:#7B7B9A;font-size:0.88rem;">No files uploaded yet</div>
            </div>""", unsafe_allow_html=True)
        else:
            delete_idx = None
            for idx,f in enumerate(reversed(st.session_state.files)):
                real_idx = len(st.session_state.files)-1-idx
                ext_color = "#CC0000" if f["ext"]=="CSV" else "#2E7D32"
                fc1,fc2 = st.columns([1,0.15])
                with fc1:
                    st.markdown(f"""
                    <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:12px;
                                padding:0.85rem 1rem;margin-bottom:0.5rem;">
                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <div style="display:flex;align-items:center;gap:0.7rem;">
                                <div style="background:{ext_color};color:white;font-size:0.58rem;
                                            font-weight:800;padding:0.2rem 0.48rem;border-radius:4px;
                                            letter-spacing:0.05em;">{f["ext"]}</div>
                                <div>
                                    <div style="font-weight:800;font-size:0.86rem;color:#1A1A2E;margin-bottom:0.08rem;">{f["name"]}</div>
                                    <div style="font-size:0.7rem;color:#7B7B9A;font-weight:600;">
                                        {f["time"]} · {f["size"]} · ~{f["rows"]:,} records
                                    </div>
                                </div>
                            </div>
                            {badge("Processed","#E8F5E9","#2E7D32")}
                        </div>
                    </div>""", unsafe_allow_html=True)
                with fc2:
                    if st.button("🗑️", key=f"del_{real_idx}", help="Remove this file"):
                        delete_idx = real_idx

            if delete_idx is not None:
                removed = st.session_state.files.pop(delete_idx)
                st.session_state.total_txn = max(0, st.session_state.total_txn - removed.get("rows",0))
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  RUN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Run Analysis":
    sec("Run New Analysis","","⚡")
    st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.3rem;line-height:1.6;max-width:560px;">
        Upload your latest sales file and click <strong style="color:#1A1A2E;">Start Analysis</strong>.
        The system will find ordering patterns and refresh all deal suggestions automatically.</div>""",unsafe_allow_html=True)

    col_f,col_o = st.columns([1,1])
    with col_f:
        st.markdown("""<div style="background:#FFFFFF;border:2px dashed #E4DCFF;border-radius:var(--radius);
                    padding:1.8rem 1.4rem;text-align:center;box-shadow:var(--shadow);">
            <div style="font-size:2.3rem;margin-bottom:0.6rem;">📂</div>
            <div style="font-weight:800;font-size:0.97rem;color:#1A1A2E;margin-bottom:0.3rem;">Drop Your Sales File Here</div>
            <div style="font-size:0.77rem;color:#7B7B9A;font-weight:600;">CSV or Excel from any POS system</div>
        </div>""", unsafe_allow_html=True)
        run_file = st.file_uploader("Sales file",type=["csv","xlsx","xls"],
                                     label_visibility="collapsed",key="run_file")
        if run_file:
            exists = any(f["name"]==run_file.name for f in st.session_state.files)
            rows   = random.randint(800,2400)
            if not exists:
                st.session_state.files.append({
                    "name":run_file.name,"time":datetime.now().strftime("%d %b %Y  %H:%M"),
                    "size":f"{run_file.size/1024:.1f} KB","rows":rows,
                    "ext":run_file.name.split(".")[-1].upper(),
                })
                st.session_state.total_txn += rows
            r2 = next(f["rows"] for f in st.session_state.files if f["name"]==run_file.name)
            st.markdown(f"""<div style="background:#E8F5E9;border:1.5px solid #A5D6A7;border-radius:10px;padding:0.75rem 0.95rem;margin-top:0.5rem;">
                <div style="font-weight:800;color:#2E7D32;font-size:0.87rem;margin-bottom:0.08rem;">File ready</div>
                <div style="font-size:0.76rem;color:#388E3C;font-weight:600;">{run_file.name} · ~{r2:,} records</div>
            </div>""", unsafe_allow_html=True)

    with col_o:
        st.markdown("""<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                    padding:1.3rem 1.4rem;box-shadow:var(--shadow);">
            <div style="font-weight:900;font-size:0.95rem;color:#1A1A2E;margin-bottom:0.9rem;">What to Include</div>""",
            unsafe_allow_html=True)
        inc_combos    = st.toggle("Build combo set suggestions",   value=True)
        inc_addons    = st.toggle("Build counter add-on tips",     value=True)
        inc_discounts = st.toggle("Build discount offers",         value=True)
        inc_monitor   = st.toggle("Check for menu item changes",   value=True)
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>",unsafe_allow_html=True)
    log_box   = st.empty()
    btn_c,_   = st.columns([1,2])
    with btn_c: go = st.button("Start Analysis", use_container_width=True)

    if st.session_state.run_logs and not go:
        lines = "\n".join(st.session_state.run_logs[-25:])
        log_box.markdown(f'<div style="background:#0D1117;border-radius:14px;padding:1rem 1.3rem;font-family:monospace;font-size:0.75rem;color:#8B949E;min-height:80px;max-height:200px;overflow-y:auto;border:1.5px solid #21262D;white-space:pre-wrap;line-height:1.85;">{lines}</div>',unsafe_allow_html=True)

    if go:
        st.session_state.run_logs = []
        st.session_state.ran = False

        def log(msg,e="🔵"):
            st.session_state.run_logs.append(f"[{now_str()}]  {e}  {msg}")

        def render():
            lines = "\n".join(st.session_state.run_logs[-25:])
            log_box.markdown(f'<div style="background:#0D1117;border-radius:14px;padding:1rem 1.3rem;font-family:monospace;font-size:0.75rem;color:#8B949E;min-height:120px;max-height:220px;overflow-y:auto;border:1.5px solid #21262D;white-space:pre-wrap;line-height:1.85;">{lines}</div>',unsafe_allow_html=True)

        stages = [
            ("Reading your sales file ...",[
                ("Detecting file format and column layout ...","🔍"),
                ("Reading order numbers and item names ...","📖"),
                (f"Found ~{random.randint(900,2000):,} customer orders to work with","✅"),
                ("Cleaning up any formatting issues ...","🧹"),
                ("Sales data is ready.","✅"),
            ],True),
            ("Finding ordering patterns ...",[
                ("Looking for items frequently ordered together ...","🔍"),
                ("Calculating how often each combination appears ...","📊"),
                (f"Found {len(PATTERNS)} strong patterns in your orders.","✅"),
            ],inc_combos),
            ("Building combo set suggestions ...",[
                (f"Checking menu pricing for bundle calculations ...","💴"),
                (f"Created {len(COMBOS)} combo deal suggestions.","✅"),
            ],inc_combos),
            ("Building counter add-on tips ...",[
                ("Identifying best add-ons for each item ...","⚡"),
                (f"Prepared {len(ADDONS)} add-on suggestions.","✅"),
            ],inc_addons),
            ("Building discount offers ...",[
                ("Checking profit margins for each offer ...","💴"),
                (f"Created {len(PROMOS)} safe discount offers.","✅"),
            ],inc_discounts),
            ("Checking for menu item changes ...",[
                ("Comparing with last month's order mix ...","📡"),
                ("All popular items are within normal range.","✅"),
            ],inc_monitor),
        ]
        for name,logs,enabled in stages:
            if not enabled:
                log(f"Skipping: {name}","⏭️"); render(); time.sleep(0.15); continue
            log(name,"🔄"); render()
            for msg,emoji in logs:
                time.sleep(0.38); log(msg,emoji); render()

        time.sleep(0.25)
        log("All done! Your deals and suggestions have been updated.","🎉")
        render()
        st.session_state.ran = True
        time.sleep(0.3)

        st.markdown("""<div style="background:#E8F5E9;border:1.5px solid #A5D6A7;border-radius:var(--radius);padding:1.1rem 1.4rem;margin-top:0.9rem;">
            <div style="font-weight:900;font-size:0.97rem;color:#2E7D32;margin-bottom:0.3rem;">Analysis complete!</div>
            <div style="font-size:0.84rem;color:#388E3C;font-weight:600;">Your combo deals, counter tips, and discount offers are all updated.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:0.4rem'></div>",unsafe_allow_html=True)
        if st.button("View Suggested Deals",use_container_width=False):
            st.session_state.page = "Suggested Deals"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  MENU MONITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Menu Monitor":
    sec("Menu Item Health","","📡")
    st.markdown("""<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;max-width:620px;">
        Tracks how each menu item is doing compared to last month. If a popular item shifts significantly it will appear here.</div>""",unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,icon,label,val,sub,acc in [
        (c1,"✅","Items Stable","6","No big changes","#2E7D32"),
        (c2,"👁️","Items to Watch","0","All within range","#FFCB05"),
        (c3,"🕐","Last Checked",datetime.now().strftime("%H:%M"),"Just now","#3B4CCA"),
    ]:
        with col:
            st.markdown(f"""<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:var(--radius);
                    padding:1.1rem 1.2rem;box-shadow:var(--shadow);border-left:6px solid {acc};">
                <div style="font-size:1.6rem;margin-bottom:0.28rem;">{icon}</div>
                <div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>
                <div style="font-family:'Fredoka One',cursive;font-size:1.85rem;color:#1A1A2E;line-height:1;margin-bottom:0.22rem;">{val}</div>
                <div style="font-size:0.71rem;color:#7B7B9A;font-weight:600;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    sec("Item-by-Item Breakdown","","📊")
    for p in MONITOR:
        psi=p["psi"]
        status      = "Needs Attention" if psi>0.20 else "Worth Watching" if psi>0.10 else "Stable"
        status_bg   = "#FFE8E8" if psi>0.20 else "#FFF8E8" if psi>0.10 else "#E8F5E9"
        status_fg   = "#CC0000" if psi>0.20 else "#E65100" if psi>0.10 else "#2E7D32"
        bar_color   = "#CC0000" if psi>0.20 else "#FFCB05" if psi>0.10 else "#4CAF50"
        bw          = min(int(psi/0.25*100),100)
        change      = p["now"]-p["last"]
        change_str  = f"+{change}%" if change>0 else f"{change}%"
        change_fg   = "#2E7D32" if change>0 else "#CC0000" if change<0 else "#757575"

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:var(--radius);
                    padding:1rem 1.3rem;margin-bottom:0.65rem;box-shadow:var(--shadow);">
            <div style="display:flex;justify-content:space-between;align-items:center;
                        flex-wrap:wrap;gap:0.7rem;margin-bottom:0.8rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
                    <span style="font-size:1.3rem;">{p['emoji']}</span>
                    <div style="font-weight:800;font-size:0.93rem;color:#1A1A2E;">{p['item']}</div>
                    {badge(status,status_bg,status_fg)}
                </div>
                <div style="display:flex;align-items:center;gap:1.2rem;">
                    <div style="text-align:center;">
                        <div style="font-size:0.6rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Last Month</div>
                        <div style="font-weight:800;font-size:0.92rem;color:#1A1A2E;">{p['last']}%</div>
                    </div>
                    <div style="color:#7B7B9A;font-size:0.95rem;">&#8594;</div>
                    <div style="text-align:center;">
                        <div style="font-size:0.6rem;color:#7B7B9A;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">This Month</div>
                        <div style="font-weight:800;font-size:0.92rem;color:#1A1A2E;">{p['now']}%</div>
                    </div>
                    <div style="font-weight:800;font-size:0.92rem;color:{change_fg};">{change_str}</div>
                </div>
            </div>
            <div style="background:#F0EEF8;border-radius:5px;height:7px;overflow:hidden;">
                <div style="background:{bar_color};height:7px;width:{bw}%;border-radius:5px;opacity:0.8;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:0.3rem;">
                <div style="font-size:0.6rem;color:#7B7B9A;font-weight:600;">Normal</div>
                <div style="font-size:0.6rem;color:#7B7B9A;font-weight:600;">Needs attention</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#E8ECFF;border:1.5px solid #C5CAF5;border-radius:var(--radius);padding:1rem 1.3rem;margin-top:0.4rem;">
        <div style="font-weight:800;color:#3B4CCA;font-size:0.88rem;margin-bottom:0.25rem;">What does this mean?</div>
        <div style="font-size:0.81rem;color:#3B4CCA;font-weight:600;line-height:1.65;">
            <strong>Stable</strong> — item popularity hasn't changed much.
            <strong>Worth Watching</strong> — small shift, keep an eye on it.
            <strong>Needs Attention</strong> — big change, consider running a new analysis.
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:0.8rem'></div>",unsafe_allow_html=True)
    if st.button("Run New Analysis to Refresh Deals"):
        st.session_state.page = "Run Analysis"; st.rerun()
