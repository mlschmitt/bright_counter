from flask import Blueprint, jsonify, request


api_blueprint = Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route("/ping", methods=["GET"])
def routes_ping_check():
    # Simple alive check for debugging or uptime monitor
    # Could be adjusted to validate connection to datastore
    return jsonify({"status": "ok"}) 
