
import json
import requests
from apiclient import errors
from apiclient.discovery import build

import datetime
import dateutil

from google.oauth2 import service_account
import google.oauth2.credentials
import google.auth.transport.requests
from google.cloud import bigquery

import pandas as pd


def build_table_if_doesnt_exist():
    """Create table if doesn't exist"""
    
    True
    
    
    



def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    
    
    # get variables
    # url
    # start date
    # BQ_DATASET_NAME
    # BQ_TABLE_NAME
    site = "frontanalytics.com"
    


    #SERVICE_ACCOUNT_FILE = "../gcp-keys/website-analytics-161019-16456165cddc.json"
    SERVICE_ACCOUNT_FILE = "./service-account-key.json"

    SCOPES = ['https://www.googleapis.com/auth/webmasters']
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build(
        'webmasters',
        'v3',
        credentials=credentials
    )
    
    # innitiates the credentials
    response = service.sites().list().execute()
    
    today = datetime.datetime.today()
    startDate = today - datetime.timedelta(days=4)
    endDate = today - datetime.timedelta(days=3)

    df_all_queries = pd.DataFrame()

    page_url = "https://frontanalytics.com/"

    # recent
    data = {
      "startDate": startDate.strftime("%Y-%m-%d"),
      "endDate": endDate.strftime("%Y-%m-%d"),
      "dimensions": ["query","device","country"],
      "dimensionFilterGroups": [
        {
          "groupType": "and",
          "filters": [
            {
              "dimension": "page",
              "operator": "contains",
              "expression": page_url
            }
          ]
        }
      ]
    }
    res = requests.post("https://www.googleapis.com/webmasters/v3/sites/"+"sc-domain:"+site+"/searchAnalytics/query?access_token="+credentials.token, json=data)

    # convert the response to a data frame
    j = json.loads(res.text).get('rows',[])

    if(len(j)):
        df_queries = pd.DataFrame(j)
        df_queries['url'] = page_url
        df_queries['property'] = site
        df_queries['start_date'] = startDate
        df_queries['update_at'] = today

        # By default the keys/dimensions are in a single column, let's split them out into separate columns.
        new_cols = df_queries['keys'].astype(str).str.replace("[","").str.replace("]","")
        new_cols = new_cols.str.split(pat=',',expand=True,n=2)

        # Give the columsn sensible names
        new_cols.columns = ["query","device","country"]

        # Bring back a key from the intial dataframe so we can join
        new_cols['key'] = df_queries['keys']

        # Get rid of quotation marks
        new_cols['query'] = new_cols['query'].str.replace("'","").str.lower()
        new_cols['device'] = new_cols['device'].str.replace("'","").str.lower()
        new_cols['country'] = new_cols['country'].str.replace("'","").str.lower()

        # Join in the new clean columns to our intiial data
        df_queries = pd.concat([df_queries, new_cols], axis=1, join='inner')

        # Drop the key columns
        df_queries = df_queries.drop(["key","keys"],axis=1)

        # save all the queries for this page with all other pages
        df_all_queries = pd.concat([df_all_queries, df_queries])

    # Bigquery


    # include the name of your project
    BQ_PROJECT_NAME = 'website-analytics-161019'

    # create the tables manually to include all the fields
    BQ_DATASET_NAME = 'test'
    BQ_TABLE_NAME = 'test_sc'


    # establish a BigQuery client
    client = bigquery.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
    dataset_id = BQ_DATASET_NAME
    table_name = BQ_TABLE_NAME

    # create a job config
    # Set the destination table

    table_id = '{}.{}.{}'.format(BQ_PROJECT_NAME, BQ_DATASET_NAME, BQ_TABLE_NAME)



    job_config = bigquery.LoadJobConfig(
        # Specify a (partial) schema. All columns are always written to the
        # table. The schema is used to assist in data type definitions.
        schema=[
            # Specify the type of columns whose type cannot be auto-detected. For
            # example the "title" column uses pandas dtype "object", so its
            # data type is ambiguous.
            #bigquery.SchemaField("title", bigquery.enums.SqlTypeNames.STRING),
            # Indexes are written if included in the schema by name.
            #bigquery.SchemaField("wikidata_id", bigquery.enums.SqlTypeNames.STRING),
        ],
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_APPEND",
    )

    job = client.load_table_from_dataframe(
        df_all_queries, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.





    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'