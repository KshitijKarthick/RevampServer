import os
import sys
import json
import gspread
import cherrypy
import ConfigParser
from jinja2 import Environment, FileSystemLoader
from oauth2client.client import SignedJwtAssertionCredentials
class Server():

    @cherrypy.expose
    def index(self):
        """
            Render HTML page in the present directory
        """

        template = env.get_template('index.html')
        return template.render()

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

    @cherrypy.expose
    def eventsOf(self, phone_num):
        """
            Returns Type : JSON
                status_code : 0 -> Success, -1 -> Failed
                message     : Status Message
                event       : Event List

            Request Type : GET Request
                URL
                    /eventsOf/<phone_num>  -> Specifed phone_num, all events returned

                Data Received -> Phone Num
        """

        try:
            events_list = self.googleFormsFindEvent(phone_num)
            return json.dumps({"status_code":0,"message":"Retrieved Successfully","events":events_list})
        except:
            self.initGoogleForms()
            events_list = self.googleFormsFindEvent(phone_num)
            return json.dumps({"status_code":0,"message":"Retrieved Successfully","events":events_list})

    @cherrypy.expose
    def payForEvent(self):
        """
            Returns Type : JSON
                status_code : 0 -> Success, -1 -> Failed
                message     : Status Message

            Request Type : POST Request
                URL
                    /payForEvent/  -> Specifed phone_num, event present in a tuples
                        status is set to Paid

                Data Received -> JSON
                    Keys:
                        phone_num   ->  Phone num of user
                        event       ->  Event name of user  
        """

        received_data = cherrypy.request.body.read()
        try:
            decoded_data = json.loads(received_data)
            phone_num = decoded_data['phone_num']
            event = decoded_data['event']
        except KeyError:
            data_sent = {"status": 2, "message": "Invalid Data Sent to the Server", 'content': ""}
            return json.dumps(data_sent)
        try:
            self.googleFormsPayEvent(phone_num, event)
            return json.dumps({"status_code":0,"message":"Updated Successfully"})
        except:
            self.initGoogleForms()
            self.googleFormsPayEvent(phone_num, event)
            return json.dumps({"status_code":0,"message":"Updated Successfully"})

    def googleFormsPayEvent(self, phone_num, event):
        """
            Search for the Phone num, obtain the specified event and set status
            to Paid.

        """

        phone_num_list = self.worksheet.findall(str(phone_num))
        for tuple_phone_num in phone_num_list:
            tuple_event = self.worksheet.row_values(tuple_phone_num.row)[5]
            if( tuple_event == event):
                self.worksheet.update_cell(tuple_phone_num.row, 7, 'Paid')

    def initGoogleForms(self):
        """
            Login to the GoogleForms, Authenticate the user details given in the config file,
            Search for the worksheet,
            Obtain the worksheet and set it as a data member.
        """

        try:
            print("Authenticating Login")
            server_config = ConfigParser.RawConfigParser()
            server_config.read('server.conf')
            spreadsheet_title=server_config.get('GoogleForms','spreadsheet_title')
            json_file_name=server_config.get('GoogleForms','oauth_service_json')
            json_file = file(json_file_name, 'r')
            key = json.loads(json_file.read())
            json_file.close()
            scope = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds']
            credentials = SignedJwtAssertionCredentials(key['client_email'],key['private_key'], scope)
            gc = gspread.authorize(credentials)
            print("Authentication Successfull")
            sh = gc.open(spreadsheet_title)
            self.worksheet = sh.get_worksheet(0)
            print("Worksheet Access Obtained")
        except Exception as e:
            print("Invalid Authentication",e)
            raise e

    def googleFormsFindEvent(self, phone_num):
        """
            Find all the tuples with the specified phone_num,
            Return type
                List -> Events for the specified Phone Num
        """

        events_list = []
        phone_num_list = self.worksheet.findall(str(phone_num))
        for phone_num in phone_num_list:
            events_list.append(self.worksheet.row_values(phone_num.row)[5])
        return list(set(events_list))


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
        },
        '/resources': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './resources'
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
