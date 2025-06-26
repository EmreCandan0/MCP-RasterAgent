# MCP-RasterAgent

A Python [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) agent for analyzing and cropping local GeoTIFF files by file path and saving the cropped file as PNG.  
Integrates seamlessly with Claude Desktop and other MCP-compatible systems.

---

## Features

- **Analyze** local GeoTIFF files: extract bounding box, metadata, color band info, and EPSG code.
- **Crop** GeoTIFFs by bounding box and export as PNG.
- **MCP Native:** Runs as a `stdio` MCP agent for direct Claude Desktop integration.
- **No file upload:** Works directly with files on disk—ideal for desktop or secure environments.  
  _(Note: Because Claude Desktop doesn't support TIFF uploads, this agent uses file paths instead of uploads.)_
- **Extensible:** Easy to add more geospatial tools.

---

## Requirements

- Python 3.8+
- [GDAL](https://gdal.org/) Python bindings
- [modelcontextprotocol (mcp) Python SDK](https://pypi.org/project/modelcontextprotocol/)  
  `pip install "mcp[cli]"`
- Claude Desktop (optional, for GUI workflow)
- PostgreSQL/PostGIS (optional, if saving metadata in a database)
- Project scripts: `main.py`, `funcs_pool.py` etc.

---

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/MCP-RasterAgent.git
    cd MCP-RasterAgent
    ```

2. **(Recommended) Create and activate a conda environment**
    ```bash
    conda create -n geotiff_mcp python=3.10 gdal
    conda activate geotiff_mcp
    ```

3. **Install Python dependencies**
    ```bash
    pip install "mcp[cli]"
    pip install psycopg2-binary   # Only if you use PostGIS
    ```

---

## Usage

### Claude Desktop Integration

1. Make sure `main.py` and `funcs_pool.py` are present in your project folder.
2. In Claude Desktop, click the menu (bars) at the top left, select **File > Settings**, and in the Developer section edit your `claude_desktop_config.json`.
3. Copy the sample config JSON file provided in this repository into your configuration.
4. Restart Claude Desktop.  
   You’ll see “MCP-RasterAgent” available as an agent/tool with two functions.
5. When prompted, enter the **full local file path** to your `.tif` or `.tiff` file.

**Note:**  
You don’t have to run `python main.py` manually—Claude Desktop handles launching the agent via `stdio`.  
If you want to use HTTP transport (for custom integrations), you can run the code directly and configure the agent accordingly.



![tools](https://github.com/user-attachments/assets/8a7182b6-b12b-4ef2-b08b-7475418bfad2)



![1](https://github.com/user-attachments/assets/042a533e-3b43-42fb-8f16-504504fc34e6)



![2](https://github.com/user-attachments/assets/15ab6c09-ef28-45f2-9217-ccca78f42ef6)




