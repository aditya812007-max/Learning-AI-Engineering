"""A small tool-calling agent powered by Groq and Tavily.

Install dependencies:
    pip install groq tavily-python python-dotenv

Add this to .env:
    GROQ_API_KEY=...
    tavily_api_key=...
"""

import ast
import json
import math
import operator
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# The lowercase name is supported exactly as requested; uppercase is convenient
# on systems where environment-variable names are case-sensitive.
TAVILY_API_KEY = os.getenv("tavily_api_key") or os.getenv("TAVILY_API_KEY")
MODEL = "openai/gpt-oss-120b"


def web_search(query: str) -> str:
    """Search the web with Tavily and return a concise, sourced result."""
    if not TAVILY_API_KEY:
        return "Tavily is not configured. Add tavily_api_key to your .env file."

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        result = client.search(query=query, search_depth="basic", max_results=5)
        results = result.get("results", [])
        if not results:
            return "No web results found."

        return "\n\n".join(
            f"{item.get('title', 'Untitled')}\n"
            f"{item.get('content', '')}\n"
            f"Source: {item.get('url', '')}"
            for item in results
        )
    except Exception as error:
        return f"Web search failed: {error}"


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CONSTANTS = {"pi": math.pi, "e": math.e}


def _evaluate_math(node: ast.AST) -> float | int:
    """Evaluate only arithmetic AST nodes; never execute arbitrary Python."""
    if isinstance(node, ast.Expression):
        return _evaluate_math(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_math(node.left)
        right = _evaluate_math(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_math(node.operand))
    raise ValueError("Only basic arithmetic (+, -, *, /, //, %, **), parentheses, pi, and e are allowed.")


def calculate(expression: str) -> str:
    """Calculate a basic mathematical expression supplied as a string."""
    try:
        if len(expression) > 500:
            raise ValueError("Expression is too long.")
        tree = ast.parse(expression, mode="eval")
        return str(_evaluate_math(tree))
    except Exception as error:
        return f"Calculation failed: {error}"


# OpenAI-compatible tool schema used by Groq.
tools: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information and return relevant results with sources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The web-search query.",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a basic mathematical expression, for example '(18 * 7) / 3'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A basic arithmetic expression to calculate.",
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]

TOOL_FUNCTIONS = {"web_search": web_search, "calculate": calculate}


def run_agent(user_input: str) -> str:
    """Send any user question to the model and complete requested tool calls."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    client = Groq(api_key=GROQ_API_KEY)
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use web_search for current facts and calculate for arithmetic. Give a clear final answer.",
        },
        {"role": "user", "content": user_input},
    ]

    # A loop supports a model calling one or both tools before it responds.
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or "I could not produce a response."

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
                function = TOOL_FUNCTIONS[function_name]
                result = function(**arguments)
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                result = f"Tool call failed: {error}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result,
                }
            )


if __name__ == "__main__":
    question = input("Ask me anything: ").strip()
    if question:
        print(run_agent(question))
