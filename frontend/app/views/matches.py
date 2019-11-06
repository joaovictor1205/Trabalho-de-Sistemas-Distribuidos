from flask import render_template, request, redirect, jsonify
from app import app
from app.proto import API_pb2
from grpc import RpcError


@app.route('/offer_job', methods=['POST'])
def offer_job():
    from app import stub

    data = request.json
    pb_match = API_pb2.Match()
    pb_match.recruiter.username = data['recruiter']
    pb_match.recruiter.token = data['token']
    pb_match.employee.username = data['employee']

    try:
        match = stub.OfferJob(pb_match)
    except RpcError as e:
        print(e)
        return {'error': True}

    return jsonify({
        'recruiter': match.recruiter.username,
        'employee': match.employee.username,
    })
