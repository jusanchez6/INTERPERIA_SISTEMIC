# Set-up de VIM3 headless

## Tabla de Contenidos
- [Set-up de VIM3 headless](#set-up-de-vim3-headless)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Instalación de la imagen de Ubuntu](#instalación-de-la-imagen-de-ubuntu)
  - [Conexión a Internet y set-up de la IP estática](#conexión-a-internet-y-set-up-de-la-ip-estática)
  - [Port-forwarding para la IP pública](#port-forwarding-para-la-ip-pública)
  - [Acceso remoto con VSCode](#acceso-remoto-con-vscode)
  - [Anotaciones del uso de server](#anotaciones-del-uso-de-server)
    - [Descarga del modelo de Imagen](#descarga-del-modelo-de-imagen)


## Instalación de la imagen de Ubuntu
Esta parte es análoga  a la que se muestra en la [documentación principal](../README.md#instalación-de-la-imagen-de-ubuntu) eligiendo esta ver la opción server `vim3-ubuntu-24.04-server-linux-5.15-fenix-1.6.9-240618.img.xz`, al ser la misma versión de la que se trabaja con gnome, debería funcionar de manera correcta con el hardware y software implementado. (Hay que revisar la versión que vaya a funcionar, voy a probar el uso de la npu con 20.04, pero si no, se trabaja con la GPU en 24.04).

En caso de que Oowow no funcione también se puede seguir este tutorial mediante [USB](https://docs.khadas.com/products/sbc/vim3/install-os/install-os-into-emmc-via-usb-tool#vim33l-install-os-into-emmc-via-usb-flash-tool).

Es posible tambien seguir este [tutorial](https://www.youtube.com/watch?v=CHXrHLNiai0) para la instalación de la imagen, al igual que dejar de una vez la IP estática sin tener necesidad de conectar la VIM3 a un monitor y teclado, sin embargo, por facilidad y conocimiento del ambiente, se va a hacer el set-up con estos accesorios.

## Conexión a Internet y set-up de la IP estática
Para eventualmente generar una conexión SSH con la máquina local, se requiere que la VIM3 tenga una IP estática, para no tener que cambiar esta dirección cada vez que se haga la conexión.

Para conectar a internet mediante wifi se siguen los pasos denotados por la documentación [oficial de Khadas](https://docs.khadas.com/products/sbc/vim3/configurations/rsdb), en primer lugar se revisan las redes disponibles con:
```
nmcli d wifi list
```
Se cifra la contraseña para ingresarla por la línea de comando, donde your_ssid es el nombre de la red y your_password es la contraseña de esta:
```
wpa_passphrase your_ssid your_password
```
Se debe guardar el texto que se genera en este comando para establecer la conexión, ingresándolo en el espacio de number_text, aquí se toma wlan0 como libre para hacer la conexión, sin embargo también se puede utilizar wlan1:
```
sudo nmcli d wifi connect your_ssid password number_text wep-key-type key ifname wlan0
```
Se puede revisar la conexión con `ifconfig`.

En caso de hacer la conexión por ethernet, solo se hace algo análogo a esta parte de establecer la IP estática, para más información, este artículo se usó de [referencia](https://www.freecodecamp.org/news/setting-a-static-ip-in-ubuntu-linux-ip-address-tutorial/).
En primer lugar, se entra a `etc/netplan` (Si no se encuentra, se debe aplicar `sudo apt install netplan.io`) desde root en la VIM3. Allí, se puede agregar un archivo que tenga prioridad sobre los otros en orden alfabético o se modifica el archivo creado por lo pasos anteriores (Se revisa su existencia con `ls`) usando `sudo nano nombre_del_archivo.yaml` se busca tener una estructura similar a la siguiente, aunque es bueno revisar la documentación de netplan para estos motivos:
```
wifis:
     wlan0:
       dhcp4: false
       addresses: [192.186.0.254/24]
       gateway4: 192.168.0.1
       nameservers:
           addresses: [8.8.8.8,8.8.8.4]
```
En donde el primer addresses es la IP estática que se busca indicar y el gateway es el gateway predeterminado de la red (Recordar que esta IP tiene que seguir con el campo libre de IPs que se presentan teniendo el IP de la red y la máscara de red). Para aplicar los cambios se aplica en command line:
```
sudo netplan try
```
Si este comando no genera ningún problema también es posible revisar la conexión a internet con un ping:
```
sudo ping -c 4 www.google.com
```

## Port-forwarding para la IP pública
Esta parte se detalla de manera más concreta en este [artículo](https://medium.com/@moligninip/how-to-connect-to-your-home-laptop-from-anywhere-with-ssh-604a7aee26a5). El port-forwarding se realiza debido a que la IP que tenemos para la máquina local solo funciona cuando ambas máquinas están conectadas a la misma red, para tener conexión desde diferentes redes, se debe vincular un puerto de la IP pública de la red al puerto de SSH de la IP privada de la máquina remota (VIM3). Para esto se debe entrar desde la máquina local desde un buscador a la IP privada del router (E.g. http://192.168.0.1) allí se ingresa el usuario y contraseña de este (Este par suelen ser admin admin). Tras entrar se hace el cambio explicado en esta página, buscando la ventana de port forwarding (Usualmente este está bajo Firewall o Advanced). Allí se pide el Inbound o External Port, que sería el puerto de entrada de la IP pública, la IP privada de la máquina remota, y el Local o Internal Port que es el puerto al que se accede al SSH de la máquina local, este siempre es 22, el external port puede ser cualquier puerto libre (Mayor a 1024) o el mismo 22 si se tiene solo una máquina remota en la misma red.

Adicionalmente se pide el protocolo a usar, se selecciona ambos o both (UDP Y TCP). Tras esto es posible acceder por la IP pública de la red a la máquina remota desde SSH.

Para hacer el acceso de la universidad es necesario hablar con el profesor Germán para abrir el port necesario.

## Acceso remoto con VSCode

Para el acceso de manera remota a la VIM3 se utilizará la extensión Remote Development, por lo que es necesario descargarla antes de hacer la conexión.
Se utiliza el siguiente artículo como [referencia](https://www.raspberrypi.com/news/coding-on-raspberry-pi-remotely-with-visual-studio-code/
). 

Se siguen estos pasos para conectar desde VSCode:
- Se presiona el botón en la esquina inferior izquierda titulado Open a Remote Window.
- Se elige Connect to Host.
- Seleccionar Add New SSH Host...
- Se escribe `ssh <username>@<ip address>` donde `<username>` sería el nombre de usuario de la máquina remota (Usualmente es khadas) y `<ip address>` sería la dirección IP configurada, ya sea la pública o la privada, con la excepción para la pública de la necesidad de agregar el número de puerto así: `ssh -p <port_number> <username>@<ip address>`.
- Se elige una configuración de SSH, en este caso se puede elegir cualquiera.
- En el menú de la izquiera de la ventana se elige Remote Explorer, se busca la IP específicada y se presiona la opción en hover "Connect in new Window", después de esto se pide la contraseña del usuario y finalmente se tiene el acceso remoto de la VIM3.

## Anotaciones del uso de server

Aquí van las soluciones de los problemas que se generen siguiendo el tutorial principal.

### Descarga del modelo de Imagen
Si bien hay bastante maneras para hacer esto, como se tiene que estos archivos tienen acceso restringido, esto se puede realizar generando un token de autorización mediante [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) de la siguiente manera:
- En la parte que dice *Select & authorize APIs* se elige *Drive API v3* y luego *https://www.googleapis.com/auth/drive.readonly*, después se presiona el botón *Authorize APIs* que lleva a la autenticación del usuario.
- En la parte *Exchange authorization code for tokens* se presiona en primer lugar el botón con el mismo nombre y luego se copia el access token que aparece abajo, notar que este tiene un tiempo de expiración, por lo que si se expira se tiene que hacer el refresco de este.

Finalmente se descarga el archivo desde la VIM3 en consola:
```
curl -H "Authorization: Bearer <access_token>" https://www.googleapis.com/drive/v3/files/<file_id>?alt=media -o <file_name>
```
Donde el `<access_token>` es el access token mencionado antes, `<file_id>` es el campo de ID que aparece en el link para compartir el archivo, y `<file_name>` es el nombre del archivo a descargar (En este caso sería `model_Vgg16_60_weapons`).

Para mayor claridad, se puede revisar el siguiente [link](https://www.baeldung.com/linux/download-large-file-gdrive-cli).
