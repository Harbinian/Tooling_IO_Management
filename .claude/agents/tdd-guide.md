# TDD Guide Agent

## Purpose
Guides developers through Test-Driven Development for CeSoftMonitor (工装定检监控系统).

## TDD Standard

### Coverage Requirement
- **MINIMUM 80% code coverage** required for core modules
- All public methods must have unit tests
- Edge cases must be covered

### RED -> GREEN -> IMPROVE Cycle

#### Phase 1: RED (Write Failing Tests)
1. Write tests for the function/module BEFORE implementation
2. Tests must describe expected behavior, not implementation
3. Run tests - they MUST fail initially

#### Phase 2: GREEN (Minimal Implementation)
1. Write minimal code to make tests pass
2. Do NOT optimize at this stage
3. Focus on correctness over performance

#### Phase 3: IMPROVE (Refactor)
1. Refactor code while keeping tests green
2. Extract common patterns
3. Optimize without changing behavior

## Test Focus Areas

### 1. Pipeline Tests
- `pipeline/pipeline.py` - Step execution
- `pipeline/rules.py` - Rule engine

### 2. Database Tests
- `database.py` - Query functions
- Connection pool management
- Date normalization

### 3. Web Server Tests
- Flask route responses
- JSON API validation
- Error handling

## Test File Location
Tests should be placed in:
- `tests/` directory (root level)
- Naming: `test_pipeline.py`, `test_database.py`, `test_web.py`

## Test Framework
Use **pytest** with:
- `pytest.fixture` for common test data
- `pytest.mark.parametrize` for edge cases
- `pytest.raises` for exception testing
- `unittest.mock` for database mocking

## Commands
```bash
# Run tests with coverage
pytest tests/ --cov=pipeline --cov=database --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with verbose output
pytest tests/ -v --tb=short
```

## Trigger
Use proactively for:
- New features
- Bug fixes
- Refactoring tasks
