# backend-engineering-challenge-solution

	unbabel_cli --input_file events.json --window_size 10

### _*python solution.py --help*_

```
optional arguments:
    --output_loc      Relative path to save results
    --to              Relative time (yyyy-mm-dd_HH:MM) to start calculation
```
*eg: python solution.py --input_file events.json --window_size 10 --to 2019-01-02_00:00 --output_loc ../output/result.json*

### Notes
this events.json contains artificially generated translation delivery json logs within the day of 2019-01-01. So if you are using this json file you will have to give a time within day of 2019-01-01 as *--to* argument. So that will become the ancore point and amount of *window_size* minutes will go back from that point backwards.

*eg: in the above example calcualtion will only consider the data from 2019-01-01 23:50 to 2019-01-02 00:00 only*

If we are not defining attribute *--to*, calculation will start from _now_ on backwards.

### Additional features

