from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

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


def get_rides_by_deployment_cycle_query_set(deployment_cycle):
    # instead of this QuerySet we can make deployment cycle id part of rides table
    # deployment cycle id can be filled during data import

    if deployment_cycle.time_pickup:
        query_set = (
            Ride.query.filter_by(vehicle_id=deployment_cycle.vehicle_id)
            .filter(
                Ride.time_ride_start.between(
                    deployment_cycle.time_deployment, deployment_cycle.time_pickup
                )
            )
            .filter(
                Ride.time_ride_end.between(
                    deployment_cycle.time_deployment, deployment_cycle.time_pickup
                )
            )
        )
    else:
        query_set = Ride.query.filter_by(vehicle_id=deployment_cycle.vehicle_id).filter(
            Ride.time_ride_start >= deployment_cycle.time_deployment
        )
    return query_set


class RideSchema(ModelSchema):
    revenue = fields.String(attribute="gross_amount")
    ride_distance = fields.String(attribute="distance")
    start_point = fields.Method('get_start_point')
    end_point = fields.Method('get_end_point')

    def get_point(self, lat, lng):
        return {
            "latitude": lat,
            "longitude": lng
        }

    def get_start_point(self, obj):
        return self.get_point(obj.start_lat, obj.start_lng)

    def get_end_point(self, obj):
        return self.get_point(obj.end_lat, obj.end_lng)

    class Meta(ModelSchema.Meta):
        model = Ride
        sqla_session = db.session
        fields = (
            "revenue",
            "ride_distance",
            "time_ride_start",
            "time_ride_end",
            "start_point",
            "end_point",
        )


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


class DeploymentCycleSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = DeploymentCycle
        sqla_session = db.session
        fields = ("deployment_task_id", "vehicle_id", "time_deployment")


def get_n_latest_deployment_cycles_by_qr_code(qr_code, n):
    return (
        DeploymentCycle.query.filter_by(qr_code=qr_code)
            .order_by(DeploymentCycle.time_deployment.desc())
            .limit(n)
            .all()
    )
