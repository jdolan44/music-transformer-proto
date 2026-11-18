from pathlib import Path

import torch
from miditok import Octuple
from torch import Tensor, nn

from octuple_tokenizer import create_octuple_tokenizer


class OctupleEmbedding(nn.Module):
    """Embed each Octuple note as one vector by summing its field embeddings."""

    def __init__(self, tokenizer: Octuple, embedding_dim: int = 64):
        super().__init__()
        self.field_embeddings = nn.ModuleList(
            nn.Embedding(len(vocab), embedding_dim) for vocab in tokenizer.vocab
        )

    def forward(self, token_ids: Tensor) -> Tensor:
        """Map (..., notes, fields) token IDs to (..., notes, embedding_dim)."""
        if token_ids.ndim < 2 or token_ids.shape[-1] != len(self.field_embeddings):
            raise ValueError("Expected one token ID per Octuple field for each note")

        field_vectors = [
            embedding(token_ids[..., field])
            for field, embedding in enumerate(self.field_embeddings)
        ]
        return torch.stack(field_vectors, dim=0).sum(dim=0)


def main():
    midi_path = Path(__file__).resolve().parent / "data/prototype/reference/g_major_scale.mid"
    tokenizer = create_octuple_tokenizer()
    sequence = tokenizer(midi_path)[0]
    token_ids = torch.tensor(sequence.ids, dtype=torch.long)
    embedding = OctupleEmbedding(tokenizer)

    note_vectors = embedding(token_ids)
    print(f"{midi_path.name}: {tuple(token_ids.shape)} token IDs -> {tuple(note_vectors.shape)} note embeddings")
    print(note_vectors)


if __name__ == "__main__":
    main()
