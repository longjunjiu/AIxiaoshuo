"""
规则模块 - 整合所有创作规则
包括通用创作规则、反AI味规则、题材规则、经典网文参考
"""

from .craft import CraftRules
from .anti_slop import AntiSlopRules
from .genre_rules import GenreRules
from .classic_novels import get_full_novel_writing_prompt

__all__ = [
    'CraftRules',
    'AntiSlopRules',
    'GenreRules',
    'get_full_novel_writing_prompt'
]
