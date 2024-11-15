#!/usr/bin/env python
# coding: utf-8

#######################################################
################# IPS RED MEDICRON ####################
#### Modelo de datos para la Cuenta de Alto Costo #####
#### nicolas.vargas@bii.com.co TEL: 3102715307 ########
#######################################################

### Steps
# 1. Cargue Excel CAC
# 1.1. Validación Estructura CAC.
# 1.2. Compilación.
# 2. Cargue Excel meds.
# 2.1. Compilación.
# 2.2. Clasificación Medicamentos de Interés.
# 3. Data Frame de Salida.

### Inicio
### Paquetes

import pandas as pd
import numpy as np
import os
import sys
import calendar
import re
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime


# 1. Cargue Excel CAC
def clean_names(df):        
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()            # Eliminar espacios al inicio y al final
    df.columns = df.columns.str.lower()            # Convertir a minúsculas
    df.columns = df.columns.str.replace(' ', '_')  # Reemplazar espacios con guiones bajos
    df.columns = df.columns.str.replace(r'\W', '') # Eliminar caracteres no alfanuméricos
    return df

def convertir_fechas(df, columna):
    try:
        df[columna] = pd.to_datetime(df[columna], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        condicion = df[columna].isna()
        df.loc[condicion, columna] = pd.to_datetime(df.loc[condicion, columna], format='%m/%d/%Y %H:%M:%S %p', errors='coerce')
    except Exception as e:
        print(f"Error al convertir las fechas en la columna {columna}: {e}")

def clean_newlines(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).replace(r'\r|\n', ' ', regex=True)
    return df

def convert_decimals(df):
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = df[col].replace(',', '.', regex=True).astype(float)
            except ValueError:
                pass
    return df

def process_excel_files(output_file):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        base_path = os.getcwd()
        
    print(f"Base path: {base_path}")
    
    dfs = []
    
    for filename in os.listdir(base_path):
        if filename.startswith('NEFRO_') and filename.endswith('.xlsx'):
            file_path = os.path.join(base_path, filename)
            df = pd.read_excel(file_path, header=0, engine='openpyxl')
            df = clean_newlines(df)
            df = clean_names(df)
 #          df = df[df['Razon social'].isin(valores_deseados)]
            df['ORIGEN'] = filename
            dfs.append(df)
    
    if dfs:
        full_joined_df = pd.concat(dfs, ignore_index=True)
        full_joined_df.to_csv(output_file, index=False, sep='|', decimal=',', encoding='utf-8')
        print(f"Datos exportados a '{output_file}' correctamente.")
        print(f"El archivo de salida contiene {full_joined_df.shape[0]} filas y {full_joined_df.shape[1]} columnas.")
        return full_joined_df
    else:
        print("No se encontraron archivos Excel para procesar.")
        return None
# Usar la función
output_file = 'resultado_CAC.txt'
df_CAC = process_excel_files(output_file)

# Si necesitas realizar transformaciones adicionales
if df_CAC is not None:
    print(df_CAC.head())
else:
    print("No hay datos disponibles para transformaciones.")
    
# 1.1. Validación Estructura CAC.
# 1.2. Compilación.



df_CAC

# 2. Cargue Excel meds.
# 2.1. Compilación.
# 2.2. Clasificación Medicamentos de Interés.

#Importar Medicamentos
def process_excel_files(output_file):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        base_path = os.getcwd()
        
    print(f"Base path: {base_path}")
    
    dfs = []
    
    for filename in os.listdir(base_path):
        if filename.startswith('MEDS_') and filename.endswith('.xlsx'):
            file_path = os.path.join(base_path, filename)
            df = pd.read_excel(file_path, header=0, engine='openpyxl')
            df = clean_newlines(df)
            df = clean_names(df)
 #          df = df[df['Razon social'].isin(valores_deseados)]
            df['ORIGEN'] = filename
            dfs.append(df)
    
    if dfs:
        full_joined_df = pd.concat(dfs, ignore_index=True)
        full_joined_df.to_csv(output_file, index=False, sep='|', decimal=',', encoding='utf-8')
        print(f"Datos exportados a '{output_file}' correctamente.")
        print(f"El archivo de salida contiene {full_joined_df.shape[0]} filas y {full_joined_df.shape[1]} columnas.")
        return full_joined_df
    else:
        print("No se encontraron archivos Excel para procesar.")
        return None
# Usar la función
output_file = 'resultado_meds.txt'
df_meds = process_excel_files(output_file)

# Si necesitas realizar transformaciones adicionales
if df_meds is not None:
    print(df_meds.head())
else:
    print("No hay datos disponibles para transformaciones.")

# Seleccion de medicamentos de interés:
# segun: https://diabetes.org/es/salud-bienestar/medicamentos/medicamentos-orales-y-otros-inyectables-para-la-diabetes

# Unique todos los medicamentos:
med = pd.DataFrame({
    'medicamento': df_meds['nombre_de_medicamento'].unique()
})
# Convertir la columna 'medicamento' a texto
med['medicamento'] = med['medicamento'].astype(str)

# Asegúrate de que todos los medicamentos estén en minúsculas para evitar problemas de mayúsculas y minúsculas
med['medicamento'] = med['medicamento'].str.upper()  # Convertir a mayúsculas para mayor consistencia

# Definir condiciones para tipo_med y grupo
med['tipo_med'] = np.select(
    [
        # Grupo HTA
        med['medicamento'].str.contains('SARTAN|SARTÁN', case=False, regex=True),
        med['medicamento'].str.contains('DIPINO|DILTIAZEM|VERAPAMILO', case=False, regex=True),
        med['medicamento'].str.contains('HIDROCLOR|CLORTALIDO|INDAPAMID', case=False, regex=True),
        med['medicamento'].str.contains('PRIL', case=False, regex=True),
        med['medicamento'].str.contains('LOL', case=False, regex=True),
        med['medicamento'].str.contains('CLONIDIN|METILDOP', case=False, regex=True),
        med['medicamento'].str.contains('PRAZOSINA|DOXAZOCINA', case=False, regex=True),
        med['medicamento'].str.contains('MINOXIDIL', case=False, regex=True),
        
        # Grupo DIABETES
        med['medicamento'].str.contains('METFORMINA', case=False, regex=True) &
        ~med['medicamento'].str.contains('GLIPTIN|GLINIDA|GLIFLOZIN|GLITAZONA|GLIMEPIRIDA|GLICLAZIDA|GLIPIZIDA|GLIBURIDA|CLORPOPAMIDA|TOLAZAMIDA|TOLBUTAMIDA', case=False, regex=True),
        med['medicamento'].str.contains('TIDA', case=False, regex=True),
        med['medicamento'].str.contains('GLINIDA', case=False, regex=True),
        med['medicamento'].str.contains('GLIFLOZIN|GLIFOZIN', case=False, regex=True) &
        ~med['medicamento'].str.contains('INSULINA|GLIPTIN', case=False, regex=True),
        med['medicamento'].str.contains('GLIPTIN', case=False, regex=True),
        med['medicamento'].str.contains('GLIMEPIRIDA|GLICLAZIDA|GLIPIZIDA|GLIBURIDA|CLORPOPAMIDA|TOLAZAMIDA|TOLBUTAMIDA|GLIBENCLAMIDA', case=False, regex=True),
        med['medicamento'].str.contains('GLITAZONA', case=False, regex=True),
        med['medicamento'].str.contains('INSULINA', case=False, regex=True) &
        ~med['medicamento'].str.contains('TIDA|TIDE', case=False, regex=True),
        med['medicamento'].str.contains('ACARBOSA', case=False, regex=True),
        
        # Grupo DISLIPIDEMIA
        med['medicamento'].str.contains('TATINA', case=False, regex=True),
        med['medicamento'].str.contains('EZETIMI', case=False, regex=True),
        med['medicamento'].str.contains('ALIROCU|EVOLOCU', case=False, regex=True)
    ],
    [
        # Tipos de medicamentos para HTA
        'ARA_2',
        'BL_CALCIO',
        'DIU',
        'IECA',
        'BETABLOQUEADORES',
        'ACCIONCENTRAL',
        'ALFA_UNO',
        'VASODILATADOR',
        
        # Tipos de medicamentos para DIABETES
        'BIGUANIDAS',
        'GLP1',
        'MEGLITINIDAS',
        'SGLT2',
        'iDPP4',
        'SULFONILUREAS',
        'TIAZOLIDINEDIONAS',
        'INSULINA',
        'INH_ALFA_GLUCOSIDASA',
        
        # Tipos de medicamentos para DISLIPIDEMIA
        'ESTATINAS',
        'EZETIMIBE',
        'IPCSK9'
    ],
    default=''
)

# Asignar el valor del grupo basado en el tipo de medicamento
med['grupo'] = np.select(
    [
        med['tipo_med'].isin(['ARA_2', 'BL_CALCIO', 'DIU', 'IECA', 'BETABLOQUEADORES', 'ACCIONCENTRAL', 'ALFA_UNO', 'VASODILATADOR']),
        med['tipo_med'].isin(['BIGUANIDAS', 'GLP1', 'MEGLITINIDAS', 'SGLT2','iDPP4', 'SULFONILUREAS', 'TIAZOLIDINEDIONAS', 'INSULINA', 'INH_ALFA_GLUCOSIDASA']),
        med['tipo_med'].isin(['ESTATINAS', 'EZETIMIBE', 'IPCSK9'])
    ],
    [
        'HTA',
        'DIABETES',
        'DISLIPIDEMIA'
    ],
    default=''
)

# Mostrar el DataFrame resultante
print(med[['medicamento', 'tipo_med', 'grupo']].head())

# Exportar el DataFrame 'med' como un archivo .txt separado por '|'
med.to_csv('medicamentos.txt', sep='|', index=False)

# Join Tipo MEdicamento 'med' y meds principal.

# Realizar el left join entre df_meds y med
df_merged = df_meds.merge(med, how='left', left_on='nombre_de_medicamento', right_on='medicamento')

# Mostrar las primeras filas del DataFrame resultante para verificar
print(df_merged.head())
# Exportar el DataFrame 'med' como un archivo .txt separado por '|'
df_merged.to_csv('medicamentos.txt', sep='|', index=False)


# Convertir las fechas a tipo datetime
df_merged['fecha_de_atencion'] = pd.to_datetime(df_merged['fecha_de_atencion'])

# Filtrar los datos por grupos
df_hta = df_merged[df_merged['grupo'] == 'HTA']
df_dm = df_merged[df_merged['grupo'] == 'DIABETES']
df_ldl = df_merged[df_merged['grupo'] == 'DISLIPIDEMIA']

# Asegúrate de que cada DataFrame sea una copia independiente
df_hta = df_hta.copy()
df_dm = df_dm.copy()
df_ldl = df_ldl.copy()

# Ahora puedes hacer las modificaciones sin el warning
df_hta['fecha_agrupada'] = pd.to_datetime(df_hta['fecha_de_atencion']).dt.to_period('M')
df_dm['fecha_agrupada'] = pd.to_datetime(df_dm['fecha_de_atencion']).dt.to_period('M')
df_ldl['fecha_agrupada'] = pd.to_datetime(df_ldl['fecha_de_atencion']).dt.to_period('M')

# Obtener el primer medicamento por documento y fecha (solo para los grupos solicitados)
med_hta_first = df_hta.groupby(['documento', 'fecha_agrupada'])['tipo_med'].first().reset_index()
med_dm_first = df_dm.groupby(['documento', 'fecha_agrupada'])['tipo_med'].first().reset_index()
med_ldl_first = df_ldl.groupby(['documento', 'fecha_agrupada'])['tipo_med'].first().reset_index()

# Obtener el último medicamento por documento y fecha (solo para los grupos solicitados)
med_hta_last = df_hta.groupby(['documento', 'fecha_agrupada'])['tipo_med'].last().reset_index()
med_dm_last = df_dm.groupby(['documento', 'fecha_agrupada'])['tipo_med'].last().reset_index()
med_ldl_last = df_ldl.groupby(['documento', 'fecha_agrupada'])['tipo_med'].last().reset_index()

# Unir las columnas para obtener el DataFrame final
final_df = pd.DataFrame({
    'documento': df_merged['documento'].unique()
})

final_df = final_df.merge(med_hta_first, on='documento', how='left', suffixes=('', '_hta')).rename(columns={'tipo_med': 'med_hta_first'})
final_df = final_df.merge(med_dm_first, on='documento', how='left', suffixes=('', '_dm')).rename(columns={'tipo_med': 'med_dm_first'})
final_df = final_df.merge(med_ldl_first, on='documento', how='left', suffixes=('', '_ldl')).rename(columns={'tipo_med': 'med_ldl_first'})
final_df = final_df.merge(med_hta_last, on='documento', how='left', suffixes=('', '_hta')).rename(columns={'tipo_med': 'med_hta_last'})
final_df = final_df.merge(med_dm_last, on='documento', how='left', suffixes=('', '_dm')).rename(columns={'tipo_med': 'med_dm_last'})
final_df = final_df.merge(med_ldl_last, on='documento', how='left', suffixes=('', '_ldl')).rename(columns={'tipo_med': 'med_ldl_last'})
final_df

# Convertir las fechas a tipo datetime
df_merged['fecha_de_atencion'] = pd.to_datetime(df_merged['fecha_de_atencion'])

# Filtrar los datos por grupos
df_hta = df_merged[df_merged['grupo'] == 'HTA']
# Asegúrate de que cada DataFrame sea una copia independiente
df_hta = df_hta.copy()

# Crear la columna 'fecha_agrupada' para agrupar por año y mes
df_hta['fecha_agrupada'] = pd.to_datetime(df_hta['fecha_de_atencion']).dt.to_period('M')

# Agrupar por documento y fecha para concatenar los medicamentos
# Usamos 'agg' para concatenar los medicamentos, y ordenarlos alfabéticamente
df_hta_grouped = df_hta.groupby(['documento', 'fecha_agrupada'])['tipo_med'].agg(lambda x: '+'.join(sorted(x.unique()))).reset_index()

# Renombrar la columna de medicamentos combinados
md_hta = df_hta_grouped.groupby('documento').agg(
    md_hta_first=('tipo_med','first'),
    md_hta_first_fecha=('fecha_agrupada','first'),
    md_hta_last=('tipo_med','last'),
    md_hta_last_fecha=('fecha_agrupada','last')
)

# Ahora, tenemos el DataFrame con los medicamentos combinados
# Unimos esta información con el DataFrame final
final_df = pd.DataFrame({
    'documento': df_merged['documento'].unique()
})

final_df = final_df.merge(md_hta, on='documento', how='left').sort_values(by='documento')

final_df

# Convertir las fechas a tipo datetime
df_merged['fecha_de_atencion'] = pd.to_datetime(df_merged['fecha_de_atencion'])

# Filtrar los datos por grupos
df_hta = df_merged[df_merged['grupo'] == 'HTA']
df_dm = df_merged[df_merged['grupo'] == 'DIABETES']
df_ldl = df_merged[df_merged['grupo'] == 'DISLIPIDEMIA']

# Asegúrate de que cada DataFrame sea una copia independiente
df_hta = df_hta.copy()
df_dm = df_dm.copy()
df_ldl = df_ldl.copy()

# Crear la columna 'fecha_agrupada' para agrupar por año y mes
df_hta['fecha_agrupada'] = pd.to_datetime(df_hta['fecha_de_atencion']).dt.to_period('M')
df_dm['fecha_agrupada'] = pd.to_datetime(df_dm['fecha_de_atencion']).dt.to_period('M')
df_ldl['fecha_agrupada'] = pd.to_datetime(df_ldl['fecha_de_atencion']).dt.to_period('M')

# Agrupar por documento y fecha para concatenar los medicamentos
# Usamos 'agg' para concatenar los medicamentos, y ordenarlos alfabéticamente
df_hta_grouped = df_hta.groupby(['documento', 'fecha_agrupada'])['tipo_med'].agg(lambda x: '+'.join(sorted(x.unique()))).reset_index()
df_dm_grouped = df_dm.groupby(['documento', 'fecha_agrupada'])['tipo_med'].agg(lambda x: '+'.join(sorted(x.unique()))).reset_index()
df_ldl_grouped = df_ldl.groupby(['documento', 'fecha_agrupada'])['tipo_med'].agg(lambda x: '+'.join(sorted(x.unique()))).reset_index()
# Renombrar la columna de medicamentos combinados
md_hta = df_hta_grouped.groupby('documento').agg(
    md_hta_first=('tipo_med','first'),
    md_hta_first_fecha=('fecha_agrupada','first'),
    md_hta_last=('tipo_med','last'),
    md_hta_last_fecha=('fecha_agrupada','last')
)
md_dm = df_dm_grouped.groupby('documento').agg(
    md_dm_first=('tipo_med','first'),
    md_dm_first_fecha=('fecha_agrupada','first'),
    md_dm_last=('tipo_med','last'),
    md_dm_last_fecha=('fecha_agrupada','last')
)
md_ldl = df_ldl_grouped.groupby('documento').agg(
    md_ldl_first=('tipo_med','first'),
    md_ldl_first_fecha=('fecha_agrupada','first'),
    md_ldl_last=('tipo_med','last'),
    md_ldl_last_fecha=('fecha_agrupada','last')
)



# Ahora, tenemos el DataFrame con los medicamentos combinados
# Unimos esta información con el DataFrame final
med_gr_df = pd.DataFrame({
    'documento': df_merged['documento'].unique()
})

med_gr_df = med_gr_df.merge(md_hta, on='documento', how='left').sort_values(by='documento')
med_gr_df = med_gr_df.merge(md_dm, on='documento', how='left').sort_values(by='documento')
med_gr_df = med_gr_df.merge(md_ldl, on='documento', how='left').sort_values(by='documento')

med_gr_df

####BORRAR
# Exportar el listado de nombres de columnas a un archivo txt
with open('nombres_columnas.txt', 'w') as f:
    for column in df_CAC.columns:
        f.write(column + '\n')

# Transformación de datos

#fechas invalidas '1845-01-01' y '' por vacío.
def limpiar_fechas(df, columnas):
    """
    Las fechas '1845-01-01', '1800-01-01' son reemplazadas por vacío NaT 
    """
    # Definir las fechas no válidas
    fechas_invalidas = ['1845-01-01', '1800-01-01']
    
    # Validar que todas las columnas existen en el DataFrame
    columnas_faltantes = [col for col in columnas if col not in df.columns]
    if columnas_faltantes:
        print(f"Error: Las columnas {columnas_faltantes} no existen en el DataFrame.")
        return df
    
    # Validar que todas las columnas son de tipo fecha o se pueden convertir
    for columna in columnas:
        if not pd.api.types.is_datetime64_any_dtype(df[columna]):
            try:
                df[columna] = pd.to_datetime(df[columna], format='mixed', errors='raise')
            except Exception as e:
                print(f"Error al convertir la columna '{columna}' a tipo fecha: {e}")
                return df
    
    # Limpiar las fechas no válidas
    for columna in columnas:
        df[columna] = df[columna].apply(lambda x: np.nan if pd.notnull(x) and x.strftime('%Y-%m-%d') in fechas_invalidas else x)
    
    print("Limpieza completada con éxito. Las fechas no válidas han sido reemplazadas por valores vacíos.")
    return df

columns=['fecha_de_ingreso','ultima_cita',
        'proximo_control','fecha_de_nac',
        'fecha_afiliacion_eps','fecha_dx_hta',
        'fecha_dx_dm','fecha_diagnostico_dislipidemias',
        'fecha_perfil_lipidico','fecha_colesterol_total',
        'fecha_colesterol_hdl','fecha_toma_trigliceridos',
        'fecha_ldl','fecha_hemoglobina_a1ac',
        'fecha_glicemia_ayuno','fecha_creatinina',
        '3_fecha_cociente_actual','fecha_uroanalisis',
        'atencion__m._interna','atencion_endocri',
        'atencion_cardio','remsion_oftalmo',
        'atencion_nefro','atencion_psico',
        'atencion_nutri','atencion_t.social',
        'fisioterapia','ekg',
        'fecha_creatinina_anterior','fecha_dx_estadio_5',
        'fecha_inicio_tmnd','fecha_diagnostico_hepatitis_b',
        'fecha_diagnostico_hepatitis_c','fecha_pth',
        'fecha_hemoglobina','fecha_albumina',
        'fecha_fosforo','fecha_muerte'
        ]
# Aplicar la función a múltiples columnas de fechas
df = limpiar_fechas(df_CAC, columns)

# General para reemplazar valroes.
def reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor):
    """
    Reemplaza valores específicos en una columna de un DataFrame con un nuevo valor.

    Parámetros:
    - df: DataFrame que contiene la columna.
    - columna: Nombre de la columna donde se realizará el reemplazo.
    - valores_a_reemplazar: Lista de valores que se van a reemplazar.
    - nuevo_valor: Valor que reemplazará a los valores especificados.

    Retorna:
    - DataFrame con los valores reemplazados en la columna especificada.
    """
    # Validar que la columna exista en el DataFrame
    if columna not in df.columns:
        print(f"Error: La columna '{columna}' no existe en el DataFrame.")
        return df

    # Reemplazar los valores
    df[columna] = df[columna].astype(str).replace(valores_a_reemplazar, nuevo_valor)
    print(f"Reemplazo completado en la columna '{columna}'.")
    
    return df

# Genero
columna='genero'
valores_a_reemplazar=['M', 'F']
nuevo_valor=['Masculino', 'Femenino']
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

# Regimen
columna='regimen'
valores_a_reemplazar=['C','S','P','E','N']
nuevo_valor=['Regimen contibutivo','Regimen subsidiado',
             'Regimenes de excepcion','Regimen especial','No asegurado']
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

# codigo_pertenencia_etnica
columna='codigo_pertenencia_etnica'
valores_a_reemplazar=['1', '2', '3', '4', '5', '6']
nuevo_valor=['Indigena','ROM (gitano)','Raizal del archipiélago de San Andrés y Providencia','Palenquero de San Basilio',
             'Negro(a), mulato(a), afrocolombiano(a) o afrodescendiente','Ninguna de las anteriores']
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

# pueblo_indigena
columna='pueblo_indigena'
valores_a_reemplazar=[
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
    '11', '12', '13', '14', '15', '16', '17', '18', 
    '19', '20', '21', '22', '23', '24', '25'
]
nuevo_valor=['Awá','Inga','Kametza',
    'Kamentsa Biya','Muruy','Nasa',
    'Pijao','Coconuco','Coreguaje',
    'Embera','Embera Chami','Embera Katio',
    'Eperara Siapidara','Guambiano','Guanaca',
    'Kofán','Misak','Pastos',
    'Quichwa','Quillacinga','Siona',
    'Totoró','Uitoto','Wounaan',
    'Yanacona'
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

# grupo_poblacional

columna='grupo_poblacional'
valores_a_reemplazar=[
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
    '11', '12', '13', '14', '15', '16', '31', '32', 
    '33', '34', '35', '36', '37', '38', '39', '50', 
    '51', '52', '53', '54', '55', '56', '57', '58', 
    '59', '99'
]
nuevo_valor=[
    'Indigentes',
    'Población infantil a cargo del ICBF',
    'Madres comunitarias',
    'Artistas, autores, compositores',
    'Otro grupo poblacional',
    'Recién nacidos',
    'Discapacitados',
    'Desmovilizados',
    'Desplazados',
    'Población ROM',
    'Población raizal',
    'Población en centros psiquiátricos',
    'Migratorio',
    'Población en centros carcelarios',
    'Población rural no migratoria',
    'Afrocolombiano',
    'Adulto mayor',
    'Cabeza de familia',
    'Mujer embarazada',
    'Mujer lactante',
    'Trabajador urbano',
    'Trabajador rural',
    'Víctima de violencia armada',
    'Jóvenes vulnerables rurales',
    'Jóvenes vulnerables urbanos',
    'Discapacitado - el sistema nervioso',
    'Discapacitado - los ojos',
    'Discapacitado - los oídos',
    'Discapacitado - los demás órganos de los sentidos (olfato, tacto y gusto)',
    'Discapacitado - la voz y el habla',
    'Discapacitado - el sistema cardiorrespiratorio y las defensas',
    'Discapacitado - la digestión, el metabolismo, las hormonas',
    'Discapacitado - el sistema genital y reproductivo',
    'Discapacitado - el movimiento del cuerpo, manos, brazos, piernas',
    'Discapacitado - la piel',
    'No definido'
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#EPS
columna='aseguradora'
eps=pd.read_csv('0_EPS.txt', delimiter='\t')
valores_a_reemplazar=eps['COD'].astype(str).tolist()
nuevo_valor=eps['EPS'].astype(str).tolist()
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#Escolaridad
columna='escolaridad'
valores_a_reemplazar=["0", "1", "2", "3", "4", "5", "6", "7"]
nuevo_valor=[
    "0) NINGUNA",
    "1) PRIMARIA INCOMPLETA",
    "2) PRIMARIA COMPLETA",
    "3) BACHILLERATO INCOMPLETO",
    "4) BACHILLERATO COMPLETO",
    "5) TECNICO",
    "6) UNIVERSITARIO",
    "7) OTRO"]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#Fumador activo
columna='fumador_activo'
valores_a_reemplazar=["1", "2", "3", "4"]
nuevo_valor=[
    "SI, CIGARILLO",
    "NO",
    "SI, CIGARRO",
    "SI, PIPA"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#Columnas SI/NO
columna=['exposicion_humo_leña',
        'consumo_alcohol',
        'dx_hta',
        'diagnostico_dislipidemias',
        'adherencia_al_tratamiento',
        'recibe_educacion',
        'valoracion_podologica',
        'realiza_actividad_fisica',
        'antecedente_familiar_enfermedad_cardiovascular',
        'tamizado_encuesta_rcv',
        'compl-cardiaca',
        'compl-cerebral',
        'compl-retiniana',
        'compl-vascular',
        'compl-renal']

valores_a_reemplazar=["1", "2"]
nuevo_valor=["SI","NO"]
for i in columna:
    df=reemplazar_valores(df, i, valores_a_reemplazar, nuevo_valor)


#Columnas SI/NO/97/98/99
columna=['cancer',
        'infeccion',
        'no_deseo',
        '6m_de_vida',
        'autocuidado',
        'enf-cv',
        'enf-vih',
        'enf-hb',
        'enf-inmun',
        'enf-cardiopul',
        'enfr-cron'
        ]

valores_a_reemplazar=["1", "2", "97", "98", "99"]
nuevo_valor=["SI",
             "NO",
             "No aplica, paciente que no tiene ERC estadio 5 (tiene ERC estadio 1 a 4) o ya tiene trasplante funcional",
             "No aplica, el paciente no tiene ERC o paciente en abandono",
             "No ha sido valorado por nefrólogo para la posibilidad de trasplante"
             ]
             
for i in columna:
    df=reemplazar_valores(df, i, valores_a_reemplazar, nuevo_valor)

#Categoria tension arterial
columna='categoria_tension_arterial'
valores_a_reemplazar=["1", "2", "3", "4", "5", "6"]
nuevo_valor=["1) OPTIMA",
             "2) PRE HIPERTENSION",
             "3) ESTADIO 1",
             "4) ESTADIO 2",
             "5) ESTADIO 3",
             "6) HTA sistolica Aislada"
            ]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#dx_dm
columna='dx_dm'
valores_a_reemplazar=["1", "2", "3", "4"]
nuevo_valor=["DM TIPO 1", "NO TIENE DM", "DM TIPO 2", "OTRAS DM"]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#farmacos_antihipertensivos
columna='farmacos_antihipertensivos'
valores_a_reemplazar=["0", "1", "2", "3", "4", "5", "6", "7", "98"]
nuevo_valor=[
    "MANEJO NO FARMACOLOGICO",
    "Hidroclorotiazida (HCTZ), únicamente",
    "IECA O ARA",
    "HCTZ + ARA O IECA",
    "HCTZ + ARA O IECA + AMLODIPINO",
    "AMLODIPINO, únicamente",
    "HCTZ + ARA O IECA + AMLODIPINO + OTRO (Metoprolol, Verapamilo, Nifedipina, Nimodipina, Espironolactona, Carbedilol, Digoxina, clonidina, asa, etc)",
    "OTRO",
    "No aplica, no es hipertenso"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#recibe_ieca o ARA
columna=['recibe_ieca','recibe_ara'] 
valores_a_reemplazar=["1", "2", "3", "98", "99"]
nuevo_valor=[
    "Sí recibe",
    "No fue formulado dentro del plan terapéutico",
    "No recibe, aunque fue formulado dentro del plan terapéutico",
    "No aplica (pacientes con ERC sin HTA ni DM)",
    "Paciente en abandono, alta voluntaria, fallecidos o desafiliados"
]

for i in columna:
    df=reemplazar_valores(df, i, valores_a_reemplazar, nuevo_valor)

#farmacos_ldl
columna='estanina'
valores_a_reemplazar=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
nuevo_valor=[
    "No recibe",
    "Lovastatina",
    "Atorvastatina",
    "Simvastatina",
    "Rosuvastatina",
    "Pravastatina",
    "Fluvastatina",
    "Cerivastatina",
    "Pitavastatina",
    "Otro"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#farmacos_antidiabeticos
columna='farmacos_antidiabeticos'
valores_a_reemplazar=["1", "2", "3", "4", "5", "6", "7", "8"]
nuevo_valor=[
    "GLIBENCLAMIDA SOLA",
    "METFORMINA SOLA",
    "METFORMINA + GLIBENCLAMIDA",
    "INSULINA NPH SOLA O COMBINADA CON ANTIDIABETICOS ORALES",
    "INSULINA NPH + CRISTALINA SOLAS O EN COMBINACION CON ANTIDIABETICOS ORALES",
    "OTRA INSULINA (GLARGINA, DETEMIR, ETC) SOLAS O COMBINADAS",
    "OTROS FARMACOS (ESPECIFIQUE EN OBSERVACIONES)",
    "NO APLICA"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)
#dx_erc
columna='dx_erc'
valores_a_reemplazar=["0","1", "2", "3"]
nuevo_valor=[
    "No presenta ERC",
    "Presenta ERC",
    "Indeterminado",
    "Paciente no estudiado para ERC en el periodo de reporte"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#Etiologia
columna='etiologia'
valores_a_reemplazar=[
    "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28"
]
nuevo_valor= [
    "Enfermedad poliquística renal",
    "Otras",
    "Desconocida o paciente en abandono (solo aplica para pacientes con ERC confirmada)",
    "Diabetes",
    "Enfermedad vascular renal (incluye Nefroangioesclerosis por hipertensión arterial)",
    "Sospecha de glomerulonefritis sin biopsia renal",
    "Glomeruloesclerosis focal y segmentaria",
    "Nefropatía membranosa",
    "Nefropatía por IgA",
    "Vasculitis",
    "Lupus eritematoso sistémico",
    "Glomerulopatía familiar o genética (incluye Alport)",
    "Otra glomerulonefritis",
    "Síndrome hemolítico urémico",
    "Nefropatía tóxica (incluye analgésicos)",
    "Nefritis intersticial",
    "Paraproteinemia (incluye mieloma múltiple)",
    "Nefropatía postparto",
    "Litiasis",
    "Displasia o hipoplasia renal congénita",
    "Pérdida de unidad renal por trauma o cirugía",
    "Carcinoma renal",
    "Nefropatía por reflujo vesicoureteral",
    "Obstrucción de cuello de la vejiga (Incluye HPB, cáncer de próstata, valvas, etc.)",
    "Nefropatía obstructiva de causa diferente a 27 (incluye cáncer de cuello uterino, tumores retroperitoneales, etc.)"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#modo_de_tto
columna='modo_de_tto'
valores_a_reemplazar=["1", "2", "3", "4", "97", "98", "99"]
nuevo_valor=[
    "Paciente que inició la TRR diálisis en hospitalización",
    "Paciente que inició la TRR diálisis ambulatoria",
    "Sin dato, el paciente inició la TRR en otra EPS diferente a la que reporta",
    "Paciente que inició la TRR con trasplante renal o TMND",
    "No aplica, paciente que nunca ha recibido TRR",
    "No aplica, el usuario a la fecha de corte no recibe ninguna de las terapias de reemplazo renal",
    "Paciente que inició la TRR en la EPS que reporta, pero no hay información en la historia clínica o paciente en abandono"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#recibe_tmnd
columna='recibe_tmnd'
valores_a_reemplazar=["1", "2"]
nuevo_valor=[
    "El usuario con ERC estadio 5 recibe solamente tratamiento médico especial y multidisciplinario sin diálisis en el momento de la fecha de corte",
    "El usuario no recibe esta terapia"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#estudio_para_transplante
columna='estudio_para_transplante'
valores_a_reemplazar=["1", "2", "97", "98", "99"]
nuevo_valor=[
    "Indicado",
    "Contraindicado",
    "No aplica porque es una persona que no está en Estadio 5 o ya tiene trasplante funcional",
    "No aplica, no tiene enfermedad renal crónica o paciente en abandono",
    "No ha sido valorado para la posibilidad de trasplante por el nefrólogo"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#causa_muerte
columna='causa_muerte'
valores_a_reemplazar=["1", "2", "3", "4", "5", "6", "98", "99"]
nuevo_valor=[
    "Enfermedad renal crónica",
    "Enfermedad cardiovascular",
    "Cáncer",
    "Infección",
    "Por causa diferente a las descritas en 1, 2, 3 y 4",
    "Causa Externa",
    "No aplica, el usuario no ha fallecido",
    "Paciente que fallece, pero no hay información sobre la causa de muerte en la historia clínica"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

#novedades
columna='novedades'
valores_a_reemplazar=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "98"]
nuevo_valor=[
    "Persona que falleció",
    "Persona que ingresó a la IPS y traía el diagnóstico de ERC",
    "Persona antigua en la IPS y se le realizó nuevo diagnóstico de ERC",
    "Persona antigua en la IPS con diagnóstico antiguo de ERC que ingresa a la BD para reporte",
    "Persona que firmó alta voluntaria del tratamiento prescrito",
    "Persona que se desafilió",
    "Persona que abandona la terapia y no es posible de ubicar - inasistente",
    "Persona que se baja de la BD por corrección de la IPS (auditoría interna), porque el caso reportado no tiene diagnóstico de ERC, HTA y DM",
    "Persona que regresa a terapia",
    "El usuario que cambió de tipo o número de identificación",
    "No aplica, no hay novedad respecto al reporte pasado"
]
df=reemplazar_valores(df, columna, valores_a_reemplazar, nuevo_valor)

# Validación de Variables Fecha.
def last_valid_fecha(series):
    # Asegura que la columna esté en formato de fecha
    series = pd.to_datetime(series, errors='coerce')
    # Filtra valores no nulos y obtiene el último
    return series.dropna().iloc[-1] if not series.dropna().empty else pd.NaT

# Validación edades 0> x <120.
def last_valid_edad(series):
    # Filtra los valores que son enteros positivos o cero, menores a 120
    valid_ages = series[(series >= 0) & (series < 120) & (series.notna())]
    # Devuelve el último valor válido o NaN si no hay valores válidos
    return valid_ages.iloc[-1] if not valid_ages.empty else np.nan

# Validacion de Tension Arterial TA

def first_valid_ta(series, date_series):
    # Asegurarte que la serie de fechas tenga el mismo índice que la serie principal
    date_series = date_series.reindex(series.index)
    # Filtrar valores que sean números positivos menores a 200
    mask = series.between(1, 200, inclusive="both")
    valid_series = series[mask]
    valid_dates = date_series[mask]

    if not valid_series.empty:
        idx = valid_series.first_valid_index()
        return valid_series[idx], valid_dates[idx]
    return np.nan, pd.NaT

def last_valid_ta(series, date_series):
    # Asegurarte que la serie de fechas tenga el mismo índice que la serie principal
    date_series = date_series.reindex(series.index)
    # Filtrar valores inválidos
    mask = series.between(1, 200, inclusive="both")
    valid_series = series[mask]
    valid_dates = date_series[mask]

    if not valid_series.empty:
        idx = valid_series.last_valid_index()
        return valid_series[idx], valid_dates[idx]
    return np.nan, pd.NaT

# Validador de examenes
def first_valid_exam(series, date_series):
    # Asegurar que la serie de fechas tenga el mismo índice que la serie principal
    date_series = date_series.reindex(series.index)
    # Filtrar valores válidos entre 1 y 200 y con fecha no nula
    mask = series.between(1, 900, inclusive="both") & date_series.notna()
    valid_series = series[mask]
    valid_dates = date_series[mask]

    if not valid_series.empty:
        idx = valid_series.first_valid_index()
        return valid_series[idx], valid_dates[idx]
    return np.nan, pd.NaT

def last_valid_exam(series, date_series):
    # Asegurar que la serie de fechas tenga el mismo índice que la serie principal
    date_series = date_series.reindex(series.index)
    # Filtrar valores válidos entre 1 y 200 y con fecha no nula
    mask = series.between(1, 900, inclusive="both") & date_series.notna()
    valid_series = series[mask]
    valid_dates = date_series[mask]

    if not valid_series.empty:
        idx = valid_series.last_valid_index()
        return valid_series[idx], valid_dates[idx]
    return np.nan, pd.NaT


# 3. Data Frame de Salida.
df_distinct = df.sort_values(by=['ORIGEN','ultima_cita'], ascending=True).groupby('numero_identificacion').agg(
    #Demográficas
    fecha_de_ingreso=('fecha_de_ingreso','last'),
    numero_identificacion=('numero_identificacion','last'),
    primer_nombre=('primer_nombre','last'),
    segundo_nombre=('segundo_nombre','last'),
    primer_apellido=('primer_apellido','last'),
    segundo_apellido=('segundo_apellido','last'),
    genero=('genero','last'),
    zona=('zona','last'),
    asentamiento=('asentamiento','last'),
    municipio_de_procedencia=('municipio_de_procedencia','last'),
    regimen=('regimen','last'),
    ips_primaria=('ips_primaria','last'),
    codigo_pertenencia_etnica=('codigo_pertenencia_etnica','last'),
    pueblo_indigena=('pueblo_indigena','last'),
    comunidad_indigena=('comunidad_indigena','last'),
    grupo_poblacional=('grupo_poblacional','last'),
    aseguradora=('aseguradora','last'),
    codigo_ips_que_hace_el_seguimiento=('codigo_ips_que_hace_el_seguimiento','last'),
    ips_de_seguimiento=('ips_de_seguimiento','last'),
    escolaridad=('escolaridad','last'),
    fumador_activo=('fumador_activo','last'),
    exposicion_humo_leña=('exposicion_humo_leña','last'),
    consumo_alcohol=('consumo_alcohol','last'),
    categoria_tension_arterial=('categoria_tension_arterial','last'),
    dx_hta=('dx_hta','last'),
    fecha_dx_hta=('fecha_dx_hta','last'),
    dx_dm=('dx_dm','last'),
    fecha_dx_dm=('fecha_dx_dm','last'),
    diagnostico_dislipidemias=('diagnostico_dislipidemias','last'),
    fecha_diagnostico_dislipidemias=('fecha_diagnostico_dislipidemias','last'),
    recibe_ieca=('recibe_ieca','last'),
    recibe_ara=('recibe_ara','last'),
    estanina=('estanina','last'),
    farmacos_antidiabeticos=('farmacos_antidiabeticos','last'),
    adherencia_al_tratamiento=('adherencia_al_tratamiento','last'),
    recibe_educacion=('recibe_educacion','last'),
    valoracion_podologica=('valoracion_podologica','last'),
    realiza_actividad_fisica=('realiza_actividad_fisica','last'),
    antecedente_familiar_enfermedad_cardiovascular=('antecedente_familiar_enfermedad_cardiovascular','last'),
    tamizado_encuesta_rcv=('tamizado_encuesta_rcv','last'),
    compl_cardiaca=('compl-cardiaca','last'),
    compl_cerebral=('compl-cerebral','last'),
    compl_retiniana=('compl-retiniana','last'),
    compl_vascular=('compl-vascular','last'),
    compl_renal=('compl-renal','last'),
    dx_erc=('dx_erc','last'),
    etiologia=('etiologia','last'),
    tfg_actual=('tfg_actual','last'),
    estadio_cac=('estadio_cac','last'),
    estadio_ips=('estadio_ips','last'),
    progresion_erc=('progresion_erc','last'),
    fecha_dx_estadio_5=('fecha_dx_estadio_5','last'),
    tfg_dx_estadio_5=('tfg_dx_estadio_5','last'),
    modo_de_tto=('modo_de_tto','last'),
    recibe_tmnd=('recibe_tmnd','last'),
    fecha_inicio_tmnd=('fecha_inicio_tmnd','last'),
    fecha_diagnostico_hepatitis_b=('fecha_diagnostico_hepatitis_b','last'),
    fecha_diagnostico_hepatitis_c=('fecha_diagnostico_hepatitis_c','last'),
    estudio_para_transplante=('estudio_para_transplante','last'),
    cancer=('cancer','last'),
    infeccion=('infeccion','last'),
    no_deseo=('no_deseo','last'),
    Seism_de_vida=('6m_de_vida','last'),
    autocuidado=('autocuidado','last'),
    enf_cv=('enf-cv','last'),
    enf_vih=('enf-vih','last'),
    enf_hb=('enf-hb','last'),
    enf_inmun=('enf-inmun','last'),
    enf_cardiopul=('enf-cardiopul','last'),
    enfr_cron=('enfr-cron','last'),
    novedades=('novedades','last'),
    causa_muerte=('causa_muerte','last'),
    fecha_muerte=('fecha_muerte','last'),
    estado=('estado','last'),
    medico=('medico','last'),
    ORIGEN=('ORIGEN','last'),
    # Clasificaciones de Riesgo
    ekg=('ekg',last_valid_fecha),
    imc=('imc','last'),
    imc_gr=('clasificacion','last'),
    riesgo_framingham=('riesgo_framingham','last'),
    clasificacion_framingham=('clasificacion_framingham','last'),
    riesgo_cardiovascular_global=('riesgo_cardiovascular_global','last'),
    #Indicadores
    ultima_cita=('ultima_cita',last_valid_fecha),
    fecha_de_nac=('fecha_de_nac',last_valid_fecha),
    fecha_afiliacion_eps=('fecha_afiliacion_eps',last_valid_fecha),
    atencion_minterna=('atencion__m._interna',last_valid_fecha),
    atencion_endocri=('atencion_endocri',last_valid_fecha),
    atencion_cardio=('atencion_cardio',last_valid_fecha),
    remsion_oftalmo=('remsion_oftalmo',last_valid_fecha),
    atencion_nefro=('atencion_nefro',last_valid_fecha),
    atencion_psico=('atencion_psico',last_valid_fecha),
    atencion_nutri=('atencion_nutri',last_valid_fecha),
    atencion_tsocial=('atencion_t.social',last_valid_fecha),
    fisioterapia=('fisioterapia',last_valid_fecha),
    edad=('edad',last_valid_edad),
    ######## EXÁMENES
    # Peso
    peso_first=('peso', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[0]),
    peso_fecha_first=('peso', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[1]),
    peso_last=('peso', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[0]),
    peso_fecha_last=('peso', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[1]),
    #Talla
    talla_first=('talla', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[0]),
    talla_fecha_first=('talla', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[1]),
    talla_last=('talla', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[0]),
    talla_fecha_last=('talla', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[1]),
    # Perimetro Abdominal
    perimetro_abdominal_first=('perimetro_abdominal', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[0]),
    perimetro_abdominal_fecha_first=('perimetro_abdominal', lambda x: first_valid_exam(x, df_CAC['ultima_cita'])[1]),
    perimetro_abdominal_last=('perimetro_abdominal', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[0]),
    perimetro_abdominal_fecha_last=('perimetro_abdominal', lambda x: last_valid_exam(x, df_CAC['ultima_cita'])[1]),
    # TA
    tas_first=('tension_arterial_sistolica', lambda x: first_valid_ta(x, df_CAC['ultima_cita'])[0]),
    tad_first=('tension_arterial_diastolica', lambda x: first_valid_ta(x, df_CAC['ultima_cita'])[0]),
    ta_fecha_first=('tension_arterial_diastolica', lambda x: first_valid_ta(x, df_CAC['ultima_cita'])[1]),
    tas_last=('tension_arterial_sistolica', lambda x: last_valid_ta(x, df_CAC['ultima_cita'])[0]),
    tad_last=('tension_arterial_diastolica', lambda x: last_valid_ta(x, df_CAC['ultima_cita'])[0]),
    ta_fecha_last=('tension_arterial_diastolica', lambda x: last_valid_ta(x, df_CAC['ultima_cita'])[1]),
    # Colesterol Total
    colesterol_total_first=('colesterol_total', lambda x: first_valid_exam(x, df_CAC['fecha_colesterol_total'])[0]),
    colesterol_total_fecha_first=('colesterol_total', lambda x: first_valid_exam(x, df_CAC['fecha_colesterol_total'])[1]),
    colesterol_total_last=('colesterol_total', lambda x: last_valid_exam(x, df_CAC['fecha_colesterol_total'])[0]),
    colesterol_total_fecha_last=('colesterol_total', lambda x: last_valid_exam(x, df_CAC['fecha_colesterol_total'])[1]),
    # Colesterol HDL
    colesterol_hdl_first=('colesterol_hdl', lambda x: first_valid_exam(x, df_CAC['fecha_colesterol_hdl'])[0]),
    colesterol_hdl_fecha_first=('colesterol_hdl', lambda x: first_valid_exam(x, df_CAC['fecha_colesterol_hdl'])[1]),
    colesterol_hdl_last=('colesterol_hdl', lambda x: last_valid_exam(x, df_CAC['fecha_colesterol_hdl'])[0]),
    colesterol_hdl_fecha_last=('colesterol_hdl', lambda x: last_valid_exam(x, df_CAC['fecha_colesterol_hdl'])[1]),
    # Colesterol LDL
    colesterol_ldl_first=('colesterol_ldl', lambda x: first_valid_exam(x, df_CAC['fecha_ldl'])[0]),
    colesterol_ldl_fecha_first=('colesterol_ldl', lambda x: first_valid_exam(x, df_CAC['fecha_ldl'])[1]),
    colesterol_ldl_last=('colesterol_ldl', lambda x: last_valid_exam(x, df_CAC['fecha_ldl'])[0]),
    colesterol_ldl_fecha_last=('colesterol_ldl', lambda x: last_valid_exam(x, df_CAC['fecha_ldl'])[1]),
    # Trigliceridos
    trigliceridos_first=('trigliceridos', lambda x: first_valid_exam(x, df_CAC['fecha_toma_trigliceridos'])[0]),
    trigliceridos_fecha_first=('trigliceridos', lambda x: first_valid_exam(x, df_CAC['fecha_toma_trigliceridos'])[1]),
    trigliceridos_last=('trigliceridos', lambda x: last_valid_exam(x, df_CAC['fecha_toma_trigliceridos'])[0]),
    trigliceridos_fecha_last=('trigliceridos', lambda x: last_valid_exam(x, df_CAC['fecha_toma_trigliceridos'])[1]),    
    # HBA1C
    hba1c_first=('hemoglobina_a1ac', lambda x: first_valid_exam(x, df_CAC['fecha_hemoglobina_a1ac'])[0]),
    hba1c_fecha_first=('hemoglobina_a1ac', lambda x: first_valid_exam(x, df_CAC['fecha_hemoglobina_a1ac'])[1]),
    hba1c_last=('hemoglobina_a1ac', lambda x: last_valid_exam(x, df_CAC['fecha_hemoglobina_a1ac'])[0]),
    hba1c_fecha_last=('hemoglobina_a1ac', lambda x: last_valid_exam(x, df_CAC['fecha_hemoglobina_a1ac'])[1]),
    # Glicemia
    glicemia_ayuno_first=('glicemia_ayuno', lambda x: first_valid_exam(x, df_CAC['fecha_glicemia_ayuno'])[0]),
    glicemia_ayuno_fecha_first=('glicemia_ayuno', lambda x: first_valid_exam(x, df_CAC['fecha_glicemia_ayuno'])[1]),
    glicemia_ayuno_last=('glicemia_ayuno', lambda x: last_valid_exam(x, df_CAC['fecha_glicemia_ayuno'])[0]),
    glicemia_ayuno_fecha_last=('glicemia_ayuno', lambda x: last_valid_exam(x, df_CAC['fecha_glicemia_ayuno'])[1]),
    # Creatinina
    creatinina_first=('creatinina', lambda x: first_valid_exam(x, df_CAC['fecha_creatinina'])[0]),
    creatinina_fecha_first=('creatinina', lambda x: first_valid_exam(x, df_CAC['fecha_creatinina'])[1]),
    creatinina_last=('creatinina', lambda x: last_valid_exam(x, df_CAC['fecha_creatinina'])[0]),
    creatinina_fecha_last=('creatinina', lambda x: last_valid_exam(x, df_CAC['fecha_creatinina'])[1]),
    # Cociente
    cociente_first=('3_____cociente_actual', lambda x: first_valid_exam(x, df_CAC['3_fecha_cociente_actual'])[0]),
    cociente_fecha_first=('3_____cociente_actual', lambda x: first_valid_exam(x, df_CAC['3_fecha_cociente_actual'])[1]),
    cociente_last=('3_____cociente_actual', lambda x: last_valid_exam(x, df_CAC['3_fecha_cociente_actual'])[0]),
    cociente_fecha_last=('3_____cociente_actual', lambda x: last_valid_exam(x, df_CAC['3_fecha_cociente_actual'])[1]),
    # Uroanálisis
    proteinas_uroanalisis_first=('proteinas_uroanalisis', lambda x: first_valid_exam(x, df_CAC['fecha_uroanalisis'])[0]),
    proteinas_uroanalisis_fecha_first=('proteinas_uroanalisis', lambda x: first_valid_exam(x, df_CAC['fecha_uroanalisis'])[1]),
    proteinas_uroanalisis_last=('proteinas_uroanalisis', lambda x: last_valid_exam(x, df_CAC['fecha_uroanalisis'])[0]),
    proteinas_uroanalisis_fecha_last=('proteinas_uroanalisis', lambda x: last_valid_exam(x, df_CAC['fecha_uroanalisis'])[1]),
    # PTH
    pth_first=('pth', lambda x: first_valid_exam(x, df_CAC['fecha_pth'])[0]),
    pth_fecha_first=('pth', lambda x: first_valid_exam(x, df_CAC['fecha_pth'])[1]),
    pth_last=('pth', lambda x: last_valid_exam(x, df_CAC['fecha_pth'])[0]),
    pth_fecha_last=('pth', lambda x: last_valid_exam(x, df_CAC['fecha_pth'])[1]),
    # Hemoglobina
    hemoglobina_first=('hemoglobina', lambda x: first_valid_exam(x, df_CAC['fecha_hemoglobina'])[0]),
    hemoglobina_fecha_first=('hemoglobina', lambda x: first_valid_exam(x, df_CAC['fecha_hemoglobina'])[1]),
    hemoglobina_last=('hemoglobina', lambda x: last_valid_exam(x, df_CAC['fecha_hemoglobina'])[0]),
    hemoglobina_fecha_last=('hemoglobina', lambda x: last_valid_exam(x, df_CAC['fecha_hemoglobina'])[1]),
    # Albumina
    albumina_first=('albumina', lambda x: first_valid_exam(x, df_CAC['fecha_albumina'])[0]),
    albumina_fecha_first=('albumina', lambda x: first_valid_exam(x, df_CAC['fecha_albumina'])[1]),
    albumina_last=('albumina', lambda x: last_valid_exam(x, df_CAC['fecha_albumina'])[0]),
    albumina_fecha_last=('albumina', lambda x: last_valid_exam(x, df_CAC['fecha_albumina'])[1]),
    # Fosforo
    fosforo_first=('fosforo', lambda x: first_valid_exam(x, df_CAC['fecha_fosforo'])[0]),
    fosforo_fecha_first=('fosforo', lambda x: first_valid_exam(x, df_CAC['fecha_fosforo'])[1]),
    fosforo_last=('fosforo', lambda x: last_valid_exam(x, df_CAC['fecha_fosforo'])[0]),
    fosforo_fecha_last=('fosforo', lambda x: last_valid_exam(x, df_CAC['fecha_fosforo'])[1]),
    # Farmacos
    farmacos_antihipertensivos=('farmacos_antihipertensivos','last'),
)
df_distinct

# join df_distinct con med_gr_df
# Asegúrate de que 'numero_identificacion' no sea un índice, si lo es, restablecer el índice
df_distinct = df_distinct.reset_index(drop=True)  # Restablecer índice si 'numero_identificacion' es el índice
med_gr_df = med_gr_df.reset_index(drop=True)  # Restablecer índice si 'numero_identificacion' es el índice

# Realizar el merge especificando las columnas correspondientes para cada DataFrame
result = df_distinct.merge(med_gr_df, left_on='numero_identificacion', right_on='documento', how='left').sort_values(by='numero_identificacion')


result

result.to_csv('data_model_excel.txt', sep='|', decimal=',', index=False)

# Indicadores CAC
result