# 必要な「道具箱」を取り出しています
import os
import json
import discord
from discord import app_commands
from groq import AsyncGroq
from dotenv import load_dotenv

# --- 設定部分 ---

# さっき作った .env ファイル（金庫）から鍵を取り出します
load_dotenv()

# 取り出した鍵を変数（箱）に入れます
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_GROQ")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq（AIの脳）を使う準備をします
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# Discordボットの設定をします
# intents（インテンツ）は「ボットがやりたいことリスト」です
intents = discord.Intents.default()
intents.message_content = True # 「メッセージの中身を読む許可」をオンにします

# ボットの本体（クライアント）を作ります
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# --- 会話履歴の管理 ---
# チャンネルIDをキーにして、メッセージ履歴リストを保存します（全ユーザー統合）
# 形式: {channel_id: [{"role": "user", "content": "[ユーザー名]: ..."}, {"role": "assistant", "content": "..."}]}
channel_histories = {}
MAX_HISTORY = 10 # 記憶する会話の往復数（これを超えると古いものから忘れます）

# 履歴ファイルの保存先ディレクトリ
HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history", "groq")


def load_history(channel_id):
    """チャンネルの会話履歴をJSONファイルから読み込みます"""
    filepath = os.path.join(HISTORY_DIR, f"channel_{channel_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(channel_id, history):
    """チャンネルの会話履歴をJSONファイルに保存します"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    filepath = os.path.join(HISTORY_DIR, f"channel_{channel_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# --- キャラクター設定 ---
# characters/groq.txt からキャラクター設定を読み込みます
CHARACTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "characters", "groq.txt")
try:
    with open(CHARACTER_FILE, "r", encoding="utf-8") as f:
        CHARACTER_SETTING = f.read()
except FileNotFoundError:
    print("警告: characters/groq.txt が見つかりません。デフォルト設定を使用します。")
    CHARACTER_SETTING = "あなたは親切なAIアシスタントです。"

# おすすめのモデル：llama-3.3-70b-versatile
# 理由：非常に賢く、日本語が自然で、キャラクターを演じるのが上手だからです。
# しかもGroqでは高速に動きます。
AI_MODEL = "llama-3.1-8b-instant"

# --- ボットの動き（イベント） ---

# 1. ボットが起動したときに動くコード
@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} としてログインしました！')

@tree.command(name="ping", description="ボットの応答速度を確認します")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong!\n応答速度: {latency}ms")

@tree.command(name="reset", description="会話履歴をリセットします")
async def reset(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    # メモリ上の履歴を削除
    if channel_id in channel_histories:
        del channel_histories[channel_id]
    # ファイルの履歴を削除
    filepath = os.path.join(HISTORY_DIR, f"channel_{channel_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    await interaction.response.send_message("会話履歴をリセットしました！🔄")

# 2. メッセージが来たときに動くコード
@client.event
async def on_message(message):
    # 自分（ボット）が喋ったメッセージは無視します（無限ループ防止）
    if message.author == client.user:
        return

    # 環境変数から特定チャンネルIDを取得
    SPECIFIC_CHANNEL_ID = os.getenv("CHANNEL_ID_GROQ")

    # メンションされているか、または特定チャンネルでの発言かを判定
    is_mentioned = client.user in message.mentions
    is_specific_channel = False
    
    if SPECIFIC_CHANNEL_ID:
        is_specific_channel = (str(message.channel.id) == SPECIFIC_CHANNEL_ID)

    # どちらの条件も満たさない場合は無視
    if not (is_mentioned or is_specific_channel):
        return

    # ユーザーが送ってきたメッセージを表示（確認用）
    print(f"メッセージ受信 ({message.author.name}): {message.content}")

    try:
        # --- Groq（AI）に返事を考えてもらう部分 ---
        
        # 「入力中...」を表示します
        async with message.channel.typing():
            channel_id = message.channel.id
            
            # 履歴をメモリから取得、なければファイルから読み込み
            if channel_id not in channel_histories:
                channel_histories[channel_id] = load_history(channel_id)
            
            history = channel_histories[channel_id]

            # ユーザーのメッセージを履歴に追加（ユーザー名を付加してAIが識別できるようにする）
            history.append({"role": "user", "content": f"[{message.author.display_name}]: {message.content}"})

            # 履歴が長すぎたら古いものを削除（システムプロンプトは別枠なので純粋な会話履歴のみ調整）
            if len(history) > MAX_HISTORY * 2: # 往復なので2倍
                history = history[-(MAX_HISTORY * 2):]
                channel_histories[channel_id] = history

            # AIに送る手紙の内容を作ります
            # システムプロンプト + 会話履歴
            messages_to_ai = [{"role": "system", "content": CHARACTER_SETTING}] + history

            # Groqに送信して、返事をもらいます
            completion = await groq_client.chat.completions.create(
                model=AI_MODEL,
                messages=messages_to_ai,
                temperature=0.7, # 0.0〜1.0。高いほど創造的で変化のある返答になります
                max_tokens=300,  # 返事の長さの上限（長すぎないように制限）
            )

            # AIからの返事を取り出します
            ai_response = completion.choices[0].message.content

            # ボットの返事も履歴に追加
            history.append({"role": "assistant", "content": ai_response})
            channel_histories[channel_id] = history

            # 履歴をファイルに保存（永続化）
            save_history(channel_id, history)

            # Discordのチャットに返事を書き込みます
            await message.channel.send(ai_response)

    except Exception as e:
        # エラーが起きたら、ここが動きます
        print(f"エラーが発生しました: {e}")
        await message.channel.send(f"エラーが発生しました：\n```\n{e}\n```")

# --- 最後の仕上げ ---
# ボットを起動します
client.run(DISCORD_TOKEN)
