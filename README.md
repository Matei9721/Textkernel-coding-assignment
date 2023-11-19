# Textkernel Coding Assignment

This repository contains the source code and documentation of the address to country matching problem.

## Overview

This repository contains a simple solution to the problem of matching an address to its origin country. The packaged 
solution takes in as input an address as a string, and it returns the hash of the closest matched country. The following
is achieved by splitting the address in sub-strings (if commas are present) or token (if no commas present) and 
subsequently matching those against our mappings of cities to countries (using fuzzy matching).

### Logic overview

A high-level overview of how the matching is achieved is described in the diagram below. The following steps are being 
applied from one end to another to achieve the required results:

1. Input string gets split into smaller chunks, and the order gets reversed based on the assumption that country or city
information is found at the end of an address.
    - If the string contains commas, the string is split based on commas --> commas tend to split street from city
    - If no strings are found, default to splitting into tokens based on spaces --> less ideal solution as seen below
2. For each sub-string, try to match it to a city or country in our dataset.
   - First we try to match the last sub-string to a country as usually the country is last in the address. If there is 
   no perfect match, we continue.
   - If no country match, we try to match the sub-strings to the cities in our dataset. We use fuzzy matching meaning we
   will always have a match (no matter how low confidence).
   - A confidence score is always returned for the matches cities, which allows further experimentation and development
   of the application to allow the user to customize the quality of the search.
3. We match the found country or city to the country code:
   - If we had a country match perfectly in the address string, we use the country_to_code mapping to retrieve the code
   of the country.
   - If there was no perfect match for a country, but we had a perfect match for a city, we use the city_to_country 
   mapping to retrieve the country code of the city we perfectly matched. If both fail, we retrieve the code of the city
   with the highest confidence (based on levenstein distance score).

![Country matching flow](resources/flow.svg)

### Code design overview

All the logic above is encompassed into a Python class (CountryMatcher) which at initialization expects the paths to the
mapping data for cities_to_countries and country_to_code. This was done this way to separate the data logic from the
matching logic. As long as the data sent to the class is in JSON format and follows the key:value format where key is 
city or country and value is country code, the code will run correctly.

The main function to be called is `find_country_hash` which accepts a single address or a list of addresses. If a list 
of addresses is passed, the code will compute the results taking advantage of Python multi-threading. All the libraries 
and logic used to match an address to a country are thread safe so multiprocessing will improve the speed of the process
with no potential issues.

### Data

The data used to match sub-strings to city names and then city names to their country's code is from the cities.jsonl 
given part of this assignment. The file has been modified to have a normal JSON (city:country) structure.

The data used to match a sub-string to a country directly is coming from the countries.json file which was downloaded 
from https://gist.github.com/almost/7748738. The file was slightly adjusted to follow the same structure as the previous
file.

Both files are available in the `datasets/` directory. The code to generate the processed files from the raw ones is
available in `utils\data_processing.ipnyb`

## Results

The resulting code can match addresses to their country code in a fast and potentially scalable manner. With the current
available data and chosen logic, the system achieves an **accuracy of ~0.90** based on the test address data supplied
at the begging of the assignment.

## Limitations
The current approach has a few known limitations and issues:

### Memory limitations
The current approach requires the system to load all the data in-memory. Depending on how much the application will be
scaled, this will become a potential (big) issue.

An alternative solution would be to change the data structure from a Python dictionary based one to a more conventional 
database. A better alternative which would allow for a different matching logic would be to use embeddings based storage
with (cosine) similarity matching. This would avoid the memory issue, while still allowing for a fast search and match
algorithm.

### Logic limitations

The current logic of matching the address to a country code based on it's substrings has a few shortcomings. First of all,
if the address does not contain strings, then the matching is done on spaces, potentially separating town names which are
composed of multiple words. This will then lead to wrong mappings between the sub-strings (tokens) and the known cities.

There is also the problem is disambiguation in the case a sub-string is can be perfectly matched to multiple cities in our
dataset. In that scenario, there is no simple way of determining which is the correct city without using additional metadata
about the address origin (language or context).

Some cities are not in our dataset which means we will never get a correct match. Because of the fuzzy algorithm we are
using, we will **always** get a match which will lead to False Positives. To somewhat minimize this, I have implemented
the minimum_threshold functionality when calling `find_country_hash` to force the algorithm to not return a country code
when unsure.

The code currently contains a limited amount of error handling. The code can also be further refactored to follow the
dry code principle. More configurability can be added to the matching logic to improve performance.

## Deployment and testing

The source code currently contains a `test` folder which contains a few simple `unit` tests for the main logic. The 
GitHub repository also contains a simple `pipeline` which build the source code and runs the test on every push to the
`main` branch for continuous development.

In the repository, you can also find a `wheel` file build using `setuptools` which can be used to easily install the
package and all of it's dependencies (at this moment, only `thefuzz` for fuzzy matching). To install the package from
the wheel file use the following command in the `root` folder: 

```python
 pip install .\dist\country_matcher-1.0-py3-none-any.whl --force-reinstall
```
To install the package from source, you can install the dependencies from the `requirements.txt` file:

```python
 pip install -r requirements.txt
```

## Project Structure

- `main.ipnyb`: An example Jupyter notebook that can be used to run the code.
- `country_matcher/`: Directory containing main code for country matching logic.
  - `country_matcher.py`: Python file containing the address-to-country matching logic.
- `utils`: Directory for utility functions and classes.
  - `data_processing.ipnyb`: Notebook that contains code needed to process raw data.
- `tests/`: Directory containing the unit tests for the source code.
- `requirements.txt`: A file listing the dependencies required for the project.
- `dataset/`: A directory containing the raw data and processed data to be used by the matching algorithm.
- `wheel/`: A directory containing the wheel distribution files.
- `setup.py`: A Python file containing the configuration for creating a new wheel file from the source code.
- `resources/`: Directory containing images or other documentation resources.
- `.github/`: A directory containing the GitHub action workflow configuration file.