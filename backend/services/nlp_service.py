"""NLP service for qualitative response analysis."""

from typing import Any, List

import structlog

logger = structlog.get_logger()


class NLPService:
    """Service for NLP operations on qualitative responses."""

    def __init__(self):
        """Initialize NLP service."""
        self._bertopic_model = None
        self._spacy_nlp = None

    async def extract_themes(
        self, texts: List[str], min_topics: int = 2, max_topics: int = 10
    ) -> List[dict[str, Any]]:
        """Extract themes from qualitative responses using BERTopic.

        Args:
            texts: List of response texts
            min_topics: Minimum number of topics
            max_topics: Maximum number of topics

        Returns:
            List of theme dictionaries
        """
        if len(texts) < min_topics * 3:
            logger.warning(
                "insufficient_texts_for_theming",
                text_count=len(texts),
                min_topics=min_topics,
            )
            return []

        try:
            from bertopic import BERTopic
            from sentence_transformers import SentenceTransformer

            # Lazy load models
            if self._bertopic_model is None:
                embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                self._bertopic_model = BERTopic(
                    embedding_model=embedding_model,
                    min_topic_size=max(2, len(texts) // max_topics),
                    nr_topics="auto",
                )

            # Fit and transform
            topics, probs = self._bertopic_model.fit_transform(texts)

            # Extract topic info
            topic_info = self._bertopic_model.get_topic_info()

            themes = []
            for _, row in topic_info.iterrows():
                if row["Topic"] == -1:  # Skip outlier topic
                    continue

                topic_id = row["Topic"]
                topic_words = self._bertopic_model.get_topic(topic_id)

                themes.append(
                    {
                        "id": int(topic_id),
                        "name": row.get("Name", f"Topic {topic_id}"),
                        "count": int(row["Count"]),
                        "keywords": [word for word, _ in topic_words[:5]],
                        "representative_texts": [
                            texts[i]
                            for i, t in enumerate(topics)
                            if t == topic_id
                        ][:3],
                    }
                )

            return themes

        except Exception as e:
            logger.error("theme_extraction_failed", error=str(e))
            return []

    async def extract_entities(self, text: str) -> List[dict[str, str]]:
        """Extract named entities from text using spaCy.

        Args:
            text: Input text

        Returns:
            List of entity dictionaries
        """
        try:
            import spacy

            # Lazy load spaCy
            if self._spacy_nlp is None:
                try:
                    self._spacy_nlp = spacy.load("ru_core_news_md")
                except OSError:
                    # Fallback to small model
                    self._spacy_nlp = spacy.load("ru_core_news_sm")

            doc = self._spacy_nlp(text)

            entities = []
            for ent in doc.ents:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )

            return entities

        except Exception as e:
            logger.error("entity_extraction_failed", error=str(e))
            return []

    async def analyze_sentiment(self, text: str) -> dict[str, float]:
        """Analyze sentiment of text.

        Args:
            text: Input text

        Returns:
            Sentiment scores
        """
        # Simple rule-based sentiment for Russian
        # In production, use a proper sentiment model

        positive_words = [
            "хороший", "отличный", "прекрасный", "удобный", "эффективный",
            "доволен", "рекомендую", "помогает", "улучшил", "быстро",
            "качественно", "надежный", "выгодно", "экономит", "решил",
        ]
        negative_words = [
            "плохой", "ужасный", "неудобный", "дорого", "медленно",
            "проблема", "ошибка", "не работает", "разочарован", "сложно",
            "недоволен", "не рекомендую", "жаль", "утратил", "потеря",
        ]

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        total = pos_count + neg_count

        if total == 0:
            return {"positive": 0.5, "negative": 0.5, "neutral": 1.0}

        pos_score = pos_count / total
        neg_score = neg_count / total

        return {
            "positive": round(pos_score, 2),
            "negative": round(neg_score, 2),
            "neutral": round(1 - pos_score - neg_score, 2),
        }

    async def summarize_responses(
        self, texts: List[str], max_length: int = 200
    ) -> str:
        """Generate summary of multiple responses.

        Args:
            texts: List of response texts
            max_length: Maximum summary length

        Returns:
            Summary text
        """
        if not texts:
            return ""

        # Simple extractive summary: most common phrases
        # In production, use a proper summarization model

        all_text = " ".join(texts)
        sentences = all_text.split(".")

        # Return first few sentences as summary
        summary = ". ".join(sentences[:3]).strip()
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary
