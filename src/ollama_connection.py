import sys
import traceback
import requests
import argparse
from ollama import Client


def create_parser() -> argparse.ArgumentParser:
    """コマンドライン引数のパーサーを作成する"""
    parser = argparse.ArgumentParser(
        description="Ollamaサーバーとの接続テスト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  1. ローカルサーバーに接続:
     python test_ollama.py
  
  2. 特定のIPアドレスに接続:
     python test_ollama.py --ip 192.168.1.7
        """,
    )

    parser.add_argument(
        "-i",
        "--ip",
        type=str,
        help="接続先サーバーのIPアドレス（デフォルト: localhost）",
    )

    return parser


def check_server_availability(base_url: str) -> bool:
    """Ollamaサーバーが利用可能かどうかを確認する"""
    try:
        response = requests.get(f"{base_url}/api/version", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_server_url(args: argparse.Namespace) -> str:
    """サーバーのURLを取得する

    Args:
        args: コマンドライン引数

    Returns:
        str: 完全なサーバーURL
    """
    if args.ip:
        return f"http://{args.ip}:11434"
    return "http://localhost:11434"


def get_available_models(base_url: str) -> list:
    """利用可能なモデルの一覧を取得する"""
    try:
        # GETメソッドを使用
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"APIレスポンス: {response.text}")  # デバッグ用
            try:
                data = response.json()
                if isinstance(data, list):
                    return [model.get("name", "") for model in data if model.get("name")]
                elif isinstance(data, dict) and "models" in data:
                    return [model.get("name", "") for model in data["models"] if model.get("name")]
                else:
                    print(f"⚠️ 予期しないレスポンス形式: {data}", flush=True)
                    return []
            except Exception as e:
                print(f"⚠️ JSONパースエラー: {str(e)}", flush=True)
                return []
        else:
            print(f"⚠️ APIエラー: ステータスコード {response.status_code}", flush=True)
            return []
    except Exception as e:
        print(f"⚠️ モデル一覧の取得中にエラー: {str(e)}", flush=True)
        return []


def test_ollama_connection(args: argparse.Namespace) -> bool:
    """Ollamaサーバーとの接続をテストする

    Args:
        args: コマンドライン引数

    Returns:
        bool: 接続テストが成功したかどうか
    """
    base_url = get_server_url(args)
    print(f"\nOllamaサーバーに接続を試みます: {base_url}", flush=True)

    # サーバーの可用性を確認
    print("サーバーの可用性を確認中...", flush=True)
    if not check_server_availability(base_url):
        print("❌ サーバーに接続できません。以下を確認してください:", flush=True)
        print("  - サーバーが起動していること", flush=True)
        print("  - URLが正しいこと", flush=True)
        print(f"  - {base_url}にアクセス可能であること", flush=True)
        return False

    print("✅ サーバーが利用可能です", flush=True)

    try:
        # Ollamaクライアントの初期化
        print("\nOllamaクライアントを初期化中...", flush=True)
        client = Client(host=base_url)
        print("✅ クライアントの初期化が完了しました", flush=True)

        # 利用可能なモデルの確認
        print("\nモデル一覧を取得中...", flush=True)
        models = get_available_models(base_url)
        if models:
            print("利用可能なモデル:")
            for model in models:
                print(f"- {model}")
        else:
            print("⚠️ 利用可能なモデルが見つかりませんでした", flush=True)

        # テスト用の簡単なプロンプト
        print("\nテストプロンプトを送信中...", flush=True)
        prompt = "print('Hello, World!')というPythonコードを出力してください。"

        response = client.generate(model="deepseek-coder-v2:16b", prompt=prompt, stream=False)

        print("\n=== 応答 ===")
        print(response["response"])
        print("=== 応答終了 ===\n")

        print("✅ Ollamaサーバーとの接続テストが成功しました！", flush=True)
        return True

    except Exception as e:
        print("\n❌ エラーが発生しました:", file=sys.stderr, flush=True)
        print(f"エラーの種類: {type(e).__name__}", file=sys.stderr, flush=True)
        print(f"エラーメッセージ: {str(e)}", file=sys.stderr, flush=True)
        print("\n=== スタックトレース ===", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        print("=== スタックトレース終了 ===\n", file=sys.stderr, flush=True)
        return False


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()

    print("=== Ollama 接続テスト ===", flush=True)
    success = test_ollama_connection(args)
    print(f"\n実行結果: {'成功 ✅' if success else '失敗 ❌'}", flush=True)


if __name__ == "__main__":
    main()
