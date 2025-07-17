import requests
import json
import ollama
import re
import sys
import os

# MCP server settings
MCP_BASE_URL = "http://127.0.0.1:11435"

# List of available tools
AVAILABLE_TOOLS = {
    "analyze_tiff": "Analyzes a TIFF file and returns metadata",
    "crop_image": "Crops the TIFF file according to the given coordinates and saves as PNG",
    "get_ndvi": "Calculates the NDVI value at the given coordinates"
}

def parse_mcp_response(response_text):
    """Parses MCP event-stream (SSE) responses as JSON."""
    if "data:" in response_text:
        lines = [line for line in response_text.splitlines() if line.startswith("data:")]
        if not lines:
            return None
        json_str = lines[-1][len("data: "):]
        try:
            data = json.loads(json_str)
            return data
        except Exception as e:
            print("JSON parse error:", e)
            return None
    else:
        try:
            return json.loads(response_text)
        except Exception as e:
            print("JSON parse error:", e)
            return None

def call_mcp_tool(tool_name, params):
    """Calls the MCP tool."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        },
        "id": 1
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    try:
        print(f"🔧 MCP call: {tool_name}")
        resp = requests.post(f"{MCP_BASE_URL}/mcp", json=payload, headers=headers)
        result = parse_mcp_response(resp.text)

        if result is None:
            print(f"❌ Could not parse MCP response: {resp.text}")
            return None

        if "result" in result:
            return result["result"]
        elif "error" in result:
            return result["error"]
        else:
            return result

    except Exception as e:
        print(f"❌ MCP connection error: {e}")
        return None

def multi_tool_pattern_matching(user_input):
    """
    Generates a list of tool calls and parameters from the user's input.
    Returns: [("tool_name", params), ...]
    """
    user_input_lower = user_input.lower()
    results = []
    used_spans = []

    # Find file path - only once
    file_patterns = [
        r'[a-zA-Z]:[/\\][^\s]+\.(?:tiff?|jp2)',  # Windows paths
        r'/[^\s]+\.(?:tiff?|jp2)',  # Unix paths
        r'[^\s]+\.(?:tiff?|jp2)',  # Relative paths
        r'"([^"]+\.(?:tiff?|jp2))"',  # Quoted paths
        r"'([^']+\.(?:tiff?|jp2))'"  # Single quoted paths
    ]
    filepath = None
    for pattern in file_patterns:
        match = re.search(pattern, user_input)
        if match:
            filepath = match.group(1) if match.groups() else match.group(0)
            filepath = filepath.strip('"\'')
            break
    if not filepath:
        return []

    # 1. Analyze
    analyze_keywords = ['analyze', 'process', 'examine', 'check', 'inspect', 'load', 'open', 'read', 'save']
    if any(k in user_input_lower for k in analyze_keywords):
        results.append(('analyze_tiff', {'filepath': filepath}))

    # 2. Crop
    crop_keywords = ['crop', 'cut', 'slice', 'extract', 'region']
    if any(k in user_input_lower for k in crop_keywords):
        coord_patterns = [
            r'minx[:\s=]+([0-9.]+)',
            r'miny[:\s=]+([0-9.]+)',
            r'maxx[:\s=]+([0-9.]+)',
            r'maxy[:\s=]+([0-9.]+)'
        ]
        coords = {}
        for i, pattern in enumerate(coord_patterns):
            match = re.search(pattern, user_input)
            if match:
                coord_names = ['minx', 'miny', 'maxx', 'maxy']
                coords[coord_names[i]] = float(match.group(1))
        # Alternative coordinate formats
        if len(coords) < 4:
            from_to_pattern = r'from\s+([0-9.]+)[,\s]+([0-9.]+)\s+to\s+([0-9.]+)[,\s]+([0-9.]+)'
            match = re.search(from_to_pattern, user_input)
            if match:
                coords = {
                    'minx': float(match.group(1)),
                    'miny': float(match.group(2)),
                    'maxx': float(match.group(3)),
                    'maxy': float(match.group(4))
                }
        if len(coords) == 4:
            crop_params = {'filepath': filepath, **coords}
            results.append(('crop_image', crop_params))

    # 3. NDVI
    ndvi_keywords = ['ndvi', 'vegetation', 'index', 'plant']
    if any(k in user_input_lower for k in ndvi_keywords):
        # Find all x/y, use the last one
        x_matches = list(re.finditer(r'x[:\s=]+([0-9.]+)', user_input, re.IGNORECASE))
        y_matches = list(re.finditer(r'y[:\s=]+([0-9.]+)', user_input, re.IGNORECASE))
        x_coord = float(x_matches[-1].group(1)) if x_matches else None
        y_coord = float(y_matches[-1].group(1)) if y_matches else None

        if x_coord is not None and y_coord is not None:
            ndvi_params = {'filepath': filepath, 'x': x_coord, 'y': y_coord}
            results.append(('get_ndvi', ndvi_params))

    return results

def provide_help_response(user_input):
    """Returns a help message for the user"""
    help_responses = {
        'analyze': """
📁 Use the following format to analyze a file:
• "Analyze this file: C:/path/to/your/file.tiff"
• "Process satellite.jp2"
        """,
        'crop': """
✂️ Use the following format to crop an image:
• "Crop image.tiff minx:100 miny:200 maxx:800 maxy:600"
• "Cut from 100,200 to 800,600 in satellite.jp2"
        """,
        'ndvi': """
🌱 Use the following format to calculate NDVI:
• "Calculate NDVI: file.tiff x:500 y:300"
• "Vegetation index at point (400, 350) in satellite.tiff"
        """,
        'general': """
🤖 Geospatial Data Processing Assistant

I can:
1. 📁 Analyze TIFF/JP2 files
2. ✂️ Crop images by coordinates
3. 🌱 Calculate NDVI (vegetation index)

Sample commands:
• "Analyze this file: C:/data/image.tiff"
• "Crop image.tiff minx:100 miny:200 maxx:800 maxy:600"
• "Calculate NDVI: satellite.tiff x:500 y:300"

Type 'help' for assistance.
        """
    }

    user_lower = user_input.lower()

    if any(word in user_lower for word in ['help', 'how']):
        return help_responses['general']
    elif any(word in user_lower for word in ['analyze']):
        return help_responses['analyze']
    elif any(word in user_lower for word in ['crop', 'cut']):
        return help_responses['crop']
    elif any(word in user_lower for word in ['ndvi', 'vegetation']):
        return help_responses['ndvi']
    else:
        return help_responses['general']

def main():
    print("🚀 MCP Tool Calling Assistant")
    print("📡 MCP Server:", MCP_BASE_URL)
    print("💡 Multi-tool support enabled\n")
    while True:
        try:
            user_input = input("➤ Your request: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Exiting!")
                break
            if not user_input:
                continue
            if any(word in user_input.lower() for word in ['help', 'how']):
                print(provide_help_response(user_input))
                continue

            tool_calls = multi_tool_pattern_matching(user_input)
            if tool_calls:
                last_result = None
                for tool_name, params in tool_calls:
                    if 'filepath' in params and not os.path.exists(params['filepath']):
                        print(f"❌ File not found: {params['filepath']}")
                        print("💡 Check the file path and try again.")
                        break

                    print(f"🔧 Calling tool: {tool_name}")
                    print(f"📋 Parameters: {params}")
                    result = call_mcp_tool(tool_name, params)
                    if result:
                        print("✅ Result:")
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                        last_result = result
                    else:
                        print("❌ Tool call failed")
                        break
            else:
                print("❓ Command not understood.")
                print(provide_help_response(user_input))
        except KeyboardInterrupt:
            print("\n👋 Exiting!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
