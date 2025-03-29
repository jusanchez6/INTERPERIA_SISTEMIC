#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdint.h>

#define I2C_DEVICE "/dev/i2c-3" // Reemplaza con el número de I2C correcto
#define I2C_SLAVE_ADDRESS 0x17

int main() {
    int file;
    char buf[32];

    // Abrir el dispositivo I2C
    if ((file = open(I2C_DEVICE, O_RDWR)) < 0) {
        perror("Failed to open the i2c bus");
        exit(1);
    }

    // Configurar la dirección del esclavo
    if (ioctl(file, I2C_SLAVE, I2C_SLAVE_ADDRESS) < 0) {
        perror("Failed to acquire bus access and/or talk to slave");
        exit(1);
    }

    for (uint8_t mem_address = 0;; mem_address = (mem_address + 32) % 256) {
        char msg[32];
        snprintf(msg, sizeof(msg), "Hello, I2C slave! - 0x%02X", mem_address);
        uint8_t msg_len = strlen(msg);

        buf[0] = mem_address;
        memcpy(buf + 1, msg, msg_len);
        
        // Escribir mensaje en la dirección de memoria del esclavo
        if (write(file, buf, 1 + msg_len) != 1 + msg_len) {
            perror("Failed to write to the i2c bus");
            continue;
        }

        printf("Write at 0x%02X: '%s'\n", mem_address, msg);

        // Leer datos del esclavo
        if (write(file, buf, 1) != 1) {
            perror("Failed to set read address");
            continue;
        }

        // Leer parcialmente
        uint8_t split = 5;
        if (read(file, buf, split) != split) {
            perror("Failed to read from the i2c bus");
            continue;
        }
        buf[split] = '\0';
        printf("Read  at 0x%02X: '%s'\n", mem_address, buf);

        if (read(file, buf, msg_len - split) != msg_len - split) {
            perror("Failed to read remaining from the i2c bus");
            continue;
        }
        buf[msg_len - split] = '\0';
        printf("Read  at 0x%02X: '%s'\n", mem_address + split, buf);

        sleep(2); // Espera antes de la siguiente iteración
    }

    close(file);
    return 0;
}
