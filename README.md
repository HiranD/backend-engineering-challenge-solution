# backend-engineering-challenge-solution

*eg: python solution.py --input_file events.json --window_size 10*

### _python solution.py --help_

```
optional arguments:
    --output_loc      Relative path to save results (Defult: same directory output_result.json).
```
*eg: python solution.py --input_file events.json --window_size 10 --output_loc ../output/result.json*

### Additional features
    --translation       Filter data by translation type (source_language:target_language).
    *eg: python solution.py --input_file events.json --window_size 10 --translation en:fr*

    --client            Filter data by client name.
    *eg: python solution.py --input_file events.json --window_size 10 --client easyjet*

### Requirements
    python 3.6
    pandas 0.23.4