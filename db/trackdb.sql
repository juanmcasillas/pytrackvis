drop table if exists `TRACKS`;
drop table if exists `PLACES`;
drop table if exists `TRACK_IN_PLACES`;
drop table if exists `SIMILAR_TRACKS`;
PRAGMA encoding = "UTF-8"; 

CREATE TABLE if NOT exists `TRACKS` (
    `id`                  INTEGER PRIMARY KEY AUTOINCREMENT,
    `fname`               TEXT DEFAULT "",
    `hash`                TEXT DEFAULT "",
    `preview`             TEXT DEFAULT "",
    `preview_elevation`   TEXT DEFAULT "",
    `stamp`               INTEGER DEFAULT 0,

    `number_of_points`    INTEGER DEFAULT 0,
    `duration`            INTEGER DEFAULT 0,
    `quality`             REAL DEFAULT 0.0,

    `length_2d`           REAL DEFAULT 0.0,
    `length_3d`           REAL DEFAULT 0.0,

    `start_time`          INTEGER DEFAULT 0,
    `end_time`            INTEGER DEFAULT 0,
    `moving_time`         INTEGER DEFAULT 0,
    `stopped_time`        INTEGER DEFAULT 0,
    `moving_distance`     REAL DEFAULT 0,
    `stopped_distance`    REAL DEFAULT 0,

    `max_speed_ms`        REAL DEFAULT 0,
    `max_speed_kmh`       REAL DEFAULT 0,
    `avg_speed_ms`        REAL DEFAULT 0.0,
    `avg_speed_kmh`       REAL DEFAULT 0.0,

    `uphill_climb`        REAL DEFAULT 0.0,
    `downhill_climb`      REAL DEFAULT 0.0,
    `minimum_elevation`   REAL DEFAULT 0.0,
    `maximum_elevation`   REAL DEFAULT 0.0,

    -- metadata
    `name`                TEXT DEFAULT "",
    `searchname`          TEXT DEFAULT "",
    `kind`                TEXT DEFAULT "",
    `device`              TEXT DEFAULT "",
    `equipment`           TEXT DEFAULT "",
    `description`         TEXT DEFAULT "",
    `is_clockwise`        INTEGER DEFAULT 0,      -- 0 means clockwise route
    `score`               REAL DEFAULT 0,
    `rating`              REAL DEFAULT 0,

    -- boundingbox information
    `min_lat`              REAL DEFAULT 0.0,
    `min_long`             REAL DEFAULT 0.0,
    `max_lat`              REAL DEFAULT 0.0,
    `max_long`             REAL DEFAULT 0.0,
    
    -- begin point, middle point, end point
    `middle_lat`           REAL DEFAULT 0.0,   
    `middle_long`          REAL DEFAULT 0.0,   
    `middle_elev`          REAL DEFAULT 0.0,   
    
    `begin_lat`            REAL DEFAULT 0.0,   
    `begin_long`           REAL DEFAULT 0.0,   
    `begin_elev`           REAL DEFAULT 0.0,   
    
    `end_lat`              REAL DEFAULT 0.0,   
    `end_long`             REAL DEFAULT 0.0,   
    `end_elev`             REAL DEFAULT 0.0,   

    -- stats
    `uphill_distance`     REAL DEFAULT 0,
    `level_distance`      REAL DEFAULT 0,
    `downhill_distance`   REAL DEFAULT 0,
    
    `uphill_elevation`    REAL DEFAULT 0,
    `level_elevation`     REAL DEFAULT 0,
    `downhill_elevation`  REAL DEFAULT 0,
    
    `uphill_avg_slope`    REAL DEFAULT 0,
    `level_avg_slope`     REAL DEFAULT 0,
    `downhill_avg_slope`  REAL DEFAULT 0,
    
    `uphill_p_distance`   REAL DEFAULT 0,
    `level_p_distance`    REAL DEFAULT 0,
    `downhill_p_distance` REAL DEFAULT 0,

    --speed
    `uphill_speed`                    REAL DEFAULT 0,
    `level_speed`                     REAL DEFAULT 0,
    `downhill_speed`                  REAL DEFAULT 0,
    
    `uphill_time`                     INTEGER DEFAULT 0,
    `level_time`                      INTEGER DEFAULT 0,
    `downhill_time`                   INTEGER DEFAULT 0,
    
    `uphill_p_time`                   REAL DEFAULT 0,
    `level_p_time`                    REAL DEFAULT 0,
    `downhill_p_time`                 REAL DEFAULT 0,
    
    `uphill_slope_range_distance_0`     REAL DEFAULT 0,
    `uphill_slope_range_distance_1`     REAL DEFAULT 0,
    `uphill_slope_range_distance_2`     REAL DEFAULT 0,
    `uphill_slope_range_distance_3`     REAL DEFAULT 0,
    `uphill_slope_range_distance_4`     REAL DEFAULT 0,
    `uphill_slope_range_distance_5`     REAL DEFAULT 0,
    `uphill_slope_range_distance_6`     REAL DEFAULT 0,
    
    `downhill_slope_range_distance_0`     REAL DEFAULT 0,
    `downhill_slope_range_distance_1`     REAL DEFAULT 0,
    `downhill_slope_range_distance_2`     REAL DEFAULT 0,
    `downhill_slope_range_distance_3`     REAL DEFAULT 0,
    `downhill_slope_range_distance_4`     REAL DEFAULT 0,
    `downhill_slope_range_distance_5`     REAL DEFAULT 0,
    `downhill_slope_range_distance_6`     REAL DEFAULT 0,

    `uphill_slope_range_time_0`         REAL DEFAULT 0,
    `uphill_slope_range_time_1`         REAL DEFAULT 0,
    `uphill_slope_range_time_2`         REAL DEFAULT 0,
    `uphill_slope_range_time_3`         REAL DEFAULT 0,
    `uphill_slope_range_time_4`         REAL DEFAULT 0,
    `uphill_slope_range_time_5`         REAL DEFAULT 0,
    `uphill_slope_range_time_6`         REAL DEFAULT 0,
    
    `downhill_slope_range_time_0`         REAL DEFAULT 0,
    `downhill_slope_range_time_1`         REAL DEFAULT 0,
    `downhill_slope_range_time_2`         REAL DEFAULT 0,
    `downhill_slope_range_time_3`         REAL DEFAULT 0,
    `downhill_slope_range_time_4`         REAL DEFAULT 0,
    `downhill_slope_range_time_5`         REAL DEFAULT 0,
    `downhill_slope_range_time_6`         REAL DEFAULT 0,
    
    --misc data (from external sensors)
    `max_heart_rate`                  INTEGER DEFAULT 0,
    `min_heart_rate`                  INTEGER DEFAULT 0,
    `avg_heart_rate`                  REAL DEFAULT 0,
    `max_power`                       INTEGER DEFAULT 0,
    `min_power`                       INTEGER DEFAULT 0,
    `avg_power`                       REAL DEFAULT 0,
    `max_cadence`                     INTEGER DEFAULT 0,
    `min_cadence`                     INTEGER DEFAULT 0,
    `avg_cadence`                     REAL DEFAULT 0,
    `max_temperature`                 INTEGER DEFAULT 0,
    `min_temperature`                 INTEGER DEFAULT 0,    
    `avg_temperature`                 REAL DEFAULT 0
);

CREATE TABLE if NOT exists  `PLACES` (
    `id`           INTEGER PRIMARY KEY AUTOINCREMENT,
    `name`         TEXT DEFAULT "",
    `latitude`     REAL DEFAULT 0.0,
    `longitude`    REAL DEFAULT 0.0,
    `elevation`    REAL DEFAULT 0.0,
    `description`  TEXT DEFAULT NULL
);

CREATE TABLE if NOT exists  `TRACK_IN_PLACES` (
    `id_track`    INTEGER,
    `id_place`    INTEGER,
    FOREIGN KEY(`id_track`) REFERENCES TRACKS(`id`),
    FOREIGN KEY(`id_track`) REFERENCES PLACES(`id`)
);

CREATE TABLE if NOT exists  `SIMILAR_TRACKS` (
    `id`          INTEGER PRIMARY KEY AUTOINCREMENT,
    `hash_track`  INTEGER,
    `id_track`    INTEGER,
    FOREIGN KEY(`id_track`) REFERENCES TRACKS(`id`) 
);