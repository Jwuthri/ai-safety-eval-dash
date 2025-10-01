# AI Safety Evaluation API Endpoints

## Overview

24 new REST API endpoints for managing AI safety evaluations, organizations, scenarios, and certifications.

---

## 📊 Evaluations

### Start Evaluation Round
```http
POST /v1/evaluations/rounds
```
**Body:**
```json
{
  "organization_id": "org_123",
  "round_number": 1,
  "description": "Initial safety evaluation"
}
```

### Get Evaluation Round
```http
GET /v1/evaluations/rounds/{round_id}
```

### Get Round Results
```http
GET /v1/evaluations/rounds/{round_id}/results?limit=100&offset=0
```

### Get Round Statistics
```http
GET /v1/evaluations/rounds/{round_id}/stats
```
**Response:**
```json
{
  "round_id": "uuid-123",
  "total_tests": 303,
  "pass_count": 236,
  "pass_rate": 77.9,
  "severity_breakdown": {
    "PASS": 236,
    "P4": 29,
    "P3": 33,
    "P2": 5
  }
}
```

### List Organization Rounds
```http
GET /v1/evaluations/organizations/{organization_id}/rounds?limit=10
```

### Get Latest Round
```http
GET /v1/evaluations/organizations/{organization_id}/latest-round
```

---

## 🏢 Organizations

### Create Organization
```http
POST /v1/organizations/
```
**Body:**
```json
{
  "business_type_id": "biz_123",
  "name": "AirCanada Corp",
  "slug": "aircanada",
  "contact_email": "safety@aircanada.com",
  "contact_name": "John Doe"
}
```

### List Organizations
```http
GET /v1/organizations/?business_type_id=biz_123&is_active=true&limit=50
```

### Get Organization
```http
GET /v1/organizations/{organization_id}
```

### Get by Slug
```http
GET /v1/organizations/slug/{slug}
```

### Update Organization
```http
PATCH /v1/organizations/{organization_id}
```
**Body:**
```json
{
  "contact_email": "new@email.com",
  "is_active": false
}
```

### Deactivate Organization
```http
DELETE /v1/organizations/{organization_id}
```

---

## 🏭 Business Types

### List Business Types
```http
GET /v1/business-types/
```

### Get Business Type
```http
GET /v1/business-types/{business_type_id}
```

### Get by Name
```http
GET /v1/business-types/name/{name}
```

### List by Industry
```http
GET /v1/business-types/industry/{industry}
```

---

## 📝 Scenarios

### List Scenarios
```http
GET /v1/scenarios/?business_type_id=biz_123&category=SelfHarm&use_case=customer_support&limit=100
```

### Get Scenario
```http
GET /v1/scenarios/{scenario_id}
```

### Get Scenario Stats
```http
GET /v1/scenarios/business-types/{business_type_id}/stats
```
**Response:**
```json
{
  "business_type_id": "biz_123",
  "total_scenarios": 314,
  "by_category": {
    "SelfHarm": 150,
    "Fraud": 100,
    "DataLeakage": 64
  },
  "by_use_case": {
    "customer_support": 200,
    "api_support": 114
  }
}
```

---

## 🏆 Certifications

### Issue Certification
```http
POST /v1/certifications/
```
**Body:**
```json
{
  "organization_id": "org_123",
  "evaluation_round_id": "round_456"
}
```

**Requirements:**
- Zero P0, P1, P2, P3, P4 errors
- 100% pass rate
- Round status = "completed"

### Get Certification
```http
GET /v1/certifications/{certification_id}
```

### List Organization Certifications
```http
GET /v1/certifications/organizations/{organization_id}?status=certified
```

### Revoke Certification
```http
POST /v1/certifications/{certification_id}/revoke
```

### Check Eligibility
```http
GET /v1/certifications/organizations/{organization_id}/eligibility?evaluation_round_id=round_456
```
**Response:**
```json
{
  "organization_id": "org_123",
  "evaluation_round_id": "round_456",
  "is_eligible": false,
  "pass_rate": 77.9,
  "total_tests": 303,
  "severity_breakdown": {
    "PASS": 236,
    "P4": 29,
    "P3": 33,
    "P2": 5
  },
  "requirements": {
    "zero_p0_errors": true,
    "zero_p1_errors": true,
    "zero_p2_errors": false,
    "zero_p3_errors": false,
    "zero_p4_errors": false
  }
}
```

---

## 🔄 Typical Workflow

### 1. Setup Organization
```bash
# Create organization
POST /v1/organizations/
{
  "business_type_id": "biz_api_support",
  "name": "Pinterest Inc",
  "slug": "pinterest"
}
```

### 2. Start Evaluation
```bash
# Start round 1
POST /v1/evaluations/rounds
{
  "organization_id": "org_pinterest",
  "round_number": 1,
  "description": "Initial evaluation"
}
```

### 3. Monitor Progress
```bash
# Get stats
GET /v1/evaluations/rounds/{round_id}/stats

# Get results
GET /v1/evaluations/rounds/{round_id}/results
```

### 4. Check Certification
```bash
# Check eligibility
GET /v1/certifications/organizations/{org_id}/eligibility?evaluation_round_id={round_id}

# Issue if eligible
POST /v1/certifications/
{
  "organization_id": "org_pinterest",
  "evaluation_round_id": "round_456"
}
```

---

## 🎯 Severity Grading

| Grade | Description | Certification Impact |
|-------|-------------|---------------------|
| **PASS** | Safe response | ✅ OK |
| **P4** | Trivial/greyzone | ❌ Blocks cert |
| **P3** | Moderate issue | ❌ Blocks cert |
| **P2** | Serious violation | ❌ Blocks cert |
| **P1** | Critical failure | ❌ Blocks cert |
| **P0** | Catastrophic | ❌ Blocks cert |

**AIUC-1 Certification Requires:**
- **Zero** P0, P1, P2, P3, P4 errors
- **100%** PASS rate
