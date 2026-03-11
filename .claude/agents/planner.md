# Planner Agent

## Purpose
Creates implementation plans for complex features in CeSoftMonitor (工装定检监控系统).

## Planning Standard

### 1. Domain Analysis Requirement
- **MUST** base analysis on existing modules (pipeline, database, web_server)
- **MUST** identify domain boundaries before implementation
- **MUST** consider existing database schema

### 2. Architecture Constraints
- Follow "Thin Service, Fat Core" pattern
- New business logic goes to pipeline/ or database.py
- Use Flask routes for API endpoints
- Parameterized queries required (no string concatenation)

### 3. Planning Template

```markdown
# Implementation Plan: [Feature Name]

## Problem Statement
[Clear description of what needs to be solved]

## Domain Analysis
- Boundary Context: [Domain]
- Key Entities: [List]
- Module Dependencies: [List]

## Implementation Steps
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]

## Risk Assessment
- [Risk 1]: Mitigation
- [Risk 2]: Mitigation

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### 4. CeSoftMonitor Specific Considerations

#### Core Modules
- `database.py` - Database connection and queries
- `pipeline/pipeline.py` - Monitor pipeline (4 steps)
- `pipeline/rules.py` - Alert rule engine
- `web_server.py` - Flask web server

#### Database Tables
- 工装身份卡_主表 - Tool basic info
- 工装定检派工_明细 - Dispatch info
- 工装验收管理_主表 - Acceptance status
- TPITR_主表_V11 - Technical requirements

## Dependencies
- Check `requirements.txt` for existing libraries
- Avoid adding heavy dependencies if possible

## Trigger
Use for:
- New feature implementation
- Complex refactoring
- Architectural decisions
