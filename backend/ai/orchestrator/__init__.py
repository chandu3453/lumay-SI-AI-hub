"""
AI Orchestrator — LangGraph workflow orchestration.

Defines composable agentic workflows as state graphs.
Each workflow is a directed graph of nodes (tool calls, LLM calls, decision points).

Exports:
  BaseWorkflow    — Abstract base for all LangGraph workflows.
  AgentState      — Typed state model passed through graph nodes.
  WorkflowRouter  — Routes requests to the appropriate workflow graph.
"""
