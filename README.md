# Patient Safety AI

> By [MEOK AI Labs](https://meok.ai) — Drug interactions, dosage validation, and clinical safety alerts

## Installation

```bash
pip install patient-safety-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `check_drug_interactions`
Check known drug interaction databases for a list of medications.

**Parameters:**
- `drugs` (str): Comma-separated list of drug names

### `assess_patient_risk`
Assess overall patient risk based on age, conditions, medications, BMI, and smoking status.

**Parameters:**
- `age` (int): Patient age
- `conditions` (str): Comma-separated medical conditions
- `medications` (str): Comma-separated current medications
- `bmi` (float): Body mass index (default: 0.0)
- `smoker` (bool): Smoking status (default: False)

### `validate_dosage`
Validate a medication dosage against evidence-based reference ranges.

**Parameters:**
- `drug` (str): Drug name
- `dose_mg` (float): Single dose in mg
- `frequency_per_day` (int): Times per day (default: 1)
- `patient_age` (int): Patient age (default: 0)
- `patient_weight_kg` (float): Patient weight (default: 0.0)

### `generate_safety_alert`
Generate a clinical safety alert for a medication issue.

**Parameters:**
- `drug` (str): Drug name
- `alert_type` (str): Alert type
- `severity` (str): Severity level (default: "moderate")
- `patient_id` (str): Patient identifier
- `details` (str): Alert details

### `check_allergy_conflicts`
Check for allergy cross-reactivity conflicts between a medication and known allergies.

**Parameters:**
- `medication` (str): Medication to check
- `allergies` (str): Comma-separated known allergies

## Authentication

Free tier: 30 calls/minute. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
