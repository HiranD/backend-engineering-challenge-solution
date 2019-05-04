# backend-engineering-challenge-solution

	unbabel_cli --input_file events.json --window_size 10

I have selected pandas to process data because of it's easyness to change, in case if I want to add more features.

### _*python solution.py --help*_

```
optional arguments:
    --output_loc      Relative path to save results (Defult: same directory output_result.json).
    --now             Relative time (yyyy-mm-dd_HH:MM) to start calculation (Defult: now()).
```
*eg: python solution.py --input_file events.json --window_size 10 --now 2019-01-02_00:00 --output_loc ../output/result.json*

### Notes
This events.json (generated using [json-generator.com](https://www.json-generator.com)) contains artificially generated translation delivery json logs within the day of 2019-01-01. So if you are using this json file you will have to give a time within day of 2019-01-01 as *--now* argument. So that will become the ancore point and amount of __window_size__ minutes will go back from that point backwards.

*eg: in the above example, calcualtion will only consider the data from 2019-01-01 23:50 to 2019-01-02 00:00 only.*

If we are not defining attribute *--now*, calculation will start from __now__ on backwards.

### Additional features
    --translation       Filter results by translation type (source_language:target_language).

*eg: python solution.py --input_file events.json --window_size 10 --now 2019-01-02_00:00 --translation en:fr*

### Requirements
    python 3.6
    pandas 0.23.4