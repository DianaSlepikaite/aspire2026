# Swagger UI Quick Reference - Role Extraction Testing

## 🚀 Quick Start

**Open Swagger UI**: http://localhost:8000/docs

## 📋 3-Step Testing Process

### Step 1: Upload Text (POST /api/v1/intake/upload/text)

**Sample Client Brief with Multiple Roles:**
```
We need to build a new customer portal from scratch. The team composition
should include 3 senior backend engineers experienced with Python/FastAPI,
a solutions architect for system design, and 2 frontend developers skilled
in React. On the product side, we need a product manager to own the roadmap
and features. For design, we require a UX researcher to conduct user testing
and a UI designer for the interface design. We also need a scrum master to
facilitate sprints and keep the team organized. For quality assurance, we
need 2 QA automation engineers. Budget is $250,000-$350,000 USD. Timeline
is 8 months. This is a high-priority project for Q2 delivery.
```

**Form Fields:**
- `text_content`: [paste sample above]
- `client_name`: Sarah Thompson
- `client_email`: sarah.thompson@techcorp.com
- `source_label`: Client Email

**→ Copy the `id` from response**

---

### Step 2: Process with Agent (POST /api/v1/agent/process-intake)

**Request Body:**
```json
{
  "intake_id": "PASTE-ID-FROM-STEP-1"
}
```

**→ Copy `client_need_id` from intermediate_steps in response**

---

### Step 3: View Roles (GET /api/v1/client-needs/{id})

**Path Parameter:**
- `id`: [paste client_need_id from Step 2]

**→ Scroll to `required_roles` in response**

---

## 🧪 Ready-to-Use Test Cases

### Test Case 1: Tech-Heavy Project
```
We need a cloud architect for AWS, 3 backend developers proficient in Node.js,
and a DevOps engineer for CI/CD pipelines. Budget $150K, 4 months.
```
**Expected**: 3 roles, all technology_engineering

---

### Test Case 2: Cross-Functional Team
```
Looking for product folks to own the roadmap, some UX help for research,
and strong cloud engineering support. Also need a scrum master and QA.
```
**Expected**: 5 roles across multiple categories

---

### Test Case 3: Data & Analytics Focus
```
Need a data scientist for ML models, a BI analyst for dashboards, and
someone for data visualization. $80K budget, 3 months.
```
**Expected**: 3 roles, all data_analytics

---

### Test Case 4: Design-Focused
```
We need a UX researcher to conduct user interviews, a UI designer for
interface design, and a service designer for journey mapping.
```
**Expected**: 3 roles, all design_ux

---

### Test Case 5: Colloquial Language
```
Need some PMs for the product, a couple of DevOps guys, QA to test stuff,
and design help for the UI.
```
**Expected**: 4 roles with normalized categories

---

## 📊 Expected Role Structure

```json
{
  "category": "technology_engineering",
  "evidence": "3 senior backend engineers experienced with Python/FastAPI",
  "description": null,
  "count": 3
}
```

**Fields:**
- `category`: Normalized canonical category (8 options)
- `evidence`: Exact wording from client brief
- `description`: Optional additional details
- `count`: Number of people (if specified)

---

## 🎯 8 Canonical Categories

1. `strategy_consulting` - Strategy, business analysts, change management
2. `product_management` - Product managers, product owners
3. `technology_engineering` - Engineers, architects, DevOps, cloud
4. `design_ux` - UX/UI designers, researchers, accessibility
5. `creative_content` - Copywriters, content strategists, brand
6. `project_program_management` - Project managers, scrum masters
7. `quality_testing` - QA engineers, testers, automation
8. `data_analytics` - Data scientists, analysts, BI

---

## ✅ Verification Checklist

After running a test:
- [ ] All mentioned roles extracted
- [ ] Correct canonical categories assigned
- [ ] Original evidence preserved verbatim
- [ ] Headcount captured when mentioned
- [ ] No hallucinated/invented roles
- [ ] Colloquial terms handled correctly

---

## 🔍 Common Colloquial Terms

| Client Says | Normalizes To |
|------------|---------------|
| "product folks" | product_management |
| "cloud guys" | technology_engineering |
| "UX help" | design_ux |
| "QA" | quality_testing |
| "DevOps" | technology_engineering |
| "scrum master" | project_program_management |
| "data team" | data_analytics |
| "BA" | strategy_consulting |

---

## 💡 Pro Tips

1. **Be Specific**: "3 developers" → count: 3
2. **Use Any Term**: "PM", "engineer", "designer" all work
3. **Mix Styles**: Formal and informal language both extract
4. **Check Evidence**: Original wording always preserved
5. **Count Validation**: Verify headcount matches brief

---

## 🆘 Troubleshooting

**Role not extracted?**
- Make role mention more explicit
- Use standard role titles
- Check spelling in client brief

**Wrong category?**
- Check [ROLE_EXTRACTION_GUIDE.md](ROLE_EXTRACTION_GUIDE.md) for mappings
- Role might fit multiple categories (uses most specific)

**Count missing?**
- Specify number in brief ("2 developers" not "some developers")

---

## 📚 Full Documentation

- **Complete Guide**: [ROLE_EXTRACTION_GUIDE.md](ROLE_EXTRACTION_GUIDE.md)
- **Testing Guide**: [AGENT_TESTING_GUIDE.md](AGENT_TESTING_GUIDE.md)
- **Swagger UI**: http://localhost:8000/docs

---

**Happy Testing! 🎉**
