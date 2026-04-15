#!/usr/bin/env python3
"""Patient Safety AI MCP Server - Drug interactions, dosage validation, and safety alerts."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

# Rate limiting
_rate_limits: dict = defaultdict(list)
RATE_WINDOW = 60
MAX_REQUESTS = 30

def _check_rate(key: str) -> bool:
    now = time.time()
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < RATE_WINDOW]
    if len(_rate_limits[key]) >= MAX_REQUESTS:
        return False
    _rate_limits[key].append(now)
    return True

# Drug interaction database (simplified but realistic)
DRUG_INTERACTIONS = {
    ("warfarin", "aspirin"): {"severity": "high", "effect": "Increased bleeding risk", "mechanism": "Both affect coagulation pathways"},
    ("warfarin", "ibuprofen"): {"severity": "high", "effect": "Increased bleeding risk and GI damage", "mechanism": "NSAID inhibits platelet function"},
    ("warfarin", "vitamin k"): {"severity": "moderate", "effect": "Reduced anticoagulant effect", "mechanism": "Vitamin K antagonizes warfarin"},
    ("metformin", "alcohol"): {"severity": "high", "effect": "Risk of lactic acidosis", "mechanism": "Both impair lactate metabolism"},
    ("ssri", "maoi"): {"severity": "critical", "effect": "Serotonin syndrome risk - potentially fatal", "mechanism": "Excessive serotonin accumulation"},
    ("lisinopril", "potassium"): {"severity": "moderate", "effect": "Hyperkalemia risk", "mechanism": "ACE inhibitors reduce potassium excretion"},
    ("simvastatin", "grapefruit"): {"severity": "moderate", "effect": "Increased statin levels - rhabdomyolysis risk", "mechanism": "CYP3A4 inhibition"},
    ("methotrexate", "nsaid"): {"severity": "high", "effect": "Methotrexate toxicity", "mechanism": "Reduced renal clearance of methotrexate"},
    ("digoxin", "amiodarone"): {"severity": "high", "effect": "Digoxin toxicity", "mechanism": "Amiodarone inhibits digoxin clearance"},
    ("lithium", "ibuprofen"): {"severity": "high", "effect": "Lithium toxicity", "mechanism": "NSAIDs reduce lithium renal clearance"},
    ("ciprofloxacin", "theophylline"): {"severity": "moderate", "effect": "Theophylline toxicity", "mechanism": "CYP1A2 inhibition"},
    ("clopidogrel", "omeprazole"): {"severity": "moderate", "effect": "Reduced antiplatelet effect", "mechanism": "CYP2C19 inhibition"},
}

# Drug class mappings
DRUG_CLASSES = {
    "aspirin": ["nsaid", "antiplatelet"], "ibuprofen": ["nsaid"], "naproxen": ["nsaid"],
    "sertraline": ["ssri"], "fluoxetine": ["ssri"], "paroxetine": ["ssri"], "citalopram": ["ssri"],
    "phenelzine": ["maoi"], "tranylcypromine": ["maoi"], "selegiline": ["maoi"],
}

# Dosage ranges (drug -> {unit, min_daily, max_daily, typical})
DOSAGE_RANGES = {
    "metformin": {"unit": "mg", "min_daily": 500, "max_daily": 2550, "typical": 1000},
    "lisinopril": {"unit": "mg", "min_daily": 2.5, "max_daily": 40, "typical": 10},
    "amlodipine": {"unit": "mg", "min_daily": 2.5, "max_daily": 10, "typical": 5},
    "metoprolol": {"unit": "mg", "min_daily": 25, "max_daily": 400, "typical": 100},
    "simvastatin": {"unit": "mg", "min_daily": 5, "max_daily": 40, "typical": 20},
    "omeprazole": {"unit": "mg", "min_daily": 10, "max_daily": 40, "typical": 20},
    "warfarin": {"unit": "mg", "min_daily": 1, "max_daily": 10, "typical": 5},
    "aspirin": {"unit": "mg", "min_daily": 75, "max_daily": 4000, "typical": 300},
    "paracetamol": {"unit": "mg", "min_daily": 500, "max_daily": 4000, "typical": 1000},
    "ibuprofen": {"unit": "mg", "min_daily": 200, "max_daily": 2400, "typical": 400},
    "amoxicillin": {"unit": "mg", "min_daily": 750, "max_daily": 3000, "typical": 1500},
    "prednisolone": {"unit": "mg", "min_daily": 1, "max_daily": 60, "typical": 10},
    "levothyroxine": {"unit": "mcg", "min_daily": 25, "max_daily": 300, "typical": 100},
    "sertraline": {"unit": "mg", "min_daily": 25, "max_daily": 200, "typical": 50},
}

# Allergy cross-reactivity
ALLERGY_CROSS_REACTIVITY = {
    "penicillin": ["amoxicillin", "ampicillin", "piperacillin", "flucloxacillin"],
    "sulfa": ["sulfamethoxazole", "sulfasalazine", "celecoxib"],
    "aspirin": ["ibuprofen", "naproxen", "diclofenac"],
    "codeine": ["morphine", "tramadol", "oxycodone"],
    "cephalosporin": ["cefuroxime", "ceftriaxone", "cefalexin"],
}

mcp = FastMCP("patient-safety-ai", instructions="Check drug interactions, validate dosages, assess patient risk, and generate safety alerts. Uses evidence-based reference data. Not a substitute for clinical judgement.")


@mcp.tool()
def check_drug_interactions(drugs: str, api_key: str = "") -> str:
    """Check known drug interaction databases for a list of medications. Pass drugs as comma-separated string."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if not _check_rate(api_key or "anon"):
        return json.dumps({"error": "Rate limit exceeded. Try again in 60 seconds."})

    drug_list = [d.strip().lower() for d in drugs.split(",") if d.strip()]
    if len(drug_list) < 2:
        return json.dumps({"error": "At least 2 drugs required for interaction check"})

    # Expand drug classes
    expanded = {}
    for drug in drug_list:
        classes = DRUG_CLASSES.get(drug, [drug])
        expanded[drug] = classes

    interactions_found = []
    checked_pairs = set()

    for i, drug_a in enumerate(drug_list):
        for drug_b in drug_list[i+1:]:
            pair_key = tuple(sorted([drug_a, drug_b]))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            # Direct lookup
            interaction = DRUG_INTERACTIONS.get((drug_a, drug_b)) or DRUG_INTERACTIONS.get((drug_b, drug_a))

            # Class-based lookup
            if not interaction:
                classes_a = expanded[drug_a]
                classes_b = expanded[drug_b]
                for ca in classes_a:
                    for cb in classes_b:
                        interaction = DRUG_INTERACTIONS.get((ca, cb)) or DRUG_INTERACTIONS.get((cb, ca))
                        if interaction:
                            break
                    if interaction:
                        break

            if interaction:
                interactions_found.append({
                    "drug_a": drug_a,
                    "drug_b": drug_b,
                    "severity": interaction["severity"],
                    "effect": interaction["effect"],
                    "mechanism": interaction["mechanism"],
                })

    severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    interactions_found.sort(key=lambda x: severity_order.get(x["severity"], 99))

    max_severity = interactions_found[0]["severity"] if interactions_found else "none"

    return json.dumps({
        "drugs_checked": drug_list,
        "pairs_analyzed": len(checked_pairs),
        "interactions_found": len(interactions_found),
        "max_severity": max_severity,
        "safe": len(interactions_found) == 0,
        "interactions": interactions_found,
        "disclaimer": "Reference data only. Always consult clinical pharmacist for complex regimens.",
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })


@mcp.tool()
def assess_patient_risk(age: int, conditions: str, medications: str, bmi: float = 0.0, smoker: bool = False, api_key: str = "") -> str:
    """Risk scoring based on patient conditions, age, and comorbidities. Conditions and medications as comma-separated strings."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if not _check_rate(api_key or "anon"):
        return json.dumps({"error": "Rate limit exceeded. Try again in 60 seconds."})

    condition_list = [c.strip().lower() for c in conditions.split(",") if c.strip()]
    med_list = [m.strip().lower() for m in medications.split(",") if m.strip()]

    risk_score = 0
    risk_factors = []

    # Age-based risk
    if age >= 80:
        risk_score += 25
        risk_factors.append({"factor": "advanced_age", "detail": f"Age {age} (>=80)", "points": 25})
    elif age >= 65:
        risk_score += 15
        risk_factors.append({"factor": "elderly", "detail": f"Age {age} (65-79)", "points": 15})
    elif age < 18:
        risk_score += 10
        risk_factors.append({"factor": "pediatric", "detail": f"Age {age} (<18) - dose adjustments may apply", "points": 10})

    # Comorbidity scoring
    high_risk_conditions = {
        "diabetes": 15, "heart failure": 20, "ckd": 20, "copd": 15,
        "liver disease": 20, "renal impairment": 20, "cancer": 15,
        "hypertension": 10, "atrial fibrillation": 15, "epilepsy": 10,
    }
    for cond in condition_list:
        for key, points in high_risk_conditions.items():
            if key in cond:
                risk_score += points
                risk_factors.append({"factor": "comorbidity", "detail": cond, "points": points})
                break

    # Polypharmacy risk
    if len(med_list) >= 10:
        risk_score += 20
        risk_factors.append({"factor": "polypharmacy_severe", "detail": f"{len(med_list)} medications", "points": 20})
    elif len(med_list) >= 5:
        risk_score += 10
        risk_factors.append({"factor": "polypharmacy", "detail": f"{len(med_list)} medications", "points": 10})

    # BMI risk
    if bmi > 0:
        if bmi >= 35:
            risk_score += 10
            risk_factors.append({"factor": "severe_obesity", "detail": f"BMI {bmi}", "points": 10})
        elif bmi >= 30:
            risk_score += 5
            risk_factors.append({"factor": "obesity", "detail": f"BMI {bmi}", "points": 5})
        elif bmi < 18.5:
            risk_score += 5
            risk_factors.append({"factor": "underweight", "detail": f"BMI {bmi}", "points": 5})

    # Smoking
    if smoker:
        risk_score += 10
        risk_factors.append({"factor": "smoker", "detail": "Active smoker", "points": 10})

    risk_score = min(100, risk_score)
    if risk_score >= 60:
        risk_level = "HIGH"
        recommendation = "Requires close monitoring and specialist review"
    elif risk_score >= 30:
        risk_level = "MODERATE"
        recommendation = "Regular monitoring recommended"
    else:
        risk_level = "LOW"
        recommendation = "Standard care pathway appropriate"

    return json.dumps({
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "risk_factors": risk_factors,
        "patient_summary": {
            "age": age,
            "conditions_count": len(condition_list),
            "medications_count": len(med_list),
            "bmi": bmi if bmi > 0 else "not provided",
            "smoker": smoker,
        },
        "assessed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "Risk assessment tool only. Clinical decisions must involve qualified healthcare professionals.",
    })


@mcp.tool()
def validate_dosage(drug: str, dose_mg: float, frequency_per_day: int = 1, patient_age: int = 0, patient_weight_kg: float = 0.0, api_key: str = "") -> str:
    """Check dosage against known safe ranges for a medication."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if not _check_rate(api_key or "anon"):
        return json.dumps({"error": "Rate limit exceeded. Try again in 60 seconds."})

    drug_lower = drug.strip().lower()
    reference = DOSAGE_RANGES.get(drug_lower)

    if not reference:
        return json.dumps({
            "drug": drug,
            "status": "UNKNOWN",
            "message": f"No dosage reference data available for '{drug}'. Consult pharmacopoeia.",
            "dose_checked": dose_mg,
        })

    daily_dose = dose_mg * frequency_per_day
    warnings = []
    status = "VALID"

    # Check against absolute max
    if daily_dose > reference["max_daily"]:
        status = "EXCEEDS_MAXIMUM"
        warnings.append({
            "type": "overdose_risk",
            "detail": f"Daily dose {daily_dose}{reference['unit']} exceeds maximum {reference['max_daily']}{reference['unit']}",
            "severity": "critical",
        })
    elif daily_dose > reference["max_daily"] * 0.8:
        warnings.append({
            "type": "near_maximum",
            "detail": f"Daily dose {daily_dose}{reference['unit']} approaching maximum ({reference['max_daily']}{reference['unit']})",
            "severity": "moderate",
        })

    # Check below minimum therapeutic dose
    if daily_dose < reference["min_daily"]:
        if status == "VALID":
            status = "BELOW_THERAPEUTIC"
        warnings.append({
            "type": "subtherapeutic",
            "detail": f"Daily dose {daily_dose}{reference['unit']} below minimum therapeutic {reference['min_daily']}{reference['unit']}",
            "severity": "moderate",
        })

    # Age-based adjustments
    if patient_age > 0:
        if patient_age >= 75 and daily_dose > reference["typical"]:
            warnings.append({
                "type": "elderly_caution",
                "detail": f"Patient age {patient_age}: consider dose reduction from {daily_dose}{reference['unit']}",
                "severity": "moderate",
            })
        if patient_age < 12:
            warnings.append({
                "type": "pediatric_caution",
                "detail": f"Patient age {patient_age}: pediatric dosing may differ significantly",
                "severity": "moderate",
            })

    # Weight-based check
    if patient_weight_kg > 0:
        dose_per_kg = daily_dose / patient_weight_kg
        if dose_per_kg > reference["max_daily"] / 50:  # rough per-kg threshold
            warnings.append({
                "type": "weight_adjusted",
                "detail": f"Dose per kg ({round(dose_per_kg, 2)}{reference['unit']}/kg) may need review",
                "severity": "low",
            })

    return json.dumps({
        "drug": drug,
        "dose_per_administration": dose_mg,
        "frequency_per_day": frequency_per_day,
        "daily_dose": daily_dose,
        "unit": reference["unit"],
        "status": status,
        "reference_range": {
            "min_daily": reference["min_daily"],
            "max_daily": reference["max_daily"],
            "typical_daily": reference["typical"],
        },
        "warnings": warnings,
        "validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "Dosage reference only. Individual patient factors may require adjustment.",
    })


@mcp.tool()
def generate_safety_alert(drug: str, alert_type: str, severity: str = "moderate", patient_id: str = "", details: str = "", api_key: str = "") -> str:
    """Create a formatted clinical safety alert. Alert types: interaction, allergy, dosage, contraindication."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if not _check_rate(api_key or "anon"):
        return json.dumps({"error": "Rate limit exceeded. Try again in 60 seconds."})

    valid_types = ["interaction", "allergy", "dosage", "contraindication", "monitoring", "other"]
    valid_severities = ["critical", "high", "moderate", "low", "info"]

    if alert_type.lower() not in valid_types:
        return json.dumps({"error": f"Invalid alert_type. Must be one of: {valid_types}"})
    if severity.lower() not in valid_severities:
        return json.dumps({"error": f"Invalid severity. Must be one of: {valid_severities}"})

    alert_id = f"SA-{int(time.time())}-{hash(drug + alert_type) % 10000:04d}"

    action_map = {
        "critical": "STOP administration immediately. Contact prescriber urgently.",
        "high": "Withhold next dose. Contact prescriber within 1 hour.",
        "moderate": "Flag for prescriber review at next opportunity.",
        "low": "Document and monitor. No immediate action required.",
        "info": "For information only. No action required.",
    }

    escalation_map = {
        "critical": ["prescriber", "pharmacy", "ward_manager", "medical_director"],
        "high": ["prescriber", "pharmacy"],
        "moderate": ["prescriber"],
        "low": [],
        "info": [],
    }

    alert = {
        "alert_id": alert_id,
        "type": alert_type.lower(),
        "severity": severity.lower(),
        "drug": drug,
        "patient_id": patient_id or "not specified",
        "details": details or f"{alert_type.capitalize()} alert for {drug}",
        "recommended_action": action_map[severity.lower()],
        "escalate_to": escalation_map[severity.lower()],
        "requires_acknowledgement": severity.lower() in ["critical", "high"],
        "auto_escalation_minutes": 15 if severity.lower() == "critical" else 60 if severity.lower() == "high" else None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "active",
    }

    return json.dumps(alert)


@mcp.tool()
def check_allergy_conflicts(medication: str, allergies: str, api_key: str = "") -> str:
    """Cross-reference a medication against patient allergies including cross-reactivity. Allergies as comma-separated string."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if not _check_rate(api_key or "anon"):
        return json.dumps({"error": "Rate limit exceeded. Try again in 60 seconds."})

    med_lower = medication.strip().lower()
    allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]

    if not allergy_list:
        return json.dumps({"medication": medication, "conflicts": [], "safe": True, "message": "No allergies provided"})

    conflicts = []

    for allergy in allergy_list:
        # Direct match
        if allergy in med_lower or med_lower in allergy:
            conflicts.append({
                "allergy": allergy,
                "medication": medication,
                "match_type": "direct",
                "severity": "critical",
                "detail": f"Direct allergy match: patient allergic to {allergy}, prescribed {medication}",
            })
            continue

        # Cross-reactivity check
        cross_reactive_drugs = ALLERGY_CROSS_REACTIVITY.get(allergy, [])
        if med_lower in cross_reactive_drugs:
            conflicts.append({
                "allergy": allergy,
                "medication": medication,
                "match_type": "cross_reactivity",
                "severity": "high",
                "detail": f"Cross-reactivity: {medication} is cross-reactive with {allergy} allergy",
            })
            continue

        # Check if medication is in a cross-reactive group
        for allergen, related_drugs in ALLERGY_CROSS_REACTIVITY.items():
            if med_lower in related_drugs and allergy in related_drugs:
                conflicts.append({
                    "allergy": allergy,
                    "medication": medication,
                    "match_type": "same_class",
                    "severity": "high",
                    "detail": f"Same drug class: both {allergy} and {medication} belong to {allergen} group",
                })
                break

    return json.dumps({
        "medication": medication,
        "allergies_checked": allergy_list,
        "conflicts_found": len(conflicts),
        "safe": len(conflicts) == 0,
        "conflicts": conflicts,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disclaimer": "Allergy cross-reactivity data is not exhaustive. Always verify with clinical pharmacist.",
    })


if __name__ == "__main__":
    mcp.run()
