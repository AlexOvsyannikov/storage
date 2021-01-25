import os

from get_data_from_csv_xls import Item
import pickle


class TempStorage:
    def __int__(self):
        self.items = []

    def add_item(self, item: Item):
        self.items.append(item)

    def get_items(self):
        return self.items


class RemoteDataStorage:
    def __init__(self):
        if os.path.exists(os.getcwdb().decode() + "/remote_storage_data"):
            with open(os.getcwdb().decode() + "/remote_storage_data", "rb") as file:
                self.items = pickle.load(file)
        else:
            self.items = []

    def save_items(self):
        print("Saving RemoteData")
        self.__del__()

    def add_item(self, item: Item):
        self.items.append(item)
        self.save_items()

    def get_items(self):
        return self.items

    def __del__(self):
        with open("remote_storage_data", "wb") as f:
            pickle.dump(self.items, f)