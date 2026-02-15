import os
import json
import discord
import google.generativeai as genai
from dotenv import load_dotenv

# --- 設定部分 ---

# .env ファイルから鍵を取り出します
load_dotenv()

# 取り出した鍵を変数に入れます
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_GEMINI2")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API の設定をします
genai.configure(api_key=GEMINI_API_KEY)

# --- キャラクター設定 ---
# characters/gemini2.txt からキャラクター設定を読み込みます
CHARACTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "characters", "gemini2.txt")
try:
    with open(CHARACTER_FILE, "r", encoding="utf-8") as f:
        CHARACTER_SETTING = f.read()
except FileNotFoundError:
    print("警告: characters/gemini2.txt が見つかりません。デフォルト設定を使用します。")
    CHARACTER_SETTING = "あなたは親切なAIアシスタントです。"

# モデルの初期化（システムプロンプトを設定）
model = genai.GenerativeModel(
    "gemini-flash-latest",
    system_instruction=CHARACTER_SETTING
)

# Discordボットの設定をします
intents = discord.Intents.default()
intents.message_content = True

# ボットの本体を作ります
client = discord.Client(intents=intents)

# --- 会話履歴の管理 ---
# ユーザーIDをキーにして、チャットセッションを保存します
chat_sessions = {}

# 履歴ファイルの保存先ディレクトリ
HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history", "gemini2")
MAX_HISTORY = 10 # 記憶する会話の往復数


def load_history(user_id):
    """ユーザーの会話履歴をJSONファイルから読み込みます"""
    filepath = os.path.join(HISTORY_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(user_id, history):
    """ユーザーの会話履歴をJSONファイルに保存します"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    filepath = os.path.join(HISTORY_DIR, f"{user_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_gemini_history(raw_history):
    """JSON履歴をGeminiのチャットセッション用の形式に変換します"""
    gemini_history = []
    for msg in raw_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    return gemini_history


# --- ボットの動き（イベント） ---

# 1. ボットが起動したときに動くコード
@client.event
async def on_ready():
    print(f'{client.user} としてログインしました！')

# 2. メッセージが来たときに動くコード
@client.event
async def on_message(message):
    # 自分（ボット）が喋ったメッセージは無視します
    if message.author == client.user:
        return

    # 環境変数から特定チャンネルIDを取得
    SPECIFIC_CHANNEL_ID = os.getenv("CHANNEL_ID_GEMINI2")

    # メンションされているか、または特定チャンネルでの発言かを判定
    is_mentioned = client.user in message.mentions
    is_specific_channel = False
    
    if SPECIFIC_CHANNEL_ID:
        is_specific_channel = (str(message.channel.id) == SPECIFIC_CHANNEL_ID)

    # どちらの条件も満たさない場合は無視
    if not (is_mentioned or is_specific_channel):
        return

    # ユーザーが送ってきたメッセージを表示
    print(f"メッセージ受信 ({message.author.name}): {message.content}")

    try:
        # --- Gemini（AI）に返事を考えてもらう部分 ---
        
        # 「入力中...」を表示します
        async with message.channel.typing():
            user_id = message.author.id

            # ユーザーごとのセッションを取得、なければ保存済み履歴から復元
            if user_id not in chat_sessions:
                saved_history = load_history(user_id)
                # 履歴が長すぎたら古いものを削除
                if len(saved_history) > MAX_HISTORY * 2:
                    saved_history = saved_history[-(MAX_HISTORY * 2):]
                gemini_history = get_gemini_history(saved_history)
                chat_sessions[user_id] = {
                    "chat": model.start_chat(history=gemini_history),
                    "raw_history": saved_history
                }
            
            session = chat_sessions[user_id]
            chat = session["chat"]
            raw_history = session["raw_history"]

            # Gemini に送信して、返事をもらいます（ユーザー名を付加）
            response = chat.send_message(f"[{message.author.display_name}]: {message.content}")

            # AIからの返事を取り出します
            ai_response = response.text

            # 履歴を保存用に記録
            raw_history.append({"role": "user", "content": message.content})
            raw_history.append({"role": "assistant", "content": ai_response})

            # 履歴が長すぎたら古いものを削除
            if len(raw_history) > MAX_HISTORY * 2:
                raw_history = raw_history[-(MAX_HISTORY * 2):]
                # セッションを新しい履歴で再作成
                gemini_history = get_gemini_history(raw_history)
                chat_sessions[user_id] = {
                    "chat": model.start_chat(history=gemini_history),
                    "raw_history": raw_history
                }

            # 履歴をファイルに保存（永続化）
            save_history(user_id, raw_history)

            # Discordのチャットに返事を書き込みます
            await message.channel.send(ai_response)

    except Exception as e:
        # エラーが起きたら、ここが動きます
        print(f"エラーが発生しました: {e}")
        await message.channel.send(f"エラーが発生しました。\nエラー内容: {e}")

# --- 最後の仕上げ ---
# ボットを起動します
client.run(DISCORD_TOKEN)
