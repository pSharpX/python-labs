# techdoc-agent

An AI-powered assistant that transforms functional requirements into structured technical proposal.

## requirements scout aget
description goes here


## tech architech agent
description goes here


                         ┌─────────────────────────┐
                         │   Tech Architect Agent  │
                         │      LangGraph          │
                         └────────────┬────────────┘
                                      │
                         LangChain @tools / BaseTool
                                      │
                  ┌───────────────────┴───────────────────┐
                  │                                       │
        ┌─────────▼─────────┐                   ┌─────────▼─────────┐
        │ Architecture MCP  │                   │ Cloud MCP Tools   │
        │ Tool Adapter      │                   │                   │
        └─────────┬─────────┘                   └─────────┬─────────┘
                  │                                       │
          ┌───────▼────────┐              ┌───────────────┼──────────────┐
          │ FastMCP Client │              │               │              │
          └───────┬────────┘       ┌──────▼─────┐  ┌──────▼─────┐ ┌──────▼─────┐
                  │                │ Microsoft  │  │    AWS     │ │   Azure    │
                  │                │ Learn MCP  │  │ MCP Server │ │ MCP Server │
                  │                └────────────┘  └────────────┘ └────────────┘
          ┌───────▼────────┐
          │ Your FastMCP   │
          │ HTTP Server    │
          └────────────────┘

## financial agent
description goes here
