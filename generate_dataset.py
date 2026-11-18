"""Generate the paired MIDI dataset using only the Python standard library."""

import json
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "data" / "prototype"
TICKS_PER_BEAT = 480
STEP = 480
DURATION = 240
PITCH_CLASSES = "C C-sharp D E-flat E F F-sharp G A-flat A B-flat B".split()
MAJOR = (0, 2, 4, 5, 7, 9, 11, 12)
MINOR = (0, 2, 3, 5, 7, 8, 10, 12)
EXERCISES = {
    "major_scale": MAJOR + MAJOR[-2::-1],
    "natural_minor_scale": MINOR + MINOR[-2::-1],
    "arpeggio": (0, 4, 7, 12, 16, 19, 24, 19, 16, 12, 7, 4, 0),
}
KEY_SPLITS = {
    "train": (0, 1, 2, 4, 5, 7, 9, 10),
    "validation": (3, 6),
    "test": (8, 11),
}


def vlq(value):
    """Encode a MIDI delta time as a variable-length quantity."""
    encoded = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        encoded.append((value & 0x7F) | 0x80)
    return bytes(reversed(encoded))


def write_midi(relative_path, pitches, onsets):
    track = bytearray(b"\x00\xff\x51\x03\x07\xa1\x20")  # 120 BPM
    previous_end = 0
    for pitch, onset in zip(pitches, onsets, strict=True):
        assert onset >= previous_end
        track.extend(vlq(onset - previous_end) + bytes((0x90, pitch, 80)))
        track.extend(vlq(DURATION) + bytes((0x80, pitch, 0)))
        previous_end = onset + DURATION
    track.extend(b"\x00\xff\x2f\x00")
    header = struct.pack(">4sIHHH", b"MThd", 6, 0, 1, TICKS_PER_BEAT)
    (ROOT / relative_path).write_bytes(header + struct.pack(">4sI", b"MTrk", len(track)) + track)


def generate():
    rng = random.Random(20261207)
    (ROOT / "reference").mkdir(parents=True, exist_ok=True)
    (ROOT / "performance").mkdir(exist_ok=True)
    rows = []
    for split, keys in KEY_SPLITS.items():
        for key in keys:
            for family, intervals in EXERCISES.items():
                exercise_id = f"{PITCH_CLASSES[key].lower()}_{family}"
                reference = f"reference/{exercise_id}.mid"
                pitches = [60 + key + interval for interval in intervals]
                onsets = [i * STEP for i in range(len(pitches))]
                write_midi(reference, pitches, onsets)

                for variant in ("clean", "pitch", "late_short", "late_long", "mixed"):
                    performance_pitches = pitches.copy()
                    delays = [0] * len(pitches)
                    if variant == "late_short":
                        index = rng.randrange(len(pitches) - 1)
                        delays[index] = rng.choice((60, 120, 180))
                    if variant in ("late_long", "mixed"):
                        # Shift a suffix to preserve note order and monophony.
                        first_late = len(pitches) - rng.randint(3, 6)
                        delay = rng.randint(2, 4) * STEP + STEP // 4
                        delays[first_late:] = [delay] * (len(pitches) - first_late)
                    if variant == "pitch":
                        pitch_errors = rng.sample(range(len(pitches)), 2)
                    elif variant == "mixed":
                        pitch_errors = (rng.randrange(first_late), rng.randrange(first_late, len(pitches)))
                    else:
                        pitch_errors = ()
                    for index in pitch_errors:
                        performance_pitches[index] += rng.choice((-2, -1, 1, 2))

                    performance = f"performance/{exercise_id}_{variant}.mid"
                    performance_onsets = [onset + delay for onset, delay in zip(onsets, delays, strict=True)]
                    write_midi(performance, performance_pitches, performance_onsets)
                    row = {
                        "exercise_id": exercise_id,
                        "split": split,
                        "family": family,
                        "tonic": PITCH_CLASSES[key],
                        "variant": variant,
                        "reference_midi": reference,
                        "performance_midi": performance,
                        "errors": [
                            [index, error_type]
                            for index, (reference_pitch, performance_pitch, delay) in enumerate(
                                zip(pitches, performance_pitches, delays, strict=True)
                            )
                            for error_type, injected in (
                                ("wrong_pitch", reference_pitch != performance_pitch),
                                ("late_onset", delay > 0),
                            )
                            if injected
                        ],
                        "pitch_delta_semitones": [b - a for a, b in zip(pitches, performance_pitches, strict=True)],
                        "onset_delay_ticks": delays,
                    }
                    rows.append(row)

    (ROOT / "manifest.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    generate()
