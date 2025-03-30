##
# @file i2c_master_python.py
# 
# @brief El script se conecta a la RPP mediante I2C con la dirección 0x17 y le envía un diccionario de datos en formato JSON
# Lee los datos enviados por el esclavo para validar la comunicación.
#  
#
# @author : Manuel Cely
# @author : Maria del Mar A. (Docs)
# 
# @date: 2025-03-29
# 
# @version: 1.0
# 
# @copyright SISTEMIC 2025
##

import smbus
import time
import json

I2C_SLAVE_ADDRESS = 0x17
I2C_BUS = 3  # Reemplaza con el número de I2C correcto

def send_dict_over_i2c(bus, address, data_dict):
    # Convertir el diccionario a una cadena JSON
    json_str = json.dumps(data_dict)
    # Convertir la cadena JSON a bytes
    json_bytes = json_str.encode('utf-8') # aqui se puede hacer encode de varías maneras
    print(json_bytes)
    # Dividir los bytes en chunks de 32 bytes (o menos para el último chunk)
    chunk_size = 32
    for i in range(0, len(json_bytes), chunk_size):
        chunk = json_bytes[i:i+chunk_size]
        try:
            bus.write_i2c_block_data(address, i, list(chunk))
            print(f"Enviado chunk {i//chunk_size + 1}: {chunk}")
        except IOError as e:
            print(f"Error al enviar chunk {i//chunk_size + 1}: {e}")
        time.sleep(0.1)  # Pequeña pausa entre chunks


        # BLOQUE DE CÓDIGO PARA VALIDAR LA INFORMACIÓN GUARDADA EN LA RASPBERRY PI PICO :D
        try:
            read_data = bus.read_i2c_block_data(I2C_SLAVE_ADDRESS, i, chunk_size)
            read_data =  bytes(read_data).decode('utf-8') # Paso de Bytes a utf-8 
            if('}' in list(read_data)):
                 
                 print(f"Read  at 0x{i:02X}: '{read_data[:read_data.index('}')+1]}'")
            else:
                 print(f"Read  at 0x{i:02X}: '{read_data}'")

           
        except IOError as e:
            print(f"Error :  {e}")

def main():
    # Inicializar el bus I2C
    bus = smbus.SMBus(I2C_BUS)

    # Ejemplo json que se envía
    mensaje_dic = {
        "tipo": "Audio",
        "deteccion": "sirena",
        "fecha": "2023-11-24T13:37:00Z",
        "nivel_confianza": 0.95
    }

    while True:
        try:
            send_dict_over_i2c(bus, I2C_SLAVE_ADDRESS, mensaje_dic)
            print("Mensaje enviado correctamente")
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")
        
        time.sleep(5)  # Espera 5 segundos antes de enviar el siguiente mensaje

if __name__ == "__main__":
    main()