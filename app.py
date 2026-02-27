import streamlit as st
from openai import OpenAI
import httpx

st.set_page_config(page_title="GrokRepurpose.ai", page_icon="🚀", layout="wide")
st.title("🚀 GrokRepurpose.ai")
st.markdown("**1 langer Text → 30+ virale Posts in Sekunden mit Grok**")

# Sidebar für API-Key
with st.sidebar:
    st.header("🔑 Dein xAI API-Key (Free Tier)")
    api_key = st.text_input("xAI Key von console.x.ai", type="password")
    st.caption("Kostenlos hier holen: [console.x.ai](https://console.x.ai)")
st.divider()
st.header("⭐ Pro (9 €/Monat – kein Key nötig)")
if st.button("Jetzt upgraden"):
    import stripe
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': 'your_price_id_here', 'quantity': 1}],  # Ersetze mit deiner Stripe Price-ID
            mode='subscription',
            success_url='https://grokrepurpose-ai.streamlit.app/?success=true',
            cancel_url='https://grokrepurpose-ai.streamlit.app/'
        )
        st.markdown(f'<meta http-equiv="refresh" content="0; url={session.url}">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
content = st.text_area("Paste deinen Blog, Transcript oder Notizen hier", height=300)

formats = st.multiselect("Was soll erstellt werden?", 
    ["X/Twitter Thread", "LinkedIn Post", "10 Instagram Captions", "Email Newsletter", "YouTube Shorts Scripts", "SEO Summary"],
    default=["X/Twitter Thread", "LinkedIn Post"])

if st.button("✨ Jetzt mit Grok repurposen", type="primary", use_container_width=True):
    if not api_key:
        st.error("Bitte xAI API-Key eingeben!")
        st.stop()
    if not content:
        st.error("Inhalt fehlt!")
        st.stop()

    with st.spinner("Grok arbeitet (10–60 Sekunden)..."):
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=httpx.Timeout(60.0)
        )
        
        prompt = f"""Du bist der beste Content-Repurposer der Welt (Grok-Stil: witzig, direkt, viral).
Inhalt: {content}

Erstelle exakt diese Formate:
{'\n'.join('- ' + f for f in formats)}

Jedes Format mit klarer Überschrift trennen."""

        response = client.chat.completions.create(
            model="grok-4-1-fast-reasoning",  # Aktuelles Model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content

    st.success("✅ Fertig!")
    st.markdown(result)
    st.download_button("📥 Als TXT herunterladen", result, "grok_repurposed.txt")
