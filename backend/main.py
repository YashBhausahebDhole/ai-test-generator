from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️ OPENAI_API_KEY not found in .env file")
    client = OpenAI(api_key=api_key)
    logger.info("✅ OpenAI client initialized")
except Exception as e:
    logger.error(f"❌ Error initializing OpenAI: {e}")
    client = None


# Models
class RequirementsInput(BaseModel):
    requirements: str
    test_type: str = "functional"  # functional | comprehensive | boundary


class TestCase(BaseModel):
    id: str
    title: str
    preconditions: str
    steps: list
    expected_result: str
    test_type: str
    priority: str | None = None   # NEW: High / Medium / Low


class TestsResponse(BaseModel):
    test_cases: list[TestCase]
    count: int


# Prompt templates
PROMPT_FUNCTIONAL = """You are an expert QA engineer. Given the following requirements, generate high-quality functional test cases.

Requirements:
{requirements}

Generate test cases in the following JSON format ONLY (no other text):
{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "Test case title",
      "preconditions": "What needs to be set up before running this test",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected_result": "What should happen",
      "test_type": "functional"
    }}
  ]
}}

Generate 5-8 test cases covering the main flows. Return ONLY valid JSON."""

PROMPT_COMPREHENSIVE = """You are an expert QA engineer. Given the following requirements, generate comprehensive test cases including functional, boundary, and negative test cases.

Requirements:
{requirements}

Generate test cases in the following JSON format ONLY (no other text):
{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "Test case title",
      "preconditions": "What needs to be set up before running this test",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected_result": "What should happen",
      "test_type": "functional"
    }}
  ]
}}

Include:
- Functional tests (happy path)
- Boundary tests (edge cases, limits)
- Negative tests (invalid inputs, error handling)

Generate 12-15 test cases total. Return ONLY valid JSON."""

PROMPT_BOUNDARY = """You are an expert QA engineer specializing in boundary value testing. Given the following requirements, generate boundary and edge case test cases.

Requirements:
{requirements}

Generate test cases in the following JSON format ONLY (no other text):
{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "Test case title",
      "preconditions": "What needs to be set up before running this test",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected_result": "What should happen",
      "test_type": "boundary"
    }}
  ]
}}

Focus on:
- Boundary values (min, max, just below, just above)
- Equivalence classes
- Edge cases

Generate 8-10 test cases. Return ONLY valid JSON."""

PROMPT_PRIORITY_WRAPPER = """You are an experienced test manager. You will assign a priority to each test case based on risk and business impact.

Priority rules:
- High: Payment, authentication, security, data loss, critical workflows.
- Medium: Important but not business critical.
- Low: Cosmetic, minor UX, non-critical optional features.

Given the following test cases in JSON, add a "priority" field with value "High", "Medium", or "Low" to each test case.

Return ONLY JSON with the same fields plus "priority".

Input test cases:
{test_cases_json}
"""


@app.get("/")
def read_root():
    return {
        "message": "✅ AI Test Generator API is running!",
        "version": "1.1",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "openai_configured": client is not None,
    }


def call_llm_for_json(prompt: str) -> dict:
    """Helper to call OpenAI and enforce JSON output."""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that ALWAYS returns valid JSON only. No markdown, no explanations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        text = response.choices[0].message.content.strip()

        # Remove markdown fences if any
        if "```json" in text:
            # Extract content inside ```json ... ```
            try:
                text = text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            except IndexError:
                # Fallback: remove all fences if splitting failed
                text = text.replace("```", "").strip()
        elif "```" in text:
            # Extract content inside ``` ... ```
            try:
                text = text.split("```", 1)[1].rsplit("```", 1)[0].strip()
            except IndexError:
                text = text.replace("```", "").strip()

        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM JSON: {e}")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail=f"Error calling LLM: {e}")


@app.post("/generate-tests", response_model=TestsResponse)
def generate_tests(input_data: RequirementsInput):
    """Generate test cases without priority tagging."""
    if not input_data.requirements.strip():
        raise HTTPException(status_code=400, detail="Requirements cannot be empty")

    logger.info(f"Generating tests ({input_data.test_type})")

    if input_data.test_type == "comprehensive":
        prompt = PROMPT_COMPREHENSIVE.format(requirements=input_data.requirements)
    elif input_data.test_type == "boundary":
        prompt = PROMPT_BOUNDARY.format(requirements=input_data.requirements)
    else:
        prompt = PROMPT_FUNCTIONAL.format(requirements=input_data.requirements)

    data = call_llm_for_json(prompt)

    test_cases: list[TestCase] = []
    for idx, tc in enumerate(data.get("test_cases", []), start=1):
        test_cases.append(
            TestCase(
                id=str(tc.get("id", f"TC{idx:03d}")),
                title=str(tc.get("title", f"Test Case {idx}")),
                preconditions=str(tc.get("preconditions", "N/A")),
                steps=tc.get("steps", []) if isinstance(tc.get("steps"), list) else ["N/A"],
                expected_result=str(tc.get("expected_result", "N/A")),
                test_type=str(tc.get("test_type", "functional")),
                priority=None,
            )
        )

    if not test_cases:
        raise HTTPException(status_code=500, detail="No test cases generated")

    return TestsResponse(test_cases=test_cases, count=len(test_cases))


@app.post("/generate-tests-priority", response_model=TestsResponse)
def generate_tests_with_priority(input_data: RequirementsInput):
    """
    Generate test cases and then run a second LLM pass to assign priority
    (High / Medium / Low) to each test.
    """
    # First, generate basic tests
    base_response = generate_tests(input_data)
    base_dict = base_response.model_dump()

    # Second, ask LLM to assign priority
    prompt = PROMPT_PRIORITY_WRAPPER.format(
        test_cases_json=json.dumps(base_dict, indent=2)
    )
    data_with_priority = call_llm_for_json(prompt)

    test_cases: list[TestCase] = []
    for idx, tc in enumerate(data_with_priority.get("test_cases", []), start=1):
        test_cases.append(
            TestCase(
                id=str(tc.get("id", f"TC{idx:03d}")),
                title=str(tc.get("title", f"Test Case {idx}")),
                preconditions=str(tc.get("preconditions", "N/A")),
                steps=tc.get("steps", []) if isinstance(tc.get("steps"), list) else ["N/A"],
                expected_result=str(tc.get("expected_result", "N/A")),
                test_type=str(tc.get("test_type", "functional")),
                priority=str(tc.get("priority", "Medium")),
            )
        )

    return TestsResponse(test_cases=test_cases, count=len(test_cases))


@app.post("/generate-tests-gherkin")
def generate_tests_gherkin(input_data: RequirementsInput):
    """Generate tests in Gherkin format (BDD style)."""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")

    prompt = f"""Convert these requirements into Gherkin-style test cases (Given-When-Then format).

Requirements:
{input_data.requirements}

Format each test case as:
Feature: Feature name
  Scenario: Scenario name
    Given [precondition]
    When [action]
    Then [expected result]

Generate 5-8 scenarios. Return ONLY Gherkin syntax, no explanations.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a BDD expert. Return only Gherkin syntax."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        gherkin_text = response.choices[0].message.content
        return {"gherkin": gherkin_text, "format": "Gherkin (BDD)"}
    except Exception as e:
        logger.error(f"Gherkin generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Gherkin: {e}")
    except Exception as e:
        logger.error(f"Gherkin generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Gherkin: {e}")


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting AI Test Generator API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
