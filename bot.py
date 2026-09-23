from pyrogram import Client, filters
import os
import time


async def progress(current, total, message, action):
    now = time.time()

    if not hasattr(progress, "last"):
        progress.last = 0

    if not hasattr(progress, "start"):
        progress.start = now

    if now - progress.last < 2 and current != total:
        return

    progress.last = now

    if total <= 0:
        return

    percent = current * 100 / total

    elapsed = now - progress.start

    if elapsed > 0:
        speed = current / elapsed
    else:
        speed = 0

    remaining = total - current

    if speed > 0:
        eta = remaining / speed
    else:
        eta = 0

    def size_format(size):
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        elif size >= 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size:.0f} B"

    if eta < 60:
        eta_text = f"{eta:.0f}s"
    else:
        eta_text = f"{eta / 60:.1f}m"

    bar_length = 20
    filled = int(bar_length * percent / 100)

    bar = "█" * filled + "░" * (bar_length - filled)

    await message.edit_text(
        f"{action}\n\n"
        f"{bar} {percent:.1f}%\n\n"
        f"📦 {size_format(current)} / {size_format(total)}\n"
        f"⚡ Speed: {size_format(speed)}/s\n"
        f"⏱️ ETA: {eta_text}"
    )


API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID", "8461488979"))

THUMB = "thumbs/thumbnail.jpg"
DOWNLOAD_DIR = "downloads"


# Folders create
os.makedirs(os.path.dirname(THUMB), exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


app = Client(
    "thumbnail_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ================= START =================

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 Hello!\n\n"
        "📹 मुझे Video भेजो।\n"
        "🖼️ मैं Custom Thumbnail के साथ वापस भेजूँगा।"
    )


# ================= MY ID =================

@app.on_message(filters.command("myid"))
async def my_id(client, message):
    await message.reply_text(
        f"🆔 Your Telegram ID:\n\n{message.from_user.id}"
    )


# ================= SET THUMB =================

@app.on_message(filters.command("setthumb"))
async def set_thumb_command(client, message):

    if message.from_user.id != OWNER_ID:
        await message.reply_text(
            "❌ आपको Thumbnail बदलने की permission नहीं है."
        )
        return

    await message.reply_text(
        "🖼️ नया Thumbnail भेजो.\n\n"
        "JPG या PNG image भेज सकते हो."
    )


# ================= HELP =================

@app.on_message(filters.command("help"))
async def help_command(client, message):

    await message.reply_text(
        "🤖 Thumbnail Bot Commands\n\n"
        "📤 Video/File भेजें\n"
        "🖼️ /setthumb - नया Thumbnail सेट करें\n"
        "👀 /showthumb - Current Thumbnail देखें\n"
        "🗑️ /delthumb - Thumbnail Delete करें\n"
        "📊 /status - Bot का Status देखें\n"
        "🆔 /myid - अपना Telegram ID देखें\n"
        "❓ /help - Commands की जानकारी"
    )

@app.on_message(filters.command("status"))
async def status_command(client, message):

    if message.from_user.id != OWNER_ID:
        await message.reply_text(
            "❌ यह command केवल Owner के लिए है."
        )
        return

    if os.path.isfile(THUMB):
        thumb_status = "✅ Custom Thumbnail Set है"
    else:
        thumb_status = "❌ कोई Thumbnail Set नहीं है"

    await message.reply_text(
        "🤖 Bot Status\n\n"
        "🟢 Bot: Running\n"
        f"🖼️ Thumbnail: {thumb_status}\n"
        f"👤 Owner ID: `{OWNER_ID}`"
    )

# ================= SHOW THUMB =================

@app.on_message(filters.command("showthumb"))
async def show_thumb(client, message):

    if not os.path.isfile(THUMB):
        await message.reply_text(
            "❌ अभी कोई Thumbnail सेट नहीं है."
        )
        return

    await client.send_photo(
        chat_id=message.chat.id,
        photo=THUMB,
        caption="🖼️ Current Custom Thumbnail"
    )


# ================= DELETE THUMB =================

@app.on_message(filters.command("delthumb"))
async def delete_thumb(client, message):

    if message.from_user.id != OWNER_ID:
        await message.reply_text(
            "❌ आपको Thumbnail delete करने की permission नहीं है."
        )
        return

    if not os.path.isfile(THUMB):
        await message.reply_text(
            "❌ अभी कोई Thumbnail सेट नहीं है."
        )
        return

    try:
        os.remove(THUMB)

        await message.reply_text(
            "🗑️ Thumbnail Successfully Deleted!\n\n"
            "अब कोई Custom Thumbnail सेट नहीं है."
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Thumbnail Delete Error:\n\n{e}"
        )


# ================= RECEIVE THUMB =================

@app.on_message(filters.photo)
async def receive_thumbnail(client, message):

    if message.from_user.id != OWNER_ID:
        return

    try:

        if os.path.exists(THUMB):
            os.remove(THUMB)

        await message.download(
    file_name=THUMB
)

        await message.reply_text(
            "✅ Thumbnail Successfully Updated! 🖼️\n\n"
            "अब नया Thumbnail Video/File में लगेगा."
        )

    except Exception as e:

        await message.reply_text(
            f"❌ Thumbnail Update Error:\n\n{e}"
        )


# ================= VIDEO HANDLER =================

@app.on_message(filters.video)
async def video_handler(client, message):

    status = await message.reply_text(
        "📥 Video Download हो रहा है..."
    )

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"video_{message.id}.mp4"
    )

    try:

        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(file_path + ".temp"):
            os.remove(file_path + ".temp")

        await client.download_media(
    message,
    file_name=file_path,
    progress=progress,
    progress_args=(status, "📥 Video Download हो रहा है...")
)

        if os.path.isfile(THUMB):

            await status.edit_text(
                "📤 Thumbnail के साथ Upload हो रहा है..."
            )

            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                thumb=THUMB,
                    progress=progress,
    progress_args=(status, "📤 Video Upload हो रहा है..."),
                caption=(
                    f"📁 {os.path.basename(file_path)}\n\n"
                    "🖼️ Custom Thumbnail"
                )
            )

        else:

            await status.edit_text(
                "📤 Normal Video Upload हो रहा है..."
            )

            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                progress=progress,
progress_args=(status, "📤 Video Upload हो रहा है..."),
                caption=(
                    f"📁 {os.path.basename(file_path)}\n\n"
                    "📤 Uploaded without Thumbnail"
                )
            )

        await status.delete()

    except Exception as e:

        await status.edit_text(
            f"❌ Error:\n\n{e}"
        )

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)


# ================= DOCUMENT HANDLER =================

@app.on_message(filters.document)
async def document_handler(client, message):

    status = await message.reply_text(
        "📥 File Download हो रही है..."
    )

    file_name = message.document.file_name

    if not file_name:
        file_name = f"file_{message.id}"

    file_path = os.path.join(
        DOWNLOAD_DIR,
        file_name
    )

    try:

        # Same file पहले से मौजूद है तो हटाओ
        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(file_path + ".temp"):
            os.remove(file_path + ".temp")


        # File download
        await client.download_media(
    message,
    file_name=file_path,
    progress=progress,
    progress_args=(status, "📥 File Download हो रही है...")
)


        # Thumbnail check
        if not os.path.isfile(THUMB):

            await status.edit_text(
                "❌ Thumbnail नहीं मिला!\n\n"
                f"Check करो:\n{THUMB}"
            )

            return


        await status.edit_text(
            "📤 Thumbnail के साथ File Upload हो रही है..."
        )


        # File + Thumbnail
        await client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            progress=progress,
progress_args=(status, "📤 File Upload हो रही है..."),
            thumb=THUMB,
            caption=(
                f"📁 {os.path.basename(file_path)}\n\n"
                "🖼️ Custom Thumbnail"
            )
        )


        await status.delete()


    except Exception as e:

        await status.edit_text(
            f"❌ Error:\n\n{e}"
        )


    finally:

        if os.path.exists(file_path):
            os.remove(file_path)


# ================= RUN BOT =================

print("🤖 Bot Started...")

app.run()
