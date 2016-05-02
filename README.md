<!--
Conversion notes (using libgdc version 59):
-->

<!-- generated styles -->
<style type=text/css>
  .tab0 {background-color:#3366cc;color:#333333;}
  .tab1 {background-color:#e5ecf9;}
  .tab2 {background-color:#aa0033;color:#333333;}
  .tab3 {background-color:#ffcccc;}
  .tab4 {background-color:#aa0033;}
  .tab5 {background-color:#999999;}
  .tab6 {background-color:#efefef;}
</style>



# Adding geographic context to your streaming data with Google’s Pubsub and Maps APIs

This example code  will allow you  to use Google Cloud Platform to build an app that receives telemetric data about geolocation, processes it, and then stores the processed and transformed data for further analysis. 

Runs on [Google Compute Engine](https://cloud.google.com/compute/docs).
Processes messages in a Google Cloud Pub/Sub queue.
Reverse geocodes latitude & longitude to convert the coordinates to a street address.
Calculates the elevation above sea level.
Converts from  Coordinated Universal Time (UTC) to local time by querying which timezone each location is in. 
Writes the data with the added geographic context to a BigQuery dataset for your analysis.

This tutorial which can be found <<here>>  discusses how this example is constructed .  The solution paper <<link here>>  discusses the concepts behind the example. 

It includes and uses data from [San Diego, CA, freeways public dataset](http://catalog.data.gov/dataset/intelligent-transportation-systems-research-data-exchange-san-diego-freeway-data-daily) . This data was captured from actual automobile journeys, recorded by using road sensors. You can [register for an account](https://www.its-rde.net/showdf?https://www.its-rde.net/showds?dataEnvironmentNumber=10012) to have access to the full dataset if you want to run your own experiments with further data.


![architecture diagrams](images/geo_bq-arch.png " Architecture diagram")

## <strong>Very Important Things</strong>

If you follow these instructions exactly, you will deploy 1  g1-small GCE
instance configure a pub/sub topic and subscription  and create a BIgQuery
table . The resources  are billed. It is very important that you follow the
instructions to turn off the resources  if you do not want to continue to be
billed for these resources.  <LInk to a calculator quote > provides an estimate
of the monthly cost of the resources provisioned in this example.

Be sure to create a brand new project for this tutorial (instructions are in
the deploy sections below). Also be sure to complete the <Delete the
Deployment> section when you're done. It's super quick and will tear down
everything you created.

## <strong>Costs</strong>
This example uses billable components of Google Cloud Platform, including:  

* 1 Compute Engine virtual machines (g1-small) ( note this is an optinal component as you 
* Google Cloud Storage Standard (5 GB)
* Google BigQuery (5 GB storage, 5 GB streaming inserts)
* Google Cloud Pub/Sub (< 200k operations)
* Google Maps API  

The cost of running this tutorial will vary depending on run time. Use the [pricing calculator estimate](https://cloud.google.com/products/calculator/#id=11387bdd-be66-4083-b814-01176faa20a0) to see a cost estimate based on your projected usage. New Cloud Platform users may be eligible for a free trial.

The Maps API standard plan offers a free quota and pay-as-you-go billing after the quota has been exceeded. You can purchase a Maps API Premium Plan for higher quotas.  If you have an existing license for the Maps API or have a Maps APIs Premium Plan, [see the documentation first](https://developers.google.com/maps/documentation/javascript/get-api-key#premium-auth) for some important notes.

You must have a Maps for Work license for any application that restricts access, such as behind a firewall or on a corporate intranet. For more details about Google Maps API pricing and plans, see the [online documentation](https://developers.google.com/maps/pricing-and-plans/).



## <strong>Conventions</strong>

The instructions in this tutorial assume you have access to a terminal on a
Linux or OS X host. For Windows hosts, [Cygwin](http://cygwin.com/) should work.

You will need to enter commands in your terminal. Those commands are indicated
in the following format, where <code>$</code> indicates a prompt (do not paste the $ into your terminal, just everything
that follows it):


<pre class=prettyprint>
$echo “this is a Sample command” 
</pre>

## <strong>Before you begin</strong>

### <strong>Cloud platform project set up</strong>

Before you deploy the sample you'll need to make sure a few things are in
order:

[Select or create a Cloud Platform Console project.](https://console.cloud.google.com/project)  

[Enable billing for your project.](https://console.cloud.google.com/billing)  

[Install the Cloud SDK](https://cloud-dot-devsite.googleplex.com/sdk/).  

Authenticate gcloud with Google Cloud Platform:


``$ gcloud init``

Click the following link to enable the required Cloud Platform APIs. If prompted, be sure to select the project you created in step 1.

[Enable APIs](https://console.developers.google.com/start/api?target=%22console%22&id=bigquery,pubsub,storage_component,storage_api,geocoding_backend,elevation_backend,timezone_backend,maps_backend)

These APIs include:

* BigQuery API
* Pubsub API
* Google Cloud Storage
* Google Maps Geocoding API
* Google Maps Elevation API
* Google Maps Time Zone API
* Google Maps Javascript API



### <strong>Creating Credentials</strong>

For this tutorial, you'll need the following credentials:

* A Google Maps API server key.
* A Maps API browser key.
* A credentials file for service account key.
* An OAuth 2.0 client ID.

##### Google Maps API credentials
If you don't already have them, you'll need Google Maps API keys. 


###### Get a server key

Click the following link to open the Cloud Console in the Credentials page. If you have more than one project, you might be prompted to select a project. 

[ Create credentials](https://console.developers.google.com/project/_/apis/credentials?target=%22console%22)

 2. Click **Create credentials** and then select **API key**. 
 3. Click **Server key**. 
 4. Name the key "Maps tutorial server key". 
 5. Click **Create**. 
 6. Click **Ok** to dismiss the dialog box that shows you the new key. You can retrieve your keys from the Cloud Console anytime. 
 7. Stay on the page.

###### Get a browser key
The browser key is a requirement for using the Maps Javascript API. Follow these steps:

1. Click Create credentials and then select API key.
1. Click Browser key.
1. Name the key "Maps tutorial browser key".
1. Click Create.
1. Click Ok to dismiss the dialog box that shows you the new key.
1. Stay on the page.


<table>
 <tr>
    <td class="tab0"></td>
    <td class="tab1"><strong>IMPORTANT: </strong>Keep your API keys secure. Publicly exposing your credentials can result in your account being compromised, which could lead to unexpected charges on your account. To keep your API keys secure, follow these [best practices](https://support.google.com/cloud/answer/6310037).</td>
 </tr>
</table>

##### Service account credentials


Create service account credentials and download the JSON file. Follow these steps:

1. Click **Create credentials** and then select **Service account key**.
1. Select **New service account**.
1. Name the account "Maps tutorial service account".
1. The key type is **JSON**.
1. Click **Create**.
1. The Cloud Console automatically downloads to your computer the JSON file that contains the service account key.
1. Click **Close** to dismiss the dialog box that shows you the new key. If you need to, you can retrieve the key file later.

<table>
 <tr>
    <td class="tab5"></td>
    <td class="tab6"><strong>NOTE: </strong>You will need this file if you decide to use Docker to run the example. For more details read the README included in the Docker folder of this repository if you wish to use Docker </td>
 </tr>
</table>

<table>
 <tr>
    <td class="tab0"></td>
    <td class="tab1"><strong>IMPORTANT: </strong>It is important that you keep this file  safe and do NOT share it publically.</td>
 </tr>
</table>

##### OAuth 2.0 client ID
Create a client ID that you can use to authenticate end-user requests to BigQuery. Follow these steps:

Open the Cloud Console to the [Credentials page](https://console.developers.google.com/project/_/apis/credentials?target=%22console%22).


1. Click Create credentials and then select **OAuth client ID**.
1. Select **Web application**.
1. In the **Name** field, enter "Maps API client ID".
1. In the Restrictions section, in** Authorized JavaScript origins**, add the following two origin URLs:

http://localhost:8000
https://localhost:8000

Adding these URLs enables an end user to access BigQuery data through JavaScript running in a browser. You need this authorization for an upcoming section of the tutorial, when you display a visualization of data on a map in your web browser.
	
<table>
 <tr>
    <td class="tab2"></td>
    <td class="tab3"><strong>WARNING: </strong>This setting allows anyone running a local web server to access your BigQuery data. It's important that you delete the localhost:8000 restrictions when you finish the tutorial. Deleting these restrictions makes your data more secure and might save you from being billed for additional costs.
</td>
 </tr>
</table>

 5.Click Save to generate the new client ID.



## <strong>Setting up Cloud Pub/Sub</strong>

Cloud Pub/Sub is the messaging queue that handles moving the data from CSV files to BigQuery. You'll need to create a topic, which publishes the messages, and a subscription, which receives the published messages. 

#### Create a Cloud Pub/Sub topic

The topic publishes the messages. Follow these steps to create the topic:

Browse to the Pub/Sub topic list page in the Cloud Console:

[Open the Pub/Sub page](https://console.developers.google.com/project/_/cloudpubsub/topicList)

1. Click **Create topic**. A dialog box opens.
1. In the **Name** field, add "traffic" to the end of the path that is provided for you. The path is determined by the system. You can provide only a name for the topic.


![pub/sub topic](images/geo_bq-topic-2.png "pub/sub topic")

3.Click Create. The dialog box closes.  

Keep the Cloud Console open on this page; you'll use it in the next section.

#### Creating a Cloud Pub/Sub subscription

The subscription receives the published messages. Follow these steps to create the subscription:

1. In the topic list, in the row that contains the traffic topic, click the down arrow on the right-hand end of the row.
1. Click **New subscription** to open the **Create a new subscription** page.  
1. In the **Subscription name** field, add "mysubscription" to the end of the path that is provided for you.


 ![pub/sub sub](images/geo_bq-subs-3.png "pub/sub sub")

4.This is a pull subscription. Set the **Delivery Type** to **Pull**, if it isn't already set by default. 

5.Click **Create**.

## <strong>Next Steps</strong>

If you want to use Docker then please refer to the README included in the Docker folder of this repository to follow through from this point onwards for instructions on setting up and running the example using Docker. If you wish to run the example on a Compute Engine instance or via CloudShell continue onto the Deployment instructions (Step by step) below 




## Deployment instructions (step by step)

This step by step deployment instructions are the best starting point if you
wish to  take the source code and modify for your specific  use case

<table>
 <tr>
    <td class="tab5"></td>
    <td class="tab6"><strong>NOTE: </strong>It is assumed that you are able to open & edit  text files , run some simple
bash scripts and have some familiarity with Python if using these step by step
instructions. Python version needs to be 2.7 </td>
 </tr>
</table>

1.First clone this repository to a local folder on your laptop or on a GCE
instance  

2.A small sample set of data files that contain real GPS vehicle journey data from San Diego freeway can be found in the resources/data folder of this repository


[See this file for copyright info:](http://storage.googleapis.com/sandiego_freeway_gps_trips/o/docs%2Flicense%20and%20copyright(san%20diego).txt)
 

4.You can get a bigger sample set for a  more realistic demo from [here](http://catalog.data.gov/dataset/intelligent-transportation-systems-research-data-exchange-san-diego-freeway-data-daily) .If you decide to do this then ensure you copy the csv files into the folder
defined by the ROOTDIR in the setup.yaml file  

5.Create your pub/sub topic by navigating to the pub/sub console from the [Google Developer Console](https://console.developers.google.com/project)  

i. Click on New Topic add the name of your topic  so the topic entry looks like
this :

 ![pub/sub topic](images/geo_bq-topic-2.png "pub/sub topic")

ii. Now create the subscription by checking the box alongside the topic  and clicking the “+ new subscription button” Ensure it is set to pull

 ![pub/sub sub](images/geo_bq-subs-3.png "pub/sub sub")

iii. Note the name of the topic and subscription 
6. change location  to the folder where you cloned the repository 
7.Now run the python script to populate the pub/sub topic using the following
command:


<pre class=prettyprint>
$ ~/push_pubsub_docker/python  config_geo_pubsub_push.py
</pre>

<table>
 <tr>
    <td class="tab2"></td>
    <td class="tab3"><strong>WARNING: </strong>Make sure you  have  the appropriate details set in the setup.yaml file and
that the script is pointing to the correct location for the  setup.yaml file</td>
 </tr>
</table>

8.Create an empty Big Query dataset using the following command:  


<pre class=prettyprint>
$bq mk sandiego_freeways 
</pre>

 

on successful creation you will see a message similar to the following:

<em>Dataset 'Your-Project_ID:sandiego_freeways' successfully created.</em>

9.Next create a table  with the following schema 

 ![BQ schema](images/geo_bq-schema-6.png "BQ schema")


10.You can do this by passing the json schema file you downloaded when cloning the
git repository  to the bq mk command as below ( or manually via the console):


<pre class=prettyprint>
$ bq mk --schema geocoded_journeys.json sandiego_freeways.geocode_journeys
</pre>

 

11.Update the setup.yaml file with the following details

<table>
 <tr>
    <td>variable to update</td>
    <td></td>
 </tr>
 <tr>
    <td>PROJECT_ID:</td>
    <td>Change to your project ID</td>
 </tr>
 <tr>
    <td>DATASET_ID:</td>
    <td>Change to  BigQuery  datasetid (sandiego_freeways)</td>
 </tr>
 <tr>
    <td>TABLE_ID:</td>
    <td>Change to  BigQuery tableid (geocoded_journeys)</td>
 </tr>
 <tr>
    <td>PUBSUB_TOPIC:</td>
    <td>Change to pub/sub topic</td>
 </tr>
 <tr>
    <td>ROOTDIR: </td>
    <td>Change to folder where csv test data kept</td>
 </tr>
 <tr>
    <td>SUBSCRIPTION: </td>
    <td>Change the following to your pub/sub pull subscription </td>
 </tr>
 <tr>
    <td>MAPS_API_KEY:</td>
    <td>Change to your Google Maps API Key, see
https://developers.google.com/maps/web-services</td>
 </tr>
</table>

12.Now run the python script to process the messages  in pub/sub topic using the
following to run the python script : 


<pre class=prettyprint>
$python config_geo_pubsub_pull.py 
</pre>


<table>
 <tr>
    <td class="tab5"></td>
    <td class="tab6"><strong>NOTE: </strong>if setup.yaml is not in the same folder as your script then either move
it there or edit the script to reflect it’s location </td>
 </tr>
</table>

The script moves messages from the pub/sub queue, reverse geocodes them
(converts latitude & longitude to a street address), calculates the elevation
above sea level, and converts from UTC time to local time by querying which
timezone the locations fall in. It then writes the data plus this added
geographic context to the BigQuery table you created earlier

Now you can start analysing the data to get some interesting insights into the
data.

## Analysing the data

  1.From the Cloud console navigate to the BigQuery link on the left hand side
  2.Open the <strong>[BigQuery web UI](https://bigquery.cloud.google.com/)</strong>.
  3.View the table schema . Under your project name, expand the sandigeo_freeways
dataset and then click <strong>geocode_journeys</strong>

The following figure shows the table schema for the  table. 

 ![BQ schema](images/geo_bq-schema-6.png "BQ schema")


4.In the BigQuery web UI, click <strong>Compose Query</strong>. 

5.Try entering  some of the following queries  in the new query text box :

Average speed by Zipcode


<pre class=prettyprint>
SELECT AVG(Speed) avg_speed, Zipcode FROM [sandiego_freeways.geocoded_journeys]
WHERE Zipcode &lt;> ''
GROUP BY Zipcode ORDER BY avg_speed DESC
</pre>

Average speed by street name


<pre class=prettyprint>
SELECT AVG(Speed) as avg_speed FROM [sandiego_freeways.geocoded_journeys] WHERE
Address CONTAINS('Vandegrift Blvd')
</pre>

Street and Zipcode where worst speeding occurs


<pre class=prettyprint>
SELECT Speed, VehicleID, Address, Zipcode FROM
[sandiego_freeways.geocoded_journeys]
WHERE Speed > 65
ORDER BY Speed DESC
</pre>

## Visualisation

As part of this repo we have provided some sample code to allow you to
visualise data stored in BigQuery on a Google Map.


<strong>NOTE:</strong/> For simplicity, this example shows how to visualise the data using OAuth 2.0 to authenticate the user against the BigQuery service. However, applications that require sign in or are not freely accessible to everyone are not permitted by the Google Maps API [terms of use](https://developers.google.com/maps/terms?hl=en) without obtaining a Maps for Work license. It’s important to emphasise that this is not the only way to share your BigQuery data on a Google Map, and there are options that do not require a Maps for Work license. You could export the query results from BigQuery and create a static map layer that doesn’t require the user to authenticate, or you could set up authentication via a service account so the end user doesn’t have to be signed in with their credentials to access the map. For more details on Maps API pricing and plans see the [online documentation](https://developers.google.com/maps/pricing-and-plans/).


1.Download the file bqapi.html  which can be found in the web folder of this repo

<table>
 <tr>
    <td class="tab5"></td>
    <td class="tab6"><strong>NOTE: </strong>if you followed the step by step deployment and cloned the repo then you will
have a local copy on the machine you are using to follow this through </td>
 </tr>
</table>

2.Make  amendments to some variables  namely clientID, ProjectID . If you changed
the name  of your dataset and table name  then replace those values as well.
You also need to add in your maps api browser key where indicated
 

<pre class=prettyprint>
&lt;script
src="https://maps.googleapis.com/maps/api/js?libraries=visualization,drawing&key=Your-Maps-Api_browser-key"
        >&lt;/script>
&lt;script type="text/javascript">
//auth
var clientId = 'Your-Client_ID follow instructions from here :
https://cloud.google.com/bigquery/authentication#clientsecrets';
var scopes = 'https://www.googleapis.com/auth/bigquery';
var projectId = 'Your-Project-ID';
var datasetId = 'sandiego_freeways';
var table_name = 'geocoded_journeys';
</pre>

3. Once you have replaced the variables  start python’s simple HTTP
server from the folder where the bqapi.html  file is 


<pre class=prettyprint>
$ python -m SimpleHTTPServer
</pre>

   

<table>
 <tr>
    <td class="tab5"></td>
    <td class="tab6"><strong>NOTE: </strong>Running this from your local workstation is the easiest approach  Python 2.7 is
a pre requsiste</td>
 </tr>
</table>

 This starts a local server on port 8000

Then  from your browser browse to the file [http://localhost:8000/bqapi.html](http://localhost:8000/bqapi.html)

Draw a rectangle over an area to see a heat map to to indicate journey density.

![Heat map](images/visual-map.png "Heat map")

When finished ctrl-c to stop the local browser

If you are using this repo as the basis for building out your own application
reading the section below on getting your web page set  provides detailed
guidance. go to the section on cleaning up when you’ve completed the tutorial

## Getting your web page set up

To use the Javascript Maps API, you’ll need to create a new Browser Key in the
Google Developer Console.

If you have never used BigQuery via its API before, you’ll need to follow the [API quickstart](https://cloud.google.com/bigquery/bigquery-api-quickstart). You can use any client you like to send queries, the API supports HTTP and
JSON. You might want to consider one of the [Google Client APIs](https://cloud.google.com/bigquery/client-libraries) to avoid writing lots of “plumbing” code to build the requests, parse
responses, and handle authentication. This article will assume you’re using the [Google Client API for Javascript](https://github.com/google/google-api-javascript-client).

### Add the Maps API drawing library to your web page.

To add drawing capabilities to your map, you’ll need to load the Google Maps
API with the optional drawing library enabled. See the [developer guide for the drawing library](https://developers.google.com/maps/documentation/javascript/drawinglayer) for more details. Firstly, make sure you’re referencing the drawing library
when you load the Javascript API. We’re going to be using the HeatmapLayer as
well, so you’ll also need the visualization library. Your script tag should
look like this:


```
&lt;script src="<a href="http://maps.googleapis.com/maps/api/js?libraries=visualization,drawing&key=YOUR_API_KEY">http://maps.googleapis.com/maps/api/js?libraries=visualization,drawing&key=YOUR_API_KEY</a>">&lt;/script>
```
### Load the Google Client API for Javascript

Make sure your page loads the Google Client API for Javascript. You can use any
other client library if you prefer. See the [Getting Started guide for the Javascript Client AP](https://developers.google.com/api-client-library/javascript/start/start-js)I to understand the basic concepts. You can reference the API with a script tag
like this:


```
&lt;script src="<a href="https://apis.google.com/js/client.js">https://apis.google.com/js/client.js</a>">&lt;/script>
```
### Authorizing the user

Your web page will need to authorize the user to access BigQuery. In this
example we’ll use OAuth 2.0 as per the [authorization section of the JavaScript Client API documentation](https://developers.google.com/api-client-library/javascript/features/authentication). You’ll need to use your Developer Project client ID and project ID to send
queries.

Having loaded the Google Client API you can then perform the following steps:

  * Authorize the user.
  * If authorized, load the BigQuery API.
  * Load the map at an initial location.

Here are some Javascript functions that would achieve these steps. You could
call authorise() from a UI element like a button, or when the page has loaded:


```
var clientId = 'your-client-id-here';
var scopes = 'https://www.googleapis.com/auth/bigquery';

//check if the user is authorised.
function authorise(event) {
  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false},
handleAuthResult);
  return false;
}

//if authorized, load BigQuery API
function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
    loadApi();
  } else {
    console.log("Not authorised.")
  }
}

//load BigQuery client API
function loadApi(){
  gapi.client.load('bigquery', 'v2').then(
    function() {
      createMap();
    }
  );
}
```
### Simple SQL query to get data for a rectangular area

The simplest way to display BigQuery data on a map is to request all rows where  
the latitude and longitude fall within a rectangle, using a less than and
greater than comparison. This could be the current map view or a shape drawn on
the map. To use a shape drawn by the user, you will need to handle the drawing
event fired when a rectangle is completed. In this example the code uses <code>getBounds()</code> to get an object representing the extent of the rectangle in map coordinates,
and passes it to a function called <code>rectangleQuery</code>:


```
google.maps.event.addListener(drawingManager, 'rectanglecomplete', function
(rectangle) {
  rectangleQuery(rectangle.getBounds());
});

```
The <code>rectangleQuery</code> function just needs to use the top right and lower left coordinates to
construct a less than/greater than comparison against each row in your BigQuery
table. Here’s an example that queries a table that has columns called
“latitude” and “longitude” which store the location values. Replace “project”,
“dataset” and “table” with the details from your BigQuery project:


```
function rectangleQuery(latLngBounds){
  var queryString = rectangleSQL(latLngBounds.getNorthEast(),
latLngBounds.getSouthWest());
  sendQuery(queryString);
}

function rectangleSQL(ne, sw){
  var queryString = "SELECT latitude, longitude "
  queryString +=  "FROM [project:dataset.table]"
  queryString += " WHERE latitude > " + sw.lat();
  queryString += " AND latitude &lt; " + ne.lat();
  queryString += " AND longitude > " + sw.lng();
  queryString += " AND longitude &lt; " + ne.lng();
  return queryString;
}
```
Here’s a Javascript function to send a query using the API. Replace “datasetId”
and “projectId” with values from your BigQuery project:


```
function sendQuery(queryString){
  var request = gapi.client.bigquery.jobs.query({
      "query": queryString,
      "timeoutMs": 30000,
      "datasetId": datasetId,
      "projectId": projectId
  });
  request.execute(function(response) {
      checkJobStatus(response.jobReference.jobId);
  });
}
```
The <code>checkJobStatus</code> function below shows how to check the status of a job periodically, using the <code>[get](https://cloud.google.com/bigquery/docs/reference/v2/jobs/get)</code> API method and the <code>jobId</code> returned by the original query request. Here’s an example that runs every 500
ms until the job is complete.


```
function checkJobStatus(jobId){
  var request = gapi.client.bigquery.jobs.get({
    "projectId": projectId,
    "jobId": jobId
  });
  request.execute(function(response){
    if(response.status.errorResult){
      //handle any errors
      console.log(response.status.error);
    } else {
      if(response.status.state == 'DONE'){
        //get the results
        clearTimeout(jobCheckTimer);
        getQueryResults(jobId);
      } else {
        //not finished, check again in a moment
        jobCheckTimer = setTimeout(checkJobStatus, 500, [jobId]);
      }
    }
  });
}
```
To get the results of a query when it has finished running, use the <code>[jobs.getQueryResults](https://cloud.google.com/bigquery/docs/reference/v2/jobs/getQueryResults)</code> API call. Here’s a Javascript example:


```
function getQueryResults(jobId){
  var request = gapi.client.bigquery.jobs.getQueryResults({
    "projectId": projectId,
    "jobId": jobId
  });
  request.execute(function(response){
    //do something with the results
  })
}
```
### Handling large datasets in the browser

BigQuery tables can be huge - Petabytes of data, and can grow by hundreds of
thousands of rows per second. So it’s important to try and limit the amount of
data returned so that it can be drawn on the map. Drawing the location of every
row in a very large result set  (tens of thousands of rows or greater) will
result in an unreadable map. There are many techniques for aggregating the
locations both in the SQL query and on the map, and you can limit the results a
query will return. 

To visualize the density of locations you could use a heatmap. The Maps API has
a [HeatmapLayer](https://developers.google.com/maps/documentation/javascript/heatmaplayer) class for this purpose. The <code>HeatmapLayer</code> takes an array of latitude, longitude coordinates so it is quite easy to
convert the rows returned from the query into a heatmap.

In the getQueryResults function, you can pass the <code>response.result.rows</code> array to a Javascript function that will create a heatmap. Here’s an example:


```
function doHeatMap(rows){
  var heatmapData = [];
  if(heatmap!=null){
    heatmap.setMap(null);
  }
  for (var i = 0; i &lt; rows.length; i++) {
      var f = rows[i].f;
      var coords = { lat: parseFloat(f[0].v), lng: parseFloat(f[1].v) };
      var latLng = new google.maps.LatLng(coords);
      heatmapData.push(latLng);
  }
  heatmap = new google.maps.visualization.HeatmapLayer({
      data: heatmapData
  });
  heatmap.setMap(map);
}

```
### Things to consider

If you’re working with very large tables, your query may return too many rows
to efficiently display on a map. Limit the results by adding a <code>WHERE</code> clause or a <code>LIMIT</code> statement.

Drawing lots of markers can make the map unreadable. Consider using a
HeatmapLayer to show the density, or cluster markers to indicate where many
data points lie using a single symbol per cluster. There are more details in
the Maps API [Too Many Markers developer guide](https://developers.google.com/maps/articles/toomanymarkers?hl=en).

BigQuery will scan the entire table with every query. To optimise your BigQuery
quota usage, only select the columns you need in your query. 

Queries will be faster if you store latitude and longitude as floats rather
than strings.

Going further

There are other ways to use SQL to run spatial queries against data in
BigQuery: radius SQL queries and [User Defined Functions](https://cloud.google.com/bigquery/user-defined-functions) which can be used to construct more advanced geometry operations. There are
examples of bounding box and radius queries in the [BigQuery reference](https://cloud.google.com/bigquery/query-reference) in the “Advanced Examples” section.

## Cleaning up 

It is very important (as mentioned in the Very Important Things section of this
document) that you delete your deployment when you are done. You will be
charged for any running resources.

Whether you followed the Quick Deploy or Stepwise Deploy instructions, deleting
resources is very easy. Simply delete the project you created at the beginning
of this tutorial:

  1. Navigate to the [Projects page of the Google Developer Console](https://console.developers.google.com/project), find your project, click the trash can icon to delete, then type the project
ID and click Delete Project.

Refs:

[https://developers.google.com/maps/web-services/](https://developers.google.com/maps/web-services/)

[https://github.com/googlemaps/google-maps-services-python/](https://github.com/googlemaps/google-maps-services-python/)

### Terms of Use

The Google Maps Web Service APIs may only be used in conjunction with a Google
map; geocoding results without displaying them on a map is prohibited. For
complete details on allowed usage, consult the [Maps API Terms of Service License Restrictions](https://developers.google.com/maps/terms#section_10).

I