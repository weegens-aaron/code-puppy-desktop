"""Model service abstraction for Dependency Inversion.

Provides an interface for model operations, allowing panels to depend on
abstractions rather than concrete code_puppy implementations.
"""

from dataclasses import dataclass, field
from typing import Optional, Protocol


@dataclass
class ModelInfo:
    """Data transfer object for model information."""
    name: str
    model_type: str = "unknown"
    context_length: int = 0
    is_current: bool = False
    config: dict = field(default_factory=dict)

    @property
    def context_display(self) -> str:
        """Get human-readable context length."""
        if self.context_length >= 1_000_000:
            return f"{self.context_length / 1_000_000:.1f}M"
        elif self.context_length >= 1_000:
            return f"{self.context_length / 1_000:.0f}K"
        return str(self.context_length)

    @property
    def type_icon(self) -> str:
        """Get icon for model type."""
        icons = {
            "anthropic": "\U0001f7e3",
            "openai": "\U0001f7e2",
            "gemini": "\U0001f535",
            "custom_openai": "\u2699\ufe0f",
            "custom_anthropic": "\u2699\ufe0f",
            "azure_openai": "\u2601\ufe0f",
            "openrouter": "\U0001f310",
            "round_robin": "\U0001f504",
            "cerebras": "\u26a1",
        }
        return icons.get(self.model_type, "\U0001f916")


class ModelServiceProtocol(Protocol):
    """Protocol defining model service operations.

    Panels depend on this protocol, not concrete implementations (DIP).
    """

    def get_available_models(self) -> list[ModelInfo]:
        """Get list of available models with their info."""
        ...

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        ...

    def set_current_model(self, model_name: str) -> bool:
        """Set the current model by name. Returns True on success."""
        ...


class ModelService:
    """Concrete implementation of ModelServiceProtocol.

    Wraps code_puppy model functions to provide a clean interface.
    """

    def __init__(self):
        self._models_config: dict = {}

    def get_available_models(self) -> list[ModelInfo]:
        """Get list of available models with their info."""
        from code_puppy.model_factory import ModelFactory
        from code_puppy.command_line.model_picker_completion import (
            get_active_model,
            load_model_names,
        )

        # Get current model
        current_model = (get_active_model() or "").lower()

        # Load model configs
        try:
            self._models_config = ModelFactory.load_config()
        except Exception:
            self._models_config = {}

        # Get model names
        try:
            model_names = load_model_names()
        except Exception:
            model_names = list(self._models_config.keys())

        # Build model info list
        models = []
        for name in model_names:
            config = self._models_config.get(name, {})
            models.append(ModelInfo(
                name=name,
                model_type=config.get("type", "unknown"),
                context_length=config.get("context_length", 0),
                is_current=(name.lower() == current_model),
                config=config,
            ))

        # Sort: current first, then alphabetically
        return sorted(models, key=lambda m: (not m.is_current, m.name.lower()))

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        from code_puppy.command_line.model_picker_completion import get_active_model

        return get_active_model()

    def set_current_model(self, model_name: str) -> bool:
        """Set the current model by name. Returns True on success."""
        from code_puppy.command_line.model_picker_completion import set_active_model

        try:
            set_active_model(model_name)
            return True
        except Exception:
            return False


# Singleton instance for convenience
_model_service: Optional[ModelService] = None


def get_model_service() -> ModelService:
    """Get the singleton model service instance."""
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service
