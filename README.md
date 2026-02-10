# Discord Chat Bot

このプロジェクトは、Discord上で動作するAIチャットボットです。
Groq APIまたはGoogle Gemini APIを使用して、ユーザーのメッセージに返信します。

## ファイル構成と役割

| ファイル名 | 役割 |
| :--- | :--- |
| **`groq.py`** | **Groq API版**のボット本体です。`llama-3.3-70b-versatile` モデルを使用し、高速で自然な日本語会話を行います。 |
| **`gemini.py`** | **Gemini API版**のボット本体です。`gemini-flash-latest` モデルを使用します。Googleの生成AIを試したい場合はこちらを実行します。 |
| **`.env`** | **機密情報（APIキーやトークン）を保存する場所**です。このファイルは他人に見せてはいけません（GitHub等にはアップロードしないでください）。 |
| **`sample.env`** | `.env` ファイルのひな形です。必要なキーの項目名だけが書かれています。配布用です。 |
| **`requirements.txt`** | **必要なライブラリの一覧**です。`pip install -r requirements.txt` コマンドで、これらを一括インストールできます。 |

## 使い方

1. `requirements.txt` のライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. `.env` ファイルを作成し（`sample.env`をコピーしてリネーム）、各APIキーを設定します。
3. 使用したいボットのスクリプトを実行します。
   - Groq版: `python groq.py`
   - Gemini版: `python gemini.py`
