import sys
import json
import argparse
import traceback
import pandas as pd
from datetime import datetime, timedelta


def main(args):
    # Calculating start and end time for the processing
    if args.now_ == "now":
        now_ = datetime.now().replace(microsecond=0, second=0)-timedelta(minutes=1)
    else:
        try:
            now_ = datetime.strptime(args.now_, "%Y-%m-%d_%H:%M")
        except ValueError:
            print("Given date-time is not comply with needed format -> yyyy-mm-dd_HH:MM")
            sys.exit(1)
        except:
            print("Error: Check following stack trace for more info.")
            print(traceback.format_exc())
            sys.exit(1)

    from_ = now_ - timedelta(minutes=args.window_size)
    print("Started calculation from {} to {}.".format(str(from_), str(now_)))

    # Read json bojects to a list
    json_list = []
    try:
        with open(args.path_to_json) as f:
            for line in f:
                json_list.append(json.loads(line))
    except ValueError as e:
        print("Please check the given file content comply with needed JSON format -> " + str(e))
        sys.exit(1)
    except:
        print("Error: Check following stack trace for more info.")
        print(traceback.format_exc())
        sys.exit(1)

    # Selects record within our time-gap
    data = []
    try:
        for record in json_list:
            t = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            if (from_ <= t and now_ > t):
                data.append(record)
    except ValueError as e:
        print("Error in timestamp conversion -> " + str(e))
        sys.exit(1)
    except:
        print("Error: Check following stack trace for more info.")
        print(traceback.format_exc())
        sys.exit(1)

    checkDataAmount(data)

    # In case sorting the rocords by time
    sortedData = sorted(data, key=lambda x: datetime.strptime(
        x['timestamp'], '%Y-%m-%d %H:%M:%S.%f'), reverse=False)
    # Creating a dataframe from selected json objets
    df = pd.DataFrame(sortedData, columns=[
                      'timestamp', 'duration', 'nr_words', 'source_language', 'target_language', 'client_name'])

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
                print("Filter results by translation -> source_language:{}, target_language:{}".format(
                    source_language, target_language))
                df = df[df.target_language == target_language]
                df = df[df.source_language == source_language]
                checkDataAmount(df.index)

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
    df = df.drop_duplicates(
        subset='timestamp', keep='last').reset_index(drop=True)
    # Renaming and converting to string
    df.rename(columns={'timestamp': 'time',
                       'MA': 'average_delivery_time'}, inplace=True)
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
    if len(data) == 0:
        print("No data within the specified time.")
        sys.exit(1)
    # I just use window_size. Because its seems like a better choice than putting a constant value.
    elif len(data) <= args.window_size:
        print("Warning: Amount of data within the specified time is very less.")


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

parser.add_argument('--now',
                    dest='now_',
                    default='now',
                    type=str,
                    help='Relative time (yyyy-mm-dd_HH:MM) to start calculation.')

parser.add_argument('--translation',
                    dest='translate',
                    type=str,
                    help='Filter results by translation type (source_language:target_language)')

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
