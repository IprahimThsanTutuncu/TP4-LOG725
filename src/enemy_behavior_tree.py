from abc import ABC, abstractmethod

class BehaviorTreeNode(ABC):
    @abstractmethod
    def update(self, bullets, walls):
        pass


class ActionNode(BehaviorTreeNode):
    def __init__(self, action_func):
        self.action_func = action_func

    def update(self, bullets, walls):
        return self.action_func(bullets, walls)


class ConditionNode(BehaviorTreeNode):
    def __init__(self, condition_func):
        self.condition_func = condition_func

    def update(self, bullets, walls):
        return self.condition_func(bullets, walls)


class SequenceNode(BehaviorTreeNode):
    def __init__(self, children):
        self.children = children

    def update(self, bullets, walls):
        for child in self.children:
            if not child.update(bullets, walls):
                return False
        return True


class SelectorNode(BehaviorTreeNode):
    def __init__(self, children):
        self.children = children

    def update(self, bullets, walls):
        for child in self.children:
            if child.update(bullets, walls):
                return True
        return False
