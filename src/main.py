import os
import sys
import gradio as gr
import requests
import traceback
from ollama import Client
from typing import Optional, Tuple


def get_server_url(ip: Optional[str] = None) -> str:
    """サーバーのURLを取得する"""
    if ip:
        return f"http://{ip}:11434"
    return "http://localhost:11434"


def check_server_availability(base_url: str) -> bool:
    """Ollamaサーバーが利用可能かどうかを確認する"""
    try:
        response = requests.get(f"{base_url}/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False


def clean_code(code: str) -> str:
    """生成されたコードをクリーンアップする"""
    # コードブロックの削除
    if "```" in code:
        # コードブロックの開始と終了を探す
        start = code.find("```")
        if start != -1:
            # 言語指定がある場合はその行を飛ばす
            next_newline = code.find("\n", start)
            if next_newline != -1:
                code = code[next_newline + 1 :]
            # 終了マーカーを削除
            end = code.rfind("```")
            if end != -1:
                code = code[:end]

    # 先頭と末尾の空白を削除
    code = code.strip()

    # インデントを修正（タブをスペースに変換）
    lines = code.splitlines()
    cleaned_lines = [line.replace("\t", "    ").rstrip() for line in lines]

    return "\n".join(cleaned_lines)


class GameGenerator:
    def __init__(self, base_url: str):
        if not check_server_availability(base_url):
            raise ConnectionError(f"Ollamaサーバー({base_url})に接続できません")

        self.client = Client(host=base_url)

    def generate_game_code(self, description: str) -> str:
        """ゲームコードを生成する"""
        prompt = f"""
以下の説明に基づいてPyxelゲームのコードを生成してください。
コードは単一のPythonファイルとして完結している必要があります。
マークダウンの装飾（```など）は使用せず、純粋なPythonコードのみを返してください。

ゲームの説明:
{description}

要件:
- Pyxelのバージョン1.9.18以上を使用
- クラスベースで実装
- 適切なコメントを含める
- 画面サイズは256x256

注意:
- マークダウンの装飾は使用しないでください
- Pythonコードのみを返してください

サンプルコード：
- Linuxのポータブルデバイスで動かすことを想定しています。物理キーで操作できるようにしてください。以下がサンプルコードです。

```python
def __init__(self):
    self.SCREEN_WIDTH = 256
    self.SCREEN_HEIGHT = 256
    pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="<Game title>")

    # アナログ入力とキーボード対応
    self.analog_inputs = [
        ("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]),  # D/Aキーで左右
        ("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]),  # S/Wキーで上下
        ("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]),  # 右左キー
        ("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]),  # 下上キー
        ("GAMEPAD1_AXIS_TRIGGERLEFT", [pyxel.KEY_Q]),  # Qキー
        ("GAMEPAD1_AXIS_TRIGGERRIGHT", [pyxel.KEY_E]),  # Eキー
    ]

    # デジタル入力とキーボード対応
    self.digital_inputs = [
        ("GAMEPAD1_BUTTON_LEFTSTICK", [pyxel.KEY_Z]),  # Zキー
        ("GAMEPAD1_BUTTON_RIGHTSTICK", [pyxel.KEY_X]),  # Xキー
        ("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]),  # Jキー
        ("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]),  # Kキー
        ("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]),  # Uキー
        ("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]),  # Iキー
        ("GAMEPAD1_BUTTON_BACK", [pyxel.KEY_B]),  # Bキー
        ("GAMEPAD1_BUTTON_GUIDE", [pyxel.KEY_G]),  # Gキー
        ("GAMEPAD1_BUTTON_START", [pyxel.KEY_RETURN]),  # Enterキー
        ("GAMEPAD1_BUTTON_LEFTSHOULDER", [pyxel.KEY_1]),  # 1キー
        ("GAMEPAD1_BUTTON_RIGHTSHOULDER", [pyxel.KEY_2]),  # 2キー
        ("GAMEPAD1_BUTTON_DPAD_UP", [pyxel.KEY_UP]),  # ↑キー
        ("GAMEPAD1_BUTTON_DPAD_DOWN", [pyxel.KEY_DOWN]),  # ↓キー
        ("GAMEPAD1_BUTTON_DPAD_LEFT", [pyxel.KEY_LEFT]),  # ←キー
        ("GAMEPAD1_BUTTON_DPAD_RIGHT", [pyxel.KEY_RIGHT]),  # →キー
    ]
```

- STARTボタンかESCキーで終了できるようにしてください。以下はサンプルコードです。

```python
def update(self):
    # STARTボタンまたはESCキーで終了
    if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
        pyxel.quit()
```
"""
        # response = self.client.generate(model="deepseek-coder-v2:16b", prompt=prompt, stream=False)
        response = self.client.generate(model="phi4", prompt=prompt, stream=False)

        # 生成されたコードをクリーンアップ
        return clean_code(response["response"])


def generate_and_save_game(description: str, ip: Optional[str] = None) -> Tuple[str, str]:
    """ゲームを生成して保存する"""
    try:
        base_url = get_server_url(ip)
        generator = GameGenerator(base_url)

        # ゲームコードの生成
        generated_code = generator.generate_game_code(description)

        # 生成されたコードを一時ファイルに保存
        temp_file = "generated_game.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(generated_code)

        return (
            generated_code,
            f"ゲームの生成が完了しました！\n実行するには以下のコマンドを使用してください：\npython {temp_file}",
        )

    except Exception as e:
        error_msg = f"エラーが発生しました: {str(e)}"
        print(error_msg, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return "", error_msg


def create_web_interface():
    """Gradioのウェブインターフェースを作成する"""
    with gr.Blocks(title="Deep Pyxel Lab") as interface:
        gr.Markdown("# 🎮 Deep Pyxel Lab")
        gr.Markdown("AIを使ってPyxelゲームを生成します")

        with gr.Row():
            with gr.Column():
                description_input = gr.Textbox(
                    label="ゲームの説明",
                    placeholder="作りたいゲームの説明を入力してください...",
                    value="ジャンプをしながらすすむアクションゲーム",
                    lines=5,
                )
                ip_input = gr.Textbox(label="Ollamaサーバーのアドレス(Option)", value="", lines=1)
                generate_btn = gr.Button("ゲームを生成", variant="primary")

            with gr.Column():
                code_output = gr.Code(label="生成されたコード", language="python")
                status_output = gr.Textbox(label="ステータス", lines=3)

        generate_btn.click(
            fn=generate_and_save_game, inputs=[description_input, ip_input], outputs=[code_output, status_output]
        )

        gr.Markdown("""
        ## 使い方
        1. 必要に応じてゲームの説明を編集
        2. 「ゲームを生成」ボタンをクリック
        3. 生成されたコードを確認
        4. 表示されるコマンドを使ってゲームを実行

        ## 注意事項
        - Pyxel 1.9.18以上が必要です
        - Ollamaサーバーが実行中である必要があります
        - deepseek-coder-v2:16bモデルがインストールされている必要があります
        """)

    return interface


def main():
    """メイン関数"""
    print("Deep Pyxel Lab を起動中...", flush=True)
    interface = create_web_interface()
    interface.launch(server_name="127.0.0.1", server_port=7861, share=True)


if __name__ == "__main__":
    main()
