from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Ride(db.Model):
    __tablename__ = "rides"

    ride_id = db.Column(db.String, primary_key=True)
    vehicle_id = db.Column(db.String)
    time_ride_start = db.Column(db.DateTime(timezone=True))
    time_ride_end = db.Column(db.DateTime(timezone=True))
    start_lat = db.Column(db.Float)
    start_lng = db.Column(db.Float)
    end_lat = db.Column(db.Float)
    end_lng = db.Column(db.Float)
    distance = db.Column(db.Float)
    gross_amount = db.Column(db.Float)


class Deployment(db.Model):
    __tablename__ = "deployments"

    task_id = db.Column(db.String, primary_key=True)
    vehicle_id = db.Column(db.String)
    time_task_created = db.Column(db.DateTime(timezone=True))
    time_task_resolved = db.Column(db.DateTime(timezone=True))


class Pickup(db.Model):
    __tablename__ = "pickups"

    task_id = db.Column(db.String, primary_key=True)
    vehicle_id = db.Column(db.String)
    qr_code = db.Column(db.String)
    time_task_created = db.Column(db.DateTime(timezone=True))
    time_task_resolved = db.Column(db.DateTime(timezone=True))


class DeploymentCycle(db.Model):
    __tablename__ = "deployment_cycles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deployment_task_id = db.Column(db.String, db.ForeignKey("deployments.task_id"))
    pickup_task_id = db.Column(db.String, db.ForeignKey("pickups.task_id"))
    vehicle_id = db.Column(db.String)
    qr_code = db.Column(db.String)
    time_deployment = db.Column(db.DateTime(timezone=True))
    time_pickup = db.Column(db.DateTime(timezone=True))
