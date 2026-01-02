# ------------------------------------------------------------
# Telegram Voice-to-Text Bot
# ------------------------------------------------------------
# This bot receives voice messages from users on Telegram
# and converts them into text using speech recognition.
# ------------------------------------------------------------


# -------------------------
# Imports
# -------------------------
# telegram & telegram.ext:
# Used to interact with Telegram Bot API and handle updates
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# pydub:
# Used to convert audio files from OGG to WAV format
import pydub

# speech_recognition:
# Used to transcribe speech from audio files into text
import speech_recognition as sr

# os:
# Used for file handling (delete temporary audio files)
import os

# asyncio:
# Used for asynchronous execution (required by python-telegram-bot async API)
import asyncio


# -------------------------
# Bot Token
# -------------------------
# Telegram bot token (should be kept secret in real projects)
TOKEN = "TOKEN"


# -------------------------
# /start Command Handler
# -------------------------
# Sends a welcome message when the user starts the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello Im a Voice-to-text bot\n"
        "Send me a voice message and I'll transcribe it for you.\n"
        "Type /help for more info. "
    )


# -------------------------
# /help Command Handler
# -------------------------
# Explains how to use the bot
async def help_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use:\n"
        "1. Record a voice message in English\n"
        "2. Send it to me\n"
        "3. I'll reply with the transcribed text\n\n"
        "Supported language: English only (high accuracy)\n"
        "More languages coming soon!"
    )


# -------------------------
# Voice Message Handler
# -------------------------
# Handles incoming voice messages and converts them to text
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        return
    
    # Download the voice file from Telegram servers
    voice_file = await voice.get_file()
    ogg_path = "voice.ogg"
    wav_path = "voice.wav"
    
    await voice_file.download_to_drive(ogg_path)
    
    try:
        # Convert OGG audio file to WAV using pydub
        sound = pydub.AudioSegment.from_ogg(ogg_path)
        sound.export(wav_path, format="wav")
        
        # Initialize speech recognizer
        recognizer = sr.Recognizer()
        
        # Load WAV file and read audio data
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        
        # Recognize speech using Google Speech Recognition (English)
        text = recognizer.recognize_google(audio, language="en-US")
        
        # Send transcribed text back to the user
        await update.message.reply_text(f"Transcribed text:\n\n{text}")
    
    # Error when speech cannot be understood
    except sr.UnknownValueError:
        await update.message.reply_text(
            "Sorry, I couldn't understand the audio. Please speak clearly in English."
        )
    
    # Error when API request fails
    except sr.RequestError:
        await update.message.reply_text(
            "Error! I couldn't process the audio. Please try again."
        )
    
    # Handle any other unexpected errors
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
        
    finally:
        # Remove temporary audio files after processing
        for path in [ogg_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)
# -------------------------
# Main Function
# -------------------------
# Initializes the bot, registers handlers, and starts polling
def main():
    app = ApplicationBuilder().token("TOKEN").build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_voice))
    
    # Register voice message handler
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("Bot is running...")
    app.run_polling()


# -------------------------
# Entry Point
# -------------------------
# Runs the main function when the script is executed
if __name__ == "__main__":
    main()                