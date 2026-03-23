from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.exceptions import NotInCallError
import yt_dlp
import asyncio

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
BOT_TOKEN = "8421035286:AAHNFAIgzmBESZTkk7ErPz1-DH2FkWRUSWs" # <- Yahan apna token daalein
SESSION = "BQAAAAYAV-Gre4YZAHift6bkKZu7W86MxiI3kiUWFSGPcK90nVJYijaUzBJe-F_zzYQGnRJQUKK9UBFy8RuPObe9_tRd6-1mpbVrgPFXb0q4iDrKIIEvfLhr7dZwBvRGpscoSU5PE15CTY087rD6ptyGlrr3za901QyL5DlE7CvjnLGIs67xra8Y_VRaYTi4APppdlxzezH9uCQLDMiMuBeLsBG3RPbMUq3FwOOf8_tu-UKXDLjKmM58DjP7HBvbPXHSZNjjlKAH0-TeHRxKYQ0GPuJZPH6ziOm-epLv_0xhBx0BnrfSMUwALfR7gInydw-1tL7XN4XYAMIwPsbe0G1jcSCdTwAAAAH3kmItAA"

# ==========================================
# 🚀 CLIENTS SETUP
# ==========================================
bot = Client("FrexxyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("FrexxyAssistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(assistant)

bot_data = {"current_ad": "✨ Welcome to Premium Frexxy Music! ✨"}

# ==========================================
# 🎵 YT-DLP FUNCTION
# ==========================================
def get_audio_url(query):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch1'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)['entries'][0]
        return info['url'], info['title']

# ==========================================
# 📢 COMMANDS & LOGIC
# ==========================================
@bot.on_message(filters.command("setad"))
async def set_ad(client, message):
    if len(message.command) < 2:
        return await message.reply("Ad text likho: `/setad Subscribe to Frexxxy`")
    bot_data["current_ad"] = message.text.split(None, 1)[1]
    await message.reply(f"✅ **Ad set:**\n{bot_data['current_ad']}")

@bot.on_message(filters.command("play") & filters.group)
async def play_command(client, message):
    if len(message.command) < 2:
        return await message.reply("Gaane ka naam do: `/play Tum Hi Ho`")
    
    song_query = message.text.split(None, 1)[1]
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Add & Play", callback_data=f"play_{song_query}")],
        [InlineKeyboardButton("❌ Close VC", callback_data="close_vc")]
    ])
    
    text = (
        f"🔍 **Searching:** `{song_query}`\n"
        f"⏱️ **Status:** Ready to add...\n"
        f"────────────────────\n"
        f"📢 **Sponsor:** {bot_data['current_ad']}\n\n"
        f"⚡ **Powered by Frexxxy**"
    )
    await message.reply(text, reply_markup=buttons)

@bot.on_callback_query()
async def button_handler(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    
    if query.data == "close_vc":
        try:
            await call_py.leave_group_call(chat_id)
            await query.edit_message_text("🛑 **Music Stopped!**\n🎤 VC is now free for chatting.\n\n⚡ **Powered by Frexxxy**")
        except Exception:
            await query.edit_message_text("❌ Pehle se hi koi nahi hai VC me!\n\n⚡ **Powered by Frexxxy**")
            
    elif query.data.startswith("play_"):
        song_query = query.data.split("_")[1]
        await query.edit_message_text(f"⏳ **Downloading track:** `{song_query}`\n*Please wait...*")
        
        try:
            audio_url, song_title = get_audio_url(song_query)
            try:
                await call_py.change_stream(chat_id, MediaStream(audio_url))
                status = "🔀 **Stream Changed!**"
            except NotInCallError:
                await call_py.join_group_call(chat_id, MediaStream(audio_url))
                status = "▶️ **Started Playing!**"
                
            final_text = (
                f"{status}\n"
                f"🎵 **Song:** {song_title}\n"
                f"────────────────────\n"
                f"📢 **{bot_data['current_ad']}**\n\n"
                f"⚡ **Powered by Frexxxy**"
            )
            close_btn = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Stop Music", callback_data="close_vc")]])
            await query.edit_message_text(final_text, reply_markup=close_btn)
            
        except Exception as e:
            await query.edit_message_text(f"❌ **Error:** `{str(e)}`")

if __name__ == "__main__":
    print("🔥 Frexxxy Premium Bot Starting on Server...")
    bot.start()
    assistant.start()
    call_py.start()
    print("✅ Bot is Online 24/7!")
    bot.loop.run_forever()
