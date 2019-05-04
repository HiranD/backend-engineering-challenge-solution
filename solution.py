import sys
import json
import argparse
import traceback
import pandas as pd
from datetime import datetime, timedelta


def main(args):
    # Read json bojects to a list
    data = []
    try:
        with open(args.path_to_json) as f:
            for line in f:
                data.append(json.loads(line))
    except ValueError as e:
        print("Please check the given file content comply with needed JSON format -> " + str(e))
        sys.exit(1)
    except:
        print("Error: Check following stack trace for more info.")
        print(traceback.format_exc())
        sys.exit(1)

    checkDataAmount(data)

    # In case sorting the rocords by time
    sortedData = sorted(data,
                        key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S.%f'), reverse=False)
    # Creating a dataframe from selected json objets
    df = pd.DataFrame(sortedData,
                      columns=['timestamp', 'duration', 'nr_words', 'source_language', 'target_language', 'client_name'])

    # Conveting to datetime and making index out of timestamp
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df = df.set_index('timestamp')

    start_time = df.index.min().floor('min')
    end_time = df.index.max().ceil('min')

    # Translation filter
    if args.translate is not None:
        try:
            [source_language, target_language] = args.translate.split(':')
        except:
            print("Please check --translation parameter has defined correctly.")
        else:
            if target_language not in df.target_language.unique():
                print('Given target_language does not exist!')
                sys.exit(1)
            elif source_language not in df.source_language.unique():
                print('Given source_language does not exist!')
                sys.exit(1)
            else:
                print("Filter results by translation -> source_language:{}, target_language:{}"
                      .format(source_language, target_language))
                df = df[df.target_language == target_language]
                df = df[df.source_language == source_language]
                checkDataAmount(df.index)

    # Resampling data for 1 minute and averaging
    df = df[['duration']].resample('min', label='right', closed='left').mean()

    # Adding missing first time slot
    idx = pd.date_range(start_time, end_time, freq='1min').rename('timestamp')
    df = df.reindex(idx)

    # Calculating moving average
    df['MA'] = df[['duration']].rolling(args.window_size, min_periods=1).mean().round(2)
    df = df[['MA']]

    # Filling NAN and reseting index
    df = df.fillna(0)
    df = df.reset_index()
    # Renaming and converting to string
    df.rename(columns={'timestamp': 'time', 'MA': 'average_delivery_time'}, inplace=True)
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Finally writing to the output file in required format
    result_dict = df.to_dict(orient='records')
    try:
        with open(args.path_to_output, "w") as write_file:
            for object_ in result_dict:
                write_file.write(json.dumps(object_) + '\n')
    except Exception as e:
        print("There is an error when saving the results -> " + str(e))
    else:
        print("Results successfully saved at " + args.path_to_output)


def checkDataAmount(data):
    # Checking for the amount of data after filtering.
    if len(data) <= 1:
        print("No enough data to process.")
        sys.exit(1)


# Parsing arguments from command prompt
parser = argparse.ArgumentParser()
parser.add_argument('--input_file',
                    dest='path_to_json',
                    required=True,
                    type=str,
                    help='Relative path to log file.')

parser.add_argument('--window_size',
                    dest='window_size',
                    required=True,
                    type=int,
                    help='Size of time gap in minutes.')

parser.add_argument('--output_loc',
                    dest='path_to_output',
                    default='output_result.json',
                    type=str,
                    help='Relative path to save results.')

parser.add_argument('--translation',
                    dest='translate',
                    type=str,
                    help='Filter results by translation type (source_language:target_language)')

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
