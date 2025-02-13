# Deep Pyxel Lab

Ollamaを使用してPyxelゲームを動的に生成するアプリケーションです。

## 必要条件

- Python 3.8以上
- Ollama（DeepSeek Coderモデルがインストールされていること）

## セットアップ

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. Ollamaのインストールと設定:
```bash
# Ollamaをインストール（macOS/Linux）
curl https://ollama.ai/install.sh | sh

# DeepSeek R1モデルをダウンロード
ollama pull deepseek-r1:14b
```

## 使用方法

1. アプリケーションの起動:
```bash
python src/main.py
```

2. 使い方:
- テキストボックスにゲームの説明を入力
- Enterキーを押してゲーム生成を開始
- 生成されたゲームが自動的に新しいウィンドウで起動
- Qキーでアプリケーションを終了

## 入力例

以下のような説明文を入力してゲームを生成できます：

- "ジャンプして障害物を避けるシンプルなアクションゲーム"
- "マウスで操作する簡単なシューティングゲーム"
- "ブロックを消していくパズルゲーム"

## 注意事項

- 生成されたゲームは一時ファイル（generated_game.py）として保存されます
- 生成には数秒から数十秒かかる場合があります
- 生成結果はAIの性質上、毎回異なる可能性があります
