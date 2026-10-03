from app.services.text_chunker import TextChunker


def test_text_chunker_natural_sentence_boundaries():
    chunker = TextChunker()
    text = "That sounds really interesting! What happened next? Did you enjoy the trip?"
    chunks = chunker.split_into_chunks(text)
    assert len(chunks) == 3
    assert chunks[0] == "That sounds really interesting!"
    assert chunks[1] == "What happened next?"
    assert chunks[2] == "Did you enjoy the trip?"


def test_text_chunker_abbreviations_handling():
    chunker = TextChunker()
    text = "Dr. Smith went to the office at 9 A.M. He had a great day!"
    chunks = chunker.split_into_chunks(text)
    assert len(chunks) >= 1
    assert "Dr. Smith" in chunks[0]
