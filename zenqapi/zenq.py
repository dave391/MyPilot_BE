import datetime
import json
import random
import string

import requests

from DB.db_core import DBCore
from ._config import *
from ._serializer import *
from ._utils import filter_order
from .signatures.response import APIStandardResponse, APIUserBalances
from .sub_account_management.api import ZagApiClient
import uuid



class Client:
    def __init__(self, apiKey: str, apiSecret: str, test: bool = True):
        """
        Initializes the client to communicate with the Zenq exchange.

        :param apiKey: The API key associated with the user account, generated from the Zenq exchange.
        :param apiSecret: The API secret key associated with the user account, generated from the Zenq exchange.
        :param test: A flag to indicate the environment. 
                     Set to True for Paper Money (test environment) or False for Real Money (live trading).

        """

        self.apiKey = apiKey
        self.apiSecret = apiSecret
        if test:
            self.base_url = test_url
        else:
            self.base_url = prod_url

    def place_limit_order(self, apiQuantity: float, apiOrderType: Union[int, str], apiPrice: float, apiTickerId: Union[int, str, Ticker]) -> APIStandardResponse:
        """
        Place a limit order on the exchange.

        :param apiQuantity: The quantity to order, expressed in base token units.
        :param apiOrderType: The type of the order. 
                             Can be a string with the value "buy" or "sell",or an integer (1 for "buy" or -1 for "sell").
        :param apiPrice: The price level at which the order is placed.
        :param apiTickerId: The market pair identifier. 
                            This can either be a string (e.g., "BTCUSDT") or the ticker ID from the Zenq exchange.
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """

        apiOrderTypeDecoded = from_textual_order_type_to_integer_order_type(apiOrderType)
        if apiOrderTypeDecoded == 0:
            return APIStandardResponse(status_code="R422", message="apiOrderType must be a valid value", is_error=True)

        symbolDecoded = from_ticker_name_or_obj_to_ticker_id(apiTickerId)
        if symbolDecoded == -1:
            return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)

        params = {
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "apiQuantity": apiQuantity,
            "apiOrderType": apiOrderTypeDecoded,
            "apiPrice": apiPrice,
            "apiTickerId": symbolDecoded,
            "outputType": "json"
        }
        url = f"{self.base_url}{place_order_url}"
        response = requests.get(url, params=params)
        content = json.loads(response.content.decode('utf-8'))

        return APIStandardResponse.from_dict(content)

    def place_market_order(self, apiQuantity: float, apiOrderType: Union[int, str], apiTickerId: [int, str, Ticker]) -> APIStandardResponse:
        """
        Place a market order on the exchange.

        :param apiQuantity: The quantity to order, expressed in base token units.
        :param apiOrderType: The type of the order. 
                             Can be a string with the value "buy" or "sell", or an integer (1 for "buy" or -1 for "sell").
        :param apiTickerId: The market pair identifier. 
                            This can either be a string (e.g., "BTCUSDT") or the ticker ID from the Zenq exchange.
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """

        apiOrderTypeDecoded = from_textual_order_type_to_integer_order_type(apiOrderType)
        if apiOrderTypeDecoded == 0:
            return APIStandardResponse(status_code="R422", message="apiOrderType must be a valid value", is_error=True)

        symbolDecoded = from_ticker_name_or_obj_to_ticker_id(apiTickerId)
        if symbolDecoded == -1:
            return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)

        params = {
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "apiQuantity": apiQuantity,
            "apiOrderType": apiOrderTypeDecoded,
            "apiTickerId": symbolDecoded,
            "outputType": "json"
        }
        url = f"{self.base_url}{place_order_url}"
        response = requests.get(url, params=params)
        content = json.loads(response.content.decode('utf-8'))

        return APIStandardResponse.from_place_order_market_dict(content)

    def search_ticker(self, symbol: Union[int, str]) -> APIStandardResponse:
        """
        Retrieve information about a specific symbol, either by its string representation (e.g., "BTC") or its ID.
        
        :param symbol: The symbol to search. 
                       This can be a string, the ticker ID from the Zenq exchange, or the ticker Object from library.
                       E.g. ADAUSDC, "ADAUSDC", 40895, ADAUSDC.ticker_id
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """

        symbolDecoded = from_ticker_id_or_obj_to_ticker_name(symbol)
        if symbolDecoded == "":
            return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)
        params = {
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "st": symbolDecoded,
            "outputType": "json"
        }
        url = f"{self.base_url}{search_ticker_url}"
        response = requests.get(url, params=params)
        content = json.loads(response.content.decode('utf-8'))
        print(url)

        return APIStandardResponse.from_search_ticker_dict(content)

    def order_list(self, apiTickerId: Union[int, str, Ticker] = "", orderId: str = ""):
        """
        Retrieve a filtered list of orders, optionally filtering by ticker ID or order ID.
        
        :param apiTickerId: The ticker ID to filter orders by. If left empty, no filtering is applied based on the ticker.
                            This can either be a string (e.g., "BTCUSDT") or the ticker ID from the Zenq exchange.
        :param orderId: The specific order ID to filter by. If left empty, no filtering is applied based on the order ID.
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """
        params = {
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "outputType": "json"
        }
        url = f"{self.base_url}{order_list_url}"
        response = requests.get(url, params=params)
        if response.status_code != 404:
            content = json.loads(response.content.decode('utf-8'))

            apiTickerNameDecoded = ""
            if apiTickerId != "":
                apiTickerNameDecoded = from_ticker_id_or_obj_to_ticker_name(apiTickerId)
                if apiTickerNameDecoded == "":
                    return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)

            filtered_content = filter_order(content, apiTickerNameDecoded, orderId)

            return APIStandardResponse.from_order_list_dict(filtered_content)
        else:
            return APIStandardResponse(status_code='R404', is_error=True, message="Error 404! Endpoint not found.")

    def order_modify(self, orderId: str, newPrice: float, newQuantity: float, marketValue: float, apiTickerId: Union[int, str, Ticker] = 0) -> APIStandardResponse:
        # {"code":"R200","data":{"orderId":"48485","message":"Order was placed successfully. Order #  48485. \u003Cbr\u003EBTCUSDT X 0.00010 @ 125213.000"},"errors":[],"extra":[]}
        # {"success":1,"message":"Success: Modify order has been done\r\n"}
        """
        Modify an existing order by updating its price and quantity.

        :param orderId: The unique identifier of the order to be modified.
        :param newPrice: The new price for the order.
        :param newQuantity: The new quantity for the order.
        :param marketValue: The current market value used to validate the modification.
        :param apiTickerId: The ticker ID. If left empty, no filtering is applied based on the ticker.
                            This can either be a string (e.g., "BTCUSDT") or the ticker ID from the Zenq exchange.
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """

        symbolDecoded = from_ticker_name_or_obj_to_ticker_id(apiTickerId)
        if symbolDecoded == -1:
            return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)

        params = {
            "orderId": orderId,
            "newPrice": newPrice,
            "newQuantity": newQuantity,
            "marketValue": marketValue,
            "apiTickerId": symbolDecoded,
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "outputType": "json"
        }
        url = f"{self.base_url}{modify_order_url}"
        response = requests.get(url, params=params)
        return APIStandardResponse.from_modify_order(response=response, status_code=response.status_code,
                                                     order_id=orderId)

    def order_cancel(self, orderId: str, apiTickerId: Union[int, str, Ticker]) -> APIStandardResponse:
        # {"code":"R200","data":{"orderId":"48485","message":"Order was placed successfully. Order #  48485. \u003Cbr\u003EBTCUSDT X 0.00010 @ 125213.000"},"errors":[],"extra":[]}
        # Success: Order #48484 has been cancelled successfully
        """
        Cancel an existing order on the exchange.

        :param orderId: The unique identifier of the order to be canceled.
        :param apiTickerId: The ticker ID. If left empty, no filtering is applied based on the ticker.
                            This can either be a string (e.g., "BTCUSDT") or the ticker ID from the Zenq exchange.
        :return: APIStandardResponse Object with this property:
             status_code: The raw status code of server response.
             order_id: The order_id code from server response if valorized otherwise is 0.
             message: The message of server response, it contains the content, also errors.
             is_error: A flag that is True if the call returned a not 2XX code.
        """
        orderId = int(orderId)

        symbolDecoded = from_ticker_name_or_obj_to_ticker_id(apiTickerId)
        if symbolDecoded == -1:
            return APIStandardResponse(status_code="R422", message="Ticker name not found into library.", is_error=True)

        params = {
            "orderId": orderId,
            "mode": 'cancel',
            "apiTickerId": apiTickerId,
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "outputType": "json"
        }

        url = f"{self.base_url}{cancel_order_url}"
        print(url)
        response = requests.get(url, params=params)
        return APIStandardResponse.from_cancel_order(response=response, status_code=response.status_code, order_id=str(orderId))

    def user_balances(self, user_id: str = "") -> APIUserBalances:
        """
        Retrieve the balances of a user account.

        :param user_id: (Optional) The unique identifier of the user.
                        If not provided, the balances for the current API key are retrieved.
        :return: #  TO DO
        """

        params = {
            "apiKeyID": self.apiKey,
            "apiKeyPassword": self.apiSecret,
            "outputType": "json"
        }

        if user_id != "":
            params["userId"] = user_id

        url = f"{self.base_url}{user_balances_url}"
        response = requests.get(url, params=params)
        content = json.loads(response.content.decode('utf-8'))
        return APIUserBalances.from_user_balance(data=content)

def login_zag(user:str, password:str):
    data = {
        "user_name": user,
        "password": password,
        "non_enc": "1",
        "outputType": "json"
    }
    url = f"{test_url}{login_url}"
    session = requests.Session()
    response = session.post(url, data=data)
    content = json.loads(response.content.decode('utf-8'))
    standard_response = {'code': content['code']}
    code = content.get('code', None)
    if code is not None:
        if code == 'R200':
            standard_response['PHPSESSID'] = session.cookies.get("PHPSESSID")
            standard_response['message'] = "Login successful!"
            standard_response['main_account_id'] = content['data']['user_id']
            DBCore().insert("registering_access", {'user': user, 'date': datetime.datetime.now()})
        else:
            standard_response['message'] = content['errors']
    return standard_response



def create_user_sub_account_zag(user:str, password:str, quantity: int, strategy: int, main_account_id: str):

    # # LOGIN
    # data = {
    #     "user_name": user,
    #     "password": password,
    #     "non_enc": "1",
    #     "outputType": "json"
    # }
    # url = f"{test_url}{login_url}"
    # session = requests.Session()
    # response = session.post(url, data=data)
    # content = json.loads(response.content.decode('utf-8'))
    # code = content.get('code', None)
    # if code is not None:
    #     if code == 'R200':
    #         main_account_id = content['data']['user_id']
    #     else:
    #         print(f"Response create sub account: {content}")
    #         return content['errors']
    # else:
    #     print(f"Response create sub account: {content}")
    #     raise Exception("Unable to contact ZAG")

    zag_client = ZagApiClient(
        base_url="https://demo.zen-q.com",
        auth_token="Pqo{Year}6hfTP50{Month}]1zJ{Day}",
        api_key="8b940be7fb78aaa6b6567dd7a3987996947460df1c668e698eb92ca77e425349",
    )

    # response = zag_client.delete_sub_account(main_account_id=main_account_id, sub_account_id=1000470)
    main_account_id = int(main_account_id)

    # CREAZIONE SUB ACCOUNT
    if strategy == 1:
        zag_response = zag_client.create_sub_account(main_account_id, f"Light CopyTrading")
    elif strategy == 2:
        zag_response = zag_client.create_sub_account(main_account_id, f"Investor CopyTrading")
    elif strategy == 3:
        zag_response = zag_client.create_sub_account(main_account_id, f"BTC Trend Catcher CopyTrading")
    else:
        zag_response = zag_client.create_sub_account(main_account_id, f"XRP Trend Catcher CopyTrading")

    standard_response = {}

    if zag_response.get("code", None) != "R200":
        print(f"{zag_response} - main: {main_account_id}")
        raise BaseException(f"Unable to create account on ZAG - {zag_response}")
    else:
        data = zag_response.get("data", {})
        sub_account_id = data.get("newUserId", 0)
        sub_account_name = data.get("newUsername", "")
        standard_response['sub_account_id'] = sub_account_id
        standard_response['sub_account_name'] = sub_account_name
        standard_response['main_account_id'] = main_account_id


    # # GENERAZIONE API KEY
    # caratteri = string.hexdigits.lower()[:16]  # solo i caratteri esadecimali (0-9, a-f)
    # key = ''.join(random.choice(caratteri) for _ in range(32))
    # confusion_key_start = ''.join(random.choice(caratteri) for _ in range(10))
    # confusion_key_end = ''.join(random.choice(caratteri) for _ in range(4))
    # confusion_key_secret_start = ''.join(random.choice(caratteri) for _ in range(6))
    # confusion_key_secret_end = ''.join(random.choice(caratteri) for _ in range(8))
    #
    # data = {"api_key_password": key,
    #     "api_key_alias": "CopyTradingAPI",
    #     "expiry_date_time": "2026-12-31T23:59:59",
    #     "enabled": "1",
    #     "place_orders": "1",
    #     "balances_positions": "1",
    #     "ip_addresses": "*"
    # }
    # headers = {
    #     "PHPSESSID": token
    # }
    # url = f"{test_url}{create_api_url}"
    # response = session.post(url, data=data, headers=headers)
    # content = json.loads(response.content.decode('utf-8'))
    # standard_response = {'code': content['code']}
    # code = content.get('code', None)
    # if code is not None:
    #     if code == 'R200':
    #         standard_response['message'] = "Creation successful!"
    #         standard_response['id'] = content['data']['id']
    #         standard_response['api_key_id'] = f"{confusion_key_start}{content['data']['api_key_id']}{confusion_key_end}"
    #         standard_response['api_key_password'] =  f"{confusion_key_secret_start}{key}{confusion_key_secret_end}"
    #         standard_response['api_key_alias'] = content['data']['api_key_alias']
    #         standard_response['expiry_date_time'] = content['data']['expiry_date_time']
    #         standard_response['sub_account_id'] = "sub_account_id"
    #         standard_response['sub_account_name'] = "sub_account_name"
    #         standard_response['token'] = token
    #         standard_response['main_account_id'] = main_account_id
    #     else:
    #         standard_response['message'] = ""
    # else:
    #     standard_response['message'] = "Unable to ping ZAG"
    return standard_response


def increase_user_account_balances_zag(user:str, password:str, quantity: int, sub_account_id:int):

    # LOGIN
    # data = {
    #     "user_name": user,
    #     "password": password,
    #     "non_enc": "1",
    #     "outputType": "json"
    # }
    # url = f"{test_url}{login_url}"
    # session = requests.Session()
    # response = session.post(url, data=data)
    # content = json.loads(response.content.decode('utf-8'))
    # code = content.get('code', None)
    # if code is not None:
    #     if code == 'R200':
    #         main_account_id = content['data']['user_id']
    #     else:
    #         return content['errors']
    # else:
    #     raise Exception("Unable to contact ZAG")

    zag_client = ZagApiClient(
        base_url="https://demo.zen-q.com",
        auth_token="Pqo{Year}6hfTP50{Month}]1zJ{Day}",
        api_key="8b940be7fb78aaa6b6567dd7a3987996947460df1c668e698eb92ca77e425349",
    )

     # response = zag_client.delete_sub_account(main_account_id=main_account_id, sub_account_id=1000470)

    if sub_account_id is 0:
        return "Error: Could not find sub account id"

    # RICARICA SUB ACCOUNT
    zag_response_credit = zag_client.add_transaction(
        operation="credit",
        amount=str(quantity),
        force_debit=0,
        reference_code=str(uuid.uuid4()),
        currency_symbol="USDC",
        target_gl_account="300 - Customers Balances",
        user_id=sub_account_id,
        voucher_type="G",
    )

    if zag_response_credit.get("code", None) != "R200":
        print(f"{zag_response_credit} - {sub_account_id}")
        return "Error: Could not add funds to sub account"

    code = zag_response_credit.get('code', None)
    standard_response = {'code': code}

    if code is not None:
        if code == 'R200':
            standard_response['sub_account_id'] = sub_account_id

    # # GENERAZIONE API KEY
    # caratteri = string.hexdigits.lower()[:16]  # solo i caratteri esadecimali (0-9, a-f)
    # key = ''.join(random.choice(caratteri) for _ in range(32))
    # confusion_key_start = ''.join(random.choice(caratteri) for _ in range(10))
    # confusion_key_end = ''.join(random.choice(caratteri) for _ in range(4))
    # confusion_key_secret_start = ''.join(random.choice(caratteri) for _ in range(6))
    # confusion_key_secret_end = ''.join(random.choice(caratteri) for _ in range(8))
    #
    # data = {"api_key_password": key,
    #     "api_key_alias": "CopyTradingAPI",
    #     "expiry_date_time": "2026-12-31T23:59:59",
    #     "enabled": "1",
    #     "place_orders": "1",
    #     "balances_positions": "1",
    #     "ip_addresses": "*"
    # }
    # headers = {
    #     "PHPSESSID": token
    # }
    # url = f"{test_url}{create_api_url}"
    # response = session.post(url, data=data, headers=headers)
    # content = json.loads(response.content.decode('utf-8'))
    # standard_response = {'code': content['code']}
    # code = content.get('code', None)
    # if code is not None:
    #     if code == 'R200':
    #         standard_response['message'] = "Creation successful!"
    #         standard_response['id'] = content['data']['id']
    #         standard_response['api_key_id'] = f"{confusion_key_start}{content['data']['api_key_id']}{confusion_key_end}"
    #         standard_response['api_key_password'] =  f"{confusion_key_secret_start}{key}{confusion_key_secret_end}"
    #         standard_response['api_key_alias'] = content['data']['api_key_alias']
    #         standard_response['expiry_date_time'] = content['data']['expiry_date_time']
    #         standard_response['sub_account_id'] = "sub_account_id"
    #         standard_response['sub_account_name'] = "sub_account_name"
    #         standard_response['token'] = token
    #         standard_response['main_account_id'] = main_account_id
    #     else:
    #         standard_response['message'] = ""
    # else:
    #     standard_response['message'] = "Unable to ping ZAG"
    return standard_response

def get_balances_of_sub_account_zag(user_id):

    # # LOGIN
    # data = {
    #     "user_name": user,
    #     "password": password,
    #     "non_enc": "1",
    #     "outputType": "json"
    # }
    # url = f"{test_url}{login_url}"
    # session = requests.Session()
    # response = session.post(url, data=data)
    # content = json.loads(response.content.decode('utf-8'))
    # code = content.get('code', None)
    # if code is not None:
    #     if code == 'R200':
    #         token = session.cookies.get("PHPSESSID")
    #         main_account_id = int(content['data']['user_id'])
    #     else:
    #         return content['errors']
    # else:
    #     raise Exception("Unable to contact ZAG")

    zag_client = ZagApiClient(
        base_url="https://demo.zen-q.com",
        auth_token="Pqo{Year}6hfTP50{Month}]1zJ{Day}",
        api_key="8b940be7fb78aaa6b6567dd7a3987996947460df1c668e698eb92ca77e425349",
    )

    response_zag = zag_client.get_sub_account_balances(user_id=user_id)

    # # /API/SubUsersAPI.php
    # # headers = {
    # #     "PHPSESSID": token
    # # }
    # params = {
    #     # "userId": main_account_id,
    #     "userId": 12000107,
    #     # "token": self.generate_token()
    #     # "outputType": "json"
    # }
    # # url = f"{test_url}/API/SubUsersAPI.php?"
    # url = f"{test_url}/API/Backend/UserBalancesPortfolioAPI3.php?userId={12000107}&access_token=7475f95b01ea038697d2e93b1a8cba4c0662f2378d34407295a2486b00675d4f&apiKey="
    # # url = f"{self.base_url}/API/JSON/UserBalancesPortfolioAPI_json.php?"
    # # https://demo.zen-q.com/API/Backend/UserBalancesPortfolioAPI3.php?userId={12000107}&access_token=7475f95b01ea038697d2e93b1a8cba4c0662f2378d34407295a2486b00675d4f&apiKey=8b940be7fb78aaa6b6567dd7a3987996947460df1c668e698eb92ca77e425349
    #
    # response = zag_client.get(url, params=params)
    # pippo = response.json()
    return response_zag

def reset_user_balance_zag(user_id, quantity: float, symbol: str):

    zag_client = ZagApiClient(
        base_url="https://demo.zen-q.com",
        auth_token="Pqo{Year}6hfTP50{Month}]1zJ{Day}",
        api_key="8b940be7fb78aaa6b6567dd7a3987996947460df1c668e698eb92ca77e425349",
    )

    if quantity > 0:
        amount_to_sell = quantity

        # vendi
        response = zag_client.add_transaction(
            operation="debit",
            amount=str(amount_to_sell),
            force_debit=0,
            reference_code=str(uuid.uuid4()),
            currency_symbol=symbol,
            target_gl_account="300 - Customers Balances",
            user_id=user_id,
            voucher_type="G",
        )

        if response.get("code", None) != "R200":
            return response

        code = response.get('code', None)

        return code
    elif quantity < 0:
        amount_to_sell = quantity

        # compra
        response = zag_client.add_transaction(
            operation="credit",
            amount=str(-amount_to_sell),
            force_debit=0,
            reference_code=str(uuid.uuid4()),
            currency_symbol=symbol,
            target_gl_account="300 - Customers Balances",
            user_id=user_id,
            voucher_type="G",
        )

        if response.get("code", None) != "R200":
            return response

        code = response.get('code', None)

        return code
    else:
        return "R200"
