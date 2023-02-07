
from main import run
import datetime


def test_main():
    '''Test main locally'''


    # construct input variables
    site = "cupcaketree.com"
    BQ_DATASET_NAME = 'data_winners_dataset'
    BQ_TABLE_NAME = 'gsc_daily_table'


    # if testing locally
    from unittest.mock import Mock
    data = {
        'site': site, 
        'BQ_DATASET_NAME':BQ_DATASET_NAME, 
        'BQ_TABLE_NAME':BQ_TABLE_NAME,
        'start_date': '2023-01-27',
        'n_days_back':2
    }
    request = Mock(get_json=Mock(return_value=data), args=data)
    run(request)

    True