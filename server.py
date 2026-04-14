#!/usr/bin/env python3
import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("patient-safety-ai-mcp")
@mcp.tool(name="check_drug_interaction")
async def check_drug_interaction(drugs: list) -> str:
    interactions = []
    if "warfarin" in [d.lower() for d in drugs] and "aspirin" in [d.lower() for d in drugs]:
        interactions.append("Increased bleeding risk")
    return json.dumps({"drugs": drugs, "interactions": interactions, "safe": len(interactions) == 0})
@mcp.tool(name="allergy_alert")
async def allergy_alert(medication: str, allergies: list) -> str:
    alert = any(a.lower() in medication.lower() for a in allergies)
    return json.dumps({"medication": medication, "allergies": allergies, "alert": alert})
if __name__ == "__main__":
    mcp.run()
