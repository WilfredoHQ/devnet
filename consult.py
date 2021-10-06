import signal
from ipaddress import IPv4Address, IPv4Network

from click import argument, command, group, secho


def sigint_handler(signum, frame):
    secho("\nEjecución finalizada", fg="yellow")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


@group()
def cli():
    pass


@command()
@argument("port_number", type=int)
def port(port_number: int):
    if port_number in range(0, 1024):
        secho("Puerto bien conocido", fg="cyan")
    elif port_number in range(1024, 49152):
        secho("Puerto registrado", fg="cyan")
    elif port_number in range(49152, 65535):
        secho("Puerto privado", fg="cyan")
    else:
        secho("Fuera de rango", fg="red")


@command()
@argument("ip_address", type=IPv4Address)
def ip(ip_address: IPv4Address):
    if ip_address.is_global:
        secho("IP Pública", fg="cyan")
    elif ip_address.is_private:
        secho("IP Privada", fg="cyan")

    if ip_address in IPv4Network("0.0.0.0/1"):
        secho("Clase A", fg="cyan")
    elif ip_address in IPv4Network("128.0.0.0/2"):
        secho("Clase B", fg="cyan")
    elif ip_address in IPv4Network("192.0.0.0/3"):
        secho("Clase C", fg="cyan")
    elif ip_address in IPv4Network("224.0.0.0/4"):
        secho("Clase D", fg="cyan")
    elif ip_address in IPv4Network("240.0.0.0/4"):
        secho("Clase E", fg="cyan")


cli.add_command(port)
cli.add_command(ip)

if __name__ == '__main__':
    cli()
