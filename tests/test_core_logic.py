"""
Unit Tests for NotASnake Core Game Logic
=======================================

Tests the fundamental game mechanics without requiring Pygame to run.
These tests focus on:
- Food spawning logic
- Snake movement and collision detection
- Score calculation
- Game state management
"""

import unittest
import random
import math

from tests.test_constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CELL_SIZE,
    DIRECTIONS,
    OPPOSITES,
    SA_TARGETS,
)


# Simplified spawn_food function for testing
def spawn_food(snake_bodies, seed=None, counter=0):
    """
    Simplified version of spawn_food for testing.
    Spawns food at a random position not occupied by snake bodies.
    """
    occupied = set(map(tuple, snake_bodies))
    cols = (SCREEN_WIDTH // CELL_SIZE) - 1
    rows = (SCREEN_HEIGHT // CELL_SIZE) - 1
    total_cells = cols * rows

    if len(occupied) >= total_cells:
        # Board is full, return first snake position or default
        return list(snake_bodies[0]) if snake_bodies else [CELL_SIZE, CELL_SIZE]

    # Use seed for deterministic testing
    if seed:
        rng = random.Random(seed)
    else:
        rng = random

    for _attempt in range(total_cells * 2):
        new_pos = [
            rng.randrange(1, (SCREEN_WIDTH // CELL_SIZE)) * CELL_SIZE,
            rng.randrange(1, (SCREEN_HEIGHT // CELL_SIZE)) * CELL_SIZE
        ]
        if tuple(new_pos) not in occupied:
            return new_pos

    # Fallback: find first available cell
    for col in range(1, SCREEN_WIDTH // CELL_SIZE):
        for row in range(1, SCREEN_HEIGHT // CELL_SIZE):
            candidate = [col * CELL_SIZE, row * CELL_SIZE]
            if tuple(candidate) not in occupied:
                return candidate

    return [CELL_SIZE, CELL_SIZE]


class TestFoodSpawning(unittest.TestCase):
    """Test food spawning logic"""
    
    def test_spawn_food_empty_board(self):
        """Test spawning food on an empty board"""
        snake_body = []
        food_pos = spawn_food(snake_body, seed=42)
        
        # Food should be within screen bounds
        self.assertGreaterEqual(food_pos[0], CELL_SIZE)
        self.assertLess(food_pos[0], SCREEN_WIDTH)
        self.assertGreaterEqual(food_pos[1], CELL_SIZE)
        self.assertLess(food_pos[1], SCREEN_HEIGHT)
        
        # Food should be aligned to cell grid
        self.assertEqual(food_pos[0] % CELL_SIZE, 0)
        self.assertEqual(food_pos[1] % CELL_SIZE, 0)
    
    def test_spawn_food_with_snake(self):
        """Test spawning food when snake occupies some cells"""
        # Create a snake body occupying some cells
        snake_body = [
            [100, 100],
            [80, 100],
            [60, 100],
        ]
        
        food_pos = spawn_food(snake_body, seed=42)
        
        # Food should not spawn on snake body
        self.assertNotIn([food_pos[0], food_pos[1]], snake_body)
        
        # Food should still be within bounds
        self.assertGreaterEqual(food_pos[0], 0)
        self.assertLess(food_pos[0], SCREEN_WIDTH)
        self.assertGreaterEqual(food_pos[1], 0)
        self.assertLess(food_pos[1], SCREEN_HEIGHT)
    
    def test_spawn_food_full_board(self):
        """Test spawning food when board is nearly full"""
        # Create a snake that fills most of the board
        snake_body = []
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                if len(snake_body) < 50:  # Just fill some cells
                    snake_body.append([x, y])
        
        food_pos = spawn_food(snake_body, seed=42)
        
        # Should still return a valid position
        self.assertIsNotNone(food_pos)
        self.assertEqual(len(food_pos), 2)
    
    def test_spawn_food_deterministic_with_seed(self):
        """Test that same seed produces same food position"""
        snake_body = [[100, 100]]
        
        food1 = spawn_food(snake_body, seed=123)
        food2 = spawn_food(snake_body, seed=123)
        
        self.assertEqual(food1, food2)
    
    def test_spawn_food_different_seeds(self):
        """Test that different seeds produce different positions"""
        snake_body = [[100, 100]]
        
        food1 = spawn_food(snake_body, seed=123)
        food2 = spawn_food(snake_body, seed=456)
        
        # They should be different (with high probability)
        # Note: There's a tiny chance they could be the same, but very unlikely
        self.assertNotEqual(food1, food2)
    
    def test_spawn_food_multiple_calls(self):
        """Test that multiple food spawns don't overlap with snake"""
        snake_body = [[100, 100], [80, 100]]
        
        positions = []
        for i in range(10):
            food_pos = spawn_food(snake_body, seed=42+i)
            positions.append(food_pos)
        
        # All positions should be valid
        for pos in positions:
            self.assertGreaterEqual(pos[0], 0)
            self.assertLess(pos[0], SCREEN_WIDTH)
            self.assertGreaterEqual(pos[1], 0)
            self.assertLess(pos[1], SCREEN_HEIGHT)


class TestSnakeMovement(unittest.TestCase):
    """Test snake movement and collision logic"""
    
    def test_movement_right(self):
        """Test snake moving right"""
        snake_pos = [100, 100]
        direction = "RIGHT"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        self.assertEqual(snake_pos, [120, 100])
    
    def test_movement_up(self):
        """Test snake moving up"""
        snake_pos = [100, 100]
        direction = "UP"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        self.assertEqual(snake_pos, [100, 80])
    
    def test_movement_left(self):
        """Test snake moving left"""
        snake_pos = [100, 100]
        direction = "LEFT"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        self.assertEqual(snake_pos, [80, 100])
    
    def test_movement_down(self):
        """Test snake moving down"""
        snake_pos = [100, 100]
        direction = "DOWN"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        self.assertEqual(snake_pos, [100, 120])
    
    def test_wall_collision_right(self):
        """Test collision with right wall"""
        snake_pos = [SCREEN_WIDTH - 10, 100]
        direction = "RIGHT"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        # Should be beyond screen width
        self.assertGreater(snake_pos[0], SCREEN_WIDTH - 1)
    
    def test_wall_collision_left(self):
        """Test collision with left wall"""
        snake_pos = [10, 100]
        direction = "LEFT"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        # Should be negative (off screen left)
        self.assertLess(snake_pos[0], 0)
    
    def test_wall_collision_top(self):
        """Test collision with top wall"""
        snake_pos = [100, 10]
        direction = "UP"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        # Should be negative (off screen top)
        self.assertLess(snake_pos[1], 0)
    
    def test_wall_collision_bottom(self):
        """Test collision with bottom wall"""
        snake_pos = [100, SCREEN_HEIGHT - 10]
        direction = "DOWN"
        
        snake_pos[0] += DIRECTIONS[direction][0]
        snake_pos[1] += DIRECTIONS[direction][1]
        
        # Should be beyond screen height
        self.assertGreater(snake_pos[1], SCREEN_HEIGHT - 1)
    
    def test_self_collision(self):
        """Test snake colliding with itself"""
        # Snake body: head at [100, 100], then [80, 100], [60, 100]
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [60, 100]  # Moving to where body segment is
        
        # Check if head position matches any body segment (excluding head itself)
        game_over = any(seg == snake_pos for seg in snake_body[1:])
        
        self.assertTrue(game_over)
    
    def test_no_self_collision(self):
        """Test snake not colliding with itself"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [120, 100]  # Moving to empty space
        
        game_over = any(seg == snake_pos for seg in snake_body[1:])
        
        self.assertFalse(game_over)
    
    def test_wrap_around_right(self):
        """Test wrap around when hitting right wall"""
        snake_pos = [SCREEN_WIDTH, 100]
        gw = (SCREEN_WIDTH // CELL_SIZE) * CELL_SIZE
        
        # Wrap around logic
        if snake_pos[0] >= gw:
            snake_pos[0] = 0
        
        self.assertEqual(snake_pos[0], 0)
    
    def test_wrap_around_left(self):
        """Test wrap around when hitting left wall"""
        snake_pos = [-CELL_SIZE, 100]
        gw = (SCREEN_WIDTH // CELL_SIZE) * CELL_SIZE
        
        # Wrap around logic
        if snake_pos[0] < 0:
            snake_pos[0] = gw - CELL_SIZE
        
        self.assertEqual(snake_pos[0], gw - CELL_SIZE)
    
    def test_wrap_around_top(self):
        """Test wrap around when hitting top wall"""
        snake_pos = [100, -CELL_SIZE]
        gh = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
        
        # Wrap around logic
        if snake_pos[1] < 0:
            snake_pos[1] = gh - CELL_SIZE
        
        self.assertEqual(snake_pos[1], gh - CELL_SIZE)
    
    def test_wrap_around_bottom(self):
        """Test wrap around when hitting bottom wall"""
        snake_pos = [100, SCREEN_HEIGHT]
        gh = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
        
        # Wrap around logic
        if snake_pos[1] >= gh:
            snake_pos[1] = 0
        
        self.assertEqual(snake_pos[1], 0)


class TestDirectionChanges(unittest.TestCase):
    """Test direction change logic"""
    
    def test_opposite_directions_right_left(self):
        """Test that snake cannot reverse from right to left"""
        current_direction = "RIGHT"
        change_to = "LEFT"
        
        # Should not allow opposite direction
        if change_to != OPPOSITES[current_direction]:
            current_direction = change_to
        
        self.assertEqual(current_direction, "RIGHT")
    
    def test_opposite_directions_up_down(self):
        """Test that snake cannot reverse from up to down"""
        current_direction = "UP"
        change_to = "DOWN"
        
        if change_to != OPPOSITES[current_direction]:
            current_direction = change_to
        
        self.assertEqual(current_direction, "UP")
    
    def test_valid_direction_change_right_to_up(self):
        """Test valid direction change from right to up"""
        current_direction = "RIGHT"
        change_to = "UP"
        
        # Should allow non-opposite direction
        if change_to != OPPOSITES[current_direction]:
            current_direction = change_to
        
        self.assertEqual(current_direction, "UP")
    
    def test_valid_direction_change_down_to_left(self):
        """Test valid direction change from down to left"""
        current_direction = "DOWN"
        change_to = "LEFT"
        
        if change_to != OPPOSITES[current_direction]:
            current_direction = change_to
        
        self.assertEqual(current_direction, "LEFT")
    
    def test_all_opposite_pairs(self):
        """Test all opposite direction pairs"""
        for direction, opposite in OPPOSITES.items():
            current = direction
            change_to = opposite
            
            if change_to != OPPOSITES[current]:
                current = change_to
            
            # Should still be the original direction
            self.assertEqual(current, direction)


class TestFoodEating(unittest.TestCase):
    """Test food eating and score logic"""
    
    def test_food_eaten(self):
        """Test detecting when snake eats food"""
        snake_pos = [100, 100]
        food_pos = [100, 100]
        
        ate = (snake_pos == food_pos)
        
        self.assertTrue(ate)
    
    def test_food_not_eaten(self):
        """Test when snake doesn't eat food"""
        snake_pos = [100, 100]
        food_pos = [120, 100]
        
        ate = (snake_pos == food_pos)
        
        self.assertFalse(ate)
    
    def test_double_food_eaten_first(self):
        """Test eating first food when both exist"""
        snake_pos = [100, 100]
        food_pos = [100, 100]
        food2_pos = [120, 100]
        
        ate = False
        if snake_pos == food_pos:
            ate = True
        elif snake_pos == food2_pos:
            ate = True
        
        self.assertTrue(ate)
    
    def test_double_food_eaten_second(self):
        """Test eating second food when both exist"""
        snake_pos = [120, 100]
        food_pos = [100, 100]
        food2_pos = [120, 100]
        
        ate = False
        if snake_pos == food_pos:
            ate = True
        elif snake_pos == food2_pos:
            ate = True
        
        self.assertTrue(ate)


class TestSnakeBodyManagement(unittest.TestCase):
    """Test snake body growth and shrinking"""
    
    def test_body_growth_on_eat(self):
        """Test snake body grows when eating food"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [120, 100]
        ate = True
        
        # Add new head
        snake_body.insert(0, list(snake_pos))
        
        # Don't remove tail if ate
        if not ate:
            snake_body.pop()
        
        # Body should have grown by 1
        self.assertEqual(len(snake_body), 4)
        self.assertEqual(snake_body[0], [120, 100])
    
    def test_body_no_growth_on_move(self):
        """Test snake body doesn't grow when not eating"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [120, 100]
        ate = False
        
        # Add new head
        snake_body.insert(0, list(snake_pos))
        
        # Remove tail if didn't eat
        if not ate:
            snake_body.pop()
        
        # Body should stay same length
        self.assertEqual(len(snake_body), 3)
        self.assertEqual(snake_body[0], [120, 100])
    
    def test_body_movement_sequence(self):
        """Test complete movement sequence"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [120, 100]
        ate = False
        
        # Movement sequence
        snake_body.insert(0, list(snake_pos))
        if not ate:
            snake_body.pop()
        
        # Body should have moved forward
        self.assertEqual(len(snake_body), 3)
        self.assertEqual(snake_body[0], [120, 100])
        self.assertEqual(snake_body[1], [100, 100])
        self.assertEqual(snake_body[2], [80, 100])
    
    def test_body_growth_sequence(self):
        """Test body growth after eating multiple foods"""
        snake_body = [[100, 100], [80, 100]]
        
        # Eat first food
        snake_body.insert(0, [120, 100])
        # Don't pop because ate
        
        # Eat second food
        snake_body.insert(0, [140, 100])
        # Don't pop because ate
        
        # Body should have grown by 2
        self.assertEqual(len(snake_body), 4)
        self.assertEqual(snake_body[0], [140, 100])
        self.assertEqual(snake_body[1], [120, 100])
        self.assertEqual(snake_body[2], [100, 100])
        self.assertEqual(snake_body[3], [80, 100])


class TestGameOverConditions(unittest.TestCase):
    """Test various game over conditions"""
    
    def test_game_over_wall_collision_no_wrap(self):
        """Test game over when hitting wall without wrap around"""
        snake_pos = [-10, 100]
        wall_kill = True
        
        game_over = wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                                  snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)
        
        self.assertTrue(game_over)
    
    def test_game_over_wall_collision_with_wrap(self):
        """Test no game over when wrap around is enabled"""
        snake_pos = [-10, 100]
        wall_kill = False  # wrap_around is True
        
        game_over = wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                                  snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)
        
        self.assertFalse(game_over)
    
    def test_game_over_self_collision(self):
        """Test game over when snake hits itself"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [80, 100]
        wall_kill = False
        
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        
        self.assertTrue(game_over)
    
    def test_no_game_over(self):
        """Test no game over in normal play"""
        snake_body = [[100, 100], [80, 100], [60, 100]]
        snake_pos = [120, 100]
        wall_kill = False
        
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        
        self.assertFalse(game_over)


class TestScoreAttackMode(unittest.TestCase):
    """Test Score Attack mode specific logic"""
    
    def test_sa_targets(self):
        """Test score attack targets are valid"""
        self.assertEqual(SA_TARGETS, [15, 30, 50])
        
        for target in SA_TARGETS:
            self.assertGreater(target, 0)
            self.assertLessEqual(target, 100)
    
    def test_sa_completion(self):
        """Test score attack completion"""
        target = 15
        score = 15
        
        completed = score >= target
        
        self.assertTrue(completed)
    
    def test_sa_not_completed(self):
        """Test score attack not completed"""
        target = 30
        score = 15
        
        completed = score >= target
        
        self.assertFalse(completed)


if __name__ == '__main__':
    unittest.main()
