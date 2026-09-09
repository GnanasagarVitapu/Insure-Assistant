
SYSTEM_MESSAGE = {"role": "system", "content": """You are a helpful assistant answering questions about Insurellm — 
its company info, contracts, employees, and products.

Answer ONLY using the context provided below. If the context doesn't contain 
enough information to answer confidently, say so explicitly rather than guessing 
or using outside knowledge.

Always cite which document/section your answer comes from.
"""}

class ConversationManager:
    def __init__(self, max_turns: int = 5):
        self.system_prompt = SYSTEM_MESSAGE
        self.max_turns = max_turns
        self.history = []

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})

    def get_history(self):
        return [self.system_prompt] + self._trim(self.history)

    def _trim(self, history):
        max_entries = self.max_turns * 2
        if len(history) > max_entries:
            return history[-max_entries:]
        return history

