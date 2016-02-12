#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
