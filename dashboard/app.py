import json
import os
import secrets
import time
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import requests
from flask import Flask, redirect, render_template, request, session, url_for

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
load_dotenv(os.path.join(ROOT, "stack.env"))
DATA = os.path.join(ROOT, "data", "rovix.json")
app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SESSION_SECRET", secrets.token_hex(32))
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:3478/auth/callback")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("BOT_TOKEN", "")
BOT_PERMISSIONS = os.getenv("DISCORD_BOT_PERMISSIONS", "8")
API = "https://discord.com/api/v10"
SERVER_CACHE = {}
SERVER_CACHE_TTL = 15

def discord(path, token, method="GET", **kwargs):
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = token
    return requests.request(method, API + path, headers=headers, timeout=15, **kwargs)

def guilds():
    r = discord("/users/@me/guilds", "Bearer " + session["token"])
    if r.status_code != 200:
        session.clear()
        return []
    return r.json()

def admin(guild):
    return guild.get("owner") or (int(guild.get("permissions", "0")) & 8) == 8

def bot_in(guild_id):
    if not BOT_TOKEN:
        return False
    return discord("/guilds/" + guild_id, "Bot " + BOT_TOKEN).status_code == 200

def discord_json(path):
    response = discord(path, "Bot " + BOT_TOKEN)
    if response.status_code != 200:
        return None, response.status_code, response.text[:500]
    try:
        value = response.json()
    except ValueError:
        return None, 502, "Discord returned invalid JSON"
    return value, 200, ""

def server_data(guild_id):
    cached = SERVER_CACHE.get(guild_id)
    if cached and time.monotonic() - cached[0] < SERVER_CACHE_TTL:
        return cached[1], cached[2], 200, 200, ""

    paths = [
        "/guilds/" + guild_id + "/channels",
        "/guilds/" + guild_id + "/roles",
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(discord_json, paths))

    channels, channel_status, channel_error = results[0]
    roles, role_status, role_error = results[1]
    SERVER_CACHE[guild_id] = (time.monotonic(), channels, roles)
    return channels, roles, channel_status, role_status, channel_error or role_error

def data():
    try:
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

def save(value):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA)

@app.get("/")
def index():
    if "token" not in session:
        return redirect(url_for("login"))
    visible = [g for g in guilds() if admin(g)]
    with ThreadPoolExecutor(max_workers=8) as executor:
        installed = executor.map(lambda g: bot_in(g["id"]), visible)
        visible = [{**g, "installed": is_installed} for g, is_installed in zip(visible, installed)]
    return render_template("index.html", user=session["user"], guilds=visible,
                           client_id=CLIENT_ID, permissions=BOT_PERMISSIONS)

@app.get("/login")
def login():
    params = {"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI,
              "response_type": "code", "scope": "identify guilds"}
    return redirect("https://discord.com/oauth2/authorize?" + urlencode(params))

@app.get("/auth/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("login"))
    r = requests.post(API + "/oauth2/token", data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT_URI
    }, timeout=15)
    r.raise_for_status()
    token = r.json()["access_token"]
    u = discord("/users/@me", "Bearer " + token)
    u.raise_for_status()
    session.clear()
    session["token"] = token
    session["user"] = u.json()
    return redirect(url_for("index"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/server/<guild_id>")
def server(guild_id):
    if "token" not in session:
        return redirect(url_for("login"))
    owned = next((g for g in guilds() if g["id"] == guild_id and admin(g)), None)
    if not owned:
        return redirect(url_for("index"))
    channels, roles, channel_status, role_status, error = server_data(guild_id)
    if channel_status != 200 or role_status != 200:
        return render_template("error.html", title="Discord API error", message=error or "Rovix could not read this server."), 502
    if not isinstance(channels, list) or not isinstance(roles, list):
        return render_template("error.html", title="Invalid Discord response", message="Discord returned an unexpected server structure."), 502
    return render_template("server.html", guild=owned, config=data().get(guild_id, {}), channels=channels, roles=roles)

@app.post("/server/<guild_id>")
def update(guild_id):
    if "token" not in session:
        return redirect(url_for("login"))
    if not any(g["id"] == guild_id and admin(g) for g in guilds()) or not bot_in(guild_id):
        return "Forbidden", 403
    all_data = data()
    config = all_data.setdefault(guild_id, {})
    automod = config.setdefault("automod", {})
    for key in ("links", "invites", "spam", "mentions", "caps"):
        automod[key] = request.form.get(key) == "on"
    tickets = config.setdefault("tickets", {})
    for key in ("category_id", "support_role_id"):
        value = request.form.get(key)
        tickets[key] = int(value) if value and value.isdigit() else None
    logging = config.setdefault("logging", {})
    value = request.form.get("logging_channel_id")
    logging["channel_id"] = int(value) if value and value.isdigit() else None
    save(all_data)
    return redirect(url_for("server", guild_id=guild_id, saved="1"))

if __name__ == "__main__":
    app.run("0.0.0.0", int(os.getenv("DASHBOARD_PORT", "3478")))

