
# Test Plan — {{title}}

---

## Overview

**Title:** {{title}}  
**Description:**  
{{description}}

---

## Scope

- **User Stories Range:** {{scope.user_stories_range}}
- **User Stories:** {{scope.user_stories}}
- **Notes:**  
{{scope.notes}}

---

## Prioritization

{{#priorities}}
### Priority {{level}} — {{label}}
{{#user_stories}}
- **{{id}}:** {{name}}
{{/user_stories}}

{{/priorities}}

---

## Test Strategy

| Test Type | Description | Execution Frequency |
|----------|------------|---------------------|
{{#test_strategy.test_types}}
| **{{type}}** | {{description}} | {{frequency}} |
{{/test_strategy.test_types}}

---

## User Story Coverage

{{#user_stories}}
### {{id}} — {{name}}
- **Priority Level:** {{priority_level}}
- **Critical:** {{critical}}

{{#areas}}
#### {{test_type}} Tests
{{#items}}
- {{.}}
{{/items}}

{{/areas}}
{{/user_stories}}

---

## Environments

| Environment | Purpose |
|------------|---------|
{{#environments}}
| **{{name}}** | {{purpose}} |
{{/environments}}

---

## Test Data

{{#test_data.datasets}}
- {{.}}
{{/test_data.datasets}}

---

## Entry & Exit Criteria

### Entry Criteria
{{#criteria.entry}}
- {{.}}
{{/criteria.entry}}

### Exit Criteria
{{#criteria.exit}}
- {{.}}
{{/criteria.exit}}

---

## Automation Strategy

- **Unit Suite Target Time:** {{automation_strategy.unit_suite_target_time}}

### Execution Rules
{{#automation_strategy.rules}}
- {{.}}
{{/automation_strategy.rules}}

### Tooling
{{#automation_strategy.tools}}
- **{{@key}}:** {{.}}
{{/automation_strategy.tools}}

---

## Risks & Mitigations

{{#risks}}
### {{name}}
**Mitigations:**
{{#mitigations}}
- {{.}}
{{/mitigations}}

{{/risks}}

---

## Maintenance

**Policy:**  
{{maintenance.policy}}

---
