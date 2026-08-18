"""
Sandbox execution service using E2B Code Interpreter.

Provides execution of generated files in an isolated environment
and returns execution results (stdout, stderr) and preview URLs.
"""

from typing import Dict, Optional
from e2b_code_interpreter import Sandbox

from app.core.config import Settings, get_settings
from app.core.exceptions import ConfigurationError, SandboxExecutionError
from app.schemas.sandbox import SandboxResult


class SandboxService:
    """Service responsible for managing and executing code in E2B sandboxes."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    async def execute_files(self, files: Dict[str, str]) -> SandboxResult:
        """
        Execute files in an E2B sandbox and return results.

        Args:
            files: Dictionary mapping filenames to their content

        Returns:
            SandboxResult containing stdout, stderr, preview_url, and optional error.
        """
        api_key = self.settings.E2B_API_KEY
        if not api_key:
            return SandboxResult(
                error="E2B_API_KEY environment variable not set. "
                      "Get your key from https://e2b.dev/docs/getting-started/api-key"
            )

        try:
            # Create sandbox instance
            sandbox = Sandbox(api_key=api_key)

            # Write all files to the sandbox
            for filename, content in files.items():
                sandbox.files.write(filename, content)

            # Determine execution strategy based on files
            stdout_parts = []
            stderr_parts = []

            if "index.html" in files:
                # For web apps, start a simple HTTP server
                sandbox.run_code(
                    "python -m http.server 8000",
                    on_stdout=lambda output: stdout_parts.append(output),
                    on_stderr=lambda output: stderr_parts.append(output),
                )

                # Get the preview URL from the sandbox (port 8000)
                preview_url = f"https://{sandbox.get_host(8000)}"

            elif any(f.endswith(".py") for f in files.keys()):
                # For Python files, execute the main file
                main_file = next((f for f in files.keys() if f.endswith(".py")), None)
                if main_file:
                    sandbox.run_code(
                        f"python {main_file}",
                        on_stdout=lambda output: stdout_parts.append(output),
                        on_stderr=lambda output: stderr_parts.append(output),
                    )
                preview_url = None

            else:
                # For other files, just list what was created
                sandbox.run_code(
                    "ls -la",
                    on_stdout=lambda output: stdout_parts.append(output),
                    on_stderr=lambda output: stderr_parts.append(output),
                )
                preview_url = None

            # Close the sandbox
            sandbox.close()

            return SandboxResult(
                stdout="".join(stdout_parts),
                stderr="".join(stderr_parts),
                preview_url=preview_url,
            )

        except Exception as e:
            return SandboxResult(
                error=f"Sandbox execution failed: {str(e)}"
            )


# Convenience module-level function
async def execute_files(files: Dict[str, str]) -> SandboxResult:
    """Module-level helper for executing files in sandbox."""
    service = SandboxService()
    return await service.execute_files(files)
