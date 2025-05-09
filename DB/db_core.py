import pymongo
from Utils.logger import get_logger
import os

logger = get_logger()


class DBCore:

    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("DB_CONNECTION_STRING"))

        self.db = self.client['ZENQ_V1']

    def insert(self, collection: str, generic_dict: dict):
        mycol = self.db[f"{collection}"]
        x = mycol.insert_one(generic_dict)
        return x

    def delete_by_id(self, collection: str, id: str):
        mycol = self.db[f"{collection}"]
        x = mycol.delete_one({"_id": id})
        return x

    def delete_stats_by_user(self, collection: str, id: str):
        mycol = self.db[f"{collection}"]
        x = mycol.delete_one({"user_id": id})
        return x

    def update_last(self):
        obj_last_id = self.reading_last_from_mongo(collection="status")["_id"]
        filtro = {"_id": obj_last_id}

        aggiornamento = {"$set": {"running": False}}

        res = self.db["status"].update_one(filtro, aggiornamento)
        return res

    def reading_last_from_mongo(self, collection: str):
        filter = {
        }
        limit = 1
        sort = list({
                        "_id": -1
                    }.items())

        mycol = self.db[f"{collection}"]
        res = mycol.find_one(filter=filter, sort=sort, limit=limit)
        return res

    def read_user(self, collection: str, user: str):
        filter = {"_id": user
                  }
        mycol = self.db[f"{collection}"]
        res = mycol.find_one(filter=filter)

        return res

    def read_white_list_user(self):
        mycol = self.db[f"white_list"]
        res = mycol.find()
        full_list = list(res)

        lst_available_email = []
        lst_used_email = []
        lst_used_nickdame = []

        for element in full_list:
            if element['user'] == '':
                lst_available_email.append(element['_id'])
            else:
                lst_used_email.append(element['_id'])
                lst_used_nickdame.append(element['user'])

        return lst_available_email, lst_used_email, lst_used_nickdame

    def update_white_list_user(self, user: str, email: str):
        mycol = self.db[f"white_list"]
        filtro = {"_id": email}
        aggiornamento = {"$set": {'user': user}}
        mycol = mycol.update_one(filtro, aggiornamento)

    def get_all_user(self, collection):
        project = {
            '_id': 1
        }
        mycol = self.db[f"{collection}"]
        res = mycol.find(projection=project)
        return list(res)

    def read_bot_last_session_starting_time(self, user: str):
        filter = {"user_id": user
                  }
        sort = list({
                        "transaction_datetime": -1
                    }.items())
        mycol = self.db[f"running_info"]
        res = mycol.find_one(filter=filter, sort=sort)
        return res

    def read_bot_stat_by_time(self, user: str):
        filter = {"user_id": user
                  }
        sort = list({
                        "stats_datetime": -1
                    }.items())
        mycol = self.db[f"running_stats"]
        res = mycol.find_one(filter=filter, sort=sort)
        return res

    def update_user_info(self, user: str, generic_dict: dict):
        filtro = {"_id": user}

        mycol = self.db["utenti"]

        aggiornamento = {"$set": generic_dict}

        mycol.update_one(filtro, aggiornamento)

    def update_user_strategy_info(self, user: str, generic_dict: dict):
        filtro = {"_id": user}

        aggiornamento = {"$set": generic_dict}

        mycol = self.db["utenti"]

        mycol.update_one(filtro, aggiornamento)

    def read_all_subscribed_user_to_strategy(self, strategy_id: str):
        filter = {f"strategia_{strategy_id}_subscribed":True}
        project = {'_id': 1}
        mycol = self.db["utenti"]
        res = mycol.find(filter=filter, projection=project)

        return list(res)

    def read_a_subscribed_user_to_strategy(self,user, strategy_id):
        filter = {f"strategia_{strategy_id}_subscribed":True, "_id": user}
        mycol = self.db["utenti"]
        res = mycol.find_one(filter=filter)
        return res

    def read_algos_subscribed_user(self,user):
        filter = {"_id": user}
        project = {
            'strategia_1_subscribed': 1,
            'strategia_2_subscribed': 1,
            'strategia_3_subscribed': 1,
            'strategia_4_subscribed': 1
        }
        mycol = self.db["utenti"]
        res = mycol.find_one(filter=filter, projection=project)
        return res

    def read_all_user(self,):
        mycol = self.db["utenti"]
        res = mycol.find()
        return res

    def get_startegy_data(self, strategy):
        projection = {"time":1,"quoteQty":1, "_id":0}
        sort = list({
                        "order": 1
                    }.items())
        mycol = self.db[f"strategia_{strategy}_andamento"]
        res = mycol.find(projection=projection, sort=sort)
        return list(res)

    def get_startegy_performance(self):
        mycol = self.db[f"performance_strategie"]
        res = mycol.find_one()
        return res

    def get_binance_wallet(self, strategy):
        mycol = self.db[f"binance_wallet_info"]
        res = mycol.find_one(filter={"_id": f"strategia_{strategy}"})
        return res

    def update_token_info(self, user: str, generic_dict: dict):
        filtro = {"_id": user}

        mycol = self.db["utenti_chiavi"]

        aggiornamento = {"$set": generic_dict}

        return mycol.update_one(filtro, aggiornamento)

    def update_transaction_info(self, user: str, generic_dict: dict, startegy_id: int):
        filtro = {"_id": user}

        mycol = self.db[f"strategia_{startegy_id}"]

        aggiornamento = {"$set": generic_dict}

        return mycol.update_one(filtro, aggiornamento)