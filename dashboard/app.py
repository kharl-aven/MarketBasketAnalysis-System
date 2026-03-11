"""
Pokemon Cafe — Staff Portal
Real market-basket analysis driven entirely from uploaded CSV/Excel files.
No backend required. All computation runs inside Streamlit.
"""
import streamlit as st
import pandas as pd
import os, time, io
from itertools import combinations
from collections import defaultdict
from datetime import datetime

st.set_page_config(
    page_title="Pokemon Cafe — Staff Portal",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── MENU MASTER DATA ──────────────────────────────────────────────────────────
MENU = [
    {"name":"The Pikachu Hamburger",                        "category":"Food",   "price":980,  "emoji":"⚡","pokemon":"pikachu",
     "desc":"Signature hamburger shaped like Pikachu's face with seasoned beef patty"},
    {"name":"Snorlax's Tummy Filling Nap Lunch Plate",      "category":"Food",   "price":1200, "emoji":"😴","pokemon":"snorlax",
     "desc":"Hearty rice and meat plate inspired by Snorlax — comes with miso soup"},
    {"name":"Pikachu & Squirtle's BFF Curry Plate",         "category":"Food",   "price":1150, "emoji":"🍛","pokemon":"squirtle",
     "desc":"Two-tone curry plate with chicken and vegetable sides"},
    {"name":"Rice Plate Meal with Eevee",                   "category":"Food",   "price":1050, "emoji":"🌿","pokemon":"eevee",
     "desc":"Eevee-decorated rice omelette with demi-glace sauce"},
    {"name":"Paldean Form Wooper Burger",                   "category":"Food",   "price":950,  "emoji":"🍔","pokemon":"wooper",
     "desc":"Ground pork burger with Paldean Wooper bun decoration"},
    {"name":"Clodsire Soup Pot",                            "category":"Food",   "price":750,  "emoji":"🍲","pokemon":"clodsire",
     "desc":"Warm creamy potato soup served in a Clodsire-shaped bowl"},
    {"name":"Pokemon Cafe's Pikachu Souffle Pancake",       "category":"Sweets", "price":880,  "emoji":"🥞","pokemon":"pikachu",
     "desc":"Fluffy Japanese souffle pancake with Pikachu face design"},
    {"name":"Pokemon Cafe's Berry Chocolate Parfait",       "category":"Sweets", "price":920,  "emoji":"🫐","pokemon":"eevee",
     "desc":"Layered parfait with fresh berries, chocolate sauce, and whipped cream"},
    {"name":"Poke Ball Dessert Bowl",                       "category":"Sweets", "price":850,  "emoji":"🔴","pokemon":"gengar",
     "desc":"Ice cream dessert bowl decorated as a Poke Ball"},
    {"name":"Assorted Dragon-Type Sweets",                  "category":"Sweets", "price":1100, "emoji":"🐉","pokemon":"gengar",
     "desc":"Plate of three dragon-themed petit fours and macarons"},
    {"name":"Fuecoco's Apple Soda Float",                   "category":"Drinks", "price":680,  "emoji":"🍎","pokemon":"fuecoco",
     "desc":"Apple-flavored soda with vanilla ice cream float and Fuecoco decoration"},
    {"name":"Quaxly's Ramune Soda Float",                   "category":"Drinks", "price":680,  "emoji":"💧","pokemon":"quaxly",
     "desc":"Ramune soda float with blue jelly and Quaxly character straw topper"},
    {"name":"Gengar's Confuse Ray Smoothie",                "category":"Drinks", "price":720,  "emoji":"👻","pokemon":"gengar",
     "desc":"Purple mixed berry smoothie with popping candy rim"},
    {"name":"Say Hello to Eevee's Royal Milk Tea",          "category":"Drinks", "price":650,  "emoji":"🍵","pokemon":"eevee",
     "desc":"Classic royal milk tea with Eevee latte art and brown sugar boba"},
    {"name":"Pokemon Latte",                                "category":"Drinks", "price":620,  "emoji":"☕","pokemon":"pikachu",
     "desc":"House latte with seasonal Pokemon latte art"},
    {"name":"Cocoa",                                        "category":"Drinks", "price":580,  "emoji":"🍫","pokemon":"snorlax",
     "desc":"Rich hot chocolate with Pokemon-themed marshmallows"},
]
MENU_NAMES  = {m["name"] for m in MENU}
MENU_LOOKUP = {m["name"]: m for m in MENU}
MENU_ALIASES = {
    "pikachu hamburger":            "The Pikachu Hamburger",
    "snorlax lunch":                "Snorlax's Tummy Filling Nap Lunch Plate",
    "curry plate":                  "Pikachu & Squirtle's BFF Curry Plate",
    "bff curry":                    "Pikachu & Squirtle's BFF Curry Plate",
    "eevee rice":                   "Rice Plate Meal with Eevee",
    "rice plate":                   "Rice Plate Meal with Eevee",
    "wooper burger":                "Paldean Form Wooper Burger",
    "clodsire soup":                "Clodsire Soup Pot",
    "soup pot":                     "Clodsire Soup Pot",
    "souffle pancake":              "Pokemon Cafe's Pikachu Souffle Pancake",
    "pikachu pancake":              "Pokemon Cafe's Pikachu Souffle Pancake",
    "parfait":                      "Pokemon Cafe's Berry Chocolate Parfait",
    "berry parfait":                "Pokemon Cafe's Berry Chocolate Parfait",
    "pokeball bowl":                "Poke Ball Dessert Bowl",
    "poke ball bowl":               "Poke Ball Dessert Bowl",
    "dessert bowl":                 "Poke Ball Dessert Bowl",
    "dragon sweets":                "Assorted Dragon-Type Sweets",
    "dragon type sweets":           "Assorted Dragon-Type Sweets",
    "apple float":                  "Fuecoco's Apple Soda Float",
    "fuecoco float":                "Fuecoco's Apple Soda Float",
    "ramune float":                 "Quaxly's Ramune Soda Float",
    "quaxly float":                 "Quaxly's Ramune Soda Float",
    "gengar smoothie":              "Gengar's Confuse Ray Smoothie",
    "confuse ray":                  "Gengar's Confuse Ray Smoothie",
    "smoothie":                     "Gengar's Confuse Ray Smoothie",
    "milk tea":                     "Say Hello to Eevee's Royal Milk Tea",
    "eevee tea":                    "Say Hello to Eevee's Royal Milk Tea",
    "royal milk tea":               "Say Hello to Eevee's Royal Milk Tea",
    "latte":                        "Pokemon Latte",
    "pokemon latte":                "Pokemon Latte",
    "cocoa":                        "Cocoa",
    "hot chocolate":                "Cocoa",
}

CATEGORY_COLORS = {
    "Food":   {"bg":"#FFF3E0","fg":"#E65100","border":"#FFCC80"},
    "Sweets": {"bg":"#FCE4EC","fg":"#AD1457","border":"#F48FB1"},
    "Drinks": {"bg":"#E3F2FD","fg":"#1565C0","border":"#90CAF9"},
}

POKEMON_SPRITES = {
    "pikachu":  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
    "eevee":    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png",
    "snorlax":  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png",
    "gengar":   "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png",
    "squirtle": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png",
    "fuecoco":  "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/909.png",
    "quaxly":   "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/914.png",
    "clodsire": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/980.png",
    "wooper":   "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/194.png",
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {
    "page": "Home", "files": [], "results": None,
    "log": [], "processing": False, "data_version": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── MBA ENGINE ────────────────────────────────────────────────────────────────
def resolve_item(raw):
    s = str(raw).strip()
    if s in MENU_NAMES:
        return s
    low = s.lower()
    if low in MENU_ALIASES:
        return MENU_ALIASES[low]
    for name in MENU_NAMES:
        if low in name.lower() or name.lower() in low:
            return name
    return None

def load_df(file_bytes, filename):
    try:
        if filename.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(file_bytes)), ""
        return pd.read_csv(io.BytesIO(file_bytes)), ""
    except Exception as e:
        return None, str(e)

def detect_cols(df):
    cols = [str(c).strip().lower() for c in df.columns]
    df.columns = cols
    txn_h  = ["order","transaction","txn","receipt","id","basket","invoice","order_id","order id","bill"]
    item_h = ["item","product","name","menu","dish","food","drink","sku","description","ordered","menu_item"]
    txn  = next((c for h in txn_h  for c in cols if h in c), cols[0] if cols else None)
    item = next((c for h in item_h for c in cols if h in c), cols[1] if len(cols)>1 else None)
    return txn, item

def run_mba(files, log_fn):
    log_fn("Loading uploaded files ...", "step")
    all_rows = []
    for f in files:
        df, err = load_df(f["bytes"], f["name"])
        if err:
            log_fn(f"Could not read {f['name']}: {err}", "warn"); continue
        txn_col, item_col = detect_cols(df)
        if not txn_col or not item_col:
            log_fn(f"Could not detect columns in {f['name']}", "warn"); continue
        log_fn(f"{f['name']} — {len(df):,} rows | order col: '{txn_col}' | item col: '{item_col}'", "ok")
        for _, row in df[[txn_col, item_col]].dropna().iterrows():
            resolved = resolve_item(str(row[item_col]))
            if resolved:
                all_rows.append({"txn": str(row[txn_col]).strip(), "item": resolved})
            else:
                pass  # silently skip unrecognised items

    if not all_rows:
        log_fn("No recognisable menu items found. Check that your item column contains menu item names.", "error")
        return {}

    orders_df = pd.DataFrame(all_rows)
    n_txn   = orders_df["txn"].nunique()
    n_items = orders_df["item"].nunique()
    log_fn(f"{len(orders_df):,} line items | {n_txn:,} unique orders | {n_items} menu items recognised", "step")

    log_fn("Counting item frequencies ...", "step")
    item_counts = orders_df.groupby("item")["txn"].count().sort_values(ascending=False)

    log_fn("Building order baskets ...", "step")
    baskets = orders_df.groupby("txn")["item"].apply(set)
    multi   = baskets[baskets.apply(len) > 1]
    n_multi = len(multi)
    log_fn(f"{n_multi:,} orders had 2+ items (used for pair analysis)", "ok")

    if n_multi == 0:
        log_fn("Not enough multi-item orders for pair analysis. Try uploading more data.", "warn")
        # Still return popularity
        pop = []
        for item, cnt in item_counts.items():
            m = MENU_LOOKUP.get(item, {})
            pop.append({"item":item,"emoji":m.get("emoji","🍽️"),"pokemon":m.get("pokemon","pikachu"),
                        "count":int(cnt),"pct":round(cnt/n_txn*100,1),"revenue":int(cnt)*m.get("price",0)})
        return {"n_txn":n_txn,"n_items":n_items,"total_rows":len(orders_df),
                "rules":[],"combos":[],"addons":[],"promos":[],"popularity":pop,
                "item_counts":item_counts.to_dict(),"analysed_at":datetime.now().strftime("%d %b %Y  %H:%M"),
                "n_files":len(files)}

    log_fn("Finding item pairs ...", "step")
    pair_counts   = defaultdict(int)
    item_in_multi = defaultdict(int)
    for items in multi:
        for item in items:
            item_in_multi[item] += 1
        for a, b in combinations(sorted(items), 2):
            pair_counts[(a, b)] += 1

    log_fn("Calculating support, confidence and lift ...", "step")
    rules = []
    for (a, b), count in pair_counts.items():
        if count < 2:
            continue
        support  = count / n_txn
        conf     = count / item_in_multi[a] if item_in_multi[a] else 0
        lift_val = support / ((item_in_multi[a]/n_txn) * (item_in_multi[b]/n_txn)) if n_txn > 0 else 0
        pct      = round(count / n_multi * 100, 1)
        rules.append({"a":a,"b":b,"count":count,"support":round(support,4),
                      "conf":round(conf*100,1),"lift":round(lift_val,2),"pct":pct})

    rules.sort(key=lambda x: (x["lift"], x["conf"]), reverse=True)
    top_rules = rules[:20]
    log_fn(f"Found {len(rules)} association rules — using top {len(top_rules)}", "ok")

    log_fn("Building combo deals ...", "step")
    combos = []
    for r in top_rules[:8]:
        ma = MENU_LOOKUP.get(r["a"], {})
        mb = MENU_LOOKUP.get(r["b"], {})
        bundle_price = int((ma.get("price",0) + mb.get("price",0)) * 0.92)
        combos.append({"a":r["a"],"b":r["b"],"conf":r["conf"],"lift":r["lift"],
                       "pct":r["pct"],"count":r["count"],"price":bundle_price,
                       "pokemon":ma.get("pokemon","pikachu"),
                       "emoji_a":ma.get("emoji","🍽️"),"emoji_b":mb.get("emoji","🍽️")})

    addons = [{"from":r["a"],"to":r["b"],"conf":r["conf"],"lift":r["lift"]}
              for r in sorted(top_rules, key=lambda x: x["conf"], reverse=True)[:8]]

    promos = []
    for r in sorted(top_rules, key=lambda x: x["lift"], reverse=True)[:5]:
        ma = MENU_LOOKUP.get(r["a"],{}); mb = MENU_LOOKUP.get(r["b"],{})
        if not ma or not mb: continue
        discount  = 15 if r["lift"] > 2.0 else 10
        est_gain  = int(r["count"] * (ma.get("price",0)+mb.get("price",0)) * 0.08)
        promos.append({"buy":r["a"],"get":r["b"],"off":f"{discount}%",
                       "margin":32,"gain":est_gain,"lift":r["lift"]})

    log_fn("Computing item popularity ...", "step")
    pop = []
    for item, cnt in item_counts.items():
        m = MENU_LOOKUP.get(item, {})
        pop.append({"item":item,"emoji":m.get("emoji","🍽️"),"pokemon":m.get("pokemon","pikachu"),
                    "count":int(cnt),"pct":round(cnt/n_txn*100,1),"revenue":int(cnt)*m.get("price",0)})

    log_fn("Analysis complete! All pages have been updated with your real data.", "done")
    return {"n_txn":n_txn,"n_items":n_items,"total_rows":len(orders_df),
            "rules":top_rules,"combos":combos,"addons":addons,"promos":promos,"popularity":pop,
            "item_counts":item_counts.to_dict(),"analysed_at":datetime.now().strftime("%d %b %Y  %H:%M"),
            "n_files":len(files)}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def now_str():   return datetime.now().strftime("%H:%M:%S")
def today_str(): return datetime.now().strftime("%d %b %Y  %H:%M")

def pill(txt, bg="#FFE8E8", fg="#CC0000", size="0.74rem"):
    return (f'<span style="background:{bg};color:{fg};font-size:{size};font-weight:700;'
            f'padding:0.22rem 0.65rem;border-radius:20px;white-space:nowrap;">{txt}</span>')

def badge(txt, bg, fg):
    return (f'<span style="background:{bg};color:{fg};font-size:0.68rem;font-weight:800;'
            f'text-transform:uppercase;letter-spacing:0.07em;padding:0.22rem 0.65rem;border-radius:6px;">{txt}</span>')

def sec(title, tag="", icon=""):
    tag_html = (f'<span style="background:#FFCB05;color:#333;font-size:0.62rem;font-weight:800;'
                f'text-transform:uppercase;letter-spacing:0.07em;padding:0.18rem 0.6rem;'
                f'border-radius:5px;margin-left:0.5rem;">{tag}</span>') if tag else ""
    st.markdown(
        f'<div style="display:flex;align-items:center;margin:1.6rem 0 0.9rem 0;">'
        f'<span style="font-size:1.2rem;margin-right:0.45rem;">{icon}</span>'
        f'<span style="font-family:\'Fredoka One\',cursive;font-size:1.08rem;'
        f'color:#1A1A2E;">{title}</span>{tag_html}</div>',
        unsafe_allow_html=True)

def stat_card(col, icon, label, value, sub, accent, dest=None):
    with col:
        if dest:
            if st.button(f"{icon}  {label}", key=f"sc_{label}_{dest}",
                         use_container_width=True, help=f"Go to {dest}"):
                st.session_state.page = dest
                st.rerun()
        mt       = "margin-top:-2.55rem;" if dest else ""
        tap_html = (f'<div style="font-size:0.68rem;color:{accent};font-weight:700;'
                    f'margin-top:0.35rem;">Tap to view →</div>') if dest else ""
        st.markdown(
            f'<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;'
            f'padding:1.2rem 1.3rem;box-shadow:0 2px 16px rgba(59,76,202,0.08);'
            f'border-left:6px solid {accent};{mt}">'
            f'<div style="font-size:1.75rem;margin-bottom:0.3rem;">{icon}</div>'
            f'<div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;'
            f'letter-spacing:0.11em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>'
            f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.95rem;'
            f'color:#1A1A2E;line-height:1;margin-bottom:0.25rem;">{value}</div>'
            f'<div style="font-size:0.72rem;color:#7B7B9A;font-weight:600;">{sub}</div>'
            f'{tap_html}'
            f'</div>',
            unsafe_allow_html=True)

def no_data_banner():
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#12102A,#1A1A3E);'
        f'border-radius:18px;padding:2.5rem;text-align:center;margin-top:1rem;">'
        f'<img src="{POKEMON_SPRITES["snorlax"]}" style="width:90px;height:90px;'
        f'object-fit:contain;opacity:0.7;margin-bottom:1rem;">'
        f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.4rem;'
        f'color:#FFCB05;margin-bottom:0.5rem;">No data yet, Trainer!</div>'
        f'<div style="font-size:0.88rem;color:#6868A8;font-weight:600;">'
        f'Upload your sales file in Data & Analysis to see real results here.</div></div>',
        unsafe_allow_html=True)
    st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)
    if st.button("Go to Data & Analysis", use_container_width=False, key="goto_da"):
        st.session_state.page = "Data & Analysis"
        st.rerun()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');
:root{
    --red:#CC0000;--red-dk:#990000;--yellow:#FFCB05;
    --blue:#3B4CCA;--green:#2E7D32;
    --bg:#F7F3FF;--card:#FFFFFF;--border:#E4DCFF;
    --text:#1A1A2E;--muted:#7B7B9A;--sidebar:#12102A;
    --radius:18px;--shadow:0 2px 16px rgba(59,76,202,0.08);
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
    margin-bottom:3px!important;transition:all 0.15s!important;box-shadow:none!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
    background:rgba(255,203,5,0.1)!important;border-color:rgba(255,203,5,0.28)!important;
    color:#FFCB05!important;transform:translateX(3px)!important;
}
.stButton>button{
    background:var(--red)!important;color:white!important;border:none!important;
    border-radius:12px!important;font-family:'Nunito',sans-serif!important;font-weight:800!important;
    font-size:0.91rem!important;padding:0.58rem 1.4rem!important;transition:all 0.15s!important;
    box-shadow:0 3px 10px rgba(204,0,0,0.2)!important;
}
.stButton>button:hover{background:var(--red-dk)!important;transform:translateY(-2px)!important;}
[data-testid="stSidebar"] .stButton>button:hover{transform:translateX(3px)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:14px!important;
    padding:4px!important;border:1.5px solid var(--border)!important;gap:2px!important;margin-bottom:1rem!important;}
.stTabs [data-baseweb="tab"]{border-radius:9px!important;font-family:'Nunito',sans-serif!important;
    font-weight:700!important;font-size:0.84rem!important;color:var(--muted)!important;padding:0.45rem 1.1rem!important;}
.stTabs [aria-selected="true"]{background:var(--red)!important;color:white!important;}
.stSlider>div>div>div{background:var(--red)!important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:1.4rem 1rem 0.6rem 1rem;">'
        '<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.8rem;">'
        '<div style="width:48px;height:48px;border-radius:50%;'
        'border:3px solid #FFCB05;box-shadow:0 0 0 2px #CC0000,0 4px 12px rgba(0,0,0,0.4);'
        'background:linear-gradient(180deg,#CC0000 50%,#FFFFFF 50%);'
        'display:flex;align-items:center;justify-content:center;position:relative;">'
        '<div style="width:14px;height:14px;background:#FFFFFF;border-radius:50%;'
        'border:3px solid #333;z-index:2;position:absolute;"></div>'
        '<div style="position:absolute;top:50%;left:0;right:0;height:3px;background:#333;'
        'transform:translateY(-50%);z-index:1;"></div></div>'
        '<div><div style="font-family:\'Fredoka One\',cursive;font-size:1.15rem;color:#FFCB05;">'
        'Pokemon Cafe</div>'
        '<div style="font-size:0.62rem;color:#4A4A6A;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.09em;">Staff Portal</div></div></div></div>',
        unsafe_allow_html=True)

    res = st.session_state.results
    if res:
        st.markdown(
            f'<div style="margin:0 0.8rem 0.6rem 0.8rem;background:rgba(46,125,50,0.12);'
            f'border:1px solid rgba(46,125,50,0.3);border-radius:10px;padding:0.5rem 0.9rem;">'
            f'<div style="font-size:0.63rem;color:#4CAF50;font-weight:800;text-transform:uppercase;'
            f'letter-spacing:0.07em;">● Live Data</div>'
            f'<div style="font-size:0.73rem;color:#6868A8;font-weight:700;margin-top:2px;">'
            f'{res["n_txn"]:,} orders · {res["n_files"]} file(s)</div>'
            f'<div style="font-size:0.62rem;color:#3A3A6A;font-weight:600;margin-top:1px;">'
            f'Run {res["analysed_at"]}</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="margin:0 0.8rem 0.6rem 0.8rem;background:rgba(255,203,5,0.08);'
            'border:1px solid rgba(255,203,5,0.18);border-radius:10px;padding:0.5rem 0.9rem;">'
            '<div style="font-size:0.63rem;color:#FFCB05;font-weight:800;text-transform:uppercase;">⚠ No Data</div>'
            '<div style="font-size:0.72rem;color:#5A5A8A;font-weight:700;margin-top:2px;">'
            'Upload a file to begin</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div style="padding:0 0.5rem;">', unsafe_allow_html=True)
    for icon, label in [
        ("🏠","Home"),("📊","Today's Summary"),("🎯","Suggested Deals"),
        ("📋","Order Patterns"),("🍽️","Menu & Pricing"),
        ("📁","Data & Analysis"),("📡","Item Monitor"),
    ]:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── TOP BAR ───────────────────────────────────────────────────────────────────
page = st.session_state.page
st.markdown(
    f'<div style="background:linear-gradient(90deg,#CC0000 0%,#990000 70%,#7A0000 100%);'
    f'margin:-1rem -1.8rem 1.8rem -1.8rem;padding:0.95rem 2.5rem;'
    f'display:flex;align-items:center;justify-content:space-between;">'
    f'<div style="display:flex;align-items:center;gap:1rem;">'
    f'<img src="{POKEMON_SPRITES["pikachu"]}" style="width:38px;height:38px;object-fit:contain;'
    f'filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3));">'
    f'<div><div style="font-family:\'Fredoka One\',cursive;font-size:1.28rem;color:#FFCB05;">{page}</div>'
    f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.4);font-weight:600;">'
    f'Pokemon Cafe · Staff Management</div></div></div>'
    f'<div style="font-size:0.73rem;color:rgba(255,255,255,0.5);font-weight:700;'
    f'background:rgba(255,255,255,0.1);border-radius:9px;padding:0.36rem 0.88rem;">'
    f'{today_str()}</div></div>',
    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    res = st.session_state.results

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#12102A 0%,#1A1A3E 55%,#0F2060 100%);'
        f'border-radius:18px;padding:1.8rem 2rem;margin-bottom:1.4rem;'
        f'box-shadow:var(--shadow);display:flex;align-items:center;'
        f'justify-content:space-between;overflow:hidden;">'
        f'<div style="flex:1;">'
        f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.75rem;color:#FFCB05;margin-bottom:0.45rem;">'
        f'Welcome back, Trainer! 👋</div>'
        f'<div style="font-size:0.9rem;color:#8888B8;font-weight:600;max-width:480px;line-height:1.65;">'
        f'{"Dashboard is live with your real sales data." if res else "Upload your sales data in Data & Analysis to get started."}'
        f'</div>'
        f'<div style="margin-top:0.9rem;display:flex;gap:0.5rem;flex-wrap:wrap;">'
        f'{pill(str(len(st.session_state.files)) + " file(s) uploaded","#1A2A4A","#6888C8","0.75rem")}'
        f'{pill((str(res["n_txn"]) + " orders analysed") if res else "No data yet","#1A2A4A","#6888C8","0.75rem")}'
        f'{pill("Run " + res["analysed_at"] if res else "Analysis not run","#1A2A4A","#6888C8","0.75rem")}'
        f'</div></div>'
        f'<div style="display:flex;">'
        f'<img src="{POKEMON_SPRITES["pikachu"]}" style="width:90px;height:90px;object-fit:contain;'
        f'filter:drop-shadow(0 4px 8px rgba(0,0,0,0.4));">'
        f'<img src="{POKEMON_SPRITES["eevee"]}" style="width:75px;height:75px;object-fit:contain;'
        f'filter:drop-shadow(0 4px 8px rgba(0,0,0,0.3));margin-left:-10px;align-self:flex-end;">'
        f'</div></div>',
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stat_card(c1,"📁","Files Uploaded",  str(len(st.session_state.files)),
              "Sales records","#3B4CCA","Data & Analysis")
    stat_card(c2,"🛒","Orders Analysed", str(res["n_txn"]) if res else "—",
              "From your data" if res else "Upload to begin","#CC0000",
              None if res else "Data & Analysis")
    stat_card(c3,"🎯","Combo Deals",     str(len(res["combos"])) if res else "—",
              "Ready to promote" if res else "Run analysis first","#2E7D32",
              "Suggested Deals" if res else None)
    stat_card(c4,"🍽️","Menu Items",      str(len(MENU)),
              "With pricing","#E65100","Menu & Pricing")

    if not res:
        no_data_banner()
        st.stop()

    left, right = st.columns([1.7, 1])
    with left:
        sec("Top Combos From Your Data","LIVE","🔥")
        for c in res["combos"][:4]:
            sprite_url = POKEMON_SPRITES.get(c["pokemon"], POKEMON_SPRITES["pikachu"])
            extra = int((c["lift"]-1)*100)
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
                f'padding:1rem 1.3rem;margin-bottom:0.6rem;box-shadow:var(--shadow);">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                f'<div style="display:flex;align-items:center;gap:0.9rem;">'
                f'<img src="{sprite_url}" style="width:52px;height:52px;object-fit:contain;">'
                f'<div>'
                f'<div style="font-weight:900;font-size:0.91rem;color:#1A1A2E;margin-bottom:0.08rem;">'
                f'{c["emoji_a"]} {c["a"]}</div>'
                f'<div style="font-size:0.78rem;color:#CC0000;font-weight:800;margin-bottom:0.28rem;">'
                f'+ {c["emoji_b"]} {c["b"]}</div>'
                f'<div style="display:flex;gap:0.35rem;flex-wrap:wrap;">'
                f'{pill(str(c["pct"]) + "% of orders","#E8ECFF","#3B4CCA","0.7rem")}'
                f'{pill(str(extra) + "% lift","#E8F5E9","#2E7D32","0.7rem")}'
                f'</div></div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.4rem;color:#CC0000;">'
                f'&#165;{c["price"]:,}</div>'
                f'<div style="font-size:0.67rem;color:#7B7B9A;font-weight:600;">Bundle</div>'
                f'</div></div></div>',
                unsafe_allow_html=True)

    with right:
        sec("Top Items","","⭐")
        for p in res["popularity"][:6]:
            sprite_url = POKEMON_SPRITES.get(p["pokemon"], POKEMON_SPRITES["pikachu"])
            bar_w = min(int(p["pct"] * 2.5), 100)
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:12px;'
                f'padding:0.65rem 1rem;margin-bottom:0.42rem;">'
                f'<div style="display:flex;align-items:center;gap:0.65rem;">'
                f'<img src="{sprite_url}" style="width:32px;height:32px;object-fit:contain;">'
                f'<div style="flex:1;min-width:0;">'
                f'<div style="font-weight:800;font-size:0.82rem;color:#1A1A2E;'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                f'{p["emoji"]} {p["item"]}</div>'
                f'<div style="background:#F0EEF8;border-radius:4px;height:4px;margin-top:0.25rem;">'
                f'<div style="background:#CC0000;height:4px;width:{bar_w}%;border-radius:4px;opacity:0.7;"></div>'
                f'</div></div>'
                f'<div style="font-weight:800;font-size:0.84rem;color:#CC0000;">{p["pct"]}%</div>'
                f'</div></div>',
                unsafe_allow_html=True)

        sec("Quick Links","","⚡")
        for label, dest in [
            ("🎯  Suggested Deals","Suggested Deals"),
            ("📋  Order Patterns","Order Patterns"),
            ("🍽️  Menu & Pricing","Menu & Pricing"),
            ("📁  Data & Analysis","Data & Analysis"),
        ]:
            if st.button(label, use_container_width=True, key=f"ql_{dest}"):
                st.session_state.page = dest
                st.rerun()
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TODAY'S SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Today's Summary":
    res = st.session_state.results
    if not res:
        no_data_banner(); st.stop()

    sec("What's Selling Well Together","FROM YOUR DATA","📊")
    c1, c2, c3 = st.columns(3)
    for col, icon, label, val, sub, acc in [
        (c1,"🍱","Combo Deals",    str(len(res["combos"])), "Ready to promote","#CC0000"),
        (c2,"⚡","Add-on Tips",    str(len(res["addons"])), "For the counter",  "#3B4CCA"),
        (c3,"🎁","Discount Offers",str(len(res["promos"])), "Profitable deals", "#FFCB05"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;'
                f'padding:1.2rem 1.3rem;box-shadow:var(--shadow);border-left:6px solid {acc};">'
                f'<div style="font-size:1.7rem;margin-bottom:0.3rem;">{icon}</div>'
                f'<div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;'
                f'letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.2rem;">{label}</div>'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.9rem;'
                f'color:#1A1A2E;line-height:1;margin-bottom:0.25rem;">{val}</div>'
                f'<div style="font-size:0.73rem;color:#7B7B9A;font-weight:600;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1A1A3E,#12102A);'
        f'border-radius:18px;padding:1.2rem 1.6rem;margin:1rem 0;'
        f'display:flex;align-items:center;gap:2rem;">'
        f'<img src="{POKEMON_SPRITES["pikachu"]}" style="width:55px;height:55px;object-fit:contain;">'
        f'<div>'
        f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.5rem;color:#FFCB05;">'
        f'{res["n_txn"]:,} total orders analysed</div>'
        f'<div style="font-size:0.82rem;color:#6868A8;font-weight:600;">'
        f'across {res["n_files"]} file(s) · Run {res["analysed_at"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True)

    sec("Most Ordered Together","","🍽️")
    rank_colors = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2","#00838F"]
    for i, r in enumerate(res["rules"][:6]):
        bw = int(r["conf"] * 0.87)
        color = rank_colors[min(i, 5)]
        rc, rm = st.columns([0.07, 1])
        with rc:
            st.markdown(
                f'<div style="width:34px;height:34px;background:#F0EEF8;border-radius:50%;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-family:\'Fredoka One\',cursive;font-size:1rem;color:{color};margin-top:0.65rem;">'
                f'{i+1}</div>', unsafe_allow_html=True)
        with rm:
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
                f'padding:0.95rem 1.3rem;margin-bottom:0.55rem;box-shadow:var(--shadow);">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
                f'margin-bottom:0.65rem;flex-wrap:wrap;gap:0.4rem;">'
                f'<div><span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r["a"]}</span>'
                f'<span style="color:#CC0000;font-size:1rem;margin:0 0.45rem;">&#8594;</span>'
                f'<span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r["b"]}</span></div>'
                f'<div style="display:flex;gap:0.4rem;flex-wrap:wrap;">'
                f'{pill(str(r["conf"]) + "% together","#FFE8E8","#CC0000","0.7rem")}'
                f'{pill(str(r["pct"]) + "% of orders","#E8ECFF","#3B4CCA","0.7rem")}'
                f'{pill(str(r["lift"]) + "x lift","#E8F5E9","#2E7D32","0.7rem")}'
                f'</div></div>'
                f'<div style="background:#F0EEF8;border-radius:5px;height:6px;overflow:hidden;">'
                f'<div style="background:{color};height:6px;width:{bw}%;border-radius:5px;opacity:0.75;"></div>'
                f'</div></div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SUGGESTED DEALS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Suggested Deals":
    res = st.session_state.results
    if not res:
        no_data_banner(); st.stop()

    tab1, tab2, tab3 = st.tabs(["🍱  Combo Sets","⚡  Counter Add-ons","🎁  Discount Offers"])

    with tab1:
        sec("Recommended Combo Sets","FROM YOUR DATA","🍱")
        for c in res["combos"]:
            sprite = POKEMON_SPRITES.get(c["pokemon"], POKEMON_SPRITES["pikachu"])
            extra  = int((c["lift"]-1)*100)
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
                f'padding:1.1rem 1.4rem;margin-bottom:0.75rem;box-shadow:var(--shadow);">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.7rem;">'
                f'<div style="display:flex;align-items:center;gap:1rem;">'
                f'<img src="{sprite}" style="width:68px;height:68px;object-fit:contain;'
                f'filter:drop-shadow(0 3px 8px rgba(0,0,0,0.18));">'
                f'<div>'
                f'<div style="font-weight:900;font-size:0.97rem;color:#1A1A2E;margin-bottom:0.12rem;">'
                f'{c["emoji_a"]} {c["a"]}</div>'
                f'<div style="font-size:0.82rem;color:#CC0000;font-weight:800;margin-bottom:0.32rem;">'
                f'+ {c["emoji_b"]} {c["b"]}</div>'
                f'<div style="display:flex;gap:0.4rem;flex-wrap:wrap;">'
                f'{pill(str(c["conf"]) + "% order together","#FFE8E8","#CC0000","0.7rem")}'
                f'{pill(str(extra) + "% more likely bundled","#E8F5E9","#2E7D32","0.7rem")}'
                f'{pill("Seen in " + str(c["count"]) + " orders","#E8ECFF","#3B4CCA","0.7rem")}'
                f'</div></div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.6rem;color:#CC0000;">'
                f'&#165;{c["price"]:,}</div>'
                f'<div style="font-size:0.67rem;color:#7B7B9A;font-weight:700;">Bundle (8% off)</div>'
                f'</div></div></div>',
                unsafe_allow_html=True)

    with tab2:
        sec("Counter Add-on Suggestions","FOR CASHIERS","⚡")
        for a in res["addons"]:
            ma = MENU_LOOKUP.get(a["from"],{})
            mb = MENU_LOOKUP.get(a["to"],{})
            sa = POKEMON_SPRITES.get(ma.get("pokemon","pikachu"), POKEMON_SPRITES["pikachu"])
            sb = POKEMON_SPRITES.get(mb.get("pokemon","eevee"),   POKEMON_SPRITES["eevee"])
            bw = int(a["conf"] * 0.84)
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
                f'padding:0.95rem 1.3rem;margin-bottom:0.6rem;box-shadow:var(--shadow);">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.7rem;">'
                f'<div style="display:flex;align-items:center;gap:0.7rem;flex-wrap:wrap;">'
                f'<img src="{sa}" style="width:40px;height:40px;object-fit:contain;">'
                f'<div style="background:#FFF8E8;border:1.5px solid #FFE8A0;border-radius:10px;padding:0.5rem 0.85rem;">'
                f'<div style="font-weight:800;font-size:0.85rem;color:#1A1A2E;">{ma.get("emoji","🍽️")} {a["from"]}</div></div>'
                f'<div style="color:#CC0000;font-size:1.3rem;font-weight:900;">&#8594;</div>'
                f'<img src="{sb}" style="width:40px;height:40px;object-fit:contain;">'
                f'<div style="background:#FFE8E8;border:1.5px solid #FFBCBC;border-radius:10px;padding:0.5rem 0.85rem;">'
                f'<div style="font-weight:800;font-size:0.85rem;color:#CC0000;">{mb.get("emoji","🍽️")} {a["to"]}</div></div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-weight:900;font-size:1rem;color:#1A1A2E;">{a["conf"]}% chance</div>'
                f'<div style="font-size:0.72rem;color:#7B7B9A;font-weight:600;">{a["lift"]}x more likely</div>'
                f'<div style="background:#EEEEFA;border-radius:4px;height:4px;margin-top:0.35rem;width:80px;">'
                f'<div style="background:#3B4CCA;height:4px;width:{bw}%;border-radius:4px;"></div>'
                f'</div></div></div></div>',
                unsafe_allow_html=True)

    with tab3:
        sec("Discount Offers","ALL PROFITABLE","🎁")
        for p in res["promos"]:
            ma = MENU_LOOKUP.get(p["buy"],{})
            sprite = POKEMON_SPRITES.get(ma.get("pokemon","pikachu"), POKEMON_SPRITES["pikachu"])
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-left:5px solid #FFCB05;'
                f'border-radius:18px;padding:1.1rem 1.4rem;margin-bottom:0.75rem;box-shadow:var(--shadow);">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.7rem;">'
                f'<div style="display:flex;align-items:center;gap:0.9rem;flex:1;min-width:240px;">'
                f'<img src="{sprite}" style="width:52px;height:52px;object-fit:contain;">'
                f'<div>'
                f'<div style="font-weight:900;font-size:0.95rem;color:#1A1A2E;margin-bottom:0.3rem;">'
                f'Buy <span style="color:#CC0000;">{p["buy"]}</span>'
                f' &#8594; Get <span style="color:#3B4CCA;">{p["get"]}</span>'
                f' <span style="color:#2E7D32;font-family:\'Fredoka One\',cursive;"> {p["off"]} off</span></div>'
                f'<div style="display:flex;gap:0.4rem;flex-wrap:wrap;">'
                f'{pill("Margin ~" + str(p["margin"]) + "%","#E8F5E9","#2E7D32","0.71rem")}'
                f'{pill("Est. &#165;" + str(p["gain"]) + " extra","#E8ECFF","#3B4CCA","0.71rem")}'
                f'{pill(str(p["lift"]) + "x lift","#FFE8E8","#CC0000","0.71rem")}'
                f'</div></div></div>'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:2.1rem;color:#FFCB05;">'
                f'{p["off"]}</div></div></div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ORDER PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Order Patterns":
    res = st.session_state.results
    if not res:
        no_data_banner(); st.stop()

    sec("How Customers Order","FROM YOUR DATA","📋")
    f1, f2 = st.columns([1,1])
    with f1: min_c = st.slider("Min confidence (%)", 0, 100, 0, 5)
    with f2: sopt  = st.selectbox("Sort by",["Lift","Confidence","Frequency"])
    skey = {"Lift":"lift","Confidence":"conf","Frequency":"pct"}
    filtered = sorted([r for r in res["rules"] if r["conf"] >= min_c],
                      key=lambda x: x[skey[sopt]], reverse=True)
    st.markdown(
        f'<div style="font-size:0.77rem;color:#7B7B9A;font-weight:700;margin-bottom:0.8rem;">'
        f'Showing {len(filtered)} patterns based on {res["n_txn"]:,} real orders</div>',
        unsafe_allow_html=True)
    colors = ["#CC0000","#3B4CCA","#2E7D32","#E65100","#7B1FA2","#00838F","#AD1457","#FF6F00","#1565C0","#558B2F"]
    for i, r in enumerate(filtered):
        bw    = int(r["conf"] * 0.87)
        color = colors[min(i, len(colors)-1)]
        st.markdown(
            f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
            f'padding:1rem 1.3rem;margin-bottom:0.55rem;box-shadow:var(--shadow);">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
            f'margin-bottom:0.7rem;flex-wrap:wrap;gap:0.4rem;">'
            f'<div><span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r["a"]}</span>'
            f'<span style="color:#CC0000;margin:0 0.45rem;">&#8594;</span>'
            f'<span style="font-weight:900;font-size:0.93rem;color:#1A1A2E;">{r["b"]}</span></div>'
            f'<div style="display:flex;gap:0.38rem;flex-wrap:wrap;">'
            f'{pill(str(r["conf"]) + "% confidence","#FFE8E8","#CC0000","0.7rem")}'
            f'{pill(str(r["pct"]) + "% of orders","#E8ECFF","#3B4CCA","0.7rem")}'
            f'{pill(str(r["lift"]) + "x lift","#E8F5E9","#2E7D32","0.7rem")}'
            f'{pill("Seen " + str(r["count"]) + "x","#F3E5F5","#7B1FA2","0.7rem")}'
            f'</div></div>'
            f'<div style="background:#F0EEF8;border-radius:5px;height:6px;overflow:hidden;">'
            f'<div style="background:{color};height:6px;width:{bw}%;border-radius:5px;opacity:0.75;"></div>'
            f'</div></div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MENU & PRICING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Menu & Pricing":
    sec("Full Menu & Pricing","","🍽️")
    res = st.session_state.results

    foods  = [m for m in MENU if m["category"]=="Food"]
    sweets = [m for m in MENU if m["category"]=="Sweets"]
    drinks = [m for m in MENU if m["category"]=="Drinks"]
    avg_p  = int(sum(m["price"] for m in MENU)/len(MENU))

    c1,c2,c3,c4 = st.columns(4)
    for col, icon, label, val, sub, acc in [
        (c1,"🍔","Food",   str(len(foods)),  "Avg &#165;" + str(int(sum(m["price"] for m in foods)/len(foods))),"#E65100"),
        (c2,"🍰","Sweets", str(len(sweets)), "Avg &#165;" + str(int(sum(m["price"] for m in sweets)/len(sweets))),"#AD1457"),
        (c3,"🥤","Drinks", str(len(drinks)), "Avg &#165;" + str(int(sum(m["price"] for m in drinks)/len(drinks))),"#1565C0"),
        (c4,"💴","Avg Price","&#165;" + str(avg_p),"All items","#2E7D32"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;'
                f'padding:1.1rem 1.2rem;box-shadow:var(--shadow);border-left:6px solid {acc};">'
                f'<div style="font-size:1.6rem;margin-bottom:0.28rem;">{icon}</div>'
                f'<div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;'
                f'letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.85rem;'
                f'color:#1A1A2E;line-height:1;margin-bottom:0.22rem;">{val}</div>'
                f'<div style="font-size:0.71rem;color:#7B7B9A;font-weight:600;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True)

    fc1, fc2 = st.columns([1,1])
    with fc1: cat_f = st.selectbox("Category",["All","Food","Sweets","Drinks"])
    with fc2: sort_m = st.selectbox("Sort by",["Category","Price: Low to High","Price: High to Low","Name"])

    fm = MENU if cat_f=="All" else [m for m in MENU if m["category"]==cat_f]
    if   sort_m=="Price: Low to High":  fm = sorted(fm, key=lambda x: x["price"])
    elif sort_m=="Price: High to Low":  fm = sorted(fm, key=lambda x: x["price"], reverse=True)
    elif sort_m=="Name":                fm = sorted(fm, key=lambda x: x["name"])

    cur_cat = None
    for m in fm:
        if m["category"] != cur_cat:
            cur_cat = m["category"]
            ci = {"Food":"🍔","Sweets":"🍰","Drinks":"🥤"}[cur_cat]
            sec(f"{ci}  {cur_cat}","","")
        cc = CATEGORY_COLORS[m["category"]]
        sprite = POKEMON_SPRITES.get(m["pokemon"], POKEMON_SPRITES["pikachu"])
        order_count = res["item_counts"].get(m["name"]) if res else None
        in_combo    = res and any(m["name"] in [c["a"],c["b"]] for c in res["combos"])
        tags = badge(m["category"],cc["bg"],cc["fg"])
        if in_combo:    tags += "&nbsp;" + pill("In a combo","#E8F5E9","#2E7D32","0.68rem")
        if order_count: tags += "&nbsp;" + pill("Ordered " + str(order_count) + "x","#E8ECFF","#3B4CCA","0.68rem")
        st.markdown(
            f'<div style="background:#FFFFFF;border:1.5px solid {cc["border"]};border-radius:14px;'
            f'padding:0.9rem 1.3rem;margin-bottom:0.5rem;box-shadow:var(--shadow);">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:0.8rem;flex-wrap:wrap;">'
            f'<div style="display:flex;align-items:center;gap:0.85rem;flex:1;min-width:200px;">'
            f'<img src="{sprite}" style="width:46px;height:46px;object-fit:contain;">'
            f'<div>'
            f'<div style="font-weight:800;font-size:0.9rem;color:#1A1A2E;margin-bottom:0.1rem;">'
            f'{m["emoji"]} {m["name"]}</div>'
            f'<div style="font-size:0.74rem;color:#7B7B9A;font-weight:600;margin-bottom:0.26rem;">{m["desc"]}</div>'
            f'<div style="display:flex;gap:0.3rem;flex-wrap:wrap;">{tags}</div>'
            f'</div></div>'
            f'<div style="text-align:right;">'
            f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.5rem;color:#CC0000;">'
            f'&#165;{m["price"]:,}</div>'
            f'<div style="font-size:0.67rem;color:#7B7B9A;font-weight:600;">per item</div>'
            f'</div></div></div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA & ANALYSIS  (merged upload + run + log)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Data & Analysis":
    res = st.session_state.results

    # Status banner
    if res:
        st.markdown(
            f'<div style="background:linear-gradient(90deg,#1B3A1B,#1A2A1A);'
            f'border:1.5px solid #2E7D32;border-radius:18px;'
            f'padding:1rem 1.6rem;margin-bottom:1.2rem;">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.6rem;">'
            f'<div style="display:flex;align-items:center;gap:0.9rem;">'
            f'<span style="font-size:1.5rem;">✅</span>'
            f'<div>'
            f'<div style="font-family:\'Fredoka One\',cursive;font-size:1rem;color:#4CAF50;">'
            f'Dashboard is live — all pages show your real data</div>'
            f'<div style="font-size:0.75rem;color:#388E3C;font-weight:600;">'
            f'{res["n_txn"]:,} orders · {len(res["combos"])} combos · '
            f'{len(res["rules"])} patterns · Run {res["analysed_at"]}</div>'
            f'</div></div>'
            f'<div style="display:flex;gap:0.5rem;">'
            f'{pill(str(res["n_files"]) + " file(s) loaded","#1B3A1B","#4CAF50","0.75rem")}'
            f'{pill("All pages updated","#1B3A1B","#4CAF50","0.75rem")}'
            f'</div></div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:linear-gradient(90deg,#1A1A3E,#12102A);'
            'border:1.5px solid rgba(255,203,5,0.25);border-radius:18px;'
            'padding:1rem 1.6rem;margin-bottom:1.2rem;">'
            '<div style="font-family:\'Fredoka One\',cursive;font-size:1rem;color:#FFCB05;">'
            'Upload your sales CSV / Excel and click Run Analysis</div>'
            '<div style="font-size:0.75rem;color:#5A5A8A;font-weight:600;margin-top:0.2rem;">'
            'The system finds ordering patterns and populates every page with real data.</div></div>',
            unsafe_allow_html=True)

    col_up, col_run = st.columns([1.1, 1])

    with col_up:
        sec("Upload Sales Files","","📂")
        st.markdown(
            '<div style="background:#FFFFFF;border:2px dashed #E4DCFF;border-radius:18px;'
            'padding:1.5rem;text-align:center;box-shadow:var(--shadow);margin-bottom:0.7rem;">'
            '<div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>'
            '<div style="font-weight:800;font-size:0.95rem;color:#1A1A2E;margin-bottom:0.25rem;">'
            'Drop your sales file here</div>'
            '<div style="font-size:0.77rem;color:#7B7B9A;font-weight:600;">'
            'CSV or Excel · needs an Order ID column and an Item Name column</div></div>',
            unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose file",type=["csv","xlsx","xls"],
                                    label_visibility="collapsed",key="uploader")
        if uploaded:
            already = any(f["name"]==uploaded.name for f in st.session_state.files)
            fbytes  = uploaded.read()
            if not already:
                st.session_state.files.append({
                    "name":  uploaded.name,
                    "time":  datetime.now().strftime("%d %b %Y  %H:%M"),
                    "size":  f"{len(fbytes)/1024:.1f} KB",
                    "bytes": fbytes,
                })
                st.success(f"Added: {uploaded.name}")
            else:
                st.info(f"{uploaded.name} is already in the list.")

        if st.session_state.files:
            st.markdown(
                f'<div style="font-size:0.72rem;font-weight:800;text-transform:uppercase;'
                f'letter-spacing:0.08em;color:#7B7B9A;margin:0.9rem 0 0.4rem 0;">'
                f'Files queued ({len(st.session_state.files)})</div>',
                unsafe_allow_html=True)
            delete_idx = None
            for idx, f in enumerate(st.session_state.files):
                ext  = f["name"].split(".")[-1].upper()
                ec   = "#CC0000" if ext=="CSV" else "#2E7D32"
                fc1, fc2 = st.columns([1, 0.13])
                with fc1:
                    st.markdown(
                        f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:10px;'
                        f'padding:0.65rem 0.9rem;margin-bottom:0.35rem;">'
                        f'<div style="display:flex;align-items:center;gap:0.6rem;">'
                        f'<div style="background:{ec};color:white;font-size:0.55rem;'
                        f'font-weight:800;padding:0.18rem 0.42rem;border-radius:4px;">{ext}</div>'
                        f'<div>'
                        f'<div style="font-weight:800;font-size:0.84rem;color:#1A1A2E;">{f["name"]}</div>'
                        f'<div style="font-size:0.68rem;color:#7B7B9A;font-weight:600;">'
                        f'{f["time"]} · {f["size"]}</div>'
                        f'</div></div></div>',
                        unsafe_allow_html=True)
                with fc2:
                    if st.button("🗑️", key=f"del_{idx}", help="Remove"):
                        delete_idx = idx
            if delete_idx is not None:
                st.session_state.files.pop(delete_idx)
                st.rerun()

    with col_run:
        sec("Run Analysis","","⚡")
        if not st.session_state.files:
            st.markdown(
                '<div style="background:#F8F6FF;border:1.5px dashed #E4DCFF;border-radius:18px;'
                'padding:2rem;text-align:center;">'
                '<div style="font-size:2rem;margin-bottom:0.5rem;">⬅️</div>'
                '<div style="font-weight:700;color:#7B7B9A;font-size:0.88rem;">'
                'Upload at least one file first</div></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
                f'padding:1.2rem 1.4rem;box-shadow:var(--shadow);margin-bottom:0.9rem;">'
                f'<div style="font-weight:800;font-size:0.95rem;color:#1A1A2E;margin-bottom:0.35rem;">'
                f'Ready to analyse {len(st.session_state.files)} file(s)</div>'
                f'<div style="font-size:0.8rem;color:#7B7B9A;font-weight:600;line-height:1.6;">'
                f'Finds item pairs, builds combo deals, add-on tips and discount suggestions, '
                f'then updates every page instantly.</div></div>',
                unsafe_allow_html=True)

            run_btn = st.button("⚡  Run Analysis Now", use_container_width=True)

        log_placeholder = st.empty()

        def render_log():
            if not st.session_state.log:
                return
            lines = "\n".join(st.session_state.log[-30:])
            log_placeholder.markdown(
                f'<div style="background:#0D1117;border-radius:14px;padding:1rem 1.3rem;'
                f'font-family:monospace;font-size:0.73rem;color:#8B949E;'
                f'min-height:80px;max-height:280px;overflow-y:auto;'
                f'border:1.5px solid #21262D;white-space:pre-wrap;line-height:1.85;">'
                f'{lines}</div>',
                unsafe_allow_html=True)

        render_log()  # show previous log on page load

        if st.session_state.files and run_btn:
            st.session_state.log     = []
            st.session_state.results = None
            render_log()

            def log_fn(msg, kind="info"):
                icons = {"step":"🔵","ok":"✅","warn":"⚠️","error":"❌","done":"🎉","info":"   "}
                st.session_state.log.append(f"[{now_str()}]  {icons.get(kind,'   ')}  {msg}")
                render_log()

            with st.spinner("Analysing ..."):
                result = run_mba(st.session_state.files, log_fn)

            if result:
                st.session_state.results      = result
                st.session_state.data_version += 1
                st.markdown(
                    '<div style="background:#E8F5E9;border:1.5px solid #A5D6A7;'
                    'border-radius:18px;padding:1rem 1.3rem;margin-top:0.8rem;">'
                    '<div style="font-weight:900;font-size:0.95rem;color:#2E7D32;margin-bottom:0.2rem;">'
                    'Done! Every page is now showing your real data.</div>'
                    '<div style="font-size:0.82rem;color:#388E3C;font-weight:600;">'
                    'Use the sidebar to explore combos, patterns and deals.</div></div>',
                    unsafe_allow_html=True)
                st.rerun()
            else:
                st.error("Analysis failed — see the log for details.")

# ══════════════════════════════════════════════════════════════════════════════
#  ITEM MONITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Item Monitor":
    res = st.session_state.results
    if not res:
        no_data_banner(); st.stop()

    sec("Item Popularity From Your Data","","📡")
    st.markdown(
        f'<div style="font-size:0.85rem;color:#7B7B9A;font-weight:600;margin-bottom:1.1rem;line-height:1.6;">'
        f'Based on {res["n_txn"]:,} real orders · {res["n_files"]} file(s) · Run {res["analysed_at"]}</div>',
        unsafe_allow_html=True)

    pop = res["popularity"]
    c1, c2, c3 = st.columns(3)
    top_item = pop[0] if pop else {}
    for col, icon, label, val, sub, acc in [
        (c1,"🏆","Top Item",     top_item.get("item","—")[:22], str(top_item.get("pct",0)) + "% of orders","#CC0000"),
        (c2,"🍽️","Items Tracked", str(len(pop)),                "Found in your data","#3B4CCA"),
        (c3,"📦","Total Orders",  str(res["n_txn"]),             "All files combined","#2E7D32"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#FFFFFF;border:2px solid #E4DCFF;border-radius:18px;'
                f'padding:1.1rem 1.2rem;box-shadow:var(--shadow);border-left:6px solid {acc};">'
                f'<div style="font-size:1.6rem;margin-bottom:0.28rem;">{icon}</div>'
                f'<div style="font-size:0.64rem;font-weight:800;text-transform:uppercase;'
                f'letter-spacing:0.1em;color:#7B7B9A;margin-bottom:0.18rem;">{label}</div>'
                f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.5rem;'
                f'color:#1A1A2E;line-height:1.1;margin-bottom:0.22rem;">{val}</div>'
                f'<div style="font-size:0.71rem;color:#7B7B9A;font-weight:600;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True)

    sec("All Items Ranked","","📊")
    max_pct = pop[0]["pct"] if pop else 1
    rank_colors = ["#CC0000","#FF6F00","#FFCB05","#2E7D32","#3B4CCA","#7B1FA2","#00838F","#AD1457","#1565C0","#558B2F"]
    for i, p in enumerate(pop):
        bw     = int(p["pct"] / max_pct * 100)
        color  = rank_colors[min(i, len(rank_colors)-1)]
        sprite = POKEMON_SPRITES.get(p["pokemon"], POKEMON_SPRITES["pikachu"])
        rev    = "&#165;" + str(p["revenue"]) if p["revenue"] else "—"
        st.markdown(
            f'<div style="background:#FFFFFF;border:1.5px solid #E4DCFF;border-radius:18px;'
            f'padding:0.9rem 1.3rem;margin-bottom:0.5rem;box-shadow:var(--shadow);">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'margin-bottom:0.65rem;flex-wrap:wrap;gap:0.5rem;">'
            f'<div style="display:flex;align-items:center;gap:0.75rem;">'
            f'<div style="font-family:\'Fredoka One\',cursive;font-size:1.3rem;'
            f'color:{color};min-width:26px;text-align:center;">#{i+1}</div>'
            f'<img src="{sprite}" style="width:38px;height:38px;object-fit:contain;">'
            f'<div style="font-weight:800;font-size:0.92rem;color:#1A1A2E;">'
            f'{p["emoji"]} {p["item"]}</div></div>'
            f'<div style="display:flex;gap:0.6rem;align-items:center;">'
            f'{pill(str(p["count"]) + " orders","#E8ECFF","#3B4CCA","0.72rem")}'
            f'{pill(str(p["pct"]) + "% share","#FFE8E8","#CC0000","0.72rem")}'
            f'<div style="font-family:\'Fredoka One\',cursive;font-size:1rem;color:#2E7D32;">{rev}</div>'
            f'</div></div>'
            f'<div style="background:#F0EEF8;border-radius:5px;height:7px;overflow:hidden;">'
            f'<div style="background:{color};height:7px;width:{bw}%;border-radius:5px;opacity:0.8;"></div>'
            f'</div></div>',
            unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    if st.button("Re-run Analysis With New Data"):
        st.session_state.page = "Data & Analysis"
        st.rerun()
