"""Generate small Freqtrade strategy adapters that enforce external leverage."""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LeverageAdapter:
    strategy_name: str
    strategy_path: pathlib.Path


def validate_leverage(value: float) -> float:
    leverage = float(value)
    if not 1.0 <= leverage <= 100.0:
        raise ValueError("leverage must be between 1 and 100")
    return leverage


def create_leverage_adapter(
    original_name: str,
    original_file: pathlib.Path,
    destination: pathlib.Path,
    leverage: float,
) -> LeverageAdapter:
    leverage = validate_leverage(leverage)
    destination.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"\W+", "_", original_name)
    leverage_token = str(leverage).replace(".", "_")
    adapter_name = f"{safe_name}__Leverage_{leverage_token}x"
    adapter_file = destination / f"{adapter_name}.py"
    source = f'''"""Generated adapter; signal logic is inherited unchanged."""
import importlib.util
import pathlib
import sys

_SOURCE = pathlib.Path({str(original_file.resolve())!r})
for _path in (_SOURCE.parent, _SOURCE.parent.parent):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
_SPEC = importlib.util.spec_from_file_location("_numb_original_{safe_name}", _SOURCE)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load strategy source: {{_SOURCE}}")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
_OriginalStrategy = getattr(_MODULE, {original_name!r})


class {adapter_name}(_OriginalStrategy):
    controlled_leverage = {leverage!r}

    def leverage(
        self, pair, current_time, current_rate, proposed_leverage,
        max_leverage, entry_tag, side, **kwargs
    ):
        return min(max(self.controlled_leverage, 1.0), max_leverage)
'''
    adapter_file.write_text(source, encoding="utf-8")
    return LeverageAdapter(strategy_name=adapter_name, strategy_path=destination)
