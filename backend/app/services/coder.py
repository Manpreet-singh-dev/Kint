"""
Coder agent service.

Generates code files from user prompts using a pluggable LLM provider.
The provider (Claude, Gemini, etc.) is injected via dependency injection,
making the CoderService provider-agnostic.

Phase 1: Single-agent implementation.
Phase 2 will add Planner and Debugger agents for multi-agent orchestration.
"""

import re
from typing import Dict
from app.core.exceptions import CodeGenerationError
from app.services.providers.base import LLMProvider


# Shared system prompt used by all LLM providers
SYSTEM_PROMPT = """You are a code generation assistant. Your job is to generate complete, working web applications based on user prompts.

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


class CoderService:
    """Service responsible for generating code via a pluggable LLM provider."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def generate_files(self, prompt: str) -> Dict[str, str]:
        """
        Generate code files from a user prompt.

        Args:
            prompt: User's description of the app to build

        Returns:
            Dictionary mapping filenames to their content

        Raises:
            CodeGenerationError: If generation fails or invalid response received
            ConfigurationError: If API key is missing
        """
        try:
            response_text = self.provider.generate_text(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
            )

            files = self._parse_files_from_response(response_text)

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

    def _parse_files_from_response(self, response: str) -> Dict[str, str]:
        """
        Parse code blocks from the LLM response into a files dictionary.

        Looks for patterns like:
        ```filename.ext
        content
        ```
        """
        files = {}
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
