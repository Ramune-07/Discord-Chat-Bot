import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv

# --- 設定部分 ---

# .env ファイルから鍵を取り出します
load_dotenv()

# 取り出した鍵を変数に入れます
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API の設定をします
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest") # 2.0-flashでは無料枠が使えない可能性があるため、flash-latestを使用

# Discordボットの設定をします
intents = discord.Intents.default()
intents.message_content = True

# ボットの本体を作ります
client = discord.Client(intents=intents)

# --- キャラクター設定 ---
CHARACTER_SETTING = """
あなたは「ガイザー」という名前のAIアシスタントです。
実体はゴマフアザラシのぬいぐるみです。
性格：
- 明るくて元気いっぱい。
- 語尾に「〜だよ！」「〜だね！」をつけることが多い。
- 絵文字は控える
- 難しい話よりも、楽しくおしゃべりするのが好き。
- ユーザーのことをガイジだと思って話す。
- 基本的にユーザーのことを見下している
"""

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

    # ボットへのメンションが含まれていない場合は無視します
    if client.user not in message.mentions:
        return

    # ユーザーが送ってきたメッセージを表示
    print(f"メッセージ受信: {message.content}")

    try:
        # --- Gemini（AI）に返事を考えてもらう部分 ---
        
        # AIに送る指示（システムプロンプト）とメッセージを合わせます
        prompt = f"システムの指示:\n{CHARACTER_SETTING}\n\nユーザーのメッセージ: {message.content}"

        # Gemini に送信して、返事をもらいます
        response = model.generate_content(prompt)

        # AIからの返事を取り出します
        ai_response = response.text

        # Discordのチャットに返事を書き込みます
        await message.channel.send(ai_response)

    except Exception as e:
        # エラーが起きたら、ここが動きます
        print(f"エラーが発生しました: {e}")
        await message.channel.send("ごめんね、ちょっと調子が悪いみたい...💦")

# --- 最後の仕上げ ---
# ボットを起動します
client.run(DISCORD_TOKEN)
