<div align="center">

# Patient Safety Ai MCP

**MCP server for patient safety ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-patient-safety-ai-mcp)](https://pypi.org/project/meok-patient-safety-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Patient Safety Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `check_drug_interactions` | Check known drug interaction databases for a list of medications. Pass drugs as  |
| `assess_patient_risk` | Risk scoring based on patient conditions, age, and comorbidities. Conditions and |
| `validate_dosage` | Check dosage against known safe ranges for a medication. |
| `generate_safety_alert` | Create a formatted clinical safety alert. Alert types: interaction, allergy, dos |
| `check_allergy_conflicts` | Cross-reference a medication against patient allergies including cross-reactivit |

## Installation

```bash
pip install meok-patient-safety-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "patient-safety-ai": {
      "command": "python",
      "args": ["-m", "meok_patient_safety_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
