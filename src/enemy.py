import pygame
import math
from abc import ABC, abstractmethod
import time

class BehaviorTreeNode(ABC):
    @abstractmethod
    def update(self, bullets, walls, enemy):
        pass


class ActionNode(BehaviorTreeNode):
    def __init__(self, action_func):
        self.action_func = action_func

    def update(self, bullets, walls, enemy):
        return self.action_func(bullets, walls, enemy)


class ConditionNode(BehaviorTreeNode):
    def __init__(self, condition_func):
        self.condition_func = condition_func

    def update(self, bullets, walls, enemy):
        return self.condition_func(bullets, walls, enemy)


class SequenceNode(BehaviorTreeNode):
    def __init__(self, children):
        self.children = children

    def update(self, bullets, walls, enemy):
        for child in self.children:
            if not child.update(bullets, walls, enemy):
                return False
        return True


class SelectorNode(BehaviorTreeNode):
    def __init__(self, children):
        self.children = children

    def update(self, bullets, walls, enemy):
        for child in self.children:
            if child.update(bullets, walls, enemy):
                return True
        return False


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.noeud = 0
        self.is_hit = False
        self.current_sprite = pygame.image.load('./assets/enemy.png')
        self.rect = self.current_sprite.get_rect()
        self.starting_position = (400, 100)
        self.rect.center = self.starting_position
        self.speed = 2
        self.backoff_time = 1000
        self.last_hit_time = 0
        self.is_waiting = False

        # Initialize the behavior tree
        self.condition_is_behind_wall = ConditionNode(self.is_behind_wall)
        self.condition_is_not_behind_wall = ConditionNode(self.is_not_behind_wall)

        self.condition_is_no_left = ConditionNode(self.is_there_no_bullet)
        self.condition_is_any_bullet = ConditionNode(self.is_there_any_bullet)

        self.condition_is_hit_recently = ConditionNode(self.is_hit_recently)

        self.action_move_to_away = ActionNode(self.move_away)
        self.action_move_to_start = ActionNode(self.move_to_starting_position)
        self.action_wait = ActionNode(self.wait)
        self.action_move_to_wall = ActionNode(self.move_to_closest_wall)

        self.root = SelectorNode([
            SequenceNode([self.condition_is_no_left, self.action_move_to_start]), 
            SequenceNode([self.condition_is_behind_wall, self.action_wait]),
            SequenceNode([self.condition_is_any_bullet, self.action_move_to_away]), 
            SequenceNode([self.condition_is_no_left, self.action_move_to_start]), 
            self.action_wait
        ])


    def is_there_no_bullet(self, bullets, walls, enemy):
        return self.closest_bullet(bullets) is None

    def is_there_any_bullet(self, bullets, walls, enemy):
        return self.closest_bullet(bullets) is not None

    def compute_distance(self, bullet):
        enemy_x, enemy_y = self.rect.center
        bullet_x, bullet_y = bullet.rect.center
        distance = math.sqrt((bullet_x - enemy_x) ** 2 + (bullet_y - enemy_y) ** 2)
        return distance
    
    def closest_bullet(self, bullets):
        closest_bullet = None
        min_distance = float('inf')

        for bullet in bullets:
            distance = self.compute_distance(bullet)
            
            if distance < min_distance:
                min_distance = distance
                closest_bullet = bullet

        return closest_bullet
    
    def is_bullet_on_left_side(self, bullets, walls, enemy):
        closest_bullet = self.closest_bullet(bullets)
        if closest_bullet:
            return closest_bullet.rect.x < self.rect.centerx
        return False

    def move_to_starting_position(self, bullets, walls, enemy):
        direction = self.starting_position[0] - self.rect.centerx
        if direction != 0:
            self.rect.x += self.speed if direction > 0 else -self.speed

    def is_behind_wall(self, bullets, walls, enemy):
        for wall in walls:
            horizontal_check = self.rect.left > wall.rect.left and self.rect.right < wall.rect.right
            vertical_check = self.rect.bottom < wall.rect.top
            if horizontal_check and vertical_check:
                return True
        return False
    
    def is_not_behind_wall(self, bullets, walls, enemy):
        for wall in walls:
            horizontal_check = self.rect.left > wall.rect.left and self.rect.right < wall.rect.right
            vertical_check = self.rect.bottom < wall.rect.top
            if horizontal_check and vertical_check:
                return False
        return True

    def move_away(self, bullets, walls, enemy):
        if(self.is_bullet_on_left_side(bullets, walls, enemy)):
            self.move_right(bullets, walls, enemy)
        else:
            self.move_left(bullets, walls, enemy)

    def move_to_closest_wall(self, bullets, walls, enemy):
        closest_wall = None
        min_distance = float('inf')

        for wall in walls:
            wall_center_x = (wall.rect.left + wall.rect.right) / 2 
            distance = self.rect.centerx - wall_center_x

            if abs(distance) < abs(min_distance):
                min_distance = distance
                closest_wall = wall

        if closest_wall:
            if min_distance < 0: 
                self.rect.x -= self.speed 
            elif min_distance > 0:
                self.rect.x += self.speed

    def move_right(self, bullets, walls, enemy):
        self.rect.x += self.speed

    def move_left(self, bullets, walls, enemy):
        self.rect.x -= self.speed

    def wait(self, bullets, walls, enemy):
        current_time = time.time() * 1000 
        if current_time - self.last_hit_time > self.backoff_time:
            self.is_waiting = False
            return True
        return False

    def is_hit_recently(self, bullets, walls, enemy):
        closest_bullet = self.closest_bullet(bullets)
        if closest_bullet and self.is_hit:
            self.last_hit_time = time.time() * 1000
            self.is_waiting = True
            return True
        return False

    def update(self, bullets, walls):
        self.root.update(bullets, walls, self)
