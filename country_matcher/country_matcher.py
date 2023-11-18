from typing import Union, List, Tuple
import json
import string
from thefuzz import fuzz, process
from concurrent.futures import ThreadPoolExecutor


class CountryMatcher:
    def __init__(self, city_to_country_mapping_path: str, country_code_mapping_path: str):
        self.__city_to_country_mapping = self.__load_mapping_from_json(city_to_country_mapping_path)
        self.__country_code_mapping = self.__load_mapping_from_json(country_code_mapping_path)
        self.__cities = list(self.__city_to_country_mapping.keys())

    def find_country(self, addresses: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(addresses, str):
            # If addresses is a string
            return self.__process_single_address(addresses)[0]
        elif isinstance(addresses, list) and all(isinstance(addr, str) for addr in addresses):
            results = []
            # If addresses is a list of strings
            for address in addresses:
                results.append(self.__process_single_address(address)[0])

            return results
        else:
            print("Invalid input. Please provide a string or a list of strings.")

    def __process_single_address(self, address: str) -> Tuple[str, int]:
        final_result, final_confidence = None, 0
        address = self.__pre_process_address(address)

        # Match tokens with cities
        for token in address:
            search_result, search_confidence = process.extractOne(token, self.__cities, scorer=fuzz.ratio)

            # Found perfect match so early stopping the search
            if search_confidence == 100:
                return self.__city_to_country_mapping[search_result], search_confidence
            else:
                if search_confidence > final_confidence:
                    # Updating the best match so far
                    final_result, final_confidence = search_result, search_confidence

        return self.__city_to_country_mapping[final_result], final_confidence

    @staticmethod
    def __load_mapping_from_json(mapping_path):
        try:
            with open(mapping_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {mapping_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding JSON in {mapping_path}. {e}")

    @staticmethod
    def __pre_process_address(address):
        address = address.translate(str.maketrans("", "", string.punctuation)).lower().split()[::-1]

        return address
