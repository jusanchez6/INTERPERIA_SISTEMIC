import smbus
import time
import json


I2C_SLAVE_ADDRESS = 0x17
I2C_BUS = 3  # Reemplaza con el número de I2C correcto


def main():
    # Inicializar el bus I2C
    bus = smbus.SMBus(I2C_BUS)

    mem_address = 0
    while True:
        msg = f"Hello, I2C slave! - 0x{mem_address:02X}"
        msg_bytes = list(msg.encode('ascii'))
        try:
            # Escribir mensaje en la dirección de memoria del esclavo
            bus.write_i2c_block_data(I2C_SLAVE_ADDRESS, mem_address, msg_bytes)
            print(f"Write at 0x{mem_address:02X}: '{msg}'")
            
            # Leer datos del esclavo
            split = 5
            read_data = bus.read_i2c_block_data(I2C_SLAVE_ADDRESS, mem_address, split)
            print(f"Read  at 0x{mem_address:02X}: '{bytes(read_data).decode('ascii')}'")
            
            read_data = bus.read_i2c_block_data(I2C_SLAVE_ADDRESS, mem_address + split, len(msg) - split)
            print(f"Read  at 0x{mem_address + split:02X}: '{bytes(read_data).decode('ascii')}'")
        
        except IOError as e:
            print(f"Error de I/O: {e}")
        
        time.sleep(2)  # Espera antes de la siguiente iteración
        mem_address = (mem_address + 32) % 256
        print(mem_address)

if __name__ == "__main__":
    main()