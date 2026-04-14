#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("patient-safety-ai-mcp")
@mcp.tool(name="check_drug_interaction")
async def check_drug_interaction(drugs: list, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    interactions = []
    if "warfarin" in [d.lower() for d in drugs] and "aspirin" in [d.lower() for d in drugs]:
        interactions.append("Increased bleeding risk")
    return {"drugs": drugs, "interactions": interactions, "safe": len(interactions) == 0}
@mcp.tool(name="allergy_alert")
async def allergy_alert(medication: str, allergies: list, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    alert = any(a.lower() in medication.lower() for a in allergies)
    return {"medication": medication, "allergies": allergies, "alert": alert}
if __name__ == "__main__":
    mcp.run()
