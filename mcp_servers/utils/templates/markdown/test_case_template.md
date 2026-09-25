
# Test Cases — {{user_story.id}} · {{user_story.title}}

This document contains the **set of test cases** derived from the user story **{{user_story.id}}**.

---

## User Story Reference

**ID:** {{user_story.id}}  
**Title:** {{user_story.title}}  
**Priority:** {{user_story.priority}}  
**Critical:** {{user_story.critical}}

---

## Test Case Summary

- **Total Test Cases:** {{summary.total}}
- **Automatable:** {{summary.automatable}}
- **Manual:** {{summary.manual}}
- **Last Updated:** {{summary.last_updated}}

---

## Test Cases

{{#test_cases}}
---

### {{id}} — {{title}}

**Description:**  
{{description}}

**Type:** {{type}}  
**Priority:** {{priority}}  
**Automation Candidate:** {{automation}}

---

#### Preconditions
{{#preconditions}}
- {{.}}
{{/preconditions}}

---

#### Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
{{#steps}}
| {{number}} | {{action}} | {{expected_result}} |
{{/steps}}

---

#### Expected Final Result

{{expected_result}}

---

#### Notes / Edge Cases
{{#notes}}
- {{.}}
{{/notes}}

---

{{/test_cases}}

## Traceability

- **Related User Story:** {{user_story.id}}
- **Generated At:** {{generated_at}}

---
