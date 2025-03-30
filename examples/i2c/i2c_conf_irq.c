/**
 * @file i2c_config_irq.c
 * @brief Archivo simple para RPP como esclavo i2c.
 * 
 * Configura una Raspberry Pi Pico como un dispositivo esclavo I2C.
 * Define una memoria de 256 bytes donde el maestro puede leer o escribir datos.
 * El código utiliza una estructura que gestiona la dirección de memoria y un manejador de eventos (i2c_slave_handler) 
 * para procesar las operaciones de lectura y escritura. 
 * Cuando el maestro envía datos, el esclavo los guarda en la memoria; cuando el maestro solicita datos, el esclavo los envía. 
 * El programa se ejecuta en un bucle infinito esperando eventos I2C, manejados por interrupciones.
 *
 * @author Manuel Cely
 * @author Maria del Mar A. (Docs)
 * @date 29/03/2025
 * @version 1.0
 * 
 * @copyright SISTEMIC 2025
 */

// Inclusión de librerías necesarias -> api pico : High level APIs
#include <hardware/i2c.h>
#include <pico/i2c_slave.h> //recordar en CmakeList agregar pico_i2c_slave
#include <pico/stdlib.h>
#include <stdio.h>
#include <string.h>


//Defino el address de la pico como esclavo
static const uint I2C_SLAVE_ADDRESS =  0X17;
static const uint I2C_BAUDRATE      =  100000; // 100kHz

static const uint I2C_SLAVE_SDA_PIN = PICO_DEFAULT_I2C_SDA_PIN; // 4
static const uint I2C_SLAVE_SCL_PIN = PICO_DEFAULT_I2C_SCL_PIN; // 5



// Defino una estructura para manejar los estados de la I2C en modo esclavo 
static struct
{
    uint8_t mem[256];
    uint8_t mem_address;
    bool mem_address_written;

} context;

// Definición del handler, el cual es llamado desde el I2C ISR el cual debe completarse lo más rapido posible
static void i2c_slave_handler(i2c_inst_t *i2c, i2c_slave_event_t event) {
    switch (event) {
    case I2C_SLAVE_RECEIVE: // El maestro ha escrito algo de información
        if (!context.mem_address_written) {
            // writes always start with the memory address
            context.mem_address = i2c_read_byte_raw(i2c);
            context.mem_address_written = true;
        } else {
            // save into memory
            context.mem[context.mem_address] = i2c_read_byte_raw(i2c);
            context.mem_address++;
        }
        break;
    case I2C_SLAVE_REQUEST: // master is requesting data
        // load from memory
        i2c_write_byte_raw(i2c, context.mem[context.mem_address]);
        context.mem_address++;
        break;
    case I2C_SLAVE_FINISH: // master has signalled Stop / Restart
        context.mem_address_written = false;
        break;
    default:
        break;
    }
}


// Configuración del esclavo
static void setup_slave(){
    gpio_init(I2C_SLAVE_SDA_PIN); // Inicializo el GPIO SDA
    gpio_set_function(I2C_SLAVE_SDA_PIN, GPIO_FUNC_I2C);  // Seteo el GPIO en modo I2C
    gpio_pull_up(I2C_SLAVE_SDA_PIN);
    
    gpio_init(I2C_SLAVE_SCL_PIN); // Inicializo el GPIO DEL SCL
    gpio_set_function(I2C_SLAVE_SCL_PIN, GPIO_FUNC_I2C); // Seteo el GPIO en modo I2C
    gpio_pull_up(I2C_SLAVE_SCL_PIN);

    i2c_init(i2c0, I2C_BAUDRATE); // Inicializo el canal I2C0 con su respectiva velocidad de transferencia

    i2c_slave_init(i2c0, I2C_SLAVE_ADDRESS, &i2c_slave_handler); // Inicio el manejador del esclavo y le asigno su dirección de memoria
}

int main(){
    stdio_init_all();
    puts("\nI2C slave first test");

    setup_slave();
    while (true)
    {
        tight_loop_contents();
    }
    
}