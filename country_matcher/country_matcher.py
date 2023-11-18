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
        self.__countries = list(self.__country_code_mapping.keys())

    def find_country(self, addresses: Union[str, List[str]], confidence_threshold: int = 0) -> Union[int, List[int]]:
        if isinstance(addresses, str):
            # If addresses is a string
            return hash(self.__process_single_address(addresses, confidence_threshold)[0])

        elif isinstance(addresses, list) and all(isinstance(addr, str) for addr in addresses):
            results = []
            # If addresses is a list of strings
            for address in addresses:
                results.append(hash(self.__process_single_address(address, confidence_threshold)[0]))
            return results
        else:
            print("Invalid input. Please provide a string or a list of strings.")

    def __process_single_address(self, address: str, threshold: int = 0) -> Tuple[str, int]:
        final_result, final_confidence = None, 0
        address = self.__pre_process_address(address)

        # Found country code using country name so early stopping. Only running this for last token based on assumption
        search_result, search_confidence = process.extractOne(address[0], self.__countries, scorer=fuzz.ratio)
        if search_confidence == 100:
            return self.__country_code_mapping[search_result], search_confidence

        # Match all tokens with cities
        for token in address:
            search_result, search_confidence = process.extractOne(token, self.__cities, scorer=fuzz.ratio)

            # Found perfect match so early stopping the search
            if search_confidence == 100:
                return self.__city_to_country_mapping[search_result], search_confidence
            else:
                if search_confidence > final_confidence:
                    # Updating the best match so far
                    final_result, final_confidence = search_result, search_confidence
        if final_confidence > threshold:
            return self.__city_to_country_mapping[final_result], final_confidence
        else:
            return "No match", final_confidence

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
        """
        Remove any punctuation signs, split into token based on spaces and reverse order of token as city or country
        are more likely to be at the end of an address (assumption based on data analysis)
        :param address: String of the address
        :return: List of tokens (strings)
        """
        address = address.translate(str.maketrans("", "", string.punctuation)).lower().split()[::-1]

        return address
