import json
import requests
from time import sleep

import common


class FileIO:
    @staticmethod
    def write(file_name, text, rewrite=True):
        if rewrite:
            file = open(file_name, 'w', encoding='UTF-8')
        else:
            file = open(file_name, 'a')
        file.write(text)
        file.close()

    @staticmethod
    def write_json(file_name, for_json, rewrite=True):
        # FileIO.write(file_name, json.dumps(for_json, sort_keys=True, indent=1, default=lambda x: x.__dict__()),
        # rewrite)
        if type(for_json) == list:
            FileIO.write(file_name, json.dumps(for_json, sort_keys=True, indent=1), rewrite)
        else:
            FileIO.write(file_name, json.dumps(for_json.__dict__(), sort_keys=True, indent=1), rewrite)

    @staticmethod
    def read(file_name):
        file = open(file_name, 'r')
        text = file.read()
        file.close()
        return text

    @staticmethod
    def read_json(file_name):
        file = open(file_name, 'r')
        text = file.read()
        file.close()
        return json.loads(text)


class InternetIO:
    @staticmethod
    def get(url, fast=False):
        try:
            # sleep(0.01)
            if common.DEBUG or fast:
                sleep(0.01)
            else:
                sleep(1)
            return requests.get(url).text
        except BaseException as e:
            print(e, e.args)
            return None
