Debemos instalar Tectonic desde una direccion especifica y según la version que querramos manejar:

- https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.15.0
- tectonic-0.15.0-x86_64-pc-windows-msvc.zip

Luego descomprimimos el .zip y el archivo .exe lo añadimos a una carpeta nueva en Program Files en el disco

- En mi caso: C:\Program Files\Tectonic\tectonic.exe

Lo añadimos a las variables de entorno de sistema editando el path predeterminado y aplicando/aceptando los cambios

Ahora, en powershell debemos poner el siguiente comando (en caso de que usemos un entorno):

- $env:PATH += ";C:\Program Files\Tectonic"

Podemos verificar en nuestra consola con el comando:

- tectonic --version

Esto iniciara tectonic que nos ayudara a generar el PDF de salida

Para iniciar la API debemos usar:

- python -m uvicorn app.main:app --reload 