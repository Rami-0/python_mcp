import os
import json
from datetime import datetime
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("file-search")

@mcp.tool()
def file_search(query: str) -> str:
    """
    Search for files containing a specific query in the current directory.

    Args:
        query: The search term to look for in filenames (case-insensitive).

    Returns:
        A JSON string containing a list of found files with their details,
        or an error message if an exception occurs.
    """
    results: List[Dict[str, Any]] = []
    search_path = '/'  # Search in the current directory and subdirectories

    try:
        for root, dirs, files in os.walk(search_path):
            try:
                if any(skip_dir in root for skip_dir in ['/proc', '/sys', '/dev', '/tmp']):
                    continue
                for file in files:
                    full_path = os.path.join(root, file)
                    if query.lower() in file.lower():  # Simple filename search (case-insensitive)
                        try:
                            stats = os.stat(full_path)
                            creation_date = datetime.fromtimestamp(stats.st_ctime).isoformat()
                            file_info = {
                                "filename": file,
                                "path": full_path,
                                "size_bytes": stats.st_size,
                                "creation_date": creation_date
                            }
                            results.append(file_info)
                            if len(results) >= 100:
                                return json.dumps({"files": results, "count": len(results)})  # Limit results
                        except (PermissionError, FileNotFoundError):
                            continue  # Skip files we can't access
            except PermissionError:
                continue  # Skip directories we can't access

        return json.dumps({"files": results, "count": len(results)})

    except Exception as e:
        return json.dumps({"error": f"Error during file search: {str(e)}"})

if __name__ == "__main__":
    mcp.run(transport='stdio')
