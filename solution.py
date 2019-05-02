import argparse
from datetime import datetime, timedelta
import json
import pandas as pd

def main(args):   
    # Calculating start and end time for the processing
    if args.now_ == "now":
        now_ = datetime.now().replace(microsecond=0,second=0)-timedelta(minutes=1)
        # now_ = datetime(2019, 1, 2)
    else:
        try:
            now_ = datetime.strptime(args.now_, "%Y-%m-%d_%H:%M")
        except ValueError:
            print("Given date-time is not comply with needed format -> yyyy-mm-dd_HH:MM")

    from_ = now_ - timedelta(minutes=args.window_size)
    print("Started calculation from " + str(from_) + " to " + str(now_))
    # Read json bojects to a list
    json_list = []
    with open(args.path_to_json) as f:
        for line in f:
            json_list.append(json.loads(line))
    # Selects record within our time-gap
    data = []
    for record in json_list:
        t = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        if (from_ <= t and now_ > t):
            data.append(record)
    # In case sorting the rocords by time
    sortedData = sorted(data,key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S.%f'), reverse=False)
    # Creating a dataframe from selected json objets
    df = pd.DataFrame(sortedData, columns=['timestamp','duration','nr_words','source_language','target_language','client_name'])
    # Conveting to datetime and making index out of timestamp
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df = df.set_index('timestamp')
    # Calculating moving average
    df['MA'] = df[['duration']].rolling('1min').mean().round(2)
    # Removing other columns, reseting index and rounding time to ceiling minute 
    df = df[['MA']]
    df = df.reset_index()
    df['timestamp'] = df['timestamp'].dt.ceil('min')
    # First minute result shoud be removed, because it was partially calcualted
    df = df.iloc[1:]
    # Remove duplicate rows using timestamp and keep last 
    df = df.drop_duplicates(subset='timestamp', keep='last').reset_index(drop=True)
    # Renaming and converting to string
    df.rename(columns={'timestamp': 'time', 'MA': 'average_delivery_time'}, inplace=True)
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    # Finally writing to the output file in required format
    result_dict = df.to_dict(orient='records')
    try:
        with open(args.path_to_output, "w") as write_file:
            for object_ in result_dict:
                write_file.write(json.dumps(object_) + '\n')
    except:
        print("There is an error when saving the results!!")
    else:
        print("Results successfully saved at " + args.path_to_output)


# Parsing arguments from command prompt   
parser = argparse.ArgumentParser()
parser.add_argument('--input_file',
                    dest='path_to_json',
                    required=True,
                    type = str,
                    help='Relative path to log file')

parser.add_argument('--window_size',
                    dest='window_size',
                    default=False,
                    required=True,
                    type = int,
                    help='Size of time gap in minutes')

parser.add_argument('--output_loc',
                    dest='path_to_output',
                    default='output_result.json',
                    type = str,
                    help='Relative path to save results')

parser.add_argument('--to',
                    dest='now_',
                    default='now',
                    type = str,
                    help='Relative time (yyyy-mm-dd_HH:MM) to start calculation')

if __name__== "__main__":
    args = parser.parse_args()
    main(args)