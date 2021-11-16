import json
import time
from ipaddress import IPv4Interface

import napalm
import netmiko
import paramiko
from click import command, group, secho
from tabulate import tabulate


@group()
def cli():
    pass


@command()
def paramiko_test():
    try:
        # Cargamos el archivo JSON donde tenemos la información de los dispositivos
        file = open('with-gns3/devices.json')
        devices = json.load(file)
        file.close()

        # Creamos una nueva instancia de Cliente
        client = paramiko.SSHClient()
        # Evitamos tener el error de los hosts conocidos
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Recorremos todos los dispositivos que tengamos
        for device in devices:
            # En esta variable en especial almacenaremos los comandos generados que ejecutaremos luego
            dc = []

            # Recorremos los comandos del dispositivo
            for command in device["commands"]:
                # Comprobamos si el comando es una lista para trabajarlo
                if isinstance(command, list):
                    # Comprobamos si el tipo de la fuente de datos es un Diccionario
                    if isinstance(device[command[0]], dict):
                        # Recorremos la fuente de datos para extraer las claves y valores
                        for key, value in device[command[0]].items():
                            # Recorremos todos los subcomandos menos el primero que es la fuente de datos
                            for sub_command in command[1:]:
                                # Comprobamos si el subcomando tiene una interpolación con la clave
                                if "{key}" in sub_command:
                                    # Generamos el comando interpolado
                                    dc.append(sub_command.format(key=key))
                                # Comprobamos si el subcomando tiene una interpolación con el valor
                                elif "{value}" in sub_command:
                                    # Generamos el comando interpolado
                                    dc.append(sub_command.format(
                                        value=IPv4Interface(value).with_netmask.replace("/", " "))
                                    )
                                # Si el subcomando no tiene una interpolación generamos el comando directamente
                                else:
                                    dc.append(sub_command)
                    # Comprobamos si el tipo de la fuente de datos es una Lista
                    elif isinstance(device[command[0]], list):
                        # Recorremos la fuente de datos para extraer los valores
                        for value in device[command[0]]:
                            # Recorremos todos los subcomandos menos el primero que es la fuente de datos
                            for sub_command in command[1:]:
                                # Comprobamos si el subcomando tiene una interpolación con el valor
                                if "{value}" in sub_command:
                                    # Generamos el comando interpolado
                                    dc.append(sub_command.format(
                                        value=IPv4Interface(
                                            device["interfaces"][value]
                                        ).network.with_hostmask.replace("/", " ")
                                    ))
                                # Si el subcomando no tiene una interpolación generamos el comando directamente
                                else:
                                    dc.append(sub_command)
                # Si el comando no era una lista generamos el comando directamente
                else:
                    dc.append(command)

            secho(f'Conectando el Router {device["ip"]} con Paramiko...', fg="cyan")
            # Nos conectamos con el dispositivo
            client.connect(hostname=device["ip"], username=device["user"], password=device["password"])
            # Abrimos el shell
            shell = client.invoke_shell()

            # Recorremos todos los comandos generados y lo enviamos uno a uno
            for c in dc:
                shell.send(f'{c}\n')

            # Dormimos el hilo de ejecución 5 segundos
            time.sleep(5)
            # Capturamos la salida
            output = shell.recv(3500)
            # Imprimimos la salida pero antes convertimos el output en un string
            print(output.decode())
            # Nos desconectamos del dispositivo
            client.close()
            print("")
    except paramiko.ssh_exception.AuthenticationException:
        secho("El usuario o la contraseña son incorrectos", fg="red")
    except paramiko.ssh_exception.NoValidConnectionsError:
        secho("No se pudo conectar verifique la IP del dispositivo", fg="red")
    except Exception as e:
        secho(e, fg="red")


@command()
def napalm_test():
    try:
        # Seleccionamos el controlador adecuado
        driver_ios = napalm.get_network_driver("ios")

        # Cargamos el archivo JSON donde tenemos la información de los dispositivos y extraemos los datos de conexión
        file = open('with-gns3/devices.json')
        devices = [driver_ios(hostname=i["ip"], username=i["user"], password=i["password"]) for i in json.load(file)]
        file.close()

        # Creamos la lista para las tablas con los encabezados incluidos
        devices_table = [["HOSTNAME", "VENDOR", "MODEL", "UPTIME", "SERIAL NUMBER"]]

        # Recorremos todos los dispositivos que tengamos
        for device in devices:
            secho(f'Conectando el Router {device.hostname} con Napalm...', fg="cyan")

            # Nos conectamos con el dispositivo
            device.open()
            secho("Se están obteniendo los datos sobre el dispositivo...", fg="cyan")
            # Obtenemos los datos del dispositivo
            device_facts = device.get_facts()

            # Agregamos la información generada a nuestra lista para mostrarlo como tabla
            devices_table.append([
                device_facts["hostname"],
                device_facts["vendor"],
                device_facts["model"],
                device_facts["uptime"],
                device_facts["serial_number"]
            ])

            # Nos desconectamos del dispositivo
            device.close()
            secho("Terminado!\n", fg="green")

        # Imprimimos en una tabla los datos almacenados en la lista
        print(tabulate(devices_table, headers="firstrow"))
    except netmiko.ssh_exception.NetmikoAuthenticationException:
        secho("El usuario o la contraseña son incorrectos", fg="red")
    except napalm.base.exceptions.ConnectionException:
        secho("No se pudo conectar verifique la IP del dispositivo", fg="red")
    except Exception as e:
        secho(e, fg="red")


@command()
def connection_test():
    try:
        # Cargamos el archivo JSON donde tenemos la información de los dispositivos
        file = open('with-gns3/devices.json')
        devices = json.load(file)
        file.close()

        # Creamos una nueva instancia de Cliente
        client = paramiko.SSHClient()
        # Evitamos tener el error de los hosts conocidos
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Recorremos todos los dispositivos que tengamos
        for device in devices:
            secho(f'Tabla de enrutamiento de {device["ip"]} con Paramiko...', fg="cyan")
            # Nos conectamos con el dispositivo
            client.connect(hostname=device["ip"], username=device["user"], password=device["password"])
            # Abrimos el shell
            shell = client.invoke_shell()
            # Enviamos el comando
            shell.send(f'show ip route\n')

            # Dormimos el hilo de ejecución 5 segundos
            time.sleep(5)
            # Capturamos la salida
            output = shell.recv(3500)
            # Convertimos el output en un string
            decoded_output = output.decode()

            # Extraemos solo la parte de las rutas y la imprimimos
            for routes in decoded_output.split("\r\n")[12:-1]:
                print(routes)

            # Nos desconectamos del dispositivo
            client.close()
            print("")
    except paramiko.ssh_exception.AuthenticationException:
        secho("El usuario o la contraseña son incorrectos", fg="red")
    except paramiko.ssh_exception.NoValidConnectionsError:
        secho("No se pudo conectar verifique la IP del dispositivo", fg="red")
    except Exception as e:
        secho(e, fg="red")


cli.add_command(paramiko_test)
cli.add_command(napalm_test)
cli.add_command(connection_test)

if __name__ == '__main__':
    cli()
