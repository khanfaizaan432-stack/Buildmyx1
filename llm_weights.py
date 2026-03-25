"""
Gemini-powered objective weight selection.
"""

# pyright: reportMissingImports=false

import json
import os
from typing import Iterable, Dict, Any

DEFAULT_QUALITY_WEIGHT = 0.60
DEFAULT_TACTIC_WEIGHT = 0.40


def _normalize_weights(quality_weight: Any, tactic_weight: Any) -> Dict[str, float]:
    """Clamp and normalize weights so they are valid and sum to 1.0."""
    try:
        q = float(quality_weight)
    except (TypeError, ValueError):
        q = DEFAULT_QUALITY_WEIGHT

    try:
        t = float(tactic_weight)
    except (TypeError, ValueError):
        t = DEFAULT_TACTIC_WEIGHT

    q = max(0.0, min(1.0, q))
    t = max(0.0, min(1.0, t))

    total = q + t
    if total <= 0:
        return {
            "quality_weight": DEFAULT_QUALITY_WEIGHT,
            "tactic_weight": DEFAULT_TACTIC_WEIGHT,
        }

    return {
        "quality_weight": round(q / total, 4),
        "tactic_weight": round(t / total, 4),
    }


def format_weight_prompt(user_text: str, dataframe_columns: Iterable[str]) -> str:
    """Build the prompt sent to Gemini using user intent + available data schema."""
    cols = sorted({str(c).strip() for c in dataframe_columns if str(c).strip()})
    cols_blob = ", ".join(cols)

    return (
        "You are selecting objective weights for a football XI optimizer.\n"
        "User goal:\n"
        f"{user_text.strip() or 'No explicit goal provided.'}\n\n"
        "Available dataframe columns:\n"
        f"{cols_blob}\n\n"
        "Choose weights for only two factors: quality_final and tactic fit.\n"
        "Return strict JSON with this exact schema:\n"
        "{\n"
        "  \"quality_weight\": number,\n"
        "  \"tactic_weight\": number,\n"
        "  \"rationale\": string\n"
        "}\n"
        "Rules:\n"
        "- Both weights must be between 0 and 1.\n"
        "- Weights must sum to 1.\n"
        "- Output JSON only, no markdown."
    )


def decide_weights_with_gemini(
    user_text: str,
    dataframe_columns: Iterable[str],
    model_name: str = "gemini-2.0-flash",
    api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Call Gemini and return normalized optimizer weights.

    Returns dict with keys:
    - quality_weight
    - tactic_weight
    - rationale
    - source ("gemini" or "fallback")
    """
    prompt = format_weight_prompt(user_text, dataframe_columns)

    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        fallback = _normalize_weights(DEFAULT_QUALITY_WEIGHT, DEFAULT_TACTIC_WEIGHT)
        return {
            **fallback,
            "rationale": "GEMINI_API_KEY not set; using default weights.",
            "source": "fallback",
        }

    try:
        # Prefer the modern Google Gen AI SDK.
        genai_mod = __import__("google.genai", fromlist=["Client", "types"])
        client = genai_mod.Client(api_key=key)
        genai_types = genai_mod.types
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        parsed = json.loads(response.text)
        normalized = _normalize_weights(
            parsed.get("quality_weight"),
            parsed.get("tactic_weight"),
        )

        return {
            **normalized,
            "rationale": str(parsed.get("rationale", "LLM-selected weights.")),
            "source": "gemini",
        }
    except Exception as primary_exc:
        try:
            # Backward-compatible fallback for older SDK availability.
            legacy = __import__("google.generativeai", fromlist=["GenerativeModel"])
            legacy.configure(api_key=key)
            model = legacy.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            parsed = json.loads(response.text)
            normalized = _normalize_weights(
                parsed.get("quality_weight"),
                parsed.get("tactic_weight"),
            )
            return {
                **normalized,
                "rationale": str(parsed.get("rationale", "LLM-selected weights.")),
                "source": "gemini",
            }
        except Exception as fallback_exc:
            fallback = _normalize_weights(DEFAULT_QUALITY_WEIGHT, DEFAULT_TACTIC_WEIGHT)
            return {
                **fallback,
                "rationale": (
                    f"Gemini call failed ({primary_exc}); legacy fallback failed "
                    f"({fallback_exc}); using default weights."
                ),
                "source": "fallback",
            }
