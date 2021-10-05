import signal

from click import argument, command, confirm, echo, group, prompt, secho, style


def sigint_handler(signum, frame):
    secho("\nEjecución finalizada", fg="yellow")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


@group()
def cli():
    pass


@command()
def create():
    exit_commands = ["q", "quit", "end", "exit"]

    file = open("devices.txt", "a")

    echo(f'\nPara cancelar el proceso presione {style("CTRL + C", fg="yellow")}')
    echo(f'Para salir puede ingresar {style(", ".join([ec for ec in exit_commands]), fg="yellow")}')

    while True:
        new_device = prompt(style("Dispositivo", fg="cyan"))

        if new_device not in exit_commands:
            file.write(new_device + "\n")
            secho("Creado correctamente.", fg="green")
        else:
            secho("Ejecución finalizada", fg="yellow")
            break

    file.close()


@command()
def read():
    file = open("devices.txt", "r")
    devices = file.readlines()

    for idx, row in enumerate(devices):
        echo(f'{style(idx, fg="cyan")} {row}'.strip())

    secho("Leído correctamente.", fg="green")


@command()
@argument("id", type=int)
def update(id):
    file = open("devices.txt", "r")
    devices = file.readlines()

    if not len(devices) <= id:
        echo(f'\nPara cancelar el proceso presione {style("CTRL + C", fg="yellow")}')
        devices[id] = prompt(style("Nuevo valor", fg="cyan"), default=devices[id].strip()) + "\n"

        file = open("devices.txt", "w")
        file.writelines(devices)
        file.close()
        secho("Actualizado correctamente.", fg="green")
    else:
        secho("No hay coincidencias", fg="red")


@command()
@argument("id", type=int)
def delete(id):
    file = open("devices.txt", "r")
    devices = file.readlines()

    if not len(devices) <= id:
        echo(devices[id].strip())

        if confirm('El registro no se podrá recuperar. ¿Desea continuar?', default=True):
            del devices[id]

            file = open("devices.txt", "w")
            file.writelines(devices)
            file.close()
            secho("Eliminado correctamente.", fg="green")
    else:
        secho("No hay coincidencias", fg="red")


cli.add_command(create)
cli.add_command(read)
cli.add_command(update)
cli.add_command(delete)

if __name__ == '__main__':
    cli()
