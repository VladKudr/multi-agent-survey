"""NLP service for qualitative response analysis.

This is a simplified version without heavy dependencies.
For full functionality, install requirements-nlp.txt
"""

from typing import Any, List

import structlog

logger = structlog.get_logger()


class NLPService:
    """Service for NLP operations on qualitative responses.
    
    This is a lightweight implementation. For advanced features
    (BERTopic, transformers), install requirements-nlp.txt
    """

    def __init__(self):
        """Initialize NLP service."""
        self._bertopic_available = False
        self._spacy_available = False
        
        # Try to import optional dependencies
        try:
            import spacy
            self._spacy_available = True
            logger.info("spaCy is available")
        except ImportError:
            logger.warning("spaCy not installed. Install: pip install spacy")
        
        try:
            from bertopic import BERTopic
            self._bertopic_available = True
            logger.info("BERTopic is available")
        except ImportError:
            logger.debug("BERTopic not installed. Install: pip install bertopic")

    async def extract_themes(
        self, texts: List[str], min_topics: int = 2, max_topics: int = 10
    ) -> List[dict[str, Any]]:
        """Extract themes from qualitative responses.
        
        Note: Requires BERTopic to be installed for full functionality.
        Without BERTopic, returns basic keyword analysis.
        """
        if not texts or len(texts) < min_topics * 3:
            logger.warning(
                "insufficient_texts_for_theming",
                text_count=len(texts),
                min_topics=min_topics,
            )
            return []

        # If BERTopic not available, do basic keyword extraction
        if not self._bertopic_available:
            logger.info("BERTopic not available, using basic keyword extraction")
            return self._basic_theme_extraction(texts)

        try:
            from bertopic import BERTopic
            from sentence_transformers import SentenceTransformer

            embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            topic_model = BERTopic(
                embedding_model=embedding_model,
                min_topic_size=max(2, len(texts) // max_topics),
                nr_topics="auto",
            )

            topics, probs = topic_model.fit_transform(texts)
            topic_info = topic_model.get_topic_info()

            themes = []
            for _, row in topic_info.iterrows():
                if row["Topic"] == -1:
                    continue

                topic_id = row["Topic"]
                topic_words = topic_model.get_topic(topic_id)

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
            return self._basic_theme_extraction(texts)

    def _basic_theme_extraction(self, texts: List[str]) -> List[dict[str, Any]]:
        """Basic keyword-based theme extraction without heavy dependencies."""
        from collections import Counter
        import re
        
        # Simple Russian/English keyword extraction
        stopwords = {
            "и", "в", "не", "на", "с", "что", "а", "по", "это", "она", 
            "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
            "бы", "по", "только", "ее", "мне", "было", "вот", "от",
            "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда",
            "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни",
            "быть", "был", "него", "до", "вас", "нибудь", "опять",
            "уж", "вам", "ведь", "там", "потом", "себя", "ничего",
            "the", "is", "and", "to", "of", "a", "in", "that", "it",
            "for", "on", "with", "as", "this", "was", "at", "by",
            "an", "be", "from", "or", "are", "not", "but", "have",
        }
        
        all_words = []
        for text in texts:
            # Simple word extraction (Russian and Latin letters)
            words = re.findall(r'\b[\u0400-\u04FFa-zA-Z]+\b', text.lower())
            all_words.extend([w for w in words if len(w) > 3 and w not in stopwords])
        
        word_counts = Counter(all_words)
        top_words = word_counts.most_common(20)
        
        if not top_words:
            return []
        
        # Group into simple "themes" based on top words
        themes = []
        for i, (word, count) in enumerate(top_words[:5]):
            # Find texts containing this word
            related_texts = [
                texts[j] for j, text in enumerate(texts)
                if word in text.lower()
            ][:3]
            
            themes.append({
                "id": i,
                "name": word,
                "count": count,
                "keywords": [word] + [w for w, _ in top_words if w != word][:4],
                "representative_texts": related_texts,
            })
        
        return themes

    async def extract_entities(self, text: str) -> List[dict[str, str]]:
        """Extract named entities from text."""
        if not self._spacy_available:
            logger.debug("spaCy not available, skipping entity extraction")
            return []

        try:
            import spacy
            
            # Load model if not already loaded
            if not hasattr(self, '_spacy_nlp'):
                try:
                    self._spacy_nlp = spacy.load("ru_core_news_md")
                except OSError:
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
        """Analyze sentiment of text."""
        # Simple rule-based sentiment for Russian
        positive_words = [
            "хороший", "отличный", "прекрасный", "удобный", "эффективный",
            "доволен", "рекомендую", "помогает", "улучшил", "быстро",
            "качественно", "надежный", "выгодно", "экономит", "решил",
            "good", "great", "excellent", "helpful", "effective", "fast",
            "reliable", "beneficial", "saves", "solved", "recommend",
        ]
        negative_words = [
            "плохой", "ужасный", "неудобный", "дорого", "медленно",
            "проблема", "ошибка", "не работает", "разочарован", "сложно",
            "недоволен", "не рекомендую", "жаль", "утратил", "потеря",
            "bad", "terrible", "uncomfortable", "expensive", "slow",
            "problem", "error", "not working", "disappointed", "difficult",
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
        """Generate summary of multiple responses."""
        if not texts:
            return ""

        all_text = " ".join(texts)
        sentences = all_text.split(".")

        summary = ". ".join(sentences[:3]).strip()
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary
