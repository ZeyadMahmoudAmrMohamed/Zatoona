import os
os.environ["USE_REAL_EXAM"] = "true"

from agents.exam_loader import load_exam

def test_real_exam():
    exam = load_exam(
        session_id="test-session-001",
        topics=["ai", "python"],
        num_questions=3
    )
    print(f"\nGot exam with {len(exam.questions)} questions — status: {exam.status}")
    for q in exam.questions:
        print(f"  - [{q.topic}] {q.question}")

if __name__ == "__main__":
    test_real_exam()