from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from bin.find_line import search_in_file
from bin.get_college import get_college_list
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

class make_search(Resource):
    def get(self):
        date_temp = request.args.get("date_field").replace("-","/")
        date_temp = date_temp.split("/")
        date_reformated = date_temp[2]+"/"+date_temp[1]+"/"+date_temp[0]
        try:
            result = search_in_file(code_college=request.args.get("college_field"),
                                    time_start=request.args.get("time_start_field"),
                                    time_stop=request.args.get("time_stop_field"),
                                    search=request.args.get("search_field"),
                                    date_spe=date_reformated,
                                    api= True)
            return {'data': result}
        except:
            return {'data':["error server side"]}


class get_college(Resource):
    def get(self):
        return {'data': get_college_list()}

api.add_resource(make_search, '/make_search') # Route_1
api.add_resource(get_college, '/get_college') # Route_2

if __name__ == '__main__':
     app.run(port='5002')
