from __future__ import annotations

from types import SimpleNamespace

from app.captions.align import align_narration


def test_long_caption_similarity_does_not_trigger_sequence_matcher_autojunk():
    expected = (
        "This local benchmark note is synthetic and exists only to exercise the verified source layout. "
        "The fictional queue latency drops from forty two milliseconds to eighteen. "
        "A generated chart shows the made up latency trend moving downward across four test passes. "
        "The synthetic timeline moves from baseline to scheduler change to validation and final pass. "
        "The comparison keeps the distinction simple: a slower fictional baseline and a faster fictional tuned state. "
        "Finally the editorial fallback proves the renderer still has a safe visual when no verified image is available."
    )
    recognized = expected.replace("forty two", "42").replace("eighteen", "18")
    words = [
        SimpleNamespace(word=word, start=index * 0.2, end=(index + 1) * 0.2)
        for index, word in enumerate(recognized.split())
    ]

    class Transcriber:
        def transcribe(self, audio, word_timestamps=True):
            return iter([SimpleNamespace(text=recognized, words=words)]), SimpleNamespace(language="en")

    cues = align_narration("narration.wav", expected, Transcriber())

    assert cues
