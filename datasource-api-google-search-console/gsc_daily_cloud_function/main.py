
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
import numpy as np

import dateutil
import pandas_gbq


import functions_framework

@functions_framework.http
def run(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    
    ##### get variables
    site = request_json.get('site')
    BQ_DATASET_NAME = request_json.get('BQ_DATASET_NAME')
    BQ_TABLE_NAME = request_json.get('BQ_TABLE_NAME')

    # optional start date defaults to 4 days ago
    n_days_ago = request_json.get('n_days_ago', 4)

    # optional
    page_url = request_json.get('page_url', None)
    # end Date is start_date+1

    # optional n_days_back
    n_days_back = request_json.get('n_days_back', 1)

    # optional start_date
    if request_json.get('start_date'):
        # given a start date so use that
        start_date = datetime.datetime.strptime( request_json.get('start_date'), '%Y-%m-%d')
    else:
        # defaults to today minus n_days_ago
        start_date = (datetime.datetime.today() - datetime.timedelta(days=n_days_ago))
    
    # optional end_date
    if request_json.get('end_date'):
        # given a start date so use that
        end_date = datetime.datetime.strptime( request_json.get('end_date'), '%Y-%m-%d')
    else:
        end_date = (start_date - datetime.timedelta(days=n_days_back))



    ##### uses the locally uploaded service account key
    SERVICE_ACCOUNT_FILE = "./service-account-key.json"
    SCOPES = [
      'https://www.googleapis.com/auth/webmasters.readonly',
      'https://www.googleapis.com/auth/webmasters',
      'https://www.googleapis.com/auth/bigquery'
    ]
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    

    #### Google Search Console
    # initiates the credentials
    service = build(
        'webmasters',
        'v3',
        credentials=credentials
    )
    response = service.sites().list().execute()


    ##### Bigquery
    # establish a BigQuery client
    client_bq = bigquery.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
    BQ_PROJECT_NAME = client_bq.project



    # determine what days to run
    # only the days that don't have any clicks yet

    def query_table_clicks(start_date, end_date, PROJECT_ID, DATASET, TABLE, property):
        QUERY = "SELECT start_date, sum(clicks) as total_clicks FROM {dataset}.{table} WHERE start_date >= '{end_date}' and start_date <= '{start_date}' and property = '{property}' group by start_date"
        
        query = QUERY.format(dataset=DATASET, table=TABLE, start_date=start_date, end_date=end_date, property=property)
        result = pd.read_gbq(query, PROJECT_ID, dialect='standard')

        result['already_loaded'] = True
        return result

    bq_results = query_table_clicks(start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"), BQ_PROJECT_NAME, BQ_DATASET_NAME, BQ_TABLE_NAME, property=site)



    output = {
        "n_days_with_zero_clicks_at_start": len(bq_results[bq_results['total_clicks']==0])
    }

    # one big table with all input dates and zero dates

    days_to_check = bq_results
    input_days_to_check = pd.DataFrame()
    dates_input_to_check = []
    for days_back in range(0, n_days_back):
        dates_input_to_check.append( (start_date - datetime.timedelta(days=days_back)).date() )
    input_days_to_check['start_date'] = dates_input_to_check
    input_days_to_check['from_inputs'] = True
    days_to_check = days_to_check.merge(input_days_to_check,how='outer')

    days_to_check["total_clicks"] = days_to_check["total_clicks"].replace(np.nan, 0)
    days_to_check = days_to_check[days_to_check['total_clicks']==0]
    # loop over the days that are missing clicks
    for index, row in days_to_check.iterrows():
        

        start_date_to_process = row['start_date']
        end_date_to_process = start_date_to_process




        # initialize for raw rows
        all_rows_as_json = []
        # initialize the dataset for formatted rows
        df_all_queries = pd.DataFrame()

        # recent daily pull query for all urls
        data = {
            "startDate": start_date_to_process.strftime("%Y-%m-%d"),
            "endDate": end_date_to_process.strftime("%Y-%m-%d"),
            "dimensions": ["date","page", "query","device","country"],
            "rowLimit": 25000,
            "type": 'web', # Possible values: 'web' (default), 'image', 'video', 'discover','googleNews'.,
            'dataState': "final"
        }

        #data_state (str): The data_state you would like to use for your report. 
        #        Possible values: 'final' (default - only finalized data), 
        #        'all' (finalized & fresh data).

        # if a page_url is given
        if page_url:
            data["dimensionFilterGroups"] = [
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

        # Assign Start Row
        start_row = 0
        # Loop over requests until all rows are pulled into DataFrame
        while True:
            data['startRow'] = start_row

            # use the service to pull API details
            res = service.searchanalytics().query(siteUrl = "sc-domain:"+site, body=data).execute()
            j = res.get('rows',[])

            # convert the response to a data frame
            if j:
                all_rows_as_json.extend(j)
            else:
                break
            if len(j) < 25000:
                break

            start_row += 25000


        if(len(all_rows_as_json)):
        
            # delete the data currently loaded just in case
            def delete_data(start_date, end_date, PROJECT_ID, DATASET, TABLE, property):
                QUERY = "delete FROM {dataset}.{table} WHERE start_date >= '{start_date}' and start_date <= '{end_date}' and property = '{property}'"
                
                query = QUERY.format(dataset=DATASET, table=TABLE, start_date=start_date, end_date=end_date, property=property)
                query_job = client_bq.query(query)  # API request
                rows = query_job.result()

                return rows



            # get all the records already loaded within the last n days
            delete_data(start_date_to_process.strftime("%Y-%m-%d"),end_date_to_process.strftime("%Y-%m-%d"), BQ_PROJECT_NAME, BQ_DATASET_NAME, BQ_TABLE_NAME, property=site)



        
            # convert the raw rows to a pandas df
            df_queries = pd.DataFrame(all_rows_as_json)
            df_queries['property'] = site
            df_queries['updated_at'] = datetime.datetime.now()

            # By default the keys/dimensions are in a single column, let's split them out into separate columns.
            new_cols = pd.DataFrame()
            # Bring back a key from the intial dataframe so we can join
            new_cols['key'] = df_queries['keys']
            new_cols[['start_date', "url", "query", "device", "country"]] = pd.DataFrame(df_queries['keys'].tolist(), index= df_queries.index)
            
            # convert string to date
            new_cols["start_date"] =  pd.to_datetime(new_cols["start_date"], format="%Y-%m-%d").dt.date

            # Join in the new clean columns to our intiial data
            df_queries = pd.concat([df_queries, new_cols], axis=1, join='inner')

            # Drop the key columns
            df_queries = df_queries.drop(["key","keys","ctr"],axis=1)

            # save all the queries for this page with all other pages
            df_all_queries = pd.concat([df_all_queries, df_queries])




            # verify there are no duplicate entries in bigquery
            # Query bigquery to determine what has already been loaded?
            # Update the in-memory credentials cache (added in pandas-gbq 0.7.0).
            pandas_gbq.context.credentials = credentials
            pandas_gbq.context.project = BQ_PROJECT_NAME
            

            def query_table(start_date, end_date, PROJECT_ID, DATASET, TABLE, property):
                QUERY = "SELECT * FROM {dataset}.{table} WHERE start_date >= '{start_date}' and start_date <= '{end_date}' and property = '{property}'"
                
                query = QUERY.format(dataset=DATASET, table=TABLE, start_date=start_date, end_date=end_date, property=property)
                result = pd.read_gbq(query, PROJECT_ID, dialect='standard')

                result['already_loaded'] = True
                return result


            # get all the records already loaded within the last n days
            already_loaded = query_table(start_date_to_process.strftime("%Y-%m-%d"),end_date_to_process.strftime("%Y-%m-%d"), BQ_PROJECT_NAME, BQ_DATASET_NAME, BQ_TABLE_NAME, property=site)

            # find the rows that aren't loaded yet
            join_cols = ['start_date','property','url','device','country']
            not_loaded = df_all_queries.merge(already_loaded[join_cols+['already_loaded']], how="left", on=join_cols)
            not_loaded = not_loaded[not_loaded['already_loaded'].isna()]
            cols = list(df_all_queries.columns)
            not_loaded = not_loaded[cols]

            # record n_records_loaded
            n_records_loaded = len(not_loaded)
            output["n_records_loaded"] = output.get("n_records_loaded",0) + n_records_loaded
            output["n_days_back_loaded"] = output.get("n_days_back_loaded",0) + 1
            if output.get('start_date') is None:
                output["start_date"] = str(start_date_to_process)

            # continue loading if not loaded yet
            if n_records_loaded:

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

                job = client_bq.load_table_from_dataframe(
                    not_loaded, table_id, job_config=job_config
                )  # Make an API request.
                job.result()  # Wait for the job to complete.

        # end nth day

    # finish
    return output