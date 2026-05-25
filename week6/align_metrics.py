"""Q5: Measure alignment between human labels and LLM judge labels."""
import json


def load_data():
    with open("results_judged.json") as f:
        judged = json.load(f)
    with open("labels.json") as f:
        human_labels = json.load(f)
    return judged, human_labels


def compute_metrics(judged, human_labels):
    tp = fp = fn = tn = 0
    disagreements = []

    for row in judged:
        question = row["question"]
        if question not in human_labels:
            continue

        judge = row["judge_label"]
        human = human_labels[question]["label"]

        if judge == "bad" and human == "bad":
            tp += 1
        elif judge == "bad" and human == "good":
            fp += 1
            disagreements.append(row)
        elif judge == "good" and human == "bad":
            fn += 1
            disagreements.append(row)
        else:
            tn += 1

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total,
        "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1,
    }, disagreements


def print_almond_milk_comparison(judged, human_labels):
    keyword = "almond milk"
    for row in judged:
        if keyword in row["question"].lower():
            q = row["question"]
            human = human_labels.get(q, {})
            print(f"\n=== Almond Milk Substitution Scenario ===")
            print(f"Question: {q}")
            print(f"Human label:   {human.get('label', 'not labeled')}")
            if human.get('failure_note'):
                print(f"Human note:    {human['failure_note']}")
            print(f"Judge label:   {row['judge_label']}")
            print(f"Judge reasoning: {row['judge_reasoning']}")
            agreed = human.get('label') == row['judge_label']
            print(f"Agreement: {'YES' if agreed else 'NO'}")
            break


def main():
    judged, human_labels = load_data()
    metrics, disagreements = compute_metrics(judged, human_labels)

    print("=== Alignment Metrics (Q5) ===")
    print(f"Total compared: {metrics['total']}")
    print(f"  TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}  TN={metrics['tn']}")
    print(f"Accuracy:  {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}  (judge 'bad' → how often correct)")
    print(f"Recall:    {metrics['recall']:.2%}  (actual 'bad' → how often judge catches it)")
    print(f"F1:        {metrics['f1']:.2%}")
    print(f"\nDisagreements: {len(disagreements)}")

    if disagreements:
        print("\n=== Disagreements ===")
        for row in disagreements:
            q = row["question"]
            human = human_labels.get(q, {})
            print(f"\nQ: {q}")
            print(f"  Human: {human.get('label')} | Judge: {row['judge_label']}")
            print(f"  Judge reasoning: {row['judge_reasoning'][:200]}...")

    print_almond_milk_comparison(judged, human_labels)


if __name__ == "__main__":
    main()
