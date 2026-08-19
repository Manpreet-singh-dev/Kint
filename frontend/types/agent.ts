export type AgentState = "idle" | "active" | "done" | "error";

export type AgentType = "planner" | "coder" | "sandbox" | "debugger";

export interface AgentStepStatus {
  type: AgentType;
  label: string;
  description: string;
  state: AgentState;
  durationSec?: number;
  error?: string;
  details?: string[];
}

export type AgentTrailState = Record<AgentType, AgentStepStatus>;
