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
    except Exception:
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
- コードは省略しないでください

注意:
- マークダウンの装飾は使用しないでください
- Pythonコードのみを返してください
- assetはありません。画像は自分で描画してください

サンプルコード：
- 以下はアクションゲームのサンプルゲームです。

```python
import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256

MAX_BUBBLE_SPEED = 1.8
NUM_INITIAL_BUBBLES = 50
NUM_EXPLODE_BUBBLES = 11


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Bubble:
    def __init__(self):
        self.r = pyxel.rndf(3, 10)

        self.pos = Vec2(
            pyxel.rndf(self.r, SCREEN_WIDTH - self.r),
            pyxel.rndf(self.r, SCREEN_HEIGHT - self.r),
        )

        self.vel = Vec2(
            pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED),
            pyxel.rndf(-MAX_BUBBLE_SPEED, MAX_BUBBLE_SPEED),
        )

        self.color = pyxel.rndi(1, 15)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.vel.x < 0 and self.pos.x < self.r:
            self.vel.x *= -1

        if self.vel.x > 0 and self.pos.x > SCREEN_WIDTH - self.r:
            self.vel.x *= -1

        if self.vel.y < 0 and self.pos.y < self.r:
            self.vel.y *= -1

        if self.vel.y > 0 and self.pos.y > SCREEN_HEIGHT - self.r:
            self.vel.y *= -1


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Bubbles", capture_scale=1)
        pyxel.mouse(True)

        self.is_exploded = False
        self.bubbles = [Bubble() for _ in range(NUM_INITIAL_BUBBLES)]

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        num_bubbles = len(self.bubbles)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i in range(num_bubbles):
                bubble = self.bubbles[i]
                dx = bubble.pos.x - pyxel.mouse_x
                dy = bubble.pos.y - pyxel.mouse_y

                if dx * dx + dy * dy < bubble.r * bubble.r:
                    self.is_exploded = True
                    new_r = pyxel.sqrt(bubble.r * bubble.r / NUM_EXPLODE_BUBBLES)

                    for j in range(NUM_EXPLODE_BUBBLES):
                        angle = 360 * j / NUM_EXPLODE_BUBBLES

                        new_bubble = Bubble()
                        new_bubble.r = new_r
                        new_bubble.pos.x = bubble.pos.x + (
                            bubble.r + new_r
                        ) * pyxel.cos(angle)
                        new_bubble.pos.y = bubble.pos.y + (
                            bubble.r + new_r
                        ) * pyxel.sin(angle)
                        new_bubble.vel.x = pyxel.cos(angle) * MAX_BUBBLE_SPEED
                        new_bubble.vel.y = pyxel.sin(angle) * MAX_BUBBLE_SPEED
                        self.bubbles.append(new_bubble)

                    del self.bubbles[i]
                    break

        for i in range(num_bubbles - 1, -1, -1):
            bi = self.bubbles[i]
            bi.update()

            for j in range(i - 1, -1, -1):
                bj = self.bubbles[j]
                dx = bi.pos.x - bj.pos.x
                dy = bi.pos.y - bj.pos.y
                total_r = bi.r + bj.r

                if dx * dx + dy * dy < total_r * total_r:
                    new_bubble = Bubble()
                    new_bubble.r = pyxel.sqrt(bi.r * bi.r + bj.r * bj.r)
                    new_bubble.pos.x = (bi.pos.x * bi.r + bj.pos.x * bj.r) / total_r
                    new_bubble.pos.y = (bi.pos.y * bi.r + bj.pos.y * bj.r) / total_r
                    new_bubble.vel.x = (bi.vel.x * bi.r + bj.vel.x * bj.r) / total_r
                    new_bubble.vel.y = (bi.vel.y * bi.r + bj.vel.y * bj.r) / total_r
                    self.bubbles.append(new_bubble)

                    del self.bubbles[i]
                    del self.bubbles[j]
                    num_bubbles -= 1
                    break

    def draw(self):
        pyxel.cls(0)

        for bubble in self.bubbles:
            pyxel.circ(bubble.pos.x, bubble.pos.y, bubble.r, bubble.color)

        if not self.is_exploded and pyxel.frame_count % 20 < 10:
            pyxel.text(96, 50, "CLICK ON BUBBLE", pyxel.frame_count % 15 + 1)


App()
```
"""
        response = self.client.generate(model="deepseek-r1:14b", prompt=prompt, stream=False)
        # response = self.client.generate(model="deepseek-coder-v2:16b", prompt=prompt, stream=False)
        # response = self.client.generate(model="phi4", prompt=prompt, stream=False)

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
        - deepseek-r1:14bモデルがインストールされている必要があります
        """)

    return interface


def main():
    """メイン関数"""
    print("Deep Pyxel Lab を起動中...", flush=True)
    interface = create_web_interface()
    interface.launch(server_name="127.0.0.1", server_port=7861, share=True)


if __name__ == "__main__":
    main()
