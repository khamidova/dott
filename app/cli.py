import structlog
import os
from db import engine, generate_query
import config
from flask.cli import AppGroup


logger = structlog.get_logger(__name__)

import_cli = AppGroup("import", help="Import data from CSV files")
generate_cli = AppGroup("generate", help="Generate data from existing data")


@import_cli.command("rides", help="Import rides from CSV files")
def import_rides():
    import_data("rides", config.RIDES_FOLDER)


@import_cli.command("deployments", help="Import deployments from CSV files")
def import_deployments():
    import_data("deployments", config.DEPLOYMENTS_FOLDER)


@import_cli.command("pickups", help="Import pickups from CSV files")
def import_pickups():
    import_data("pickups", config.PICKUPS_FOLDER)


@generate_cli.command(
    "deployment-cycles", help="Combine deployments and pickups into deployment cycles"
)
def generate_deployment_cycles():
    logger.info("Generate deployment cycles: Starting...")
    generate_deployment_cycles_db()
    logger.info("Generate deployment cycles: Done.")


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = os.listdir(path_to_dir)
    return [
        os.path.join(path_to_dir, filename)
        for filename in filenames
        if filename.endswith(suffix)
    ]


def import_data(table, folder_prefix):
    logger.info(f"Importing {table}: Starting...")

    csv_folder = os.path.join(config.IMPORT_CSV_FILES_LOCATION, folder_prefix)
    csv_files = find_csv_filenames(csv_folder)
    for csv_file in csv_files:
        logger.info(f"Importing {table}: Reading from csv file {csv_file}")
        import_data_from_csv(table, csv_file)

    logger.info(f"Importing {table}: Done.")


def import_data_from_csv(table, csv_file):
    """
    as we expect to have large amounts of data, import is done in 3 steps:
    step 1 - create temporary table (which would be automatically remove on commit)
    step 2 - load data from csv into temp table via COPY statement (this way is much faster than via flask objects)
    step 3 - upsert data into destination table, which allows us to customize import if needed
             e.g. if vehicle will be a separate model with an integer id,
             we can find vehicle internal id as part of upsert statement.
    """

    with open(csv_file, encoding="utf8") as csvfile:
        conn = engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(generate_query("create_temp_table", table))
        copy_sql = generate_query("copy_sql", table)
        cursor.copy_expert(sql=copy_sql, file=csvfile)
        cursor.execute(generate_query("upsert_data", table))
        cursor.close()
        conn.commit()


def generate_deployment_cycles_db():
    # TODO: possibly should be optimized
    # depends on how/when deployments and pickups are created
    # ideas:
    # - generate deployments cycles only for the past n days (filter on dates)
    # - generate only deployments cycles for "open" deployments, which are not part of deployment cycles yet
    # - generate only latest 5 deployments per vehicle (if this table's only purpose is getting 5 latest deployments)

    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        truncate table deployment_cycles
        """
    )
    cursor.execute(
        """
        with deployments_pickups as (
        select
          deployments.task_id as deployment_task_id,
          pickups.task_id as pickup_task_id,
          pickups.vehicle_id as vehicle_id,
          pickups.qr_code as qr_code,
          deployments.time_task_resolved as time_deployment,
          pickups.time_task_created as time_pickup,
          rank() over (partition by deployments.vehicle_id, deployments.task_id order by pickups.time_task_created) as rank
        from
          -- left join to keep 'open' deployments
          deployments left join pickups
          on
            deployments.vehicle_id=pickups.vehicle_id
            and deployments.time_task_resolved<pickups.time_task_created
        )

        insert into deployment_cycles (
          deployment_task_id,
          pickup_task_id,
          vehicle_id,
          qr_code,
          time_deployment,
          time_pickup
        )
        select
          deployment_task_id,
          pickup_task_id,
          vehicle_id,
          qr_code,
          time_deployment,
          time_pickup
        from deployments_pickups where rank=1
        """
    )
    cursor.close()
    conn.commit()
