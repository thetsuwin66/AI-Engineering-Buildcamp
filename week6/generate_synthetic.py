"""Bonus: Generate synthetic evaluation scenarios for all 15 recipes."""
import csv
import json
from pydantic import BaseModel
from pydantic_ai import Agent


class Question(BaseModel):
    question: str
    category: str
    type: str


class GeneratedQuestions(BaseModel):
    questions: list[Question]


generator = Agent(
    'openai:gpt-4o-mini',
    output_type=GeneratedQuestions,
    instructions="Generate evaluation questions for a recipe assistant.",
)


def generate_for_recipe(recipe: dict) -> list[dict]:
    prompt = f"""Given this recipe, generate exactly 5 questions a user might ask the recipe assistant.
Include one of each type:
1. factual - "What ingredients do I need for X?"
2. how-to - "How do I make X?"
3. detail - a specific detail question (temperature, time, servings, etc.)
4. substitution - "Can I replace Y with Z in X?"
5. comparison - compare X with another dish or technique

Recipe: {recipe['name']}
Cuisine: {recipe['cuisine']}
Difficulty: {recipe['difficulty']}
Ingredients: {', '.join(recipe['ingredients'])}
Instructions: {recipe['instructions']}"""

    result = generator.run_sync(prompt)
    return [q.model_dump() for q in result.output.questions]


def main():
    with open("recipes.json") as f:
        recipes = json.load(f)

    all_questions = []

    for i, recipe in enumerate(recipes):
        print(f"[{i+1}/{len(recipes)}] Generating questions for: {recipe['name']}")
        questions = generate_for_recipe(recipe)
        all_questions.extend(questions)
        print(f"  Generated {len(questions)} questions")

    with open("synthetic_scenarios.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "category", "type"])
        writer.writeheader()
        writer.writerows(all_questions)

    print(f"\nSaved {len(all_questions)} synthetic scenarios to synthetic_scenarios.csv")


if __name__ == "__main__":
    main()
