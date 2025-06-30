# MCP-RasterAgent

A Python [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) agent for analyzing and cropping local GeoTIFF files by file path and saving the cropped file as PNG then calculating NDVI Mean and for the given points as X,Y coordinates.  
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



![tools](https://github.com/user-attachments/assets/67727bbc-76dd-4d6a-80c0-dd2eb093b1e7)



![1](https://github.com/user-attachments/assets/075b476f-8794-4889-9419-1d2d0d4205a9)



![2](https://github.com/user-attachments/assets/69d04073-b5e5-46b7-a780-f3d800b00192)


![image](https://github.com/user-attachments/assets/a129e40c-5d01-4157-9af0-5652ca4b4b4b)



