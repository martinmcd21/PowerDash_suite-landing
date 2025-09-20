import json
import urllib.parse as up
from typing import List, Dict

import streamlit as st

st.set_page_config(page_title="PowerDash HR — AI Tools", page_icon="⚡️", layout="wide")

# ---------- Theming & CSS ----------
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap"
st.markdown(f"<link href='{GOOGLE_FONTS}' rel='stylesheet'>", unsafe_allow_html=True)

st.markdown(
    """
<style>
:root{
  --brand:#111827;
  --chip:#ffe58f;
}
html, body, [class*="css"], textarea, input{
  font-family:'Source Sans 3', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif !important;
}
.hero { display:flex; align-items:center; gap:1rem; margin-bottom:1rem; }
.app-card{
  border:1px solid rgba(0,0,0,.08); border-radius:16px; padding:18px; height:100%;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.footer{
  margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(0,0,0,.08); text-align:center; opacity:.85;
}
.brand-chip{
  display:inline-flex; align-items:center; gap:.5rem; padding:.25rem .5rem; border-radius:999px;
  background:#fffbe6; border:1px solid var(--chip);
}
.logo-row { display:flex; gap:14px; justify-content:flex-end; align-items:center; }
.logo-row img { max-height:40px; border-radius:8px; background:white; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Default apps ----------
DEFAULT_APPS = [
    {
        "name": "Job Description Generator",
        "slug": "jd-generator",
        "url": "https://powerdash-job-description-generator-uxpd5q5mwglnlg2lassxar.streamlit.app",
        "desc": "Create clean, inclusive JDs from a brief or refine drafts. Export to DOCX/MD.",
        "emoji": "📝",
    },
    {
        "name": "Interview Question Template",
        "slug": "iqt",
        "url": "",
        "desc": "Generate structured interview packs tailored to the role and seniority.",
        "emoji": "❓",
    },
    {
        "name": "Job Ad Generator",
        "slug": "job-ad",
        "url": "",
        "desc": "Turn a JD into a compelling, on-brand job advertisement for boards and LinkedIn.",
        "emoji": "📣",
    },
    {
        "name": "Policy Generator",
        "slug": "policy",
        "url": "",
        "desc": "Draft HR policies with your jurisdiction and house style as guardrails.",
        "emoji": "📄",
    },
    {
        "name": "Hiring Manager Toolkit",
        "slug": "hmt",
        "url": "",
        "desc": "Auto-assemble core docs for a vacancy: intake brief, scorecards, comms, etc.",
        "emoji": "🧰",
    },
    {
        "name": "Interview Feedback Collector",
        "slug": "feedback",
        "url": "",
        "desc": "Collect structured panel feedback and export summaries to share with TA.",
        "emoji": "🗒️",
    },
]

def get_apps() -> List[Dict]:
    """Load tiles from Streamlit Secrets if provided, else use defaults."""
    data = DEFAULT_APPS
    try:
        if "APPS_JSON" in st.secrets:
            data = json.loads(st.secrets["APPS_JSON"])
        elif "APPS" in st.secrets:
            raw = st.secrets["APPS"]
            if isinstance(raw, dict):
                data = [raw[k] for k in sorted(raw.keys())]
            elif isinstance(raw, list):
                data = raw
    except Exception:
        pass
    return data

# ---------- Tenant + logo context via query params / secrets ----------
q = st.query_params.to_dict()
tenant = q.get("tenant", [""])[0] if isinstance(q.get("tenant"), list) else q.get("tenant", "")
client_logo_qp = q.get("logo", [""])[0] if isinstance(q.get("logo"), list) else q.get("logo", "")
pd_logo_qp = q.get("pd_logo", [""])[0] if isinstance(q.get("pd_logo"), list) else q.get("pd_logo", "")

# Prefer query params, else Secrets, else local asset for PD logo
client_logo_url = client_logo_qp or st.secrets.get("CLIENT_LOGO_URL", "")
powerdash_logo_url = pd_logo_qp or st.secrets.get("POWERDASH_LOGO_URL", "")

# ---------- Header with right-aligned logos ----------
left, right = st.columns([0.72, 0.28], vertical_alignment="center")

with left:
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    title = "PowerDash HR — AI Tools"
    if tenant:
        title += f" · {tenant}"
    st.markdown(f"### {title}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Your central hub for PowerDash HR white-label apps. Use the tiles below to launch each tool.")

with right:
    # Render client logo (if any) and PowerDash logo (URL or local asset)
    logos_html = "<div class='logo-row'>"
    if client_logo_url:
        logos_html += f"<img src='{client_logo_url}' alt='Client logo'/>"
    if powerdash_logo_url:
        logos_html += f"<img src='{powerdash_logo_url}' alt='PowerDash HR'/>"
    else:
        # fallback to local asset path if present
        # (Streamlit can serve repo image files via st.image, but for layout we use markdown)
        try:
            # Try to show local asset via st.image if URL not supplied
            st.image("assets/powerdash-logo.png", width=140)
            logos_html = ""  # we already placed an image
        except Exception:
            # If asset missing, render nothing
            pass
    logos_html += "</div>"
    if logos_html != "</div>":
        st.markdown(logos_html, unsafe_allow_html=True)

# ---------- Grid of apps ----------
apps = get_apps()
cols = st.columns(3)

for i, app in enumerate(apps):
    with cols[i % 3]:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown(f"**{app.get('emoji','')} {app['name']}**")
        st.write(app["desc"])

        url = app.get("url") or ""
        label_suffix = app.get("slug") or str(i)

        if url:
            # Append tenant params to child app URL if present
            if tenant or client_logo_url:
                sep = "&" if "?" in url else "?"
                qp = {}
                if tenant: qp["tenant"] = tenant
                if client_logo_url: qp["logo"] = client_logo_url
                url = url + sep + up.urlencode(qp)

            # unique label (no key arg needed)
            st.link_button(f"Open · {label_suffix}", url, use_container_width=True)
        else:
            st.button(f"Add URL in settings · {label_suffix}",
                      disabled=True, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown(
    """
<div class='footer'>
  <span class='brand-chip'>⚡️ Powered by <strong>PowerDash HR</strong></span>
</div>
""",
    unsafe_allow_html=True,
)
