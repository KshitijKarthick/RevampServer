import cherrypy
import ConfigParser
import json
import mimetypes
import os
from jinja2 import Environment, FileSystemLoader
class Server():

    @cherrypy.expose
    def index(self):

        return "Seems Like You're Lost :D"

    @cherrypy.expose
    def eventsList(self,choice):
        ''' 
            Returns Type : JSON
                status_code : 0 -> Success, -1 -> Failed
                message     : Status Message
                events      : List of Events

            Request Type : Get Request
                /eventsList/Technical  ->   Technical Event List
                /eventsList/Cultural   ->   Cultural Event List
                /eventsList/Sports     ->   Sports Event List
                /eventsList/Management ->   Management Event List
        '''
        message="Success, Event List Obtained"
        status_code=0;
        events=[]
        try:
            if choice.title() == "Technical":
                events = technical_event_list['events']
            elif choice.title() == "Cultural":
                events = cultural_event_list['events']
            elif choice.title() == "Sports":
                events = sports_event_list['events']
            elif choice.title() == "Management":
                events = management_event_list['events']
            else:
                status_code=-1
                message="Failed, No Such Event Type Enlisted"
        except:
                status_code=-1
                message="Failed, Server Error! Error Occured while retreiving Event List"
        return json.dumps({'status_code':status_code,'message':message,'events':events})

    @cherrypy.expose
    def eventsStatus(self,choice):
        ''' 
            Returns Type : JSON
                status_code : 0 -> Success, -1 -> Failed
                message     : Status Message
                hash        : Hash of the List of Events

            Request Type : Get Request
                /eventsStatus/Technical  ->   Technical Status Details
                /eventsStatus/Cultural   ->   Cultural Status Details
                /eventsStatus/Sports     ->   Sports Status Details
                /eventsStatus/Management ->   Management Status Details
                /eventsStatus/All        ->   All Events Status Details
        '''

        message="Success, Event List Obtained"
        status_code=0;
        events=[]
        try:
            if choice.title() == "Technical":
                events = technical_event_list['events']
            elif choice.title() == "Cultural":
                events = cultural_event_list['events']
            elif choice.title() == "Management":
                events = management_event_list['events']
            elif choice.title() == "Sports":
                events = sports_event_list['events']
            elif choice.title() == "All":
                events = technical_event_list['events'] + cultural_event_list['events'] + sports_event_list['events'] + management_event_list['events']
            else:
                status_code=-1
                message="Failed, No Such Event Type Enlisted"
        except:
                status_code=-1
                message="Failed, Server Error! Error Occured while retreiving Event List"
        return json.dumps({'status_code':status_code,'message':message,'hash':json.dumps(events).__hash__()})

if __name__ == '__main__':
    ''' Setting up the Server with Specified Configuration'''

    server_config = ConfigParser.RawConfigParser()
    env = Environment(loader=FileSystemLoader(''))
    conf = {
        '/':{
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/events': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './events'
        }
    }
    technical_event_list=json.loads(open("events/technical.json","r").read())
    cultural_event_list=json.loads(open("events/cultural.json","r").read())
    management_event_list=json.loads(open("events/management.json","r").read())
    sports_event_list=json.loads(open("events/sports.json","r").read())
    server_config.read('server.conf')
    server_port=server_config.get('server','port')
    server_host=server_config.get('server','host')
    cherrypy.config.update({'server.socket_host': server_host})
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', server_port))})
    cherrypy.quickstart(Server(),'/',conf)
