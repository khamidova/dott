from flask import Blueprint, jsonify, abort, make_response
from models import (
    DeploymentCycleSchema,
    Ride,
    RideSchema,
    get_rides_by_deployment_cycle_query_set,
    get_n_latest_deployment_cycles_by_qr_code
)


views = Blueprint("views", __name__)


@views.route("/vehicles/<qr_code>/", methods=["GET"])
def get_vehicle_stats_by_deployment_cycles(qr_code):
    target_num_items = 5

    deployment_cycles = get_n_latest_deployment_cycles_by_qr_code(qr_code, target_num_items)

    if not deployment_cycles:
        abort(404)

    latest_deployment = deployment_cycles.pop(0)
    rides = (
        get_rides_by_deployment_cycle_query_set(latest_deployment)
        .order_by(Ride.gross_amount.desc())
        .limit(5)
        .all()
    )
    rides.sort(key=lambda r: r.time_ride_start)

    result = {}
    num_rides = len(rides)
    num_deployment_cycles = len(deployment_cycles)

    if num_rides:
        result["rides"] = RideSchema(many=True).dump(rides)

    if num_rides < target_num_items:
        # add up to <target_num_items> deployments
        num_deployment_cycles_to_add = min(target_num_items - num_rides, num_deployment_cycles)
        result["deployments"] = DeploymentCycleSchema(many=True).dump(
            deployment_cycles[0:num_deployment_cycles_to_add]
        )

    return make_response(jsonify(result))
