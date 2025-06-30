from mcp.server.fastmcp import FastMCP
from funcs_pool import get_geom_wkt_and_bounds, save_metadata, get_epsg_from_dataset, clear_temp_dirs
from osgeo import gdal
import os
from datetime import datetime
import atexit

mcp = FastMCP("GeoTIFF Cropping Agent")

@atexit.register
def cleanup():
    clear_temp_dirs()

@mcp.tool()
def analyze_tiff(filepath: str) -> dict:
    """
    Gets the filepath from user and returns metadata/extent
    """

    dataset = gdal.Open(filepath)
    metadata = dataset.GetMetadata()

    source_path = os.path.abspath(filepath)
    key = "AREA_OR_POINT"
    value = metadata.get(key)
    file_size = round(os.path.getsize(source_path) / (1024 * 1024), 2)

    band_type_list = []
    for i in range(dataset.RasterCount):
        band = dataset.GetRasterBand(i + 1)
        color_interp_code = band.GetColorInterpretation()
        color_name = gdal.GetColorInterpretationName(color_interp_code).capitalize()
        if color_name:
            band_type_list.append(color_name)
    if set(band_type_list) == {"Red", "Green", "Blue"}:
        band_type = "RGB"
    elif "Gray" in band_type_list or len(band_type_list) == 1:
        band_type = "Panchromatic"
    else:
        band_type = ",".join(band_type_list)

    geom_str = get_geom_wkt_and_bounds(dataset)
    epsg_code = get_epsg_from_dataset(dataset)
    upload_time = datetime.now()

    save_metadata(
        os.path.basename(filepath),
        upload_time,
        epsg_code,
        value,
        geom_str,
        source_path,
        file_size,
        band_type
    )


    reprojected_path = f'temp/reprojected_{os.path.basename(filepath)}'
    warp_result = gdal.Warp(reprojected_path, filepath, dstSRS='EPSG:4326')
    if warp_result is None:
        return {"error": "Warp failed"}

    ds = gdal.Open(reprojected_path)
    gt = ds.GetGeoTransform()
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + (ds.RasterXSize * gt[1])
    miny = maxy + (ds.RasterYSize * gt[5])

    return {
        "message": "TIFF analyzed successfully.",
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy,
        "filename": os.path.basename(filepath)
    }

@mcp.tool()
def crop_image(filepath: str, minx: float, miny: float, maxx: float, maxy: float) -> dict:
    """
    Crops and saves a png file according to the given TIFF
    """
    reprojected_path = f'temp/reprojected_{os.path.basename(filepath)}'
    output_path = f'static/outputs/{os.path.splitext(os.path.basename(filepath))[0]}_cropped.png'

    if not os.path.exists(reprojected_path):
        return {"error": "Reprojected file not found"}

    options = gdal.TranslateOptions(
        format='PNG',
        projWin=[minx, maxy, maxx, miny],
        outputType=gdal.GDT_Byte,
        scaleParams=[[0, 1, 0, 255]]
    )

    gdal.Translate(output_path, reprojected_path, options=options)

    return {"image_url": output_path}

@mcp.tool()
def get_ndvi(filepath: str, x: float, y: float) -> dict:

    reprojected_path = f'temp/reprojected_{os.path.basename(filepath)}'


    if not os.path.exists(reprojected_path):
        gdal.Warp(reprojected_path, filepath, dstSRS='EPSG:4326', format='GTiff')

    dataset = gdal.Open(reprojected_path)
    red_band = dataset.GetRasterBand(1).ReadAsArray().astype(float)
    nir_band = dataset.GetRasterBand(2).ReadAsArray().astype(float)

    ndvi = (nir_band - red_band) / (nir_band + red_band)
    ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=0.0, neginf=0.0)
    ndvi_mean = ndvi.mean()

    gt = dataset.GetGeoTransform()
    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])

    if 0 <= px < ndvi.shape[1] and 0 <= py < ndvi.shape[0]:
        ndvi_point = ndvi[py, px]
    else:
        ndvi_point = None

    return {
        "ndvi_mean": ndvi_mean,
        "ndvi_point": ndvi_point
    }


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    os.makedirs("static/outputs", exist_ok=True)
    mcp.run(transport="stdio")
