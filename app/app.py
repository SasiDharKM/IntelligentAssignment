#!flask/bin/python
from flask import Flask
import flask
from flask import Flask, jsonify, abort, request, make_response, url_for
import json_unpacker
import matching_model
from user import User
from team import Team
import user
import json
import clustering as clst

def extract_users(req):
	exper_data,users = ([],[])
	for user in req['users']:
		exper_data.append([float(data) for data in user['ranks']])
		if "history" in user:
			users.append(User(exper_data[-1],user['pid'],user['history']))
		else:
			users.append(User(exper_data[-1],user['pid']))
	return exper_data,users

def send_teams_as_json(teams): #this method currently uses the classes defined for bidding
	json_obj = [[user.pid for user in team.members] for team in teams]
	return flask.Response(json.dumps({"teams":json_obj,"users":flask.request.json['users']}),  mimetype='application/json')

def extract_task_data(req):
	#extract json data and convert to python object here
	#do not necessarily have to use user class here, it is already defined if you would like to use it
	return req

def send_assigned_tasks_as_json(tasks):
	#convert python objects to simple maps and lists
	return flask.Response(json.dumps({"info":tasks}))

app = Flask(__name__)

@app.route('/merge_teams',methods=['POST'])
def clstbuild():
    if not 'users' in flask.request.json or not 'max_team_size' in flask.request.json or sum([not 'ranks' in user or not 'pid' in user for user in flask.request.json['users']]) > 0:
    	flask.abort(400)
    data,users = extract_users(flask.request.json)
    teams,users = clst.kmeans_assignment(data,users, flask.request.json['max_team_size'])
    return send_teams_as_json(teams)

@app.route("/match", methods=['POST']) #using the post method with /match in the url to get the required app route
def matching():
    if not request.json: #will abort the request if it fails to load the json
        abort(400)  #will have a return status of 400 in case of failure
    bidding_data = json_unpacker.JsonUnpacker(request.json) #calles the json_unpacker to get the necessary bidding_data
    model = matching_model.MatchingModel(bidding_data.student_ids,
                                bidding_data.topic_ids,
                                bidding_data.student_preferences_map,
                                bidding_data.topic_preferences_map, bidding_data.q_S) #model to get the student_ids,topic_ids,student_preference_map,topic_prefernce_map
    return jsonify(model.get_matching()) #returns a json object

if __name__ == "__main__":
	app.run(debug=True)
