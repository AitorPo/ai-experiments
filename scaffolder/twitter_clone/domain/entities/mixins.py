"""
Base mixins for domain entities.
"""

from typing import Dict, Any
from abc import ABC


class ToDictMixin(ABC):
    """Mixin to add to_dict functionality to entities."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        if hasattr(self, 'model_dump'):
            # Pydantic model
            return self.model_dump()
        elif hasattr(self, '__dict__'):
            # Regular class
            return self.__dict__.copy()
        else:
            raise NotImplementedError("to_dict not implemented for this entity type")
