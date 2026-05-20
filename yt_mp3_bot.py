import os
import asyncio
import logging
import glob
import uuid
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
TOKEN = os.getenv("BOT_TOKEN", "8802747025:AAFxeyliELIK0ILXoy0trI-pXr675t7iZLo")
DEVELOPER_NAME = "Thiha Min Zin"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"မင်္ဂလာပါ {user.first_name}! 🎵\n\n"
        f"ကျွန်တော်က YouTube ဗီဒီယိုတွေကို MP3 အဖြစ် ပြောင်းပေးနိုင်တဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "**အသုံးပြုနည်း:**\n"
        "YouTube Link တစ်ခုခုကို ဒီကို ပို့ပေးလိုက်ပါ၊ ကျွန်တော် MP3 အဖြစ် ပြောင်းပေးပါ့မယ်။\n\n"
        f"👤 **Developer:** {DEVELOPER_NAME}"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ **အသုံးပြုနည်းလမ်းညွှန်**\n\n"
        "၁။ YouTube ကနေ သင်နှစ်သက်တဲ့ ဗီဒီယို link ကို copy ယူပါ။\n"
        "၂။ ဒီ Bot ဆီကို link ပို့ပေးလိုက်ပါ။\n"
        "၃။ ခဏစောင့်ပါ၊ Bot က MP3 အဖြစ် ပြောင်းပြီး ပို့ပေးပါလိမ့်မယ်။\n\n"
        "ပြဿနာတစ်စုံတစ်ရာရှိပါက Developer ကို ဆက်သွယ်နိုင်ပါတယ်။"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 **Bot အကြောင်း**\n\n"
        "ဤ Bot ကို YouTube ဗီဒီယိုများမှ အသံဖိုင်များကို အလွယ်တကူ ထုတ်ယူနိုင်ရန် ရည်ရွယ်၍ ဖန်တီးထားခြင်း ဖြစ်ပါသည်။\n\n"
        f"👤 **Developer:** {DEVELOPER_NAME}\n"
        "🛠 **Powered by:** Python, yt-dlp, FFmpeg\n\n"
        "ကျေးဇူးတင်စွာဖြင့် အသုံးပြုနိုင်ပါသည်။"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

def download_mp3_sync(url):
    download_id = str(uuid.uuid4())
    download_path = f'downloads/{download_id}'
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        files = glob.glob(f'{download_path}/*.mp3')
        if files:
            return files[0]
        return None
    except Exception as e:
        logging.error(f"yt-dlp error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        status_message = await update.message.reply_text("⏳ ခဏစောင့်ပေးပါ၊ ဗီဒီယိုကို MP3 အဖြစ် ပြောင်းလဲနေပါတယ်...")
        try:
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(None, download_mp3_sync, url)
            
            if file_path and os.path.exists(file_path):
                await update.message.reply_audio(audio=open(file_path, 'rb'))
                await status_message.delete()
                
                # Cleanup
                os.remove(file_path)
                os.rmdir(os.path.dirname(file_path))
            else:
                await status_message.edit_text("❌ စိတ်မကောင်းပါဘူး၊ အသံဖိုင်ကို ဒေါင်းလုဒ်ဆွဲလို့ မရပါဘူး။")
        except Exception as e:
            logging.error(f"Error: {e}")
            await status_message.edit_text("❌ အမှားတစ်ခု ဖြစ်သွားပါတယ်။ နောက်မှ ပြန်ကြိုးစားကြည့်ပါ။")
    else:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော YouTube Link ကို ပို့ပေးပါ။")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    application.run_polling()
