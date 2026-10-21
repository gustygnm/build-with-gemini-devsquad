# Copyright 2026 Google LLC
# Public API Tool for AI Dev Team Agent
import requests
from typing import Dict, Any

def check_pypi_package_info(package_name: str) -> Dict[str, Any]:
    """Look up real-time metadata, latest version, and license for any Python package on PyPI.
    
    Useful for the Developer and QA roles when evaluating library dependencies or verifying compatibility.
    
    Args:
        package_name: Name of the Python package (e.g. 'fastapi', 'pydantic', 'pytest').
        
    Returns:
        Dictionary with package summary, latest version, author, home page, and license.
    """
    url = f"https://pypi.org/pypi/{package_name.strip()}/json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return {"error": f"Package '{package_name}' not found on PyPI."}
        response.raise_for_status()
        data = response.json()
        info = data.get("info", {})
        return {
            "name": info.get("name"),
            "version": info.get("version"),
            "summary": info.get("summary"),
            "license": info.get("license"),
            "home_page": info.get("home_page") or info.get("project_url"),
            "requires_python": info.get("requires_python"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch package information: {str(e)}"}
