# Music Transformer Prototype
### By Joseph Dolan
## Prototype dataset

[data/prototype/manifest.json](data/prototype/manifest.json) contains 180 paired performances for 36 monophonic exercises. Each of the 12 chromatic tonics has an ascending and descending major scale, natural minor scale, and two-octave major arpeggio. Each exercise has five performances covering clean playing, wrong pitches, one short onset delay, a long onset delay across consecutive notes, and combined pitch and onset errors.

| Split | Exercises | Performances |
| --- | ---: | ---: |
| Train | 24 | 120 |
| Validation | 6 | 30 |
| Test | 6 | 30 |

The manifest assigns splits by tonic, so each exercise and all of its variants stay together. MIDI paths are relative to the manifest directory.

Each row's `errors` array holds `[note_index, error_type]` pairs, indexed from zero in reference onset order. For example, `[[3, "wrong_pitch"], [3, "late_onset"]]` marks both errors on the fourth note. A clean performance has `"errors": []`.

For training, load the MIDI pair and choose `wrong_pitch` or `late_onset` as the practice goal. Build one boolean per reference note by marking the indices listed for that goal as true and filling the rest with false. Use the MIDI pair and goal as model inputs and keep the remaining manifest fields as metadata or supervision.

The manifest also records signed pitch changes in semitones and onset delays in MIDI ticks. Both MIDI files use 480 ticks per beat at 120 BPM. A short delay moves one note by 60 to 180 ticks. A long delay shifts the final three to six notes together by 2.25 to 4.25 beats, preserving note order and keeping the performance monophonic. Each reference note has one corresponding performance note.

Regenerate the dataset with `python generate_dataset.py`.
