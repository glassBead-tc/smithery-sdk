from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError as PydanticValidationError
from starlette.requests import Request

T = TypeVar("T")


class Ok:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err:
    def __init__(self, problem: Dict[str, Any]):
        self.problem = problem

    def __repr__(self) -> str:
        return f"Err({self.problem!r})"


_RESERVED = {"config", "api_key", "profile"}


def _deep_merge(a: MutableMapping[str, Any], b: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """
    Deep-merge mapping b into mapping a (in place). Values from b override a.
    """
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _deep_merge(a[k], v)
        else:
            a[k] = v
    return a


def _set_nested(target: MutableMapping[str, Any], path: List[str], value: Any) -> None:
    """
    Set nested value on a mapping given a path of keys.
    """
    cur = target
    for key in path[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    cur[path[-1]] = value


def _brackets_to_dots(key: str) -> str:
    """
    Convert bracket-style keys (a[b][c]) to dot-style (a.b.c).
    """
    out = []
    buf = []
    i = 0
    while i < len(key):
        ch = key[i]
        if ch == "[":
            # flush buffer to out
            if buf:
                out.append("".join(buf))
                buf = []
            # read until closing bracket
            j = i + 1
            seg = []
            while j < len(key) and key[j] != "]":
                seg.append(key[j])
                j += 1
            out.append("".join(seg))
            i = j  # will increment below; at ']' or end
        elif ch == "]":
            # skip stray closers
            pass
        else:
            buf.append(ch)
        i += 1
    if buf:
        out.append("".join(buf))
    # remove empty segments
    out = [seg for seg in out if seg]
    return ".".join(out)


def _parse_dot_and_bracket_params(query: Mapping[str, str]) -> Dict[str, Any]:
    """
    Parse dot and bracket notation from query parameters into a nested dict.

    Examples:
      a.b.c=1 -> {"a": {"b": {"c": "1"}}}
      a[b][c]=x -> {"a": {"b": {"c": "x"}}}
    """
    result: Dict[str, Any] = {}
    for key, value in query.items():
        if key in _RESERVED:
            continue
        dotted = _brackets_to_dots(key)
        path = dotted.split(".") if "." in dotted else [dotted]
        if len(path) == 1 and path[0] == "":
            continue
        _set_nested(result, path, value)
    return result


def parse_and_validate_config(
    request: Request,
    schema: Optional[Type[BaseModel]] = None,
) -> Union[Ok, Err]:
    """
    Parse and optionally validate a configuration payload from a Starlette/FastAPI Request.

    Behavior parity target (TS):
      - Accept base64 `config` query parameter containing JSON object
      - Merge dot/bracket-notation query params on top (e.g., a.b.c=x, a[b][c]=x)
      - Reserved params (`config`, `api_key`, `profile`) are skipped during dot/bracket parsing
      - If `schema` provided (Pydantic model), validate and produce structured 422 problem on error
      - 400 error for invalid base64 or non-JSON `config` payloads

    Returns:
      Ok[T] where T is the schema instance (if provided) or dict when validation passes
      Err[ProblemDetails] on parse/validation failure

    ProblemDetails (shape):
      {
        "title": str,
        "status": int,
        "detail": str,
        "instance": str,  # request path
        "configSchema": {...},  # when schema provided
        "errors": [
          { "param": str, "pointer": str, "reason": str, "received": Any }
        ]
      }
    """
    instance = str(request.url.path)

    # Start with config from base64 if present
    config_obj: Dict[str, Any] = {}
    base64_config = request.query_params.get("config")
    if base64_config:
        try:
            decoded = base64.b64decode(base64_config, validate=True)
            parsed = json.loads(decoded.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("Decoded config is not a JSON object")
            config_obj = parsed
        except Exception as e:
            problem: Dict[str, Any] = {
                "title": "Invalid config encoding",
                "status": 400,
                "detail": "The 'config' query parameter must be base64-encoded JSON object.",
                "instance": instance,
                "errors": [
                    {
                        "param": "config",
                        "pointer": "config",
                        "reason": str(e),
                        "received": base64_config[:64] + ("..." if len(base64_config) > 64 else ""),
                    }
                ],
            }
            # Include schema if provided for better client UX
            if schema is not None:
                try:
                    problem["configSchema"] = schema.model_json_schema()
                except Exception:
                    pass
            return Err(problem)

    # Merge dot/bracket params on top (they override base config)
    dot_params = _parse_dot_and_bracket_params(request.query_params)
    _deep_merge(config_obj, dot_params)

    # If schema provided, validate using Pydantic
    if schema is not None:
        try:
            model = schema(**config_obj)
            return Ok(model)
        except PydanticValidationError as e:
            errs = []
            for err in e.errors():
                # Pydantic v2 error structure includes "loc", "msg", "type", "input" etc.
                loc = err.get("loc", ())
                pointer = ".".join([str(p) for p in loc]) if loc else ""
                errs.append(
                    {
                        "param": pointer,
                        "pointer": pointer,
                        "reason": err.get("msg", "Invalid value"),
                        "received": err.get("input"),
                    }
                )

            problem = {
                "title": "Invalid configuration",
                "status": 422,
                "detail": "Configuration failed schema validation.",
                "instance": instance,
                "configSchema": schema.model_json_schema(),
                "errors": errs,
            }
            return Err(problem)

    # No schema → return the merged dict
    return Ok(config_obj)
