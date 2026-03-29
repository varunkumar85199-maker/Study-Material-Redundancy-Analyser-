"""
topic_analyzer.py
=================
Multiple PDFs ke text me se common topics dhundhta hai
aur same-topic sentences ko merge karta hai.
"""

import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from pdf_processor import PDFProcessor

processor = PDFProcessor()


class TopicAnalyzer:

    def __init__(self, similarity_threshold: float = 0.45):
        """
        similarity_threshold: 0–1 range.
        Zyada value = sirf jinke meaning bahut similar ho un sentences ko merge karega.
        """
        self.threshold = similarity_threshold

    # ───────────────────────────────────────────────────────────────
    # MAIN FUNCTION: Find Common Topics
    # ───────────────────────────────────────────────────────────────
    def find_common_topics(self, texts: dict[str, str]) -> list[dict]:
        """
        texts = { "file1.pdf": "full text...", "file2.pdf": "..." }
        Returns → topic list with merged text.
        """

        # Step 1: Each file ke sentences split karo
        file_sentences: dict[str, list[str]] = {}
        for fname, text in texts.items():
            clean = processor.clean(text)
            file_sentences[fname] = processor.split_into_sentences(clean)

        # Step 2: Headings detect karo
        headings = self._extract_headings(texts)

        # Step 3: Har heading ke lie related sentences group karo
        topics = []
        for heading in headings:
            group = self._gather_sentences_for_topic(heading, file_sentences)
            if not group:
                continue

            merged = self._merge_similar_sentences(group)

            topics.append({
                "topic": heading,
                "sources": list(group.keys()),
                "merged_text": merged,
                "overlap": self._overlap_score(group),
            })

        # Step 4: Agar headings na milen to TF-IDF auto-topic detection
        if not topics:
            topics = self._auto_cluster(file_sentences)

        return topics

    # ───────────────────────────────────────────────────────────────
    # Extract Headings From Text
    # ───────────────────────────────────────────────────────────────
    def _extract_headings(self, texts: dict[str, str]) -> list[str]:
        """
        Headings detect karta hai:
        - numbered headings
        - ALL CAPS headings
        - ## / ### style
        """

        heading_pattern = re.compile(
            r'^(\d+[\.\)]\s+.{5,60}|[A-Z][A-Z\s]{5,50}|#{1,3}\s+.+)$',
            re.MULTILINE
        )

        found: dict[str, int] = defaultdict(int)

        for text in texts.values():
            for match in heading_pattern.finditer(text):
                h = match.group().strip().title()
                found[h] += 1

        # Agar 1 file hai to heading ek hi file se allow
        min_files = 1 if len(texts) == 1 else 2

        return [h for h, c in found.items() if c >= min_files][:20]

    # ───────────────────────────────────────────────────────────────
    # Collect sentences related to a topic
    # ───────────────────────────────────────────────────────────────
    def _gather_sentences_for_topic(
        self, topic: str, file_sentences: dict[str, list[str]]
    ) -> dict[str, list[str]]:

        keywords = set(topic.lower().split())
        group: dict[str, list[str]] = {}

        for fname, sentences in file_sentences.items():
            related = [
                s for s in sentences
                if any(kw in s.lower() for kw in keywords)
            ]
            if related:
                group[fname] = related

        return group

    # ───────────────────────────────────────────────────────────────
    # Merge similar sentences (deduplication)
    # ───────────────────────────────────────────────────────────────
    def _merge_similar_sentences(self, group: dict[str, list[str]]) -> str:

        all_sentences = []
        for sents in group.values():
            all_sentences.extend(sents)

        if len(all_sentences) <= 1:
            return all_sentences[0] if all_sentences else ""

        # TF-IDF similarity
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(all_sentences)
            similarity_matrix = cosine_similarity(matrix)
        except Exception:
            # fallback
            return " ".join(all_sentences[:5])

        kept = []
        used = set()

        # Greedy duplicate-removal
        for i, sent in enumerate(all_sentences):
            if i in used:
                continue

            kept.append(sent)

            for j in range(i + 1, len(all_sentences)):
                if similarity_matrix[i][j] >= self.threshold:
                    used.add(j)

        return " ".join(kept)

    # ───────────────────────────────────────────────────────────────
    # Calculate overlap score between multiple files
    # ───────────────────────────────────────────────────────────────
    def _overlap_score(self, group: dict[str, list[str]]) -> int:
        if len(group) < 2:
            return 100

        all_words = [
            set(w.lower() for s in sents for w in s.split())
            for sents in group.values()
        ]

        common = all_words[0].intersection(*all_words[1:])
        total = all_words[0].union(*all_words[1:])

        return int(len(common) / len(total) * 100) if total else 0

    # ───────────────────────────────────────────────────────────────
    # Auto Topic Detection: Uses TF-IDF keywords
    # ───────────────────────────────────────────────────────────────
    def _auto_cluster(self, file_sentences: dict[str, list[str]]) -> list[dict]:

        all_sents = [s for sents in file_sentences.values() for s in sents]
        if not all_sents:
            return []

        try:
            vectorizer = TfidfVectorizer(max_features=10, stop_words="english")
            vectorizer.fit(all_sents)
            keywords = vectorizer.get_feature_names_out().tolist()
        except Exception:
            return []

        topics = []
        for kw in keywords:
            group = self._gather_sentences_for_topic(kw, file_sentences)

            if group:
                merged = self._merge_similar_sentences(group)

                topics.append({
                    "topic": kw.title(),
                    "sources": list(group.keys()),
                    "merged_text": merged,
                    "overlap": self._overlap_score(group),
                })

        return topics
