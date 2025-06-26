CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE tiff_metadata (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_time TIMESTAMP NOT NULL,
    epsg INTEGER,
    value TEXT,
    geom geometry(POLYGON, 4326),  -- 4326 is WGS84 (latitude/longitude)
    source_path TEXT,
    file_size FLOAT,
    band_type TEXT
);
