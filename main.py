from retriever import Retriever
from vectorstore_chroma_db import VectorStore
from rag_chat import answer_question
from memory import ConversationManager


def main():
    print("loading Vector Store... with knowledge base")
    store = VectorStore()
    retriever = Retriever(store)
    memory = ConversationManager()

    print("Insurellm Knowledge Assistant — ask about company, contracts, employees, or products.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("you: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Exiting...")
            break

        try: 
            answer = answer_question(memory, retriever, question)
        except Exception as e:
            print(f"[Error] Something went wrong: {e}\n")
            continue

        print(f"\nassistant: {answer}\n")

if __name__ == "__main__":
    main()