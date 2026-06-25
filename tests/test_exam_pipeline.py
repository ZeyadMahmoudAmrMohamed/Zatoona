import os
os.environ["USE_REAL_EXAM"] = "true"

from agents.exam_loader import load_exam

def test_real_exam():
    exam = load_exam(
        session_id="session_001",
        topics=["World War 2", "The French Revolution"],
        num_questions=5
    )
    print(f"Got exam with {len(exam.questions)} questions")
    for q in exam.questions:
        print(f"  - {q.question}")

if __name__ == "__main__":
    test_real_exam()