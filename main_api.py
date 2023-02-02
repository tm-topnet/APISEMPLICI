# import classici
from rds.rdscli import rdscli
#from src.mqtt.mqtt_client import MQTTClient
from configparser import ConfigParser
from datetime import datetime
import json
# import numpy as np
import operator
# import per liot
from flask import Flask, request, jsonify
#from src.buffer.buffer import Buffer
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields
import uuid



rdscli.connect('facedetected')

# Initializing Flask App Service
app = Flask("application")

#for swagger
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Jetson API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] ="/swagger" 
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/" 
api = Api(app)

blp_auth = Blueprint("GET_AUTHORIZATION",__name__, description="Data una faccia ritorna l'autorizzazione con jsold")



class GetAuthSchema(Schema):
    jetsonId=fields.Str(required=True)
    camera=fields.Str(required=True)
    face=fields.Str(required=True)
    uniqueId=fields.Str(required=True)
    timestamp=fields.Str(required=True)

@blp_auth.route('/API_GET_AUTHORIZATION') #mettiamo periocular service ma in realtà calcola solo la firma
class ProvaRispostaApi(MethodView):

    @blp_auth.arguments(GetAuthSchema)
    @blp_auth.response(200,OutGetAuthSchema)
    def post(self, input):
        """
        """
        
        return {"jetsonId":"a","camera":"b","face":"c","uniqueId":"d","timestamp":"e"}



if __name__=='__main__':

    app.run()