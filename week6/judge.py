import json

from pydantic import BaseModel
from typing import Literal
from pydantic_ai import Agent


class JudgeEvaluation(BaseModel):
    reasoning: str
    label: Literal["good", "bad"]


judge_instructions = """You are an expert evaluator assessing a recipe assistant that answers
cooking questions using a fixed recipe collection of 15 recipes.

A response is "good" if ANY of these apply:
1. It accurately presents recipe information (ingredients, times, steps) from the collection
2. It correctly says a recipe is not in the collection — even if it politely offers
   to suggest alternatives or similar recipes from the collection
3. It correctly declines out-of-scope questions (not about cooking/recipes)
4. It correctly answers dietary questions (vegetarian, vegan, dairy) based on the
   ingredient list in the recipe — factual statements about ingredients
   (e.g. "feta is dairy", "anchovy paste is not vegetarian") are NOT hallucination

A response is "bad" if ANY of these apply:
1. It invents specific recipes, ingredients, or step-by-step instructions not in the collection
2. It gives specific cooking advice (substitution ratios, nutrition counts, storage durations)
   that it made up rather than found in the recipe data
3. It claims a recipe does not exist when a matching recipe is actually in the collection
4. It gives verifiably wrong details from a recipe (wrong temperature, wrong cook time,
   wrong ingredients for a recipe that IS in the collection)

Key distinctions:
- Saying "I don't have a sushi recipe, but I can suggest alternatives" is GOOD
- Saying "almond milk works as a 1:1 substitute" when the recipe doesn't mention it is BAD
- Saying "this recipe contains butter, so it is not vegan" is GOOD (factual, from ingredients)
- Saying "you can store leftovers for 3-5 days" when the recipe doesn't say this is BAD
- Offering to help find alternatives after a correct refusal is GOOD, not hallucination
"""

with open('recipes.json') as f:
    _recipes = json.load(f)

RECIPE_NAMES = ', '.join(r['name'] for r in _recipes)

judge_agent = Agent(
    'openai:gpt-4o-mini',
    output_type=JudgeEvaluation,
    instructions=judge_instructions,
)

with open('results.json') as f:
    results = json.load(f)

for i, row in enumerate(results):
    prompt = f"""The recipe collection contains EXACTLY these 15 recipes:
{RECIPE_NAMES}

Any recipe NOT in this list does not exist in the collection.
Any recipe IN this list does exist — treat information about it as potentially correct.

Question: {row['question']}
Agent response: {row['output']}"""

    evaluation = judge_agent.run_sync(prompt)
    row['judge_label'] = evaluation.output.label
    row['judge_reasoning'] = evaluation.output.reasoning
    print(f"[{i+1}/{len(results)}] {row['judge_label']}: {row['question']}")

with open('results_judged.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved judged results to results_judged.json")
