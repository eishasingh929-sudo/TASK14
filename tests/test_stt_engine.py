from pathlib import Path

from uniguru.stt import STTEngine


def test_manifest_stt_engine_matches_filename_entry() -> None:
    manifest_path = Path(__file__).resolve().parents[1] / "uniguru" / "stt" / "sample_manifest.json"
    engine = STTEngine(provider_name="manifest", manifest_path=str(manifest_path))

    result = engine.transcribe(
        b"fake-audio",
        filename="sample-hi.wav",
        content_type="audio/wav",
        hinted_language="hi",
    )

    assert result["text"] == "ahimsa ka arth kya hai"
    assert result["language"] == "hi"
    assert result["provider"] == "manifest"
