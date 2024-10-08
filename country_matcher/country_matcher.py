from typing import Union, List, Tuple
import json
from thefuzz import fuzz, process
import hashlib
from concurrent.futures import ThreadPoolExecutor


class CountryMatcher:
    """
    Python class responsible for encapsulating the logic of matching an address to a country code using fuzzy string
    matching.
    """
    def __init__(self, city_to_country_mapping_path: str, country_code_mapping_path: str):
        self.__city_to_country_mapping = self.__load_mapping_from_json(city_to_country_mapping_path)
        self.__country_code_mapping = self.__load_mapping_from_json(country_code_mapping_path)
        self.__cities = list(self.__city_to_country_mapping.keys())
        self.__countries = list(self.__country_code_mapping.keys())

    def find_country_hash(self, addresses: Union[str, List[str]], confidence_threshold: int = 0) -> \
            Union[str, List[str]]:
        """
        Main method that contain the logic for processing a single address or a batch of addresses. This function
        retrieves the country code for each address, hashes it and returns it to the user.
        :param addresses: String or List of Strings (addresses)
        :param confidence_threshold: Confidence threshold for the matching
        :return: Hashed value for the country code
        """
        if isinstance(addresses, str):
            # If addresses is a string
            return self.__hash_string_sha256(self.__process_single_address(addresses, confidence_threshold)[0])

        elif isinstance(addresses, list) and all(isinstance(addr, str) for addr in addresses):
            results = []
            # If addresses is a list of strings
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(self.__process_single_address, addresses))
            results = [self.__hash_string_sha256(result[0]) for result in results]
            return results
        else:
            print("Invalid input. Please provide a string or a list of strings.")

    def __process_single_address(self, address: str, threshold: int = 0) -> Tuple[str, int]:
        """
        Method responsible for matching a single address to its country. It uses fuzzy matching between each sub-string
        of the address.
        :param address: String of the address
        :param threshold: Confidence threshold for the matching
        :return: Country code (string)
        """
        final_result, final_confidence = None, 0
        address = self.pre_process_address(address)

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
    def pre_process_address(address):
        """
        Split the address in sub-strings if commas are present in the string. If no commas available, split into tokens
        based on empty spaces between words. Reverse the order of the sub-strings as the most important information
        is usually at the end of an address.
        :param address: String of the address
        :return: List of tokens (strings)
        """
        address = address.lower()

        if "," in address:
            address = address.split(",")[::-1]
        else:
            address = address.split()[::-1]

        return address

    @staticmethod
    def __hash_string_sha256(input_string):
        # Return the hexadecimal representation of the SHA-256 hash
        return hashlib.sha256(input_string.encode('utf-8')).hexdigest()
