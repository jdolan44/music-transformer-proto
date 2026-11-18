from pathlib import Path

from miditok import Octuple, TokenizerConfig, TokSequence


def create_octuple_tokenizer() -> Octuple:
    config = TokenizerConfig(
        beat_res={(0, 16): 8},
        use_velocities=False,
        use_time_signatures=False,
    )
    return Octuple(config)


def tokenize_midi(midi_path: str | Path) -> list[TokSequence]:
    """Return the Octuple token sequences for a MIDI file."""
    return create_octuple_tokenizer()(Path(midi_path))


def main():
    midi_path = (
        Path(__file__).resolve().parent
        / "data"
        / "prototype"
        / "reference"
        / "g_major_scale.mid"
    )
    sequences = tokenize_midi(midi_path)

    print(f"Octuple tokens for {midi_path.name}")
    for sequence in sequences:
        for note_tokens in sequence.tokens:
            print(note_tokens)


if __name__ == "__main__":
    main()
