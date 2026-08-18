"""
Coder agent module using Claude API.

Generates code files from user prompts. In Phase 1, this is a single-agent
implementation. Phase 2 will add Planner and Debugger agents for multi-agent
orchestration.
"""

import os
import re
from anthropic import Anthropic


class CodeGenerationError(Exception):
    """Raised when code generation fails."""
    pass


def generate_files_from_prompt(prompt: str) -> dict[str, str]:
    """
    Generate code files from a user prompt using Claude.

    Args:
        prompt: User's description of the app to build

    Returns:
        Dictionary mapping filenames to their content

    Raises:
        CodeGenerationError: If API key is missing or generation fails
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise CodeGenerationError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your key from https://console.anthropic.com/"
        )

    client = Anthropic(api_key=api_key)

    system_prompt = """You are a code generation assistant. Your job is to generate complete, working web applications based on user prompts.

Generate HTML, CSS, and JavaScript files as needed. Always include:
1. An index.html file as the entry point
2. Inline CSS or separate CSS files for styling
3. JavaScript if needed for interactivity

Format your response with clear file markers:
```filename.ext
file content here
```

Example response format:
```index.html
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Hello World</h1>
    <script src="script.js"></script>
</body>
</html>
```

```style.css
body {
    font-family: sans-serif;
}
```

Generate clean, modern, functional code. Use semantic HTML, responsive CSS, and vanilla JavaScript.
Focus on making it work first, then making it look good."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract files from the response
        response_text = message.content[0].text
        files = _parse_files_from_response(response_text)

        if not files:
            raise CodeGenerationError(
                "No files were generated. The model may not have followed the expected format."
            )

        # Ensure we have at least an index.html
        if "index.html" not in files:
            raise CodeGenerationError(
                "Generated code must include an index.html file as the entry point."
            )

        return files

    except Exception as e:
        if isinstance(e, CodeGenerationError):
            raise
        raise CodeGenerationError(f"Failed to generate code: {str(e)}")


def _parse_files_from_response(response: str) -> dict[str, str]:
    """
    Parse code blocks from Claude's response into a files dictionary.

    Looks for patterns like:
    ```filename.ext
    content
    ```

    Args:
        response: Raw text response from Claude

    Returns:
        Dictionary mapping filenames to their content
    """
    files = {}

    # Pattern to match: ```filename.ext followed by content until next ``` or end
    pattern = r"```(\S+)\n(.*?)```"
    matches = re.finditer(pattern, response, re.DOTALL)

    for match in matches:
        filename = match.group(1).strip()
        content = match.group(2).strip()

        # Skip language markers that aren't filenames (like ```html, ```css)
        if "." not in filename:
            continue

        files[filename] = content

    return files