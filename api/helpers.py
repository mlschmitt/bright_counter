from flask import jsonify

# Should move this into MethodView base class if expanding to more endpoints
def error_response(error_message, status_code=400):
    robj = {
        "status": "error",
        "error_message": error_message,
        "error_code": status_code
    }
    return jsonify(robj), status_code
