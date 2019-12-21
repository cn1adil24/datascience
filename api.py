import flask
from flask import request, jsonify
from py2neo import Graph, NodeMatcher
from py2neo import Node, Relationship
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
graph = Graph('http://localhost:7474', password='1234')
matcher = NodeMatcher(graph)


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Social Search API</h1>
<p>A prototype API for retrieveing Social Search results.</p>'''


@app.route('/api/socialsearch/tweet/all', methods=['GET'])
def api_tweet_all():

    key  = request.args.get('key', None)
    
    if key == None:
        return "Error: No key field provided. Please specify a key."
    else:
        key = str(key)

    ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(tweet:Tweet) RETURN tweet").data()
    
    result = []
    for s in ss:
        result.append(s['tweet'])
    
    result = sorted(result, key=lambda k: k['Retweet_count'], reverse=True)
    
    return jsonify(result)


@app.route('/api/socialsearch/tweet', methods=['GET'])
def api_tweet_id():

    id  = request.args.get('id', None)
    key  = request.args.get('key', None)

    
    if id == None:
        return "Error: No id field provided. Please specify an id."
    else:
        id = int(id)
    
    if key == None:
        return "Error: No key field provided. Please specify a key."
    else:
        key = str(key)

    # Create an empty list for our results
    result = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(tweet:Tweet {Topic: " + str(id) + "}) RETURN tweet").data()
    
    result = []
    for s in ss:
        result.append(s['tweet'])
    
    result = sorted(result, key=lambda k: k['Retweet_count'], reverse=True)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(result)


@app.route('/api/socialsearch/video/all', methods=['GET'])
def api_video_all():

    key  = request.args.get('key', None)
    
    if key == None:
        return "Error: No key field provided. Please specify a key."
    else:
        key = str(key)

    ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(video:Video) RETURN video").data()
    
    result = []
    for s in ss:
        result.append(s['video'])
    
    return jsonify(result)

@app.route('/api/socialsearch/video', methods=['GET'])
def api_video_id():

    id  = request.args.get('id', None)
    key  = request.args.get('key', None)

    
    if id == None:
        return "Error: No id field provided. Please specify an id."
    else:
        id = int(id)
    
    if key == None:
        return "Error: No key field provided. Please specify a key."
    else:
        key = str(key)

    # Create an empty list for our results
    result = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(video:Video {Topic: " + str(id) + "}) RETURN video").data()
    
    result = []
    for s in ss:
        result.append(s['video'])
    

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(result)


@app.route('/api/socialsearch/summary', methods=['GET'])
def api_summary():
    
    key  = request.args.get('key', None)
    
    if key == None:
        return "Error: No key field provided. Please specify a key."
    else:
        key = str(key)
    
    ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(summary:Summary) RETURN summary").data()
    
    result = []
    for s in ss:
        result.append(s['summary'])
    
    return jsonify(result)
        

app.run()