# 必要な「道具箱」を取り出しています
import os
import discord
from groq import Groq
from dotenv import load_dotenv

# --- 設定部分 ---

# さっき作った .env ファイル（金庫）から鍵を取り出します
load_dotenv()

# 取り出した鍵を変数（箱）に入れます
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq（AIの脳）を使う準備をします
groq_client = Groq(api_key=GROQ_API_KEY)

# Discordボットの設定をします
# intents（インテンツ）は「ボットがやりたいことリスト」です
intents = discord.Intents.default()
intents.message_content = True # 「メッセージの中身を読む許可」をオンにします

# ボットの本体（クライアント）を作ります
client = discord.Client(intents=intents)

# --- キャラクター設定 ---
# ここを変えるとボットの性格が変わります！
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

# おすすめのモデル：llama-3.3-70b-versatile
# 理由：非常に賢く、日本語が自然で、キャラクターを演じるのが上手だからです。
# しかもGroqでは高速に動きます。
AI_MODEL = "llama-3.3-70b-versatile"

# --- ボットの動き（イベント） ---

# 1. ボットが起動したときに動くコード
@client.event
async def on_ready():
    print(f'{client.user} としてログインしました！')

# 2. メッセージが来たときに動くコード
@client.event
async def on_message(message):
    # 自分（ボット）が喋ったメッセージは無視します（無限ループ防止）
    if message.author == client.user:
        return

    # ボットへのメンションが含まれていない場合は無視します
    if client.user not in message.mentions:
        return

    # ユーザーが送ってきたメッセージを表示（確認用）
    print(f"メッセージ受信: {message.content}")

    try:
        # --- Groq（AI）に返事を考えてもらう部分 ---
        
        # AIに送る手紙の内容を作ります
        messages_to_ai = [
            # system: AIへの「役作り」の指示
            {"role": "system", "content": CHARACTER_SETTING},
            # user: ユーザーからの実際のメッセージ
            {"role": "user", "content": message.content}
        ]

        # Groqに送信して、返事をもらいます
        completion = groq_client.chat.completions.create(
            model=AI_MODEL,
            messages=messages_to_ai,
            temperature=0.7, # 0.0〜1.0。高いほど創造的で変化のある返答になります
            max_tokens=300,  # 返事の長さの上限（長すぎないように制限）
        )

        # AIからの返事を取り出します
        ai_response = completion.choices[0].message.content

        # Discordのチャットに返事を書き込みます
        await message.channel.send(ai_response)

    except Exception as e:
        # エラーが起きたら、ここが動きます
        print(f"エラーが発生しました: {e}")
        await message.channel.send("ごめんね、ちょっと調子が悪いみたい...💦")

# --- 最後の仕上げ ---
# ボットを起動します
client.run(DISCORD_TOKEN)