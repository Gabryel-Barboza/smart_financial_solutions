from .base_agent import BaseAgent


class TaxSpecialistAgent(BaseAgent):
    """Agente especialista responsável por cálculos e validação de impostos."""

    def __init__(self, *, current_session: dict[str, BaseAgent | str]):
        gemini_key = current_session.get('gemini_key')
        groq_key = current_session.get('groq_key')

        super().__init__(gemini_key=gemini_key, groq_key=groq_key)

    @classmethod
    async def create(self):
        return NotImplemented
