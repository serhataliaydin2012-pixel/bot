import json
import os
import re
import threading
from datetime import timedelta
from pathlib import Path

import discord
from discord.ext import commands
from flask import Flask, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
WARNINGS_PATH = BASE_DIR / "warnings.json"

DEFAULT_CONFIG = {
    "banned_words": [],
    "warning_limit": 3,
    "timeout_minutes": 10,
    "log_channel_id": "",
    "ignore_admins": True,
}


def load_json(path, default):
    if not path.exists():
        save_json(path, default)
        return default.copy()

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = default.copy()

    return {**default, **data} if isinstance(default, dict) else data


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def normalize_text(text):
    text = text.lower()
    replacements = str.maketrans({
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "ü": "u",
        "ş": "s",
        "ç": "c",
        "ğ": "g",
    })
    text = text.translate(replacements)
    return re.sub(r"[^a-z0-9]", "", text)


def contains_banned_word(message_text, banned_words):
    normalized_message = normalize_text(message_text)

    for word in banned_words:
        normalized_word = normalize_text(word)
        if normalized_word and normalized_word in normalized_message:
            return word

    return None


config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
warnings = load_json(WARNINGS_PATH, {})

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)
app.secret_key = os.getenv("PANEL_SECRET", "change-this-secret")


def panel_password():
    return os.getenv("PANEL_PASSWORD", "admin123")


def is_logged_in():
    return session.get("logged_in") is True


@app.route("/", methods=["GET"])
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    current_config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    warning_data = load_json(WARNINGS_PATH, {})
    total_warnings = sum(warning_data.values()) if warning_data else 0

    return render_template(
        "dashboard.html",
        config=current_config,
        total_warnings=total_warnings,
        bot_name=str(bot.user) if bot.user else "Bot aciliyor",
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        if request.form.get("password") == panel_password():
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Panel sifresi yanlis."

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/settings", methods=["POST"])
def update_settings():
    if not is_logged_in():
        return redirect(url_for("login"))

    current_config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    current_config["warning_limit"] = max(1, int(request.form.get("warning_limit", 3)))
    current_config["timeout_minutes"] = max(1, int(request.form.get("timeout_minutes", 10)))
    current_config["log_channel_id"] = request.form.get("log_channel_id", "").strip()
    current_config["ignore_admins"] = request.form.get("ignore_admins") == "on"
    save_json(CONFIG_PATH, current_config)
    refresh_config()

    return redirect(url_for("dashboard"))


@app.route("/words/add", methods=["POST"])
def add_word():
    if not is_logged_in():
        return redirect(url_for("login"))

    word = request.form.get("word", "").strip()
    current_config = load_json(CONFIG_PATH, DEFAULT_CONFIG)

    if word and word not in current_config["banned_words"]:
        current_config["banned_words"].append(word)
        current_config["banned_words"].sort(key=str.lower)
        save_json(CONFIG_PATH, current_config)
        refresh_config()

    return redirect(url_for("dashboard"))


@app.route("/words/delete", methods=["POST"])
def delete_word():
    if not is_logged_in():
        return redirect(url_for("login"))

    word = request.form.get("word", "")
    current_config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    current_config["banned_words"] = [
        item for item in current_config["banned_words"] if item != word
    ]
    save_json(CONFIG_PATH, current_config)
    refresh_config()

    return redirect(url_for("dashboard"))


@app.route("/warnings/clear", methods=["POST"])
def clear_warnings():
    if not is_logged_in():
        return redirect(url_for("login"))

    save_json(WARNINGS_PATH, {})
    warnings.clear()

    return redirect(url_for("dashboard"))


def refresh_config():
    global config
    config = load_json(CONFIG_PATH, DEFAULT_CONFIG)


async def send_log(message, matched_word, warning_count):
    log_channel_id = str(config.get("log_channel_id", "")).strip()
    if not log_channel_id.isdigit():
        return

    channel = bot.get_channel(int(log_channel_id))
    if not channel:
        return

    await channel.send(
        "Kufur engellendi.\n"
        f"Kullanici: {message.author.mention}\n"
        f"Kanal: {message.channel.mention}\n"
        f"Yakalanan kelime: `{matched_word}`\n"
        f"Uyari sayisi: `{warning_count}`"
    )


@bot.event
async def on_ready():
    print(f"{bot.user} olarak giris yapildi.")


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    if config.get("ignore_admins", True):
        permissions = message.author.guild_permissions
        if permissions.administrator or permissions.manage_messages:
            await bot.process_commands(message)
            return

    matched_word = contains_banned_word(message.content, config.get("banned_words", []))
    if not matched_word:
        await bot.process_commands(message)
        return

    try:
        await message.delete()
    except discord.Forbidden:
        await message.channel.send(
            "Mesaji silemedim. Bana `Mesajlari Yonet` izni vermen gerekiyor.",
            delete_after=8,
        )
        return

    user_key = f"{message.guild.id}:{message.author.id}"
    warnings[user_key] = warnings.get(user_key, 0) + 1
    save_json(WARNINGS_PATH, warnings)

    warning_count = warnings[user_key]
    warning_limit = int(config.get("warning_limit", 3))
    timeout_minutes = int(config.get("timeout_minutes", 10))

    await message.channel.send(
        f"{message.author.mention}, bu sunucuda kufur yasak. "
        f"Uyari: {warning_count}/{warning_limit}",
        delete_after=7,
    )

    if warning_count >= warning_limit:
        try:
            await message.author.timeout(
                timedelta(minutes=timeout_minutes),
                reason="Kufur filtresi uyari limiti doldu.",
            )
            warnings[user_key] = 0
            save_json(WARNINGS_PATH, warnings)
            await message.channel.send(
                f"{message.author.mention} {timeout_minutes} dakika susturuldu.",
                delete_after=8,
            )
        except discord.Forbidden:
            await message.channel.send(
                "Timeout atamadim. Bot rolunu kullanici rollerinin ustune tasimayi dene.",
                delete_after=8,
            )

    await send_log(message, matched_word, warning_count)


@bot.command(name="panel")
@commands.has_permissions(administrator=True)
async def panel_command(ctx):
    public_url = os.getenv("PUBLIC_URL", "Render adresini PUBLIC_URL olarak ekleyebilirsin.")
    await ctx.reply(f"Web panel: {public_url}")


def run_web_panel():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN ortam degiskeni eksik.")

    threading.Thread(target=run_web_panel, daemon=True).start()
    bot.run(token)
