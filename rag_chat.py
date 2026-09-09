import config
from retriever import Retriever
from vectorstore import VectorStore
from memory import ConversationManager



def format_context(results):
    context_blocks = []
    for score, chunk in results:
        context_blocks.append(
            f"[Source: {chunk['document_name']} - {chunk['section']}]\n{chunk['chunk_text']}"
            )
    return "\n\n--\n\n".join(context_blocks)

def answer_question(memory: ConversationManager, retriever: Retriever, question: str, top_k:int=5):
    rewritten_prompt = rewrite_question(memory.get_history(), question)
    results = retriever.retrieve(rewritten_prompt, top_k=top_k)
    context = format_context(results)

    augmented_prompt = f"context:{context}\n\n Question: {rewritten_prompt}"

    messages = memory.get_history() + [{"role": "user", "content": augmented_prompt}]
    
    
    response = config.client.chat.completions.create(
        model=config.model_name,
        messages=messages
    )
    memory.add_user_message(question)
    memory.add_assistant_message(response.choices[0].message.content)
    return response.choices[0].message.content


def format_history_for_rewrite(history: list) -> str:
    lines = []
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            lines.append(f"{msg['role'].capitalize()}: {msg['content']}")
    return "\n".join(lines)

def rewrite_question(history: list, new_question: str):
    formatted_history = format_history_for_rewrite(history)
    rewrite_prompt = f"""
    Given the conversation history below, rewrite the final 
question into a fully self-contained question that doesn't rely on any prior 
context (resolve pronouns like "he/she/it/his/her" into the actual name/entity).

If the question is already self-contained, return it unchanged.

Conversation history:
{formatted_history}

Final question: {new_question}

Rewritten question:"""

    result = config.emb_client.chat.completions.create(
        model = config.model_name,
        messages = [{"role": "user", "content": rewrite_prompt}]
    )

    return result.choices[0].message.content.strip()