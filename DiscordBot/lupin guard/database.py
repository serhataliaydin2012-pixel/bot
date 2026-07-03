import sqlite3

db = sqlite3.connect("data/database.db")

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS guild_settings (

    guild_id INTEGER PRIMARY KEY,

    log_channel INTEGER DEFAULT 0,

    welcome_channel INTEGER DEFAULT 0,

    automod INTEGER DEFAULT 1,

    invite_filter INTEGER DEFAULT 1,

    link_filter INTEGER DEFAULT 0,

    caps_filter INTEGER DEFAULT 0,

    spam_filter INTEGER DEFAULT 0

)
""")

db.commit()