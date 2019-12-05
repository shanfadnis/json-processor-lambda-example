import unittest
import os
import sys
import json
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from jsonprocessor import app


class JsonProcessorTest(unittest.TestCase):
    def test_camel_to_underscores(self):
        self.assertEqual(app.camel_to_underscores('HelloWorld'), 'hello_world')
        self.assertEqual(app.camel_to_underscores(
            'MACAddress'), 'm_a_c_address')

    def test_transform_block(self):
        self.assertEqual(app.transform_block(None), "null")
        self.assertEqual(app.transform_block(
            '2019-03-01T12:31:40.746Z'), '2019-03-01 12:31:40')

    def test_flatten_json(self):
        in_value = {
            "header": {
                "messageId": "9eb86408-f578-42fe-bccf-c2bca576tttttttt",
                "timestamp": "2019-03-01T12:31:40.746Z"
            },
            "timeOfCollection": "2019-04-02T09:50:24.585Z",
            "value": "null"
        }
        out_value = {
            "header_message_id": "9eb86408-f578-42fe-bccf-c2bca576tttttttt",
            "header_timestamp": "2019-03-01 12:31:40",
            "time_of_collection": "2019-04-02 09:50:24",
            "value": "null"
        }
        self.assertEqual(app.flatten_json(in_value), out_value)

    def test_filter_rules(self):
        self.assertEqual(app.filter_rules(
            'android_payload_battery_level'), 'battery_level')


if __name__ == '__main__':
    unittest.main()
