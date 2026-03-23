"""Prompt builders for agent personas."""

from schemas.agent import AgentConfig, CommunicationStyle, RiskAppetite


class PromptBuilder:
    """Builds system prompts and user prompts for agent simulations."""

    @staticmethod
    def build_system_prompt(config: AgentConfig) -> str:
        """Build system prompt from agent config."""
        dm = config.decision_maker

        style_desc = {
            CommunicationStyle.FORMAL: "формальном и деловом",
            CommunicationStyle.INFORMAL: "неформальном и разговорном",
            CommunicationStyle.MIXED: "сбалансированном, адаптирующемся к ситуации",
        }[dm.communication_style]

        risk_desc = {
            RiskAppetite.LOW: "консервативный, избегающий рисков",
            RiskAppetite.MEDIUM: "умеренный, взвешивающий риски и возможности",
            RiskAppetite.HIGH: "склонный к риску, ориентированный на рост",
        }[dm.risk_appetite]

        pain_points_text = "\n".join(f"- {p}" for p in config.pain_points)
        values_text = "\n".join(f"- {v}" for v in config.values)

        prompt = f"""Ты — {dm.role} в компании «{config.company_name}» ({config.legal_type}).

## О компании
- Отрасль: {config.industry}
- Размер: {config.size}
- Регион: {config.region}
- Годовая выручка: {config.annual_revenue}
- Цифровая зрелость: {config.digital_maturity}/5

## О принимающем решения
- Возраст: {dm.age} лет
- Пол: {'мужской' if dm.gender == 'male' else 'женский'}
- Образование: {dm.education}
- Тип личности (MBTI): {dm.mbti}
- Стиль коммуникации: {style_desc}
- Отношение к риску: {risk_desc}

## Болевые точки
{pain_points_text}

## Ценности компании
{values_text}

## Чувствительность к бюджету
{config.budget_sensitivity.value}

Твоя задача — отвечать на вопросы опроса исключительно с точки зрения этой персоны. Отвечай так, как ответил бы реальный человек с такими характеристиками в контексте своего бизнеса."""

        return prompt

    @staticmethod
    def build_quantitative_prompt(
        question_text: str,
        min_value: int,
        max_value: int,
        min_label: str | None = None,
        max_label: str | None = None,
    ) -> str:
        """Build prompt for quantitative question."""
        scale_desc = f"Шкала: {min_value} ({min_label or 'минимум'}) — {max_value} ({max_label or 'максимум'})"

        return f"""Вопрос: {question_text}

{scale_desc}

Сначала объясни своё рассуждение (chain-of-thought), затем дай окончательный ответ в формате JSON:
{{
  "reasoning": "твоё рассуждение от первого лица (2-3 предложения)",
  "response_value": число от {min_value} до {max_value}
}}"""

    @staticmethod
    def build_qualitative_prompt(
        question_text: str,
        min_words: int = 150,
        max_words: int = 400,
    ) -> str:
        """Build prompt for qualitative question."""
        return f"""Вопрос: {question_text}

Дай развёрнутый ответ объёмом {min_words}-{max_words} слов, пиши от первого лица как {config.decision_maker.role}. 

Сначала обдумай вопрос (внутренний монолог, 2-3 предложения), затем напиши финальный ответ.

Верни результат в формате JSON:
{{
  "reasoning": "внутренний монолог перед ответом",
  "answer_text": "твой развёрнутый ответ на вопрос"
}}"""


class AgentPromptBuilder(PromptBuilder):
    """Prompt builder with agent config context."""

    def __init__(self, config: AgentConfig):
        """Initialize with agent config."""
        self.config = config

    def build_qualitative_prompt(
        self,
        question_text: str,
        min_words: int = 150,
        max_words: int = 400,
    ) -> str:
        """Build prompt for qualitative question with config context."""
        return f"""Вопрос: {question_text}

Дай развёрнутый ответ объёмом {min_words}-{max_words} слов, пиши от первого лица как {self.config.decision_maker.role} компании «{self.config.company_name}».

Сначала обдумай вопрос (внутренний монолог, 2-3 предложения), затем напиши финальный ответ.

Верни результат в формате JSON:
{{
  "reasoning": "внутренний монолог перед ответом",
  "answer_text": "твой развёрнутый ответ на вопрос"
}}"""
