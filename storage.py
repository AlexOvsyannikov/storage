import json
import os
import pickle

from remote_data_storage import TempStorage, RemoteDataStorage
from render_storage import RenderStorage, Cell
from get_data_from_csv_xls import Item, WayBill


class TalkToDB:
    def __init__(self):
        self.remote_data_storage = RemoteDataStorage()

        self.temp_data_storage = TempStorage()
        self.remote_temp_data_storage = TempStorage()

    def make_temp_storages(self):
        self.temp_data_storage = TempStorage()
        self.remote_temp_data_storage = TempStorage()

    def send_to_db(self, item: Item, cell: Cell):
        self.temp_data_storage.add_pair(item, cell)
        print("sent to db " + item.name)

    def get_position_from_db(self, key):
        pass

    def send_to_remote_db(self, item):
        self.remote_temp_data_storage.add_item(item)
        self.remote_data_storage.add_item(item)
        print("sent to remote db " + item.name)


class StorageMaker:
    def __init__(self, host='5000', port='127.0.0.1'):
        if os.path.exists(os.getcwdb().decode() + "/storage"):
            with open(os.getcwdb().decode() + "/storage", "rb") as file:
                self.storage = pickle.load(file)
        else:
            self.storage = StorageImproved(port=port, host=host)

    def save(self):
        print("Saving data...")
        self.__del__()

    def __del__(self):
        try:
            with open(os.getcwdb().decode() + "/storage", "wb") as f:
                pickle.dump(self.storage, f)
        except:
            pass


class Storage(RenderStorage):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.item_uuid_cell_name_dict = {}
        self.database_sender = TalkToDB()

    def put(self, way_bill: WayBill):
        """START PROCESS OF PUTTING"""
        data = way_bill.create_item_list()
        return self._solve_how_to_put(data)

    def _solve_how_to_put(self, items):
        """SOLVE HOW TO PUT ITEM TO DB"""
        _data_to_send_to_api = []
        self.database_sender.make_temp_storages()
        for _item_num in range(len(items) - 1, -1, -1):
            _item_was_put = False
            for _block_num in range(self.height - 1, -1, -1):
                for _cell_num in range(self.width - 1, -1, -1):
                    _cell = self.cells[_block_num][_cell_num]
                    _item = items[_item_num]
                    _gab = self._check_gabarits(_item, _cell)
                    if not _cell.busy:
                        if _gab:
                            if _cell.size_height + _cell.size_width + _cell.size_depth == _gab:
                                _cell.put_to_cell(_item)
                                self.item_uuid_cell_name_dict.update({_item.uuid: _cell.name})

                                if _cell.merged:
                                    for _merged_cell in _cell.merged_with:
                                        self.easy_find_cell_by_name[_merged_cell].put_to_cell(_item)

                                _data_to_send_to_api.append({"uuid": _item.uuid,
                                                             "destination": [
                                                                 _cell.name] if not _cell.merged else _cell.merged_with})
                                self.database_sender.send_to_db(_item, _cell)

                                _item_was_put = True
                                break
                        else:
                            self.database_sender.send_to_remote_db(_item)
                            _item_was_put = True
                            break
                if _item_was_put:
                    break

            # отправляем на удаленный склад, если место не найдено
            if not _item_was_put:
                self.database_sender.send_to_remote_db(items[_item_num])

        _resp = json.loads(self.put_item_api(_data_to_send_to_api))
        if _resp["status"] == "ok":
            super(Storage, self).render()
            return "OK"
        else:
            return "Error"

    def _check_gabarits(self, _item: Item, _cell):
        """CHECK SIZE OF ITEM"""
        if ((_item.height + _item.width + _item.depth) > 5) or _item.height > 2 or _item.width > 2 or _item.depth > 2:
            return 0
        elif _item.height == 1 and _item.width == 1 and _item.depth == 1:
            return 3
        elif ((_item.height == 2 and _item.depth == 1 and _item.width == 1) or (
                _item.height == 1 and _item.depth == 2 and _item.width == 1) or (
                      _item.height == 1 and _item.depth == 1 and _item.width == 2)):
            return 4
        else:
            return 5

    def get(self, uuid="", type_of_work=0, cell_name=""):
        """GET POSITION FROM STORAGE"""
        try:
            if type_of_work == 0:
                _cell = self.easy_find_cell_by_name[self.item_uuid_cell_name_dict[uuid.lower()]]
            else:
                _cell = self.easy_find_cell_by_name[cell_name]
        except:
            return "NO SUCH UUID OR CELL NAME FOUND"

        _resp = json.loads(self.position_api({"destination": [_cell.name] if not _cell.merged else _cell.merged_with}))
        _cell._make_free()
        if _cell.merged:
            for _merged_cell in _cell.merged_with:
                self.easy_find_cell_by_name[_merged_cell]._make_free()
        if _resp["status"] == "position is empty":
            return "Position is empty"
        elif _resp["status"] == "ok":
            self.render()
            return "OK"
        else:
            return "ERROR"


class StorageImproved(Storage):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.unique_cells = []
        for cell_block in self.cells:
            for cell in cell_block:
                if not cell.merged:
                    self.unique_cells.append(cell)

                if cell.merged and not cell.rendered:
                    self.unique_cells.append(cell)
                    for merged_cell in cell.merged_with:
                        self.easy_find_cell_by_name[merged_cell].make_rendered()
        for cell_block in self.cells:
            for cell in cell_block:
                if cell.merged:
                    cell.make_not_rendered()

    def get_json_data_unique_cells(self):
        data = []
        for i in self.unique_cells:
            if not i.busy:
                data.append(i.__dict__)
            else:
                _ = {}
                _.update({"name": i.name, "lvl": i.lvl, "merged": i.merged, "merged_with": i.merged_with,
                          "size_width": i.size_width, "size_height": i.size_height, "size_depth": i.size_depth,
                          "busy": i.busy, "rendered": i.rendered, "contained_item": i.contained_item.__dict__})
                data.append(data)
        print(data)
        return data
