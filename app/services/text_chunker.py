import re
from typing import List


ABBREVIATIONS = {"Mr.", "Mrs.", "Dr.", "Prof.", "Sr.", "Jr.", "vs.", "e.g.", "i.e.", "St.", "Co.", "Ltd."}


class TextChunker:
    """Intelligent text chunker that splits LLM responses into natural sentence chunks optimal for TTS synthesis."""

    def __init__(self, min_chunk_len: int = 15, max_chunk_len: int = 200):
        self.min_chunk_len = min_chunk_len
        self.max_chunk_len = max_chunk_len

    def split_into_chunks(self, text: str) -> List[str]:
        clean_text = text.strip()
        if not clean_text:
            return []

        # Regex to split on sentence-ending punctuation while preserving delimiters
        raw_sentences = re.split(r'(?<=[.!?;\n])\s+', clean_text)
        sentences: List[str] = []

        # Merge abbreviation false splits
        idx = 0
        while idx < len(raw_sentences):
            curr = raw_sentences[idx].strip()
            if not curr:
                idx += 1
                continue
            
            # Check if last word is an abbreviation
            words = curr.split()
            if words and words[-1] in ABBREVIATIONS and idx + 1 < len(raw_sentences):
                curr = curr + " " + raw_sentences[idx + 1].strip()
                idx += 1

            sentences.append(curr)
            idx += 1

        # Process sentence list to optimize chunk lengths
        optimized_chunks: List[str] = []
        current_acc = ""

        for sent in sentences:
            if not current_acc:
                current_acc = sent
            else:
                # If current accumulation is too short, merge with next sentence
                if len(current_acc) < self.min_chunk_len and (len(current_acc) + len(sent) + 1 <= self.max_chunk_len):
                    current_acc += " " + sent
                else:
                    optimized_chunks.append(current_acc)
                    current_acc = sent

        if current_acc:
            optimized_chunks.append(current_acc)

        # Final pass: check if any individual chunk exceeds max_chunk_len, split on clause boundaries
        final_chunks: List[str] = []
        for chunk in optimized_chunks:
            if len(chunk) > self.max_chunk_len:
                sub_clauses = re.split(r'(?<=[,:\n])\s+', chunk)
                sub_acc = ""
                for clause in sub_clauses:
                    if not sub_acc:
                        sub_acc = clause
                    elif len(sub_acc) + len(clause) + 1 <= self.max_chunk_len:
                        sub_acc += " " + clause
                    else:
                        final_chunks.append(sub_acc)
                        sub_acc = clause
                if sub_acc:
                    final_chunks.append(sub_acc)
            else:
                final_chunks.append(chunk)

        return [c.strip() for c in final_chunks if c.strip()]
