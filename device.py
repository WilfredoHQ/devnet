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
    echo(f'\nPara cancelar el proceso presione {style("CTRL + C", fg="yellow")}')

    with open("devices.txt", "a") as file:
        while True:
            new_device = prompt(style("Dispositivo", fg="cyan"))
            file.write(new_device + "\n")
            secho("Creado correctamente.", fg="green")


@command()
def read():
    with open("devices.txt", "r") as file:
        devices = file.readlines()

        for idx, row in enumerate(devices):
            echo(f'{style(idx, fg="cyan")} {row}'.strip())

    secho("Leído correctamente.", fg="green")


@command()
@argument("id", type=int)
def update(id: int):
    with open("devices.txt", "r") as file:
        devices = file.readlines()

        if not len(devices) <= id:
            echo(f'\nPara cancelar el proceso presione {style("CTRL + C", fg="yellow")}')
            devices[id] = prompt(style("Nuevo valor", fg="cyan"), default=devices[id].strip()) + "\n"

            with open("devices.txt", "w") as file:
                file.writelines(devices)
                secho("Actualizado correctamente.", fg="green")
        else:
            secho("No hay coincidencias", fg="red")


@command()
@argument("id", type=int)
def delete(id: int):
    with open("devices.txt", "r") as file:
        devices = file.readlines()

        if not len(devices) <= id:
            echo(f'{style(id, fg="cyan")} {devices[id]}'.strip())

            if confirm('El registro no se podrá recuperar. ¿Desea continuar?', default=True):
                del devices[id]

                with open("devices.txt", "w") as file:
                    file.writelines(devices)
                    secho("Eliminado correctamente.", fg="green")
        else:
            secho("No hay coincidencias", fg="red")


cli.add_command(create)
cli.add_command(read)
cli.add_command(update)
cli.add_command(delete)

if __name__ == '__main__':
    cli()
