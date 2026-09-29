"""Small, sequential runner for the fixed Day 7 prompt evaluation."""

import json
from datetime import datetime, timezone

from openai import OpenAIError

MODEL = "gpt-4o-mini"
ALLOWED_VALUES = {
    "feedback_type": ["Feature Request", "Usability Issue", "Bug", "Positive Feedback", "Other"],
    "product_theme": ["Onboarding", "Performance", "Navigation", "Reporting", "Integrations", "Billing", "Permissions", "Reliability", "Other"],
    "severity": ["High", "Medium", "Low"],
}
SCHEMA = {
    "type": "object",
    "properties": {
        field: {"type": "string", "enum": values}
        for field, values in ALLOWED_VALUES.items()
    },
    "required": list(ALLOWED_VALUES),
    "additionalProperties": False,
}


def compare_result(case, actual, error=""):
    """Build one table row. Missing answers fail scored fields."""
    row = {
        "case_id": case["case_id"],
        "feedback_text": case["feedback_text"],
    }
    failed_fields = []
    unscored = False
    for field in ALLOWED_VALUES:
        expected = case["expected"][field]
        value = actual.get(field)
        if expected is None:
            match = "Not scored"
            unscored = True
        elif value == expected:
            match = "Pass"
        else:
            match = "Fail"
            failed_fields.append(field)
        row[f"expected_{field}"] = expected
        row[f"actual_{field}"] = value
        row[f"{field}_match"] = match

    row["failed_fields"] = ", ".join(failed_fields) or "None"
    if error:
        row["overall"] = "Error"
    elif failed_fields:
        row["overall"] = "Fail"
    elif unscored:
        row["overall"] = "Partial"
    else:
        row["overall"] = "Pass"
    row["error"] = error
    row["evaluation_note"] = case.get("evaluation_note") or ""
    return row


def field_accuracy(results):
    """Exclude null expectations; failed requests still count as non-matches."""
    summary = {}
    for field in ALLOWED_VALUES:
        scored = [row for row in results if row[f"{field}_match"] != "Not scored"]
        passed = sum(row[f"{field}_match"] == "Pass" for row in scored)
        summary[field] = {"passed": passed, "scored": len(scored)}
    return summary


def run_evaluation(client, prompt_path, cases_path, on_progress=None):
    # Read once so every case in this run uses exactly the same prompt text.
    prompt = prompt_path.read_text(encoding="utf-8")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    started_at = datetime.now(timezone.utc).isoformat()
    results = []

    for index, case in enumerate(cases, start=1):
        actual = {}
        error = ""
        try:
            # Expected answers and evaluation notes are never sent to the API.
            response = client.responses.create(
                model=MODEL,
                instructions=prompt,
                input=case["feedback_text"],
                text={"format": {
                    "type": "json_schema",
                    "name": "feedback_classification",
                    "strict": True,
                    "schema": SCHEMA,
                }},
                store=False,
            )
            if response.status != "completed" or not response.output_text:
                raise ValueError("The model did not return a complete classification.")
            parsed = json.loads(response.output_text)
            if not isinstance(parsed, dict) or set(parsed) != set(ALLOWED_VALUES):
                raise ValueError("The response must contain exactly the three classification fields.")
            for field, allowed in ALLOWED_VALUES.items():
                if parsed[field] not in allowed:
                    raise ValueError(f"Invalid value for {field}.")
            actual = parsed
        except OpenAIError as exc:
            # Avoid exposing raw request data or credentials in the results.
            error = f"OpenAI request failed ({type(exc).__name__})."
        except ValueError as exc:
            error = str(exc)

        row = compare_result(case, actual, error)
        row.update(prompt_file=prompt_path.name, model=MODEL, run_time=started_at)
        results.append(row)
        if on_progress is not None:
            on_progress(index, len(cases))

    return results
