from requests import get
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame
from time import sleep
from io import StringIO
from django.core.management.base import BaseCommand
from stations.models import Station, RegistrationData  
from datetime import datetime
import numpy as np
import pytz

station_data = {}

# Função para encontrar a coluna correspondente
def find_matching_column(df: DataFrame, substring: str):
    matching_columns = [col for col in df.columns if substring.lower() in col.lower()]
    return matching_columns[0] if matching_columns else None

# Função para processar os dados extraídos e encontrar as colunas correspondentes
def process_historical_data(historical_data: DataFrame):
    map_db_data = [
        'DataHora'
        'Bateria',
        'ContAguaSolo100',
        'ContAguaSolo200',
        'ContAguaSolo400',
        'CorrPSol',
        'DirVelVentoMax',
        'dirVento',
        'NivMare',
        'hora',
        'NivRegua',
        'Pluvio',
        'PressaoAtm',
        'RadSolAcum',
        'RadSolGlob',
        'TempAr',
        'TempMax',
        'TempMin',
        'TempInt',
        'TempSolo100',
        'TempSolo200',
        'TempSolo400',
        'UmidInt',
        'UmiRel',
        'VelVento',
        'VelVento10m',
        'VelVentoMax',
    ]

    extracted_data = {item: [] for item in map_db_data}
    for item in map_db_data:
        column_name = find_matching_column(historical_data, item)
        if column_name:
            extracted_data[item] = historical_data[column_name].tolist()

    return extracted_data

def extract_data(url: str):
    response = get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        rows = soup.find_all('tr')
        table_data = []

        for row in rows[2:]: 
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            table_data.append(cols)

        # Converter para DataFrame do pandas
        df_html = pd.DataFrame(table_data, columns=['ID', 'Estação', 'Municipio'])

        for index, row in df_html.iterrows(): #type: ignore
            station_id = int(row['ID'])
            station_name = row['Estação']
            city = row['Municipio']

            station_data[station_id] = {
                'station_name': station_name,
                'city': city
            }

        for station_id in df_html['ID']:
            print(station_id)
            url = f"http://sinda.crn.inpe.br/PCD/SITE/novo/site/tabela.php?id={station_id}"

            print(url)

            response = get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                table_registration = soup.find_all('table', {'align': 'center'}).__str__()
                df_registration = pd.read_html(StringIO(table_registration))[0].fillna(value=np.nan)
                df_registration = df_registration.where(pd.notnull(df_registration), None)
                
                print ("DataFrame Empty: ", df_registration.empty)

                print ('-'*50)
                if not df_registration.empty:
                    
                    proprietario = df_registration.iloc[1, 0]
                    #estacao = df_registration.iloc[1, 1]
                    #municipio = df_registration.iloc[1, 2]
                    uf = df_registration.iloc[1, 3]
                    latitude = df_registration.iloc[1, 4]
                    longitude = df_registration.iloc[1, 5]
                    #altitude = df_registration.iloc[1, 6]

                    Station.objects.update_or_create(
                        station_id=station_id, 
                        station_name=station_data[int(station_id)]['station_name'], 
                        city=station_data[int(station_id)]['city'],
                        owner=proprietario,
                        latitude=latitude,
                        longitude=longitude,
                        uf=uf
                    )
                
                    read_csv_url = f"http://sinda.crn.inpe.br/PCD/SITE/novo/site/dadosCSV.php?id={station_id}"

                    historical_data = pd.read_csv(read_csv_url, sep=',', encoding='utf-8', encoding_errors='ignore')

                    station = Station.objects.get(station_id=station_id)

                    if len(historical_data.columns) > 1 and not historical_data.empty:
                        #extracted_data = process_historical_data(historical_data)

                        historical_data = historical_data.map(lambda x: None if pd.isna(x) else str(x))

                        # Deletar dados antigos
                        RegistrationData.objects.filter(station_id=station).delete()
                        
                        for index, row in historical_data.iterrows(): #type: ignore
                            RegistrationData.objects.create(
                                station_id=station,
                                DataHora_GMT=datetime.strptime(row.get(find_matching_column(historical_data, 'DataHora'), None), "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('GMT')) if row.get(find_matching_column(historical_data, 'DataHora'), None) else None,
                                Bateria_volts=row.get(find_matching_column(historical_data, 'Bateria'), None),
                                ContAguaSolo100_m3=row.get(find_matching_column(historical_data, 'ContAguaSolo100'), None),
                                ContAguaSolo200_m3=row.get(find_matching_column(historical_data, 'ContAguaSolo200'), None),
                                ContAguaSolo400_m3=row.get(find_matching_column(historical_data, 'ContAguaSolo400'), None),
                                CorrPSol_logico=row.get(find_matching_column(historical_data, 'CorrPSol'), None),
                                DirVelVentoMax_oNV=row.get(find_matching_column(historical_data, 'DirVelVentoMax'), None),
                                dirVento_oNV=row.get(find_matching_column(historical_data, 'dirVento'), None),
                                NivMare_m=row.get(find_matching_column(historical_data, 'NivMare'), None),
                                hora=datetime.strptime(row.get(find_matching_column(historical_data, 'hora'), None).split()[-1].strip(), "%H:%M:%S").time() if row.get(find_matching_column(historical_data, 'hora'), None) else None,
                                NivRegua_m=row.get(find_matching_column(historical_data, 'NivRegua'), None),
                                Pluvio_mm=row.get(find_matching_column(historical_data, 'Pluvio'), None),
                                PressaoAtm_mb=row.get(find_matching_column(historical_data, 'PressaoAtm'), None),
                                RadSolAcum_MJm2=row.get(find_matching_column(historical_data, 'RadSolAcum'), None),
                                RadSolGlob_Wm2=row.get(find_matching_column(historical_data, 'RadSolGlob'), None),
                                TempAr_C=row.get(find_matching_column(historical_data, 'TempAr'), None),
                                TempMax_C=row.get(find_matching_column(historical_data, 'TempMax'), None),
                                TempMin_C=row.get(find_matching_column(historical_data, 'TempMin'), None),
                                TempInt_C=row.get(find_matching_column(historical_data, 'TempInt'), None),
                                TempSolo100_C=row.get(find_matching_column(historical_data, 'TempSolo100'), None),
                                TempSolo200_C=row.get(find_matching_column(historical_data, 'TempSolo200'), None),
                                TempSolo400_C=row.get(find_matching_column(historical_data, 'TempSolo400'), None),
                                UmidInt_pct=row.get(find_matching_column(historical_data, 'UmidInt'), None),
                                UmiRel_pct=row.get(find_matching_column(historical_data, 'UmiRel'), None),
                                VelVento_ms=row.get(find_matching_column(historical_data, 'VelVento'), None),
                                VelVento10m_ms=row.get(find_matching_column(historical_data, 'VelVento10m'), None),
                                VelVentoMax_ms=row.get(find_matching_column(historical_data, 'VelVentoMax'), None)
                            )
                        
                    sleep(3)

class Command(BaseCommand):
    help = 'Import data from meteorological stations'

    def handle(self, *args, **kwargs): #type: ignore
        url = 'http://sinda.crn.inpe.br/PCD/SITE/novo/site/cidades.php?uf=RN'
        extract_data(url)
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
