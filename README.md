[![MCP Scorecard: 86/100](https://img.shields.io/badge/proofof.ai-86%2F100-5b21b6)](https://proofof.ai/scorecard/patient-safety-ai-mcp.html)

mcp-name: io.github.CSOAI-ORG/patient-safety-ai-mcp

<div align="center">

# Patient Safety Ai MCP

[![MEOK AI Labs](https://img.shields.io/badge/MEOK-AI%20Labs-667eea)](https://meok.ai)
[![GSPC](https://img.shields.io/badge/GSPC-UNMEASURED-9ca3af)](https://councilof.ai/api/gspc)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Install-3775a9)](https://pypi.org/project/patient_safety_ai_mcp/)

> Check drug interactions, validate dosages, assess patient risk, and generate safety alerts

Check drug interactions, validate dosages, assess patient risk, and generate safety alerts. Uses evidence-based reference data. Not a substitute for clinical judgement.

---

## 🚀 Quick Start

```bash
# Install via pip
pip install patient_safety_ai_mcp

# Or install via Smithery
npx -y @smithery/cli@latest install patient-safety-ai-mcp --client claude
```

## ✨ Features

- Real-time AI safety monitoring
- Byzantine fault-tolerant consensus
- EU AI Act compliance tracking
- Incident alert system
- Multi-agent governance

## 📖 Documentation

- [Full Documentation](https://docs.meok.ai/patient-safety-ai-mcp)
- [API Reference](https://api.meok.ai)
- [EU AI Act Compliance Guide](https://councilof.ai/compliance)

## 🛡️ Compliance

This MCP server is built with **EU AI Act compliance** built-in:

- ✅ Article 9 — Risk Management System
- ✅ Article 13 — Transparency & Instructions for Use
- ✅ Article 15 — Bias Detection & Testing
- ✅ Article 26 — FRIA Support (where applicable)
- ✅ Article 50 — AI Content Watermarking (where applicable)

Need help getting compliant? **[Book a free 15-min diagnostic →](https://cal.com/csoai/august-audit)**

## How MEOK charges

MEOK has no subscriptions and no tiers. You pay per job, and only when the agreed artifact has been delivered to you. There is no public price list. See <https://meok.ai/pricing>.

This repository's source is MIT-licensed and free to self-host.

## 🤝 Part of the MEOK Ecosystem

This server is part of the **[MEOK AI Labs](https://meok.ai)** ecosystem — 300+ MCP servers for sovereign AI governance.

| Domain | Purpose |
|--------|---------|
| [councilof.ai](https://councilof.ai) | EU AI Act compliance marketplace |
| [safetyof.ai](https://safetyof.ai) | AI safety & monitoring |
| [meok.ai](https://meok.ai) | Sovereign AI platform |
| [cobolbridge.ai](https://cobolbridge.ai) | Legacy modernization |

## 📜 License

MIT © [CSOAI-ORG](https://github.com/CSOAI-ORG)

---

<p align="center">
  <sub>Built with 💜 by <a href="https://meok.ai">MEOK AI Labs</a> · UK Companies House 16939677</sub>
</p>
MIT © [MEOK AI Labs](https://meok.ai)

<!-- meok-moat-footer-v1 -->
---

## Pairs with MEOK Governance Suite

Build something that touches users? You need compliance. MEOK ships 38 governance MCPs that drop in alongside this tool — EU AI Act, DORA, NIS2, CRA, GDPR, ISO 42001, FDA SaMD, MDR, Basel, MiFID II, MiCA, COPPA, and more.

```bash
# One-shot install of the governance pack
npx meok-setup --pack governance
```


→ Full catalogue: [councilof.ai](https://councilof.ai)
→ MEOK AI Labs: [meok.ai](https://meok.ai)



## Configuration

Add to your `claude_desktop_config.json` (Claude Desktop) or your MCP client config:

```json
{
  "mcpServers": {
    "patient-safety-ai-mcp": {
      "command": "uvx",
      "args": ["patient-safety-ai-mcp"]
    }
  }
}
```

Or: `pip install patient-safety-ai-mcp` then run the `patient-safety-ai-mcp` command (stdio transport).

## Examples

Once configured, ask your assistant, for example:
- "Use `check_drug_interactions` to …"
- "Use `assess_patient_risk` to …"
- "Use `validate_dosage` to …"
