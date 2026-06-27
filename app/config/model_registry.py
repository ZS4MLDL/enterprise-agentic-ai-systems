"""
Model registry — maps logical tiers to actual model IDs.
Modules use tiers (cheap/default/powerful), never hard-coded model strings.
"""
from enum import Enum
from app.config.settings import get_settings


class ModelTier(str, Enum):
    CHEAP = "cheap"        # classification, routing, low-stakes tasks
    DEFAULT = "default"    # general agent tasks
    POWERFUL = "powerful"  # complex reasoning, final synthesis


def get_model(tier: ModelTier = ModelTier.DEFAULT) -> str:
    s = get_settings()
    return {
        ModelTier.CHEAP: s.MODEL_CHEAP,
        ModelTier.DEFAULT: s.MODEL_DEFAULT,
        ModelTier.POWERFUL: s.MODEL_POWERFUL,
    }[tier]
