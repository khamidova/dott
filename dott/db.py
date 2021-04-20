from sqlalchemy import create_engine

from .config import SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI)


def generate_query(query_type, table):
    if query_type == "copy_sql":
        query = f"""
            COPY {table}_temp FROM stdin
            WITH (
                FORMAT CSV,
                HEADER,
                DELIMITER ','
            )        
        """
    elif query_type == "create_temp_table":
        if table == "rides":
            query = """
                CREATE TEMPORARY TABLE rides_temp (
                    ride_id varchar not null,
                    vehicle_id varchar,
                    time_ride_start timestamp with time zone,
                    time_ride_end timestamp with time zone,
                    start_lat double precision,
                    start_lng double precision,
                    end_lat double precision,
                    end_lng double precision,
                    gross_amount double precision
                ) ON COMMIT DROP;
            """
        elif table == "deployments":
            query = """
                CREATE TEMPORARY TABLE deployments_temp (
                    task_id varchar not null,
                    vehicle_id varchar,
                    time_task_created timestamp with time zone,
                    time_task_resolved timestamp with time zone
                ) ON COMMIT DROP;
            """
        elif table == "pickups":
            query = """
                CREATE TEMPORARY TABLE pickups_temp (
                    task_id varchar not null,
                    vehicle_id varchar,
                    qr_code varchar,
                    time_task_created timestamp with time zone,
                    time_task_resolved timestamp with time zone
                ) ON COMMIT DROP;
            """
    elif query_type == "upsert_data":
        if table == "rides":
            query = """
                insert into rides (
                    ride_id,
                    vehicle_id,
                    time_ride_start,
                    time_ride_end,
                    start_lat,
                    start_lng,
                    end_lat,
                    end_lng,
                    distance,
                    gross_amount
                )
                select
                    ride_id,
                    vehicle_id,
                    time_ride_start,
                    time_ride_end,
                    start_lat,
                    start_lng,
                    end_lat,
                    end_lng,
                    -- calculates distance in miles and converts to km
                    (point(start_lng,start_lat) <@> point(end_lng,end_lat)) * 1.609 as distance,
                    gross_amount
                from rides_temp
                on conflict do nothing
            """
        elif table == "deployments":
            query = """
                insert into deployments (
                    task_id,
                    vehicle_id,
                    time_task_created,
                    time_task_resolved
                )
                select
                    task_id,
                    vehicle_id,
                    time_task_created,
                    time_task_resolved
                from deployments_temp
                on conflict do nothing
            """
        elif table == "pickups":
            query = """
                insert into pickups (
                    task_id,
                    vehicle_id,
                    qr_code,
                    time_task_created,
                    time_task_resolved
                )
                select
                    task_id,
                    vehicle_id,
                    qr_code,
                    time_task_created,
                    time_task_resolved
                from pickups_temp
                on conflict do nothing
            """
    if not query:
        raise NotImplementedError

    return query
