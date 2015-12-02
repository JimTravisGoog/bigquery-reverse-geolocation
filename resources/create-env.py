#!/usr/bin/env python
# commands to craete pub/sub topic and subscriptiona nd BigQuery schema
# TODO: add code to craete BQ schema or call out to comamnd to do this- dunno yet

import httplib2
import sys
import yaml
from apiclient import discovery
from oauth2client import client as oauth2client

with open("setup.yaml", 'r') as  varfile:
    cfg = yaml.load(varfile)

# default; set to your traffic topic. Can override on command line.
TRAFFIC_TOPIC = cfg["env"]["PUBSUB_TOPIC"]
# default; set to your traffic topic. Can override on command line.
TRAFFIC_SUBS =  cfg["env"]["SUBSCRIPTION"]
PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']

def create_pubsub_client(http=None):
    credentials = oauth2client.GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(PUBSUB_SCOPES)
    if not http:
        http = httplib2.Http()
    credentials.authorize(http)
    return discovery.build('pubsub', 'v1', http=http)


def main(argv):

   client = create_pubsub_client()

   topic = client.projects().topics().create(
    name=TRAFFIC_TOPIC, body={}).execute()

   print 'Created: %s' % topic.get('name')  

    # Create a POST body for the Pub/Sub request
   body = {
     # The name of the topic from which this subscription receives messages
    'topic': TRAFFIC_TOPIC,
    
   }

   subscription = client.projects().subscriptions().create(name=TRAFFIC_SUBS, body=body).execute()

   print 'Created: %s' % subscription.get('name')  

if __name__ == '__main__':
        main(sys.argv)
