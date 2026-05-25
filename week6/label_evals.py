"""Simple terminal labeling tool for results.json.

Usage: python label_evals.py
Saves labels to labels.json
"""
import json


def load_existing_labels(path="labels.json") -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_labels(labels: dict, path="labels.json"):
    with open(path, "w") as f:
        json.dump(labels, f, indent=2)
    print(f"Saved {len(labels)} labels to {path}")


def main():
    with open("results.json") as f:
        results = json.load(f)

    labels = load_existing_labels()
    total = len(results)

    print(f"\nLoaded {total} results. {len(labels)} already labeled.\n")
    print("For each response, enter: g=good  b=bad  s=skip  q=quit\n")
    print("-" * 70)

    for i, row in enumerate(results):
        question = row["question"]

        # Skip already labeled unless re-labeling
        if question in labels:
            continue

        print(f"\n[{i+1}/{total}] Category: {row['category']} | Type: {row['type']}")
        print(f"Q: {question}")
        print(f"\nA: {row['output']}")
        print()

        while True:
            choice = input("Label [g=good / b=bad / s=skip / q=quit]: ").strip().lower()
            if choice in ("g", "b", "s", "q"):
                break
            print("  Please enter g, b, s, or q")

        if choice == "q":
            save_labels(labels)
            break
        elif choice == "s":
            continue
        else:
            label = "good" if choice == "g" else "bad"
            failure_note = ""
            if label == "bad":
                failure_note = input("  Why bad? (hallucination/wrong-scope/incomplete/wrong-detail): ").strip()
            labels[question] = {"label": label, "failure_note": failure_note}
            print(f"  Saved: {label}")

        if (i + 1) % 5 == 0:
            save_labels(labels)
            print(f"  Auto-saved after {i+1} labels.")

    save_labels(labels)

    good = sum(1 for v in labels.values() if v["label"] == "good")
    bad = sum(1 for v in labels.values() if v["label"] == "bad")
    print(f"\nSummary: {good} good, {bad} bad out of {len(labels)} labeled")


if __name__ == "__main__":
    main()
