# Discord Chat Bot

このプロジェクトは、Discord上で動作するAIチャットボットです。
Groq APIまたはGoogle Gemini APIを使用して、ユーザーのメッセージに返信します。

## ファイル構成と役割

| ファイル名 | 役割 |
| :--- | :--- |
| **`groq_bot.py`** | **Groq API版**のボット本体です。`llama-3.3-70b-versatile` モデルを使用し、高速で自然な日本語会話を行います。 |
| **`gemini2_bot.py`** | **Gemini API版（2号機）**のボット本体です。`gemini.py` と同じ構造ですが、別のキャラクター設定・Discordトークンで動作します。 |
| **`gemini.py`** | **Gemini API版**のボット本体です。`gemini-flash-latest` モデルを使用します。Googleの生成AIを試したい場合はこちらを実行します。 |
| **`characters/`** | **キャラクター設定ファイル**を格納するディレクトリです。各ボットの性格をテキストファイルで管理します。 |
| **`.env`** | **機密情報（APIキーやトークン）を保存する場所**です。各ボットのDiscordトークンとAPIキーを設定します（GitHub等にはアップロードしないでください）。 |
| **`sample.env`** | `.env` ファイルのひな形です。必要なキーの項目名だけが書かれています。配布用です。 |
| **`requirements.txt`** | **必要なライブラリの一覧**です。`pip install -r requirements.txt` コマンドで、これらを一括インストールできます。 |
| **`chat_history/`** | ユーザーごとの会話履歴がJSON形式で自動保存されるディレクトリです（ボット再起動後も会話を記憶します）。 |

## 使い方

1. `requirements.txt` のライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. `.env` ファイルを作成し（`sample.env`をコピーしてリネーム）、各トークン・APIキーを設定します。
3. `characters/` ディレクトリ内のテキストファイルで、各ボットの性格を設定します。
   - `characters/groq.txt` — groq_bot用
   - `characters/gemini2.txt` — gemini2_bot用
   - `characters/gemini.txt` — gemini用
4. 使用したいボットのスクリプトを実行します。
   - Groq版: `python groq_bot.py`
   - Gemini版（2号機）: `python gemini2_bot.py`
   - Gemini版: `python gemini.py`

