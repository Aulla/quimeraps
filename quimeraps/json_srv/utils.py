from flask import jsonify, request
import json


def format_response(response):
    result = jsonify(response)
    result.headers.add("Access-Control-Allow-Origin", "*")
    result.headers.add("Access-Control-Allow-Headers", "*")
    result.headers.add("Access-Control-Allow-Methods", "*")
    return result


def load_data():
    received_data = request.get_data()
    return json.loads(received_data.decode(encoding="UTF-8"))
