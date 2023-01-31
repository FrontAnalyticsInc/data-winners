
from main import run
import datetime


def test_main():
    '''Test main locally'''


    # construct input variables
    site = "bikelanes.com"
    page_url = "https://bikelanes.com/"
    today = datetime.datetime.today()
    start_date = today - datetime.timedelta(days=4)
    end_date = today - datetime.timedelta(days=3)
    BQ_DATASET_NAME = 'data_winners_dataset'
    BQ_TABLE_NAME = 'gsc_daily_table'


    # if testing locally
    from unittest.mock import Mock
    data = {
        'site': site, 
        'start_date':str(start_date.date()), 
        'end_date':str(end_date.date()), 
        'BQ_DATASET_NAME':BQ_DATASET_NAME, 
        'BQ_TABLE_NAME':BQ_TABLE_NAME
    }
    request = Mock(get_json=Mock(return_value=data), args=data)
    run(request)