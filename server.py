import cherrypy
import ConfigParser
import json
import mimetypes
import os
import gspread
import sys
from jinja2 import Environment, FileSystemLoader
class Server():

    worksheet = None
    @cherrypy.expose
    def index(self):

        return "Seems Like You're Lost :D"

    @cherrypy.expose
    def eventsList(self,choice):
        """ 
            Returns Type : JSON
                status_code : 0 -> Success, -1 -> Failed
                message     : Status Message
                events      : List of Events

            Request Type : Get Request
                /eventsList/Technical  ->   Technical Event List
                /eventsList/Cultural   ->   Cultural Event List
                /eventsList/Sports     ->   Sports Event List
                /eventsList/Management ->   Management Event List
        """
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

    def googleFormsOperation(self, phone_num, event):

        phone_num_list = self.worksheet.findall(str(phone_num))
        for tuple_phone_num in phone_num_list:
            tuple_event = self.worksheet.row_values(tuple_phone_num.row)[5]
            if( tuple_event == event):
                self.worksheet.update_cell(tuple_phone_num.row, 7, 'Paid')

    def initGoogleForms(self):

        gc = gspread.login('hasanandroidapp@gmail.com', '31dec14!')
        sh = gc.open("Testing python (Responses)")
        self.worksheet = sh.get_worksheet(0)

    @cherrypy.expose
    def pay(self):

        received_data = cherrypy.request.body.read()
        try:
            decoded_data = json.loads(received_data)
            phone_num = decoded_data['phone_num']
            event = decoded_data['event']
        except KeyError:
            data_sent = {"status": 2, "message": "Invalid Data Sent to the Server", 'content': ""}
            return json.dumps(data_sent)
        try:
            self.googleFormsOperation(phone_num, event)
            print("No Error")
            return json.dumps({"status_code":0,"status":"Updated Successfully"})
        except:
            self.initGoogleForms()
            self.googleFormsOperation(phone_num, event)
            return json.dumps({"status_code":0,"status":"Updated Successfully"})

    @cherrypy.expose
    def eventsStatus(self,choice):
        """ 
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
        """

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
    """ Setting up the Server with Specified Configuration"""

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
