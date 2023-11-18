import unittest
from country_matcher.country_matcher import CountryMatcher
import hashlib
import json


class MyTestCase(unittest.TestCase):

    @staticmethod
    def read_addresses_file(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            addresses = []
            for line in file:
                # Load each line as a JSON object
                json_data = json.loads(line)
                address_to_country_dict = json_data["address"], json_data["country"]
                addresses.append(address_to_country_dict)

        return addresses

    @classmethod
    def setUpClass(cls):
        # Initialize CountryMatcher class
        cls.country_matcher = CountryMatcher("dataset/city_to_country_mapping.json",
                                             "dataset/country_to_code_mapping.json")

        cls.test_addresses = cls.read_addresses_file("tests/data/addresses.jsonl")

    def test_good_address(self):
        address_input = self.test_addresses[0][0]
        expected_output = hashlib.sha256(self.test_addresses[0][1].encode('utf-8')).hexdigest()

        output = self.country_matcher.find_country_hash(address_input)

        self.assertEqual(expected_output, output)

    def test_batch_address_processing(self):
        addresses = self.test_addresses[:25] + self.test_addresses[-5:]
        addresses_input = [address[0] for address in addresses]
        expected_output = [hashlib.sha256(address[1].encode('utf-8')).hexdigest() for address in addresses]

        output = self.country_matcher.find_country_hash(addresses_input)
        self.assertEqual(expected_output, output)

    def test_minimum_accuracy(self):
        addresses = self.test_addresses[:100] + self.test_addresses[-100:]
        addresses_input = [address[0] for address in addresses]
        expected_output = [hashlib.sha256(address[1].encode('utf-8')).hexdigest() for address in addresses]
        output = self.country_matcher.find_country_hash(addresses_input)

        correct_predictions = sum(1 for e, a in zip(expected_output, output) if e == a)
        total_predictions = len(expected_output)
        accuracy = correct_predictions / total_predictions

        self.assertTrue(accuracy > 0.90)

    def test_address_splitting(self):
        input_with_commas = "Het Kwadrant 34, Amsterdam"
        input_no_commas = "Het Kwadrant 34 Amsterdam"

        output_with_commas = self.country_matcher.pre_process_address(input_with_commas)
        output_no_commas = self.country_matcher.pre_process_address(input_no_commas)

        self.assertEqual([" amsterdam", "het kwadrant 34"], output_with_commas)
        self.assertEqual(["amsterdam", "34", "kwadrant", "het"], output_no_commas)


if __name__ == '__main__':
    unittest.main()
