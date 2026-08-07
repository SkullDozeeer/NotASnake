# NotASnake Test Suite

## Overview

This directory contains automated and manual tests for the NotASnake game.

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── test_constants.py     # Game constants for testing
├── test_core_logic.py    # Unit tests for core game logic
├── MANUAL_TEST_CHECKLIST.md  # Manual test checklist
└── README.md             # This file
```

---

## Running Automated Tests

### Prerequisites

- Python 3.8 or higher
- No additional dependencies required (tests use only standard library)

### Running All Tests

```bash
# From the repository root:
python -m unittest tests.test_core_logic

# Or from the tests directory:
cd tests
python -m unittest test_core_logic
```

### Running Specific Test Classes

```bash
# Run only food spawning tests
python -m unittest tests.test_core_logic.TestFoodSpawning

# Run only snake movement tests
python -m unittest tests.test_core_logic.TestSnakeMovement

# Run only direction change tests
python -m unittest tests.test_core_logic.TestDirectionChanges

# Run only food eating tests
python -m unittest tests.test_core_logic.TestFoodEating

# Run only snake body management tests
python -m unittest tests.test_core_logic.TestSnakeBodyManagement

# Run only game over condition tests
python -m unittest tests.test_core_logic.TestGameOverConditions

# Run only score attack mode tests
python -m unittest tests.test_core_logic.TestScoreAttackMode
```

### Running with Verbose Output

```bash
python -m unittest tests.test_core_logic -v
```

### Running and Discovering All Tests

```bash
# Discover and run all tests in the tests directory
python -m unittest discover tests -v
```

---

## Test Coverage

The automated tests cover the following areas:

### Food Spawning Logic
- Spawning on empty board
- Spawning with snake on board
- Spawning on nearly full board
- Deterministic spawning with seeds
- Multiple spawns without overlap

### Snake Movement
- Movement in all 4 directions (UP, DOWN, LEFT, RIGHT)
- Wall collision detection (all 4 walls)
- Self-collision detection
- Wrap-around logic (all 4 edges)

### Direction Changes
- Blocking opposite direction changes (RIGHT<->LEFT, UP<->DOWN)
- Allowing valid direction changes
- All opposite direction pairs

### Food Eating
- Detecting food eaten
- Detecting food not eaten
- Double food eating (both food items)

### Snake Body Management
- Body growth when eating
- Body no growth when moving
- Complete movement sequences
- Multiple food eating sequences

### Game Over Conditions
- Wall collision with/without wrap
- Self collision
- No game over in normal play

### Score Attack Mode
- Target validation
- Completion detection

---

## Manual Testing

For comprehensive testing, use the manual test checklist:

- [MANUAL_TEST_CHECKLIST.md](MANUAL_TEST_CHECKLIST.md)

This checklist covers:
- Basic gameplay
- All game modes
- Settings
- Collision detection
- Food system
- UI/UX
- Save system
- Edge cases
- Performance
- Audio and visual tests
- Multiplayer-specific tests

---

## Writing New Tests

### Adding Unit Tests

1. Create a new test file or add to existing one
2. Import necessary modules and constants
3. Create a test class inheriting from `unittest.TestCase`
4. Add test methods (must start with `test_`)
5. Use assertions: `self.assertEqual()`, `self.assertTrue()`, etc.

Example:

```python
import unittest
from test_constants import CELL_SIZE, SCREEN_WIDTH

class TestNewFeature(unittest.TestCase):
    def test_new_feature_works(self):
        result = new_feature_function()
        self.assertEqual(result, expected_value)
    
    def test_new_feature_edge_case(self):
        result = new_feature_function(edge_case_input)
        self.assertTrue(result > 0)
```

### Adding Manual Tests

1. Edit `MANUAL_TEST_CHECKLIST.md`
2. Add new sections or test cases as needed
3. Keep tests organized by feature

---

## Test Data

The tests use simplified versions of game functions to avoid dependencies on Pygame. The test constants match the actual game constants:

- Screen dimensions: 1366x768
- Cell size: 20px
- Directions: UP, DOWN, LEFT, RIGHT
- Difficulty levels: Story game (6), The Classic (10), Faster! (16), Whoosh!!! (24)

---

## Continuous Integration

To set up CI for automated testing:

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Run tests
      run: python -m unittest discover tests -v
```

---

## Troubleshooting

### Tests Fail with Import Errors

Make sure you're running tests from the repository root or have the parent directory in your Python path.

```bash
# From repository root:
python -m unittest tests.test_core_logic

# Or add to PYTHONPATH:
export PYTHONPATH=${PYTHONPATH}:.
python -m unittest tests.test_core_logic
```

### Tests Fail Intermittently

Some tests use random seeds for deterministic behavior. If a test fails, it might indicate a bug in the logic. Run with verbose output to see which test failed.

---

## Contributing

When adding new features or fixing bugs:

1. Add unit tests for the new/changed functionality
2. Update the manual test checklist if needed
3. Run all tests before submitting a pull request
4. Ensure all existing tests still pass

---

## License

The test suite is part of the NotASnake project and is licensed under the same terms (GNU GPL v3.0).
