from src.main import create_web_interface
import gradio as gr
import pytest


def test_web_interface_creation():
    """ウェブインターフェースが正しく作成されることをテスト"""
    interface = create_web_interface()
    assert isinstance(interface, gr.Blocks)
    # ここで、インターフェースの要素（Textbox, Buttonなど）が正しく作成されているか確認することもできます。
    # 例えば、description_input が存在することを確認する
    # for component in interface.blocks:
    #     if component.label == "ゲームの説明":
    #         assert isinstance(component, gr.Textbox)
