from typing import Any


def speech_to_text_and_speech(
    *,
    input_audio_path:   str,
    output_audio_path:  str,
    llm_output_path:    str,
    prompt_json_path:   str = "prompt.json"
) -> Any:
    """
    STT + LLM + TTS
    """
    pass
    # python main.py --input input.wav --output output.wav --llm_output llm_output.txt --prompt prompt.json


def text_to_speech(
    *,
    input_text_path:        str,
    reference_audio_path:   str,
    output_audio_path:      str,
) -> Any:
    """
    TTS only
    """
    pass
    # python main2.py --input_text input.txt --reference_audio reference.wav --output output.wav