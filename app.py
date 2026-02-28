import streamlit as st
from openai import OpenAI
import httpx
from PyPDF2 import PdfReader
import tweepy
from requests_oauthlib import OAuth1Session
import facebook
import requests

st.set_page_config(page_title="GrokRepurpose.ai", page_icon="🚀", layout="wide")
st.title("🚀 GrokRepurpose.ai")
st.markdown("**1 langer Text → 30+ virale Posts in Sekunden mit Grok**")

# Sidebar
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
                line_items=[{'price': 'your_price_id', 'quantity': 1}],  # Ersetze mit deiner Stripe Price-ID
                mode='subscription',
                success_url='https://grokrepurpose-ai.streamlit.app/?success=true',
                cancel_url='https://grokrepurpose-ai.streamlit.app/'
            )
            st.markdown(f'<meta http-equiv="refresh" content="0; url={session.url}">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.divider()
    st.header("Social Accounts verbinden")
    # Twitter
    TWITTER_API_KEY = "your_twitter_api_key"  # Aus developer.twitter.com
    TWITTER_API_SECRET = "your_twitter_api_secret"
    if st.button("Twitter verbinden"):
        oauth = OAuth1Session(TWITTER_API_KEY, client_secret=TWITTER_API_SECRET)
        fetch_response = oauth.fetch_request_token('https://api.twitter.com/oauth/request_token?oauth_callback=https://grokrepurpose-ai.streamlit.app')
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')
        authorization_url = oauth.authorization_url('https://api.twitter.com/oauth/authorize')
        st.markdown(f'[Twitter verbinden]({authorization_url})')
        st.session_state['twitter_resource_owner_key'] = resource_owner_key
        st.session_state['twitter_resource_owner_secret'] = resource_owner_secret

    if 'oauth_verifier' in st.experimental_get_query_params():
        verifier = st.experimental_get_query_params()['oauth_verifier'][0]
        oauth = OAuth1Session(TWITTER_API_KEY, client_secret=TWITTER_API_SECRET,
                              resource_owner_key=st.session_state['twitter_resource_owner_key'],
                              resource_owner_secret=st.session_state['twitter_resource_owner_secret'],
                              verifier=verifier)
        oauth_tokens = oauth.fetch_access_token('https://api.twitter.com/oauth/access_token')
        st.session_state['twitter_access_token'] = oauth_tokens['oauth_token']
        st.session_state['twitter_access_secret'] = oauth_tokens['oauth_token_secret']
        st.success("Twitter verbunden!")

    # Facebook/Instagram
    FACEBOOK_APP_ID = "your_facebook_app_id"  # Aus developers.facebook.com
    FACEBOOK_APP_SECRET = "your_facebook_app_secret"
    if st.button("Facebook/Instagram verbinden"):
        dialog_url = f"https://www.facebook.com/v20.0/dialog/oauth?client_id={FACEBOOK_APP_ID}&redirect_uri=https://grokrepurpose-ai.streamlit.app&scope=publish_to_groups,pages_manage_posts,instagram_basic,instagram_content_publish"
        st.markdown(f'[Facebook/Instagram verbinden]({dialog_url})')

    if 'code' in st.experimental_get_query_params():
        code = st.experimental_get_query_params()['code'][0]
        access_url = f"https://graph.facebook.com/v20.0/oauth/access_token?client_id={FACEBOOK_APP_ID}&client_secret={FACEBOOK_APP_SECRET}&redirect_uri=https://grokrepurpose-ai.streamlit.app&code={code}"
        response = requests.get(access_url)
        if 'access_token' in response.json():
            st.session_state['facebook_access_token'] = response.json()['access_token']
            st.success("Facebook/Instagram verbunden!")
        else:
            st.error("Fehler bei Verbindung")

# Hauptbereich
content = st.text_area("Paste deinen Blog, Transcript oder Notizen hier", height=300)

uploaded_file = st.file_uploader("Lade eine Datei hoch (Bild oder PDF)", type=["jpg", "png", "pdf"])
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() + "\n"
        content += extracted_text
        st.write("Text aus PDF extrahiert!")
    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        st.image(uploaded_file, caption="Hochgeladenes Bild")
        st.session_state['uploaded_image'] = uploaded_file.getvalue()  # Bytes für Posting

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
            model="grok-4-1-fast-reasoning",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content

    st.success("✅ Fertig!")
    st.markdown(result)
    st.download_button("📥 Als TXT herunterladen", result, "grok_repurposed.txt")
    st.session_state['result'] = result

# Posting auf Social (mit Bild, wenn hochgeladen)
if 'result' in st.session_state:
    result = st.session_state['result']
    uploaded_image = st.session_state.get('uploaded_image', None)
    
    if st.session_state.get('twitter_access_token'):
        if st.button("Auf Twitter posten"):
            auth = tweepy.OAuth1UserHandler("your_twitter_api_key", "your_twitter_api_secret", st.session_state['twitter_access_token'], st.session_state['twitter_access_secret'])
            api = tweepy.API(auth)
            if uploaded_image:
                api.update_status_with_media(status=result, filename="image.jpg", file=uploaded_image)
            else:
                api.update_status(status=result)
            st.success("Auf Twitter gepostet!")

    if st.session_state.get('facebook_access_token'):
        if st.button("Auf Facebook posten"):
            graph = facebook.GraphAPI(st.session_state['facebook_access_token'])
            graph.put_object("me", "feed", message=result)
            st.success("Auf Facebook gepostet!")

        if st.button("Auf Instagram posten"):
            graph = facebook.GraphAPI(st.session_state['facebook_access_token'])
            instagram_id = "your_instagram_business_id"  # Ersetze mit deiner ID
            if uploaded_image:
                media = graph.post(path=f"{instagram_id}/media", caption=result, image_url=uploaded_image)  # Für Image-Posts
                publish = graph.post(path=f"{instagram_id}/media_publish", creation_id=media['id'])
                st.success("Auf Instagram gepostet!")
            else:
                st.error("Bild erforderlich für Instagram!")
