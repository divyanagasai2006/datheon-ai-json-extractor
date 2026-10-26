
import ast
import operator
import os
from pathlib import Path

from dotenv import load_dotenv
from ddgs import DDGS
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# Load API key from .env
load_dotenv()

# Store files inside the workspace folder
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = (BASE_DIR / "workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)

# Create a sample file if it does not exist
sample_file = WORKSPACE / "notes.txt"

if not sample_file.exists():
    sample_file.write_text(
        "Python is a programming language.\n"
        "Generative AI can create text and other content.\n"
        "RAG retrieves relevant documents before generating an answer.\n",
        encoding="utf-8",
    )


# Safe arithmetic operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):
    """Calculate arithmetic expressions without using eval()."""

    if len(expression) > 200:
        raise ValueError("Expression is too long.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Only numbers are allowed.")

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)

            if operator_type not in OPERATORS:
                raise ValueError("Unsupported operator.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")

            result = OPERATORS[operator_type](left, right)

            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)

            if operator_type not in OPERATORS:
                raise ValueError("Unsupported unary operator.")

            return OPERATORS[operator_type](evaluate(node.operand))

        raise ValueError("Invalid arithmetic expression.")

    return evaluate(tree)


# TOOL 1: Python calculator
@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression using Python.
    Use this tool for arithmetic calculations.
    Example: (250 * 4) + 100
    """

    try:
        result = safe_calculate(expression)
        return f"Calculation: {expression} = {result}"
    except Exception as error:
        return f"Calculation error: {error}"


# TOOL 2: Real-time web search
@tool
def web_search(query: str) -> str:
    """Search the web for current information.
    Use this tool when the user asks for recent facts, latest versions,
    current information, or information that needs online research.
    """

    try:
        with DDGS() as search_engine:
            results = list(
                search_engine.text(query, max_results=5)
            )

        if not results:
            return "No web search results were found."

        formatted_results = []

        for number, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            body = result.get("body", "No description")
            url = result.get("href", "")

            formatted_results.append(
                f"{number}. {title}\n"
                f"Description: {body}\n"
                f"URL: {url}"
            )

        return "\n\n".join(formatted_results)

    except Exception as error:
        return f"Web search error: {error}"


# TOOL 3: Local file reader
@tool
def read_local_file(filename: str) -> str:
    """Read a local .txt, .md, or .csv file from the workspace folder.
    Use this tool when the user asks to read or summarize a local file.
    Example filename: notes.txt
    """

    try:
        requested_path = (WORKSPACE / filename).resolve()

        # Prevent reading files outside the workspace
        if not requested_path.is_relative_to(WORKSPACE):
            return "Error: Access outside the workspace is not allowed."

        if requested_path.suffix.lower() not in {".txt", ".md", ".csv"}:
            return "Error: Only .txt, .md, and .csv files are supported."

        if not requested_path.is_file():
            return (
                f"Error: File '{filename}' was not found in the workspace."
            )

        content = requested_path.read_text(encoding="utf-8")

        if not content.strip():
            return f"The file '{filename}' is empty."

        if len(content) > 15000:
            content = content[:15000] + "\n...[Content truncated]"

        return f"Contents of {filename}:\n{content}"

    except UnicodeDecodeError:
        return "Error: The file is not readable as UTF-8 text."
    except Exception as error:
        return f"File reading error: {error}"


# Check API key
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY was not found. Check your .env file."
    )


# Initialize Gemini
model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest"
)

# Create the AI agent with all three tools
agent = create_agent(
    model=model,
    tools=[calculator, web_search, read_local_file],
    system_prompt=(
        "You are a helpful multi-tool AI assistant. "
        "Use the calculator for arithmetic, web_search for current "
        "online information, and read_local_file for local documents. "
        "Use tools when needed instead of guessing. "
        "For questions requiring multiple steps, use the necessary "
        "tools in sequence and combine their results. "
        "Include source URLs when using web search results. "
        "Clearly explain the final answer using the tool results. "
        "Do not claim a tool succeeded if it returned an error. "
        "Do not reveal hidden reasoning. You may briefly describe "
        "which tools you used and what they returned."
    ),
)


# Run the console assistant
def main():
    print("=" * 55)
    print("       MULTI-TOOL AUTONOMOUS AI AGENT")
    print("=" * 55)
    print("Available tools: Calculator, Web Search, File Reader")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_query = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAgent stopped.")
            break

        if user_query.lower() in {"exit", "quit", "end"}:
            print("Agent: Goodbye!")
            break

        if not user_query:
            continue

        try:
            response = agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": user_query}
                    ]
                }
            )

            print("\n--- Tool Activity ---")

            for message in response["messages"]:
                # Show tool calls selected by the AI
                tool_calls = getattr(message, "tool_calls", [])

                for call in tool_calls:
                    print(f"\n[ACTION] Tool: {call.get('name', 'unknown')}")
                    print(f"[ACTION] Input: {call.get('args', {})}")

                # Show tool results without hidden metadata
                if getattr(message, "type", "") == "tool":
                    print(
                        f"\n[OBSERVATION] "
                        f"{message.name}:"
                    )
                    print(message.content)

            # Display only the final text answer
            final_message = response["messages"][-1]
            content = final_message.content

            print("\nAgent:")

            if isinstance(content, str):
                print(content)

            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            print(item.get("text", ""))
                    elif isinstance(item, str):
                        print(item)

            else:
                print(content)

            print()

        except Exception as error:
            print(f"\nAgent error: {error}\n")


if __name__ == "__main__":
    main()
