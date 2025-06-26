import shutil
from db_pool import db_pool
from osgeo import osr,gdal
import os



def get_epsg_from_dataset(dataset):
    """
       Extract the EPSG code from a GDAL dataset.

       :param dataset: GDAL dataset object.
       :type dataset: gdal.Dataset
       :return: EPSG code as a string (e.g., '4326') or None if unavailable.
       :rtype: str | None
       """
    proj = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(proj)

    if srs.IsProjected():
        return srs.GetAttrValue("AUTHORITY", 1)
    elif srs.IsGeographic():
        return srs.GetAttrValue("AUTHORITY", 1)
    else:
        return None

def save_metadata(filename:str, upload_time, epsg_code:int, value:str, geom_str:str,source_path:str,
                  file_size:float,band_type:str):
    """
    Save metadata for a TIFF file into the database.

    :param filename: The name of the uploaded TIFF file.
    :type filename: str
    :param upload_time: The upload timestamp (UTC).
    :type upload_time: datetime.pyi
    :param epsg_code: EPSG code of the original dataset projection.
    :type epsg_code: int
    :param value: The AREA_OR_POINT metadata value.
    :type value: str
    :param geom_str: WKT representation of the bounding box.
    :type geom_str: str
    :param source_path: Path to the TIFF file
    :type source_path:str
    :param file_size: TIFF file size as MB
    :type file_size: float
    :param band_type: Color band definition RGB or Panchromatic
    :type band_type:str
    :return: None
    :rtype: Null
    """
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        save = f"""
               INSERT INTO tiff_metadata (
                   filename, upload_time, epsg, value, geom,
                   source_path, file_size, band_type
               ) VALUES (
                   %s, %s, %s, %s,
                   ST_Transform(ST_SetSRID(ST_GeomFromText(%s), {epsg_code}), 4326),
                   %s, %s, %s
               )
           """
        cur.execute(save, (
            filename, upload_time, epsg_code, value, geom_str,
            source_path, file_size, band_type
        ))
        conn.commit()
        cur.close()
    except Exception as e:
        print("Metadata Insert Error:", e)
    finally:
        db_pool.putconn(conn)

def get_geom_wkt_and_bounds(dataset):
    """
    Generate the bounding box and WKT polygon of a raster dataset.

    :param dataset: The GDAL dataset object to extract bounding info from.
    :type dataset: gdal.Dataset
    :return: A tuple containing the WKT polygon and 4326 converted bounding box coordinates (minx, miny, maxx, maxy).
    :rtype: str
    """

    gt = dataset.GetGeoTransform()
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + (dataset.RasterXSize * gt[1])
    miny = maxy + (dataset.RasterYSize * gt[5])

    polygon_wkt = f"POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))"
    return polygon_wkt


def clear_temp_dirs():
    print("Cleaning up temp and upload directories...")
    for folder in ['uploads', 'temp']:
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                print(f"Failed to delete {path}: {e}")
