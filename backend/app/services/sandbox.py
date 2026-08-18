"""
Sandbox execution service using E2B Cloud Sandbox.

Provides execution of generated files in an isolated environment
and returns execution results (stdout, stderr) and preview URLs.

Uses the core `e2b.Sandbox` (not `e2b_code_interpreter`) because we need
`commands.run()` for shell commands and `get_host()` for public preview URLs.
"""

import time
from typing import Dict, Optional
from e2b import Sandbox

from app.core.config import Settings, get_settings
from app.core.exceptions import ConfigurationError, SandboxExecutionError
from app.schemas.sandbox import SandboxResult


class SandboxService:
    """Service responsible for managing and executing code in E2B sandboxes."""

    # Port used for serving web applications inside the sandbox
    SERVE_PORT = 3000

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    async def execute_files(self, files: Dict[str, str]) -> SandboxResult:
        """
        Execute files in an E2B sandbox and return results.

        For web apps (containing index.html), starts a static HTTP server and
        returns a public preview URL. The sandbox is kept alive so the preview
        iframe can access the running app (E2B auto-terminates after its default
        timeout, typically 5 minutes).

        Args:
            files: Dictionary mapping filenames to their content

        Returns:
            SandboxResult containing stdout, stderr, preview_url, sandbox_id, and optional error.
        """
        api_key = self.settings.E2B_API_KEY
        if not api_key:
            raise ConfigurationError(
                "E2B_API_KEY environment variable not set. "
                "Get your key from https://e2b.dev/docs/getting-started/api-key"
            )

        try:
            # Create sandbox instance with the E2B API key
            sandbox = Sandbox(api_key=api_key)

            # Write all generated files to the sandbox filesystem
            for filename, content in files.items():
                sandbox.files.write(filename, content)

            preview_url: Optional[str] = None
            stdout = ""
            stderr = ""

            if "index.html" in files:
                # Web app: start a static HTTP server in the background
                sandbox.commands.run(
                    f"python3 -m http.server {self.SERVE_PORT}",
                    background=True,
                )

                # Brief pause for the server to bind to the port
                time.sleep(1)

                # Get the public preview URL for the running server
                host = sandbox.get_host(self.SERVE_PORT)
                preview_url = f"https://{host}"
                stdout = f"HTTP server started on port {self.SERVE_PORT}"

            elif any(f.endswith(".py") for f in files):
                # Python project: execute the main Python file
                main_file = next(
                    (f for f in files if f.endswith(".py")), None
                )
                if main_file:
                    result = sandbox.commands.run(f"python3 {main_file}")
                    stdout = result.stdout or ""
                    stderr = result.stderr or ""

            else:
                # Other files: list what was created
                result = sandbox.commands.run("ls -la")
                stdout = result.stdout or ""
                stderr = result.stderr or ""

            # NOTE: We intentionally do NOT call sandbox.kill() here.
            # The sandbox must stay alive so the frontend iframe can access
            # the preview URL. E2B will auto-terminate the sandbox after its
            # default timeout (typically 5 minutes).

            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                preview_url=preview_url,
                sandbox_id=sandbox.sandbox_id,
            )

        except ConfigurationError:
            raise
        except Exception as e:
            raise SandboxExecutionError(f"Sandbox execution failed: {str(e)}")


# Convenience module-level function
async def execute_files(files: Dict[str, str]) -> SandboxResult:
    """Module-level helper for executing files in sandbox."""
    service = SandboxService()
    return await service.execute_files(files)
