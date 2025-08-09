import json
import base64
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def create_smithery_url(
    base_url: str,
    *,
    api_key: Optional[str] = None,
    profile: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a Smithery URL with optional configuration parameters encoded in base64
    and optional API key/profile query parameters.

    Parity target: TS createSmitheryUrl(baseUrl, { apiKey?, profile?, config? })

    Args:
        base_url: The base URL to use.
        api_key: Optional API key to add as a query parameter (?api_key=...).
        profile: Optional profile identifier to add as a query parameter (?profile=...).
        config: Optional configuration object. Will be JSON-serialized and base64-encoded
                then added as the 'config' query parameter.

    Returns:
        The complete URL with any configuration parameters and credentials added.
    """
    # Parse the URL
    parsed_url = urlparse(base_url)

    # Parse existing query parameters into a dict[str, list[str]]
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)

    # Add config if provided (base64-encoded JSON)
    if config is not None:
        config_json = json.dumps(config, separators=(",", ":"), ensure_ascii=False)
        config_base64 = base64.b64encode(config_json.encode("utf-8")).decode("utf-8")
        query_params["config"] = [config_base64]

    # Add API key if provided
    if api_key:
        query_params["api_key"] = [api_key]

    # Add profile if provided
    if profile:
        query_params["profile"] = [profile]

    # Rebuild the query string
    new_query = urlencode(query_params, doseq=True)

    # Rebuild the URL with the new query string
    url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )
    return url
