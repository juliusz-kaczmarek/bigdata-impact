# BigData Impact

**BigData Impact** is an automated Monte Carlo simulation solution designed to generate large-scale results from a single configuration, facilitating comprehensive theorycrafting and data-driven analysis for Genshin Impact. It serves as a weapon, artifact set, and main stat swapper.

## Getting Started

### Dependencies

To use **BigData Impact**, ensure the following prerequisites are met:
* [Python 3.12.5+](https://www.python.org/)
* [GCSim CLI](https://github.com/genshinsim/gcsim)
* Any software that allows you to edit .csv file, such as Microsoft Excel

### Installing

1. Place `batchsim.py` in the same directory as the GCSim CLI executable.
2. For ease of use, keep the config and variable sheets in the same directory.

### Executing program

1. **Prepare the GCSim Config:**
   - Adjust your GCSim config to include `$charX` (where X is the character number 1-4) instead of specific weapon, artifact, or stat entries. This references the variable sheet for dynamic data replacement. Please refer to `example_config.txt` for guidance.

2. **Set Up the Variable Sheet:**
   - Use `variable_sheet_template.csv` for setting up your data. Follow GCSim’s naming conventions (e.g., `staffofhoma` instead of `Staff of Homa`). Refer to `example_variable_sheet.csv` for guidance. Leave character columns empty if no changes are needed.
  
3. **Execute the Program:**
   - Run the following command to start the simulation:

     ```bash
     python batchsim.py -cfg "config_name.txt" -var "variable_sheet_name.csv"
     ```

   - Replace `"config_name.txt"` with the name of your adjusted GCSim config file and `"variable_sheet_name.csv"` with the name of your variable sheet.

## Authors

BigData Impact was made by Juliusz Kaczmarek ([juliusz-kaczmarek](https://github.com/juliusz-kaczmarek)).

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
