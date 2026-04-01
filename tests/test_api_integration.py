import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from memora.llm import get_llm_client
from memora.embeddings import get_text_embedding, get_text_embeddings
from memora.config import LLM_MODEL, EMBEDDING_MODEL


def test_llm_chat():
    print("\n=== Testing LLM Chat ===")
    client = get_llm_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": "你好，请回复 'LLM调用成功'"}
        ],
    )
    content = response.choices[0].message.content
    print(f"LLM Response: {content}")
    assert "成功" in content, f"Expected '成功' in response, got: {content}"
    print("LLM Chat Test PASSED")


def test_embedding_single():
    print("\n=== Testing Single Embedding ===")
    embedding = get_text_embedding("今天天气真好")
    print(f"Embedding dimension: {len(embedding)}")
    assert len(embedding) > 0, "Embedding should not be empty"
    print("Single Embedding Test PASSED")


def test_embedding_batch():
    print("\n=== Testing Batch Embeddings ===")
    texts = ["今天是星期一", "明天是星期二", "后天是星期三"]
    embeddings = get_text_embeddings(texts)
    print(f"Number of embeddings: {len(embeddings)}")
    assert len(embeddings) == 3, f"Expected 3 embeddings, got {len(embeddings)}"
    for i, emb in enumerate(embeddings):
        print(f"  Embedding {i+1} dimension: {len(emb)}")
        assert len(emb) > 0, f"Embedding {i+1} should not be empty"
    print("Batch Embeddings Test PASSED")


def test_embedding_similarity():
    print("\n=== Testing Embedding Similarity ===")
    from memora.embeddings import cosine_similarity

    emb1 = get_text_embedding("我喜欢吃苹果")
    emb2 = get_text_embedding("苹果是一种水果")
    emb3 = get_text_embedding("今天天气很好")

    sim_12 = cosine_similarity(emb1, emb2)
    sim_13 = cosine_similarity(emb1, emb3)

    print(f"Similarity between '我喜欢吃苹果' and '苹果是一种水果': {sim_12:.4f}")
    print(f"Similarity between '我喜欢吃苹果' and '今天天气很好': {sim_13:.4f}")

    assert sim_12 > sim_13, "Similar sentences should have higher similarity"
    print("Embedding Similarity Test PASSED")


if __name__ == "__main__":
    try:
        test_llm_chat()
        test_embedding_single()
        test_embedding_batch()
        test_embedding_similarity()
        print("\n" + "=" * 50)
        print("ALL API TESTS PASSED!")
        print("=" * 50)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
