import flask
from flask import request, jsonify
from py2neo import Graph, NodeMatcher
from py2neo import Node, Relationship
import json
import base64
from dateutil.parser import parse
from datetime import date
from spellchecker import SpellChecker
import subprocess


app = flask.Flask(__name__)
app.config["DEBUG"] = True
graph = Graph('http://localhost:7474', password='1234')
matcher = NodeMatcher(graph)

spell = SpellChecker()
spell.distance = 3
dictionary = []
query = "MATCH (n:Entity) RETURN n"
users = graph.run(query).to_table()
for user in users:
    dictionary.append(user[0]['name'])
spell.word_frequency.load_words(dictionary)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Social Search API</h1>
<p>A prototype API for retrieveing Social Search results.</p>'''


@app.route('/api/socialsearch/tweet/all', methods=['GET'])
def api_tweet_all():

    key  = request.args.get('key', None)
    id = request.args.get('id', None)
    
    #if key == None:
    #    return "Error: No key field provided. Please specify a key."
    #else:
    #    key = str(key)
        
    #if id == None:
    #    return "Error: No id field provided. Please specify an id."
    #else:
    #    id = str(id)
   
       
    
    #result = []
    #for s in ss:
    #    result.append(s['tweet'])
    
    #result = sorted(result, key=lambda k: k['Retweet_count'], reverse=True)
    #result = sorted(result, key=lambda k: k['Created_time'], reverse=True)
    
    #return jsonify(result)
    return jsonify("This endpoint returns nothing")


@app.route('/api/socialsearch/tweet', methods=['GET'])
def api_tweet_id():

    id  = request.args.get('id', None)
    key  = request.args.get('key', None)

    
    if id == None:
        return "Invalid format"
    else:
        id = str(id)
    
    if key == None:
        return "Invalid format"  
    else:
        key = str(key)    

    result = []
    
    key = SpellCheck(key)
    
    try:
        # Retrieving all tweets
        query = "MATCH (n:Entity { name: \"" + key + "\" })-->(s:Summary) MATCH (s:Summary {Topic : " + id + "})-->(tweet:Tweet) RETURN tweet"

        ss = graph.run(query).to_table()
            
        for s in ss:
            result.append(s[0])
        
        result = sorted(result, key=lambda k: k['Retweet_count'], reverse=True)[:100]
        #result = sorted(result, key=lambda k: str(parse(k['Created_time'])).split()[0], reverse=True)
        #result = sorted(result, key=lambda k: (str(parse(k['Created_time'])).split()[0], k['Retweet_count']), reverse=True)

        return jsonify(result)
    
    except Exception:
        return jsonify(result)


@app.route('/api/socialsearch/video/all', methods=['GET'])
def api_video_all():

    key  = request.args.get('key', None)
    
    #if key == None:
    #    return "Error: No key field provided. Please specify a key."
    #else:
    #    key = str(key)

    #ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(video:Video) RETURN video").data()
    
    #result = []
    #for s in ss:
    #    result.append(s['video'])
    
    #result = sorted(result, key=lambda k: k['Published_date'], reverse=True)
    
    
    #return jsonify(result)
    return jsonify("This endpoint returns nothing")

@app.route('/api/socialsearch/video', methods=['GET'])
def api_video_id():

    id  = request.args.get('id', None)
    key  = request.args.get('key', None)

    
    if id == None:
        return "Invalid format"  
    else:
        id = str(id)
    
    if key == None:
        return "Invalid format"  
    else:
        key = str(key)
    
    result = []
    
    key = SpellCheck(key)
    
    try:
        # Retrieving all tweets
        query = "MATCH (n:Entity { name: \"" + key + "\" })-->(s:Summary) MATCH (s:Summary {Topic : " + id + "})-->(video:Video) RETURN video"

        ss = graph.run(query).to_table()
            
        for s in ss:
            result.append(s[0])
            
        #result = sorted(result, key=lambda k: k['Published_date'], reverse=True)

        return jsonify(result[:25])
    
    except Exception:
        return jsonify(result)


@app.route('/api/socialsearch/summary', methods=['GET'])
def api_summary():
    
    key  = request.args.get('key', None)
    id = request.args.get('id', None)
    
    if key == None:
        return "Invalid format"  
    else:
        key = str(key)
        
    if id == None:
        return "Invalid format"
    
    result = []
    
    if not key:
        return jsonify(result)
    
    key = SpellCheck(key)
    
    try:
        # Storing user's search results
        user = graph.evaluate("MATCH (n:User) WHERE ID(n)=" + str(id) + " RETURN n")
        node = Node("User_search", name=key, Date=str(date.today()))
        graph.create(node)
        r = Relationship(user, "SEARCHED_FOR", node)
        graph.create(r)

        # Retrieving all summaries
        ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(summary:Summary) RETURN summary").to_table()
        
        if not ss:
            print('Initiate real-time timeline')
            print(key)
            
            # Extract tweets
            print('Extracting tweets...')
            p1 = subprocess.Popen('python twitter_api_realtime.py ' + key)
            p1.wait()
            
            # Cluster tweets
            print('Clustering topics...')
            p2 = subprocess.Popen('python topic_clustering_realtime.py ' + key)
            p2.wait()

            # Summarize topics
            print('Summarizing clusters...')
            p3 = subprocess.Popen('python text_summarization_realtime.py ' + key)
            p3.wait()

            # Create graph
            print('Creating graph...')
            p4 = subprocess.Popen('python create_graph_realtime.py ' + key)
            p4.wait()

            ss = graph.run("MATCH (n:Entity { name: '" + key + "' })-->(summary:Summary) RETURN summary").to_table()
            
        for s in ss:        
            result.append(s[0])
        
        result = sorted(result, key=lambda k: k['Date'], reverse=True)
        
        return jsonify(result)
        
    except Exception:
        return jsonify(result)
                

@app.route('/api/socialsearch/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'POST':
        
        # In case of form data
        #email = request.form['email']
        #password = request.form['password']
        
        req_data = request.get_json()
        
        if 'email' not in req_data:
            return "Invalid format"
        else:
            email = req_data['email']
            
        if 'password' not in req_data:
            return "Invalid format"
        else:
            password = req_data['password']
        
        pass1 = password
        # Encrypt password to match from database
        password = base64.b64encode(password.encode("utf-8"))
        
        
        try:
            # Check for user
            user = graph.run("MATCH (n:User {Email:\"" + email + "\", Password:\"" + str(password) + "\"}) RETURN n, ID(n)").data()
            
            if not user:        
                return "Invalid credentials"                
            else:
                dict = {"name" : user[0]["n"]["name"], "email" : user[0]["n"]["Email"], "password" : pass1, "id" : user[0]["ID(n)"]}                
                return jsonify(dict)
            
        except Exception:
            return "Error"
                


@app.route('/api/socialsearch/register', methods=['GET', 'POST'])
def api_register():
    if request.method == 'POST':
        
        # In case of form data
        #email = request.form['email']
        #password = request.form['password']
        
        req_data = request.get_json()
        
        
        if 'email' not in req_data:
            return "Invalid format"
        else:
            email = req_data['email']
            
        if 'password' not in req_data:
            return "Invalid format"
        else:
            password = req_data['password']
            
        if 'name' not in req_data:
            return "invalid format"
        else:
            name = req_data['name']
     
        try:
            # Check for existing node
            user = graph.run("MATCH (n:User {Email:\"" + email + "\"}) RETURN n").data()
            
            if not user:
            
                # Encrypt the password
                password = base64.b64encode(password.encode("utf-8"))
                
                # Create a node
                res = graph.run("CREATE (n:User{name:\"" + name + "\", Password:\"" + str(password) + "\", Email:\"" + email + "\"})")
                
                return "Successfully registered"
                
            else:
            
                return "Email already exists in record"
                
        except Exception:
        
            return "Error"
        


@app.route('/api/socialsearch/history', methods=['GET'])
def api_history():

    id = request.args.get('id', None)
        
    if id == None:
        return "Invalid format"  
        
    query = "MATCH p=(u:User)-[r:SEARCHED_FOR]->(s:User_search) WHERE ID(u)=" + str(id) + " RETURN s"
    
    ss = graph.run(query).to_table()
    
    result = []
    for s in ss:        
        result.append(s[0])
    
    
    return jsonify(result)


@app.route('/api/socialsearch/edit', methods=['GET', 'POST'])
def api_edit():
    if request.method == 'POST':
        
        req_data = request.get_json()        
        
        if 'id' not in req_data:
            return "Invalid format"
        else:
            id = req_data['id']
        
        try:
            user = graph.evaluate("MATCH(n:User) WHERE ID(n)=" + str(id) + " RETURN n")        
        
            if not user:
                return "No such user exists"
            else:
                p = base64.b64encode(req_data['password'].encode("utf-8"))
                query = "MATCH(n:User) WHERE ID(n)=" + str(id) + " SET n.Password = \"" + str(p) + "\", n.name = \"" + req_data['name'] + "\" RETURN n"
                #graph.evaluate(query)
                    
                return "Successfully edited"
                
        except Exception:
            return "Error"
        
        

def SpellCheck(query):
    flag = False
    res = ""
    # Check if query exists in dictionary
    for key in dictionary:
        if query == key:
            res = key
            #print("Found: ", key)
            flag = True
            break
            
    # Word is misspelled, correct it
    if not flag:
        candidate = spell.correction(query)
         
        # Keyword was out of place
        if candidate == query:
            res = query
        # Keyword was corrected
        else:
            res = candidate
            #print(query, "->", candidate)
    return res
    
app.run(host="0.0.0.0", port=8000)
