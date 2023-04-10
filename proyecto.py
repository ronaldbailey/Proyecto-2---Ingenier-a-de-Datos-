import pandas as pd
import numpy as np
import boto3
import psycopg2
import configparser
import matplotlib.pyplot as plt

DB_USER="admincuentas2"
DB_NAME="cuentas"
DB_PASSWORD="cuentas2admin2023"
DB_PORT=3306
DB_HOST="cuentas2.clptjw9nvvtu.us-east-1.rds.amazonaws.com"

mysql_driver = "mysql+pymysql://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
print(mysql_driver)

data_tipo_transacciones = [
     {'id_tipo_transac': 85095, 'tipo_transaccion': 'Depóito'}, 
     {'id_tipo_transac': 85098, 'tipo_transaccion': 'Retiro'},
     {'id_tipo_transac': 85194, 'tipo_transaccion': 'Transferencia'},
     {'id_tipo_transac': 85133, 'tipo_transaccion': 'Pago Prestamo'}
]
print(data_tipo_transacciones)

df_transaccion = pd.DataFrame(data_tipo_transacciones)
df_transaccion

#response = df_transaccion.to_sql('tipo_transacciones',mysql_driver,index = False, if_exists ='append')
#response 

datos_crudos = pd.read_excel('../datos/cxc_cxp_bancos_el_rosario.xlsx')
#datos ingresados son reales, solo el numero de factura o recibo no se contaba con el, por lo que se coloco uno para posteriormente ya llenarlo con datos reales al usar el codigo. 
datos_crudos

datos_crudos_clientes = pd.read_csv('../datos/Clientes_Info.csv')
#datos ingresados son reales, solo el numero de factura o recibo no se contaba con el, por lo que se coloco uno para posteriormente ya llenarlo con datos reales al usar el codigo. 
datos_crudos_clientes

datos_crudos.info()

datos_crudos_clientes.info()

datos_crudos.describe()

datos_crudos.plot(kind = 'scatter', x = 'Fecha_Estm_Pago', y = 'Total_Pagar')

plt.show()

clientes_limpios = datos_crudos_clientes.drop_duplicates().sort_values('Id_Cliente').reset_index(drop = True)
clientes_limpios

# Insertar los datos en la tabla MySQL
datos_crudos.to_sql(name='datos_cuentas', con=mysql_driver, if_exists='replace', index=False)
clientes_limpios.to_sql(name='datos_clientes', con=mysql_driver, if_exists='replace', index=False)

# Leer la primera tabla
df1 = pd.read_sql_query("SELECT * FROM datos_cuentas", mysql_driver)

# Leer la segunda tabla
df2 = pd.read_sql_query("SELECT * FROM datos_clientes", mysql_driver)

nuevo_df = pd.merge(df1, df2, on="Id_Cliente")
nuevo_df

nuevo_df.describe()

nuevo_df.info()

nuevo_df.plot(kind = 'scatter', x = 'Fecha_Estm_Pago', y = 'Total_Pagar')

plt.show()

df = nuevo_df
df['quincena'] = nuevo_df['Fecha_Estm_Pago'].apply(lambda x: 2 * (x.day // 15) + 1)
df_quincenas = df.groupby('quincena').sum('Total_Libre')
df_quincenas[['Total_Libre']]


frecuencia_clientes = df['Id_Cliente'].value_counts()
id_cliente_mas_cuentas = frecuencia_clientes.idxmax()
df_cliente_mas_cuentas = df[df['Id_Cliente'] == id_cliente_mas_cuentas]

# Sumamos la columna 'Total_Pagar' para obtener el total que debe ese cliente
total_deuda_cliente_mas_cuentas = df_cliente_mas_cuentas['Total_Pagar'].sum()

# Imprimimos los resultados
print(f"El cliente con ID {id_cliente_mas_cuentas} es el que tiene más cuentas abiertas.")
print(f"El total que debe este cliente es de ${total_deuda_cliente_mas_cuentas}.")
print(f"El cliente con ID 21 es: {nuevo_df[nuevo_df.Id_Cliente == 21].Cliente}")

cuenta_mas_grande = df['Total_Pagar'].nlargest(1)
print(f"La Cuenta mas grande es: {nuevo_df[nuevo_df.index == 38].Cliente} con un total a pagar de: {cuenta_mas_grande}")

# Agrupar los datos por vendedor y sumar las ventas totales
ventas_por_vendedor = df.groupby('Vendedor_Asignado')['Total_Pagar'].sum()

# Obtener el vendedor que vendió más
vendedor_top = ventas_por_vendedor.idxmax()

# Obtener el total de ventas de cada vendedor
print(ventas_por_vendedor)
print(f"el vendedor top es: {vendedor_top}")

# Agrupar los datos por cuenta y sumar las ventas totales
ventas_por_cuenta = df.groupby('tipo_cuenta')['Total_Pagar'].sum()


# Obtener el total de ventas de cada cuenta
print(ventas_por_cuenta)


