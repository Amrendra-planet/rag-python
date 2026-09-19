from src.agent import answer_question

if __name__ == "__main__":
    question = input("Ask an operational question: ")
    print(answer_question(question))
