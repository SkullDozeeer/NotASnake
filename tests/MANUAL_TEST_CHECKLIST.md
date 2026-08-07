# NotASnake Manual Test Checklist

## Overview
This checklist helps you manually verify that your Snake game works correctly across all features and edge cases.

---

## Setup
- [ ] Game launches without errors
- [ ] All assets load correctly (images, sounds, fonts)
- [ ] Main menu displays properly

---

## Basic Gameplay Tests

### Single Player Mode
- [ ] Snake starts at correct position
- [ ] Snake moves in all 4 directions (UP, DOWN, LEFT, RIGHT)
- [ ] Snake cannot reverse direction instantly (e.g., RIGHT -> LEFT is blocked)
- [ ] Snake grows when eating food
- [ ] Score increases when eating food
- [ ] New food spawns after eating
- [ ] Food never spawns on snake body
- [ ] Game over when snake hits wall (without wrap around)
- [ ] Game over when snake hits itself

### Movement Tests
- [ ] Movement is smooth and responsive
- [ ] Snake speed matches selected difficulty
- [ ] Snake wraps around screen edges (when wrap_around enabled)
- [ ] Snake doesn't wrap around (when wrap_around disabled)

---

## Game Modes Tests

### Classic Mode
- [ ] Standard snake gameplay works
- [ ] Score tracking works
- [ ] High score saves and loads

### Score Attack Mode
- [ ] Target scores (15, 30, 50) are displayed
- [ ] Progress towards target is tracked
- [ ] Best times for each target are saved
- [ ] Completion is recorded

### Multiplayer Mode
- [ ] Both snakes start at correct positions
- [ ] Both snakes can move independently
- [ ] Snake 1 uses correct controls
- [ ] Snake 2 uses correct controls
- [ ] Collision between snakes causes game over
- [ ] Scores are tracked separately for each player
- [ ] Winner is determined correctly

### Special Modes
- [ ] Hardcore mode works (no wrap, timer visible)
- [ ] Fog of War mode hides parts of the map
- [ ] Double Food mode spawns 2 food items
- [ ] Pacifist mode (if implemented)
- [ ] Chaos mode (if implemented)
- [ ] Rewind mode (if implemented)
- [ ] Shrink mode (if implemented)
- [ ] Trust mode (if implemented)

---

## Settings Tests

### Display Settings
- [ ] Light mode toggles correctly
- [ ] Dark mode works
- [ ] Grid opacity setting works (0-100%)
- [ ] Show timer toggle works
- [ ] Background style changes work

### Gameplay Settings
- [ ] Wrap around toggle works
- [ ] Double food toggle works
- [ ] Fog of War toggle works
- [ ] Snake pattern toggle works
- [ ] Start length setting works
- [ ] FPS limit setting works

### Audio Settings
- [ ] Music mute toggle works
- [ ] Music plays during gameplay
- [ ] Music stops when paused
- [ ] Sound effects play (food eaten, game over, etc.)

### Control Schemes
- [ ] WASD + Arrows control scheme works
- [ ] Alternative control schemes work (if implemented)
- [ ] Joystick/gamepad controls work (if implemented)

---

## Collision Detection Tests

### Wall Collisions
- [ ] Top wall collision detected
- [ ] Bottom wall collision detected
- [ ] Left wall collision detected
- [ ] Right wall collision detected
- [ ] Wall collision with wrap_around enabled doesn't cause game over
- [ ] Wall collision with wrap_around disabled causes game over

### Self Collisions
- [ ] Hitting own body causes game over
- [ ] Head can be adjacent to body without causing game over
- [ ] Long snake self-collision works correctly

### Multiplayer Collisions
- [ ] Snake 1 head hitting Snake 2 body causes game over
- [ ] Snake 2 head hitting Snake 1 body causes game over
- [ ] Head-to-head collision causes game over

---

## Food System Tests

### Single Food
- [ ] Food spawns at valid position
- [ ] Food doesn't spawn on snake
- [ ] Food doesn't spawn on walls
- [ ] Eating food increases score by 1
- [ ] Eating food increases snake length by 1

### Double Food
- [ ] Two food items spawn when enabled
- [ ] Both food items can be eaten
- [ ] Eating either food increases score
- [ ] Eating either food increases snake length
- [ ] Food doesn't spawn on each other

### Special Food Types
- [ ] Leftover food appears when enabled
- [ ] Eating leftover food triggers burst mode
- [ ] Burst mode timer works
- [ ] Burst mode visual effect works

---

## UI/UX Tests

### Main Menu
- [ ] All menu options visible
- [ ] Single Player button works
- [ ] Multiplayer button works
- [ ] Settings button works
- [ ] Quit button works
- [ ] Version number displayed

### Pause Menu
- [ ] Game pauses when ESC pressed
- [ ] Pause menu displays
- [ ] Resume option works
- [ ] Quit to Menu option works
- [ ] Settings can be accessed from pause menu

### Game Over Screen
- [ ] Game over screen displays
- [ ] Final score displayed
- [ ] Play Again button works
- [ ] Main Menu button works
- [ ] Quit button works

### Settings Menu
- [ ] All settings options visible
- [ ] Settings can be changed
- [ ] Changes are saved
- [ ] Settings persist between game sessions

### HUD
- [ ] Score displays correctly
- [ ] Timer displays when enabled
- [ ] High score displays
- [ ] Version info displays
- [ ] Seed info displays when applicable

---

## Save System Tests

### Save File
- [ ] save.txt is created on first run
- [ ] Settings are saved to file
- [ ] Settings are loaded from file
- [ ] High score is saved
- [ ] High score is loaded
- [ ] Game stats are saved (games played, apples eaten, etc.)

### Legacy Compatibility
- [ ] Old highscore.txt is migrated to new format
- [ ] Migration doesn't break existing saves

---

## Edge Cases Tests

### Extreme Conditions
- [ ] Snake fills entire board (no space for food)
- [ ] Very long snake (100+ segments)
- [ ] Very short snake (1 segment)
- [ ] Maximum score achieved
- [ ] Game played for very long time (no crashes)

### Rapid Input
- [ ] Rapid direction changes handled correctly
- [ ] Multiple key presses queued correctly
- [ ] No input lag

### Boundary Conditions
- [ ] Snake at exact screen edge
- [ ] Food at exact screen edge
- [ ] Snake moving from one edge to opposite edge (with wrap)

---

## Performance Tests

- [ ] Game runs at 60 FPS (or selected FPS limit)
- [ ] No frame drops during normal gameplay
- [ ] No frame drops with long snake
- [ ] No frame drops with many food items
- [ ] Memory usage stable over time

---

## Audio Tests

- [ ] Background music plays
- [ ] Music volume adjustable
- [ ] Music can be muted
- [ ] Sound effects play
- [ ] Sound effects volume adjustable
- [ ] No audio glitches

---

## Visual Tests

- [ ] Snake renders correctly
- [ ] Food renders correctly
- [ ] Walls/boundaries visible (if applicable)
- [ ] Grid visible (if enabled)
- [ ] All colors display correctly
- [ ] Animations are smooth
- [ ] No visual glitches

---

## Multiplayer-Specific Tests

- [ ] Player 1 controls work independently
- [ ] Player 2 controls work independently
- [ ] Both snakes can move simultaneously
- [ ] Collision detection works for both snakes
- [ ] Scores tracked separately
- [ ] Winner determined correctly
- [ ] Tie handled correctly

---

## Bug Regression Tests

Check for previously fixed bugs:
- [ ] No infinite loop on food spawn when board full
- [ ] No crash when eating food at same time as collision
- [ ] No crash when rapidly changing directions
- [ ] No crash when window is resized (if supported)
- [ ] No crash when game is minimized and restored

---

## Compatibility Tests

### Platform Tests
- [ ] Works on Windows
- [ ] Works on macOS
- [ ] Works on Linux

### Python Version Tests
- [ ] Works on Python 3.8+
- [ ] Works with required Pygame version

---

## Test Results Tracking

| Test Date | Tester | Tests Passed | Tests Failed | Notes |
|-----------|--------|--------------|--------------|-------|
|           |        |              |              |       |
|           |        |              |              |       |

---

## How to Use This Checklist

1. **Before each release**: Run through all tests
2. **After major changes**: Run tests for affected areas
3. **Bug reports**: Check if the issue is covered by existing tests
4. **New features**: Add new test cases to this checklist

---

## Reporting Issues

When a test fails:
1. Note which test failed
2. Describe what happened
3. Note the steps to reproduce
4. Include screenshots if visual
5. Include error messages if any

---

*Last updated: [Date]*
*Version: 3.5*
