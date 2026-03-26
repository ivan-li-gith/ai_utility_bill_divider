from flask import g
from werkzeug.local import LocalProxy
from supabase.client import Client, ClientOptions
from src.app.core.flask_storage import FlaskSessionStorage
from config import Config

url = Config.SUPABASE_URL
key = Config.SUPABASE_KEY

def get_supabase() -> Client:
    if "supabase" not in g:
        g.supabase = Client(
            url,
            key,
            options=ClientOptions(
                storage=FlaskSessionStorage(),
                flow_type="pkce"
            ),
        )
    return g.supabase

supabase: Client = LocalProxy(get_supabase)