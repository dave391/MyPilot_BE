import csv
import datetime
import io
import os
import uvicorn
from fastapi import FastAPI, Form, File, UploadFile
from starlette.responses import JSONResponse, Response

from DB.db_core import DBCore
from Utils.logger import configure_log, get_logger
from zenqapi.zenq import login_zag, create_user_sub_account_zag, \
    get_balances_of_sub_account_zag, increase_user_account_balances_zag, reset_user_balance_zag
import pandas as pd

logger = get_logger()
app = FastAPI()
env = str(os.getenv('ENV'))
port = int(os.getenv('PORT', '4000'))
if env == 'SVIL':
    env_svil = True
else:
    env_svil = False

@app.post("/login/")
async def login(user: str = Form(...), password: str = Form(...)):

    try:
        # qui verifico credenziali
        standard_response = login_zag(user=user, password=password)
        # qui vado a vedere se l utente ha mai fatto l accesso
    except BaseException:
        standard_response = {}

    return standard_response


def generate_base_db_record(user: str, password: str, quantity: int, strategy: int):
    try:
        generic_dict = {"_id": user,
                        f'main_account_id_1': "",
                        f'sub_account_id_1': "",
                        f'sub_account_name_1': "",
                        "strategia_1_subscribed": False,
                        "strategia_1_capital": 0,
                        "strategia_1_proportional": 0,
                        "strategia_1_subscribed_date": "date",
                        "strategia_1_stop_loss": 0,
                        "strategia_1_take_profit": 0,
                        f'main_account_id_2': "",
                        f'sub_account_id_2': "",
                        f'sub_account_name_2': "",
                        "strategia_2_subscribed": False,
                        "strategia_2_capital": 0,
                        "strategia_2_proportional": 0,
                        "strategia_2_subscribed_date": "date",
                        "strategia_2_stop_loss": 0,
                        "strategia_2_take_profit": 0,
                        f'main_account_id_3': "",
                        f'sub_account_id_3': "",
                        f'sub_account_name_3': "",
                        "strategia_3_subscribed": False,
                        "strategia_3_capital": 0,
                        "strategia_3_proportional": 0,
                        "strategia_3_subscribed_date": "date",
                        "strategia_3_stop_loss": 0,
                        "strategia_3_take_profit": 0,
                        f'main_account_id_4': "",
                        f'sub_account_id_4': "",
                        f'sub_account_name_4': "",
                        "strategia_4_subscribed": False,
                        "strategia_4_capital": 0,
                        "strategia_4_proportional": 0,
                        "strategia_4_subscribed_date": "date",
                        "strategia_4_stop_loss": 0,
                        "strategia_4_take_profit": 0,
                        }

        DBCore().insert(collection="utenti", generic_dict=generic_dict)

    except BaseException:
        raise Exception

    return


def create_user_sub_account(user:str, password: str, quantity:int, strategy: int, main_account_id: str):

    try:

        standard_response = create_user_sub_account_zag(user=user, password=password, quantity=quantity, strategy=strategy, main_account_id=main_account_id)
        logger.info(f"La standard response è: {standard_response}")
        return standard_response

    except BaseException:
        standard_response = {}

    return standard_response

def increase_user_account_balances(user:str, password: str, quantity:int, sub_account_id: int):

    try:

        standard_response = increase_user_account_balances_zag(user=user, password=password, quantity=quantity, sub_account_id=sub_account_id)

        return standard_response

    except BaseException:
        standard_response = {}

    return standard_response


def get_sub_account_id(user: str):
    response = DBCore().read_user(collection="utenti_chiavi", user=user)
    main_account_id = response['main_account_id'] # oppure main_account_id
    sub_account_id = response['sub_account_id'] # oppure main_account_id
    return main_account_id, sub_account_id

    # if verify_token(user=user, token=token):
    #     response = DBCore().read_user(collection="utenti_chiavi", user=user)
    #     # api_key = response['api_key_id'][10:-4]
    #     # api_password = response['api_key_password'][6:-8] # cancella primi 4 e ultimi 5
    #     # return api_key, api_password, user_id
    #     user_id = response['sub_account_id'] # oppure main_account_id
    #     return user_id
    # else:
    #     return "", "", ""

@app.get("/start/{user}/{qty_user}/{strategy}/{take_profit}/{stop_loss}/{password}/")
async def start(user: str, qty_user: int, strategy: int, take_profit: float, stop_loss: float, password: str):

    if password=="notUsed":

        user_exist = DBCore().read_user(collection="utenti", user=user)
        if not user_exist:
            # Se non sono mai state create le creo la prima volta
            generate_base_db_record(user=user, password=password, quantity=qty_user, strategy=strategy)

        # a questo punto lo user esiste e vado a sistemare il record sul db
        binance_wallet = DBCore().get_binance_wallet(strategy=strategy)['wallet']

        proportional_value = qty_user / binance_wallet

        user_info = DBCore().read_user(collection="utenti", user=user)
        if user_info[f'sub_account_id_{strategy}'] != "":
            # condizzione in cui è gia partito una volta
            sub_account_id = user_info[f'sub_account_id_{strategy}']
            standard_response = increase_user_account_balances(user=user, password=password, quantity=qty_user, sub_account_id=sub_account_id)
            update_info = {f"strategia_{strategy}_subscribed": True,
                           f"strategia_{strategy}_capital": qty_user,
                           f"strategia_{strategy}_proportional": proportional_value,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": stop_loss,
                           f"strategia_{strategy}_take_profit": take_profit,
                           f'sub_account_id_{strategy}': standard_response['sub_account_id'],
                           }

        else:
            standard_response = create_user_sub_account(user=user, password=password, quantity=qty_user, strategy=strategy)

            update_info = {f"strategia_{strategy}_subscribed": False,
                           f"strategia_{strategy}_capital": 0,
                           f"strategia_{strategy}_proportional": 0,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": 0,
                           f"strategia_{strategy}_take_profit": 0,
                           f'main_account_id_{strategy}': standard_response['main_account_id'],
                           f'sub_account_id_{strategy}': standard_response['sub_account_id'],
                           f'sub_account_name_{strategy}': standard_response['sub_account_name']
                           }
            DBCore().update_user_strategy_info(generic_dict=update_info, user=user)

            sub_account_id = standard_response['sub_account_id']
            standard_response_2 = increase_user_account_balances(user=user, password=password, quantity=qty_user,
                                                               sub_account_id=sub_account_id)
            update_info = {f"strategia_{strategy}_subscribed": True,
                           f"strategia_{strategy}_capital": qty_user,
                           f"strategia_{strategy}_proportional": proportional_value,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": stop_loss,
                           f"strategia_{strategy}_take_profit": take_profit,
                           f'main_account_id_{strategy}': standard_response['main_account_id'],
                           f'sub_account_id_{strategy}': standard_response_2['sub_account_id'],
                           }
        DBCore().update_user_strategy_info(generic_dict=update_info, user=user)

        return "ok"

@app.get("/start_sso/{user}/{qty_user}/{strategy}/{take_profit}/{stop_loss}/{password}/{main_account_id}")
async def start_sso(user: str, qty_user: int, strategy: int, take_profit: float, stop_loss: float, password: str, main_account_id: str):

    if password=="notUsed":

        user_exist = DBCore().read_user(collection="utenti", user=user)
        if not user_exist:
            # Se non sono mai state create le creo la prima volta
            generate_base_db_record(user=user, password=password, quantity=qty_user, strategy=strategy)

        # a questo punto lo user esiste e vado a sistemare il record sul db
        binance_wallet = DBCore().get_binance_wallet(strategy=strategy)['wallet']

        proportional_value = qty_user / binance_wallet

        user_info = DBCore().read_user(collection="utenti", user=user)
        if user_info[f'sub_account_id_{strategy}'] != "":
            # condizzione in cui è gia partito una volta
            sub_account_id = user_info[f'sub_account_id_{strategy}']
            standard_response = increase_user_account_balances(user=user, password=password, quantity=qty_user, sub_account_id=sub_account_id)
            update_info = {f"strategia_{strategy}_subscribed": True,
                           f"strategia_{strategy}_capital": qty_user,
                           f"strategia_{strategy}_proportional": proportional_value,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": stop_loss,
                           f"strategia_{strategy}_take_profit": take_profit,
                           f'sub_account_id_{strategy}': standard_response['sub_account_id'],
                           }

        else:
            standard_response = create_user_sub_account(user=user, password=password, quantity=qty_user, strategy=strategy, main_account_id=main_account_id)

            update_info = {f"strategia_{strategy}_subscribed": False,
                           f"strategia_{strategy}_capital": 0,
                           f"strategia_{strategy}_proportional": 0,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": 0,
                           f"strategia_{strategy}_take_profit": 0,
                           f'main_account_id_{strategy}': standard_response['main_account_id'],
                           f'sub_account_id_{strategy}': standard_response['sub_account_id'],
                           f'sub_account_name_{strategy}': standard_response['sub_account_name']
                           }
            DBCore().update_user_strategy_info(generic_dict=update_info, user=user)

            sub_account_id = standard_response['sub_account_id']
            standard_response_2 = increase_user_account_balances(user=user, password=password, quantity=qty_user,
                                                               sub_account_id=sub_account_id)
            update_info = {f"strategia_{strategy}_subscribed": True,
                           f"strategia_{strategy}_capital": qty_user,
                           f"strategia_{strategy}_proportional": proportional_value,
                           f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                           f"strategia_{strategy}_stop_loss": stop_loss,
                           f"strategia_{strategy}_take_profit": take_profit,
                           f'main_account_id_{strategy}': standard_response['main_account_id'],
                           f'sub_account_id_{strategy}': standard_response_2['sub_account_id'],
                           }
        DBCore().update_user_strategy_info(generic_dict=update_info, user=user)

        return "ok"


@app.get("/stop/{user}/{strategy}")
async def stop(user: str, strategy: int):

    user_data = DBCore().read_user(user=user, collection="utenti")
    if user_data:
        if user_data[f'main_account_id_{strategy}'] != "":
            user_balances = get_balances_of_sub_account_zag(user_data[f'sub_account_id_{strategy}'])
            data = user_balances.get("data", [])
            if data:
                try:
                    for item in data['Balances']:
                        symbol = item['currencySymbol']
                        quantity = item['availableForTrading']
                        if symbol != "EUR":
                            response = reset_user_balance_zag(user_id=user_data[f'sub_account_id_{strategy}'], quantity=float(quantity),
                                                              symbol=symbol)
                            if response != "R200":
                                raise BaseException(response)
                    reset_user_db_data(user=user, strategy=strategy)
                except BaseException as e:
                    logger.error(e)

    return "ok"



@app.get("/get_performance_graph/{strategy}")
def get_performance_data(strategy: str):
    data = DBCore().get_startegy_data(strategy)
    return data

@app.get("/get_performance_number")
def get_performance_data():
    data = DBCore().get_startegy_performance()
    # clenaning data
    data['_id'] = ""
    return data

@app.post("/update_performance_data_preview")
async def get_performance_data(file: UploadFile = File(...)):
    file_content = await file.read()
    file_stream = io.BytesIO(file_content)

    df_dict = {}

    # Lettura dei dati dalle colonne specificate
    df = pd.DataFrame(pd.read_excel(file_stream))
    df = df.iloc[1:].reset_index(drop=True)

    def extract_and_format(df, col1, col2):
        temp_df = df.iloc[:, [col1, col2]].dropna()
        temp_df.columns = ["time", "quoteQty"]
        temp_df = temp_df.sort_values(by="time", ascending=True)
        temp_df["time"] = pd.to_datetime(temp_df["time"], errors='coerce').dt.strftime('%d/%m/%Y')
        temp_df["quoteQty"] = temp_df["quoteQty"].astype(float)
        temp_df["order"] = range(1, len(temp_df) + 1)  # Aggiunge la colonna order incrementale
        return temp_df

    # Creazione dei dataframe
    df_dict['df_light'] = extract_and_format(df, 0, 1)
    df_dict['df_investor'] = extract_and_format(df, 0, 2)
    df_dict['df_btc'] = extract_and_format(df, 10, 11)
    df_dict['df_xrp'] = extract_and_format(df, 5, 6)

    df_extra = pd.read_excel(file_stream, usecols="Q:U", dtype=str)
    df_extra = df_extra.dropna(how="all")  # Rimuove righe vuote

    extra_data = {}
    id_counter = 1
    for i in range(0, len(df_extra), 2):
        if i + 1 < len(df_extra):
            name = df_extra.iloc[i, 0]
            key_row = df_extra.iloc[i].tolist()[1:]
            value_row = df_extra.iloc[i + 1].tolist()[1:]

            formatted_values = {}
            for key, v in zip(key_row, value_row):
                if key == "Days":
                    formatted_values[key] = v  # Mantiene i giorni invariati
                else:
                    try:
                        num = float(v) * 100  # Converti il numero e moltiplica per 100
                        formatted_values[key] = f"{num:.2f}%".replace('.',
                                                                      ',')  # Formatta e sostituisci il punto con la virgola
                    except ValueError:
                        formatted_values[key] = v  # Se non è un numero, lascia invariato

            formatted_values["name"] = name
            extra_data[f'{id_counter}'] = formatted_values
            id_counter += 1


@app.get("/get_active/{user}/{strategy}")
def get_active_user(user: str, strategy: int):
    data = DBCore().read_a_subscribed_user_to_strategy(user=user, strategy_id=strategy)
    if data:
        if data[f'strategia_{strategy}_subscribed'] == True:
            return JSONResponse(status_code=200, content="")
        else:
            return JSONResponse(status_code=201, content="")
    else:
        return JSONResponse(status_code=201, content="")

@app.get("/get_active/{user}")
def get_active_user_algos(user: str):
    data = DBCore().read_algos_subscribed_user(user=user)
    if data:
        return sum(1 for key, value in data.items() if isinstance(value, bool) and value)
    else:
        return 0

@app.get("/get_user_data/{user}")
def get_user_data(user: str):

    user_data = DBCore().read_user(user=user, collection="utenti")
    if user_data:
        total_balances=0.0
        strategia_1_capital_invested = 0
        strategia_2_capital_invested = 0
        strategia_3_capital_invested = 0
        strategia_4_capital_invested = 0
        usd_sub_account_1 = 0
        usd_sub_account_2 = 0
        usd_sub_account_3 = 0
        usd_sub_account_4 = 0


        if user_data['main_account_id_1'] != "":
            user_balances_1 = get_balances_of_sub_account_zag(user_data['sub_account_id_1'])
            usd_sub_account_1 = float(user_balances_1['data']['Equity'][0]['EquityValue']) * 1.08 # TODO prendere valore usd da altre parti
            strategia_1_capital_invested = user_data['strategia_1_capital']
            total_balances = total_balances + usd_sub_account_1

        if user_data['main_account_id_2'] != "":
            user_balances_2 = get_balances_of_sub_account_zag(user_data['sub_account_id_2'])
            usd_sub_account_2 = float(user_balances_2['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_2_capital_invested = user_data['strategia_2_capital']
            total_balances = total_balances + usd_sub_account_2

        if user_data['main_account_id_3'] != "":
            user_balances_3 = get_balances_of_sub_account_zag(user_data['sub_account_id_3'])
            usd_sub_account_3 = float(user_balances_3['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_3_capital_invested = user_data['strategia_3_capital']
            total_balances = total_balances + usd_sub_account_3

        if user_data['main_account_id_4'] != "":
            user_balances_4 = get_balances_of_sub_account_zag(user_data['sub_account_id_4'])
            usd_sub_account_4 = float(user_balances_4['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_4_capital_invested = user_data['strategia_4_capital']
            total_balances = total_balances + usd_sub_account_4

        somma_allocazioni = strategia_1_capital_invested + strategia_2_capital_invested + strategia_3_capital_invested + strategia_4_capital_invested

        pnl = total_balances - somma_allocazioni

        user_total_balances = {'total_capital': 0 if total_balances <= 0 else total_balances,
                               'invested_capital':somma_allocazioni,
                               'pnl': 0 if (-3.0 <  pnl < 0) else pnl,
                               'roi':  0 if somma_allocazioni == 0 else ( 0 if (-3.0 <  (pnl / somma_allocazioni)*100 < 0) else (pnl / somma_allocazioni)*100 ) ,
                               'light_capital_invested': strategia_1_capital_invested,
                               'light_capital': 0 if usd_sub_account_1 <= 0 else usd_sub_account_1,
                               'light_capital_pnl': 0 if (-3.0 <  (usd_sub_account_1-strategia_1_capital_invested) < 0) else (usd_sub_account_1-strategia_1_capital_invested),
                               'light_capital_roi': 0 if strategia_1_capital_invested == 0 else ( 0 if (-0.3 <  ((usd_sub_account_1-strategia_1_capital_invested) / strategia_1_capital_invested)*100 < 0) else ((usd_sub_account_1-strategia_1_capital_invested) / strategia_1_capital_invested)*100 ),

                               'investor_capital_invested': strategia_2_capital_invested,
                               'investor_capital': 0 if usd_sub_account_2 <= 0 else usd_sub_account_2,
                               'investor_capital_pnl': 0 if (-3.0 <  (usd_sub_account_2-strategia_2_capital_invested) < 0) else (usd_sub_account_2-strategia_2_capital_invested),
                               'investor_capital_roi': 0 if strategia_2_capital_invested == 0 else ( 0 if (-0.3 <  ((usd_sub_account_2-strategia_2_capital_invested) / strategia_2_capital_invested)*100 < 0) else ((usd_sub_account_2-strategia_2_capital_invested) / strategia_2_capital_invested)*100 ),

                               'btc_capital_invested': strategia_3_capital_invested,
                               'btc_capital': 0 if usd_sub_account_3 <= 0 else usd_sub_account_3,
                               'btc_capital_pnl': 0 if (-3.0 <  (usd_sub_account_3-strategia_3_capital_invested) < 0) else (usd_sub_account_3-strategia_3_capital_invested),
                               'btc_capital_roi': 0 if strategia_3_capital_invested == 0 else ( 0 if (-0.3 <  ((usd_sub_account_3-strategia_3_capital_invested) / strategia_3_capital_invested)*100 < 0) else ((usd_sub_account_3-strategia_3_capital_invested) / strategia_3_capital_invested)*100 ),

                               'xrp_capital_invested': strategia_4_capital_invested,
                               'xrp_capital': 0 if usd_sub_account_4 <= 0 else usd_sub_account_4,
                               'xrp_capital_pnl': 0 if (-3.0 <  (usd_sub_account_4-strategia_4_capital_invested) < 0) else (usd_sub_account_4-strategia_4_capital_invested),
                               'xrp_capital_roi': 0 if strategia_4_capital_invested == 0 else ( 0 if (-0.3 <  ((usd_sub_account_4-strategia_4_capital_invested) / strategia_4_capital_invested)*100 < 0) else ((usd_sub_account_4-strategia_4_capital_invested) / strategia_4_capital_invested)*100 ),

            'pie_chart':[{"name": "Light", "value": 0 if total_balances == 0 else round((usd_sub_account_1 / total_balances)*100, 2), "fill": "var(--blue-8)"},
                        {"name": "Investor", "value": 0 if total_balances == 0 else round((usd_sub_account_2 / total_balances)*100, 2), "fill": "var(--purple-8)"},
                        {"name": "BTC Trend Catcher", "value": 0 if total_balances == 0 else round((usd_sub_account_3 / total_balances)*100, 2), "fill": "var(--orange-8)"},
                        {"name": "XRP Trend Catcher", "value": 0 if total_balances == 0 else round((usd_sub_account_4 / total_balances)*100, 2), "fill": "var(--yellow-8)"}],
                               }
        return user_total_balances
    else:
        user_total_balances = {'total_capital': 0,
                               'invested_capital': 0,
                               'pnl': 0,
                               'roi': 0,
                               'pie_chart': [{"name": "No algo active", "value": 100,
                                              "fill": "var(--blue-8)"}],
                               'light_capital_invested': 0,
                               'light_capital': 0,
                               'light_capital_pnl': 0,
                               'light_capital_roi': 0,
                               'investor_capital_invested': 0,
                               'investor_capital': 0,
                               'investor_capital_pnl': 0,
                               'investor_capital_roi': 0,
                               'btc_capital_invested': 0,
                               'btc_capital': 0,
                               'btc_capital_pnl': 0,
                               'btc_capital_roi': 0,
                               'xrp_capital_invested': 0,
                               'xrp_capital': 0,
                               'xrp_capital_pnl': 0,
                               'xrp_capital_roi': 0,
                               }

        return user_total_balances

# @app.get("/get_user_stats/{user}")
def get_user_stats(user: any):
    """
    :param user: l'id dell utente che nel nostro caso è la mail oppure il dizionario del record di mongo della col utenti
    :return: dizionario con tutte le info sulle strategie sottoscritte.
    """
    if isinstance(user, str):
        user_data = DBCore().read_user(user=user, collection="utenti")
    else:
        user_data = user
    logger.info(f"user: {user_data['_id']}")
    if user_data:
        main_account_id = 0
        account_id = user_data['_id']

        if user_data['main_account_id_1'] != "" and isinstance(user_data['main_account_id_1'], int):
            user_balances_1 = get_balances_of_sub_account_zag(user_data['sub_account_id_1'])
            strategia_1_end_capital = float(user_balances_1['data']['Equity'][0]['EquityValue']) * 1.08 # TODO prendere valore usd da altre parti
            strategia_1_end_date = datetime.datetime.now()
            strategia_1_start_capital = user_data['strategia_1_capital']
            strategia_1_start_date = user_data['strategia_1_subscribed_date']
            sub_account_id_1 = user_data['sub_account_id_1']
            main_account_id = user_data['main_account_id_1']
            account_id = user_data['_id']
        else:
            strategia_1_end_capital = 0
            strategia_1_end_date = 0
            strategia_1_start_capital = 0
            strategia_1_start_date = 0
            sub_account_id_1 = 0

        if user_data['main_account_id_2'] != "" and isinstance(user_data['main_account_id_2'], int):
            user_balances_2 = get_balances_of_sub_account_zag(user_data['sub_account_id_2'])
            strategia_2_end_capital = float(
                user_balances_2['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_2_end_date = datetime.datetime.now()
            strategia_2_start_capital = user_data['strategia_2_capital']
            strategia_2_start_date = user_data['strategia_2_subscribed_date']
            sub_account_id_2 = user_data['sub_account_id_2']
            main_account_id = user_data['main_account_id_2']
            account_id = user_data['_id']
        else:
            strategia_2_end_capital = 0
            strategia_2_end_date = 0
            strategia_2_start_capital = 0
            strategia_2_start_date = 0
            sub_account_id_2 = 0

        if user_data['main_account_id_3'] != "" and isinstance(user_data['main_account_id_3'], int):
            user_balances_3 = get_balances_of_sub_account_zag(user_data['sub_account_id_3'])
            strategia_3_end_capital = float(
                user_balances_3['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_3_end_date = datetime.datetime.now()
            strategia_3_start_capital = user_data['strategia_3_capital']
            strategia_3_start_date = user_data['strategia_3_subscribed_date']
            sub_account_id_3 = user_data['sub_account_id_3']
            main_account_id = user_data['main_account_id_3']
            account_id = user_data['_id']
        else:
            strategia_3_end_capital = 0
            strategia_3_end_date = 0
            strategia_3_start_capital = 0
            strategia_3_start_date = 0
            sub_account_id_3 = 0

        if user_data['main_account_id_4'] != "" and isinstance(user_data['main_account_id_4'], int):
            user_balances_4 = get_balances_of_sub_account_zag(user_data['sub_account_id_4'])
            strategia_4_end_capital = float(
                user_balances_4['data']['Equity'][0]['EquityValue']) * 1.08  # TODO prendere valore usd da altre parti
            strategia_4_end_date = datetime.datetime.now()
            strategia_4_start_capital = user_data['strategia_4_capital']
            strategia_4_start_date = user_data['strategia_4_subscribed_date']
            sub_account_id_4 = user_data['sub_account_id_4']
            main_account_id = user_data['main_account_id_4']
            account_id = user_data['_id']
        else:
            strategia_4_end_capital = 0
            strategia_4_end_date = 0
            strategia_4_start_capital = 0
            strategia_4_start_date = 0
            sub_account_id_4 = 0

        return {
            "account": account_id,
            "main_account": main_account_id,

            "light_sub_account": sub_account_id_1,
            "light_start_date": strategia_1_start_date,
            "light_start_capital": strategia_1_start_capital,
            "light_end_capital": strategia_1_end_capital,
            "light_end_date": strategia_1_end_date,

            "investor_sub_account": sub_account_id_2,
            "investor_start_date": strategia_2_start_date,
            "investor_start_capital": strategia_2_start_capital,
            "investor_end_capital": strategia_2_end_capital,
            "investor_end_date": strategia_2_end_date,

            "btc_sub_account": sub_account_id_3,
            "btc_start_date": strategia_3_start_date,
            "btc_start_capital": strategia_3_start_capital,
            "btc_end_capital": strategia_3_end_capital,
            "btc_end_date": strategia_3_end_date,

            "xrp_sub_account": sub_account_id_4,
            "xrp_start_date": strategia_4_start_date,
            "xrp_start_capital": strategia_4_start_capital,
            "xrp_end_capital": strategia_4_end_capital,
            "xrp_end_date": strategia_4_end_date,
        }


@app.get("/get_all_users_stats")
def get_all_users_stats():
    users = DBCore().read_all_user()

    logger.info("start")
    all_users_data = [get_user_stats(user) for user in users]

    output = io.StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=all_users_data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(all_users_data)

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=users_stats.csv"
    response.headers["Content-Type"] = "text/csv"
    # file_path = "users_stats.csv"
    # with open(file_path, mode="w", newline="", encoding="utf-8") as file:
    #     csv_writer = csv.DictWriter(file, fieldnames=all_users_data[0].keys(), delimiter=";")
    #     csv_writer.writeheader()
    #     csv_writer.writerows(all_users_data)
    logger.info("Fine")
    return response

def reset_user_db_data(user, strategy):
    update_info = {f"strategia_{strategy}_subscribed": False,
                   f"strategia_{strategy}_capital": 0,
                   f"strategia_{strategy}_proportional": 0,
                   f"strategia_{strategy}_subscribed_date": datetime.datetime.now(),
                   f"strategia_{strategy}_stop_loss": 0,
                   f"strategia_{strategy}_take_profit": 0,
                   }

    DBCore().update_user_strategy_info(generic_dict=update_info, user=user)

@app.get("/reset_user_data/{user}")
def reset_user_data(user: str):

    user_data = DBCore().read_user(user=user, collection="utenti")
    if user_data:

        if user_data['main_account_id_1'] != "":
            user_balances_1 = get_balances_of_sub_account_zag(user_data['sub_account_id_1'])
            data = user_balances_1.get("data", [])
            if data:
                for item in data['Balances']:
                    symbol = item['currencySymbol']
                    quantity = item['availableForTrading']
                    if symbol != "EUR":
                        if quantity == "0.00":
                            quantity_computed = float(item['actualCostDefaultCurrency']) * float(item['AVGCost_DefaultCurrency'])
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_1'], quantity=quantity_computed, symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_1']}, {quantity_computed}, {symbol}, {response}")

                        else:
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_1'], quantity=float(quantity), symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_1']}, {quantity}, {symbol}, {response}")
                reset_user_db_data(user=user, strategy=1)


        if user_data['main_account_id_2'] != "":
            user_balances_2 = get_balances_of_sub_account_zag(user_data['sub_account_id_2'])
            data = user_balances_2.get("data", [])
            if data:
                for item in data['Balances']:
                    symbol = item['currencySymbol']
                    quantity = item['availableForTrading']
                    if symbol != "EUR":
                        if quantity == "0.00":
                            quantity_computed = float(item['actualCostDefaultCurrency']) * float(
                                item['AVGCost_DefaultCurrency'])
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_2'],
                                                              quantity=quantity_computed, symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_2']}, {quantity_computed}, {symbol}, {response}")

                        else:
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_2'],
                                                              quantity=float(quantity), symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_2']}, {quantity}, {symbol}, {response}")
                reset_user_db_data(user=user, strategy=2)

        if user_data['main_account_id_3'] != "":
            user_balances_3 = get_balances_of_sub_account_zag(user_data['sub_account_id_3'])
            data = user_balances_3.get("data", [])
            if data:
                for item in data['Balances']:
                    symbol = item['currencySymbol']
                    quantity = item['availableForTrading']
                    if symbol != "EUR":
                        if quantity == "0.00":
                            quantity_computed = float(item['actualCostDefaultCurrency']) * float(
                                item['AVGCost_DefaultCurrency'])
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_3'],
                                                              quantity=quantity_computed, symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_3']}, {quantity_computed}, {symbol}, {response}")

                        else:
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_3'],
                                                              quantity=float(quantity), symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_3']}, {quantity}, {symbol}, {response}")
                reset_user_db_data(user=user, strategy=3)

        if user_data['main_account_id_4'] != "":
            user_balances_4 = get_balances_of_sub_account_zag(user_data['sub_account_id_4'])
            data = user_balances_4.get("data", [])
            if data:
                for item in data['Balances']:
                    symbol = item['currencySymbol']
                    quantity = item['availableForTrading']
                    if symbol != "EUR":
                        if quantity == "0.00":
                            quantity_computed = float(item['actualCostDefaultCurrency']) * float(
                                item['AVGCost_DefaultCurrency'])
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_4'],
                                                              quantity=quantity_computed, symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_4']}, {quantity_computed}, {symbol}, {response}")

                        else:
                            response = reset_user_balance_zag(user_id=user_data['sub_account_id_4'],
                                                              quantity=float(quantity), symbol=symbol)
                            logger.info(f"{user_data['sub_account_id_4']}, {quantity}, {symbol}, {response}")
                reset_user_db_data(user=user, strategy=4)



if __name__ == "__main__":
    logger = configure_log()

    logger.info("-------------------------------------")
    logger.info("--------INIZIO APPLICAZIONE----------")
    logger.info("-------------------------------------")

    logger.info(f"Enviroment: {env}")
    logger.info(f"Ciabot is running on port: {port}")

    # get_all_users_stats()

    if env_svil:
        uvicorn.run("main:app", host="127.0.0.1", port=port)  # <--- local run
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=port)
