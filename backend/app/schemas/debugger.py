"""
Debugger schemas for Debugger and Coder agents (Phase 2 Multi-Agent Orchestration).

Defines structured data contracts for error diagnoses, root causes, and fix instructions.
"""

from typing import List
from pydantic import BaseModel, Field


class DebugDiagnosis(BaseModel):
    """Structured diagnosis produced by Debugger agent and consumed by Coder agent."""

    error_summary: str = Field(
        ...,
        description="High-level summary of the bug, syntax issue, or sandbox execution error",
    )
    root_cause: str = Field(
        ...,
        description="Technical diagnosis of why the code failed in the sandbox",
    )
    fix_instruction: str = Field(
        ...,
        description="Specific, actionable code repair instructions for the Coder agent",
    )
    files_to_modify: List[str] = Field(
        default_factory=list,
        description="List of filenames that require modification to resolve the issue",
    )
