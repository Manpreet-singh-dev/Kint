"""
Coder agent service using Claude API.

Generates code files from user prompts. In Phase 1, this is a single-agent
implementation. Phase 2 will add Planner and Debugger agents for multi-agent
orchestration.
"""

import re
from typing import Dict, Optional
from anthropic import Anthropic

from app.core.config import Settings, get_settings
from app.core.exceptions import CodeGenerationError, ConfigurationError


class CoderService:
    """Service responsible for generating code via Anthropic Claude API."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def _get_client(self) -> Anthropic:
        """Initialize Anthropic client or raise ConfigurationError."""
        api_key = self.settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your key from https://console.anthropic.com/",
                status_code=400,
            )
        return Anthropic(api_key=api_key)

    def generate_files(self, prompt: str) -> Dict[str, str]:
        """
        Generate code files from a user prompt using Claude.

        Args:
            prompt: User's description of the app to build

        Returns:
            Dictionary mapping filenames to their content

        Raises:
            CodeGenerationError: If generation fails or invalid response received
            ConfigurationError: If API key is missing
        """
        client = self._get_client()

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
                model=self.settings.CLAUDE_MODEL,
                max_tokens=self.settings.CLAUDE_MAX_TOKENS,
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
            if isinstance(e, (CodeGenerationError, ConfigurationError)):
                raise
            raise CodeGenerationError(f"Failed to generate code: {str(e)}")

    def _parse_files_from_response(self, response: str) -> Dict[str, str]:
        """
        Parse code blocks from Claude's response into a files dictionary.

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


# Convenience module-level function
def generate_files_from_prompt(prompt: str) -> Dict[str, str]:
    """Module-level helper for generating files."""
    service = CoderService()
    return service.generate_files(prompt)
