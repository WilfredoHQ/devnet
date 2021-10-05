import signal
from ipaddress import IPv4Interface

from click import command, group, secho, style


def sigint_handler(signum, frame):
    secho("\nEjecución finalizada", fg="yellow")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


@group()
def cli():
    pass


initial_db = {
    "AR_1": {
        "Fa0/0": "193.168.0.2/28",
        "Fa1/0": "10.0.0.1/23",
        "Gig0/1/0": "172.16.0.1/20",
        "Se0/3/0": "173.16.0.2/30"
    },
    "AR_2": {
        "Gig0/0": "172.16.16.1/26",
        "Gig0/1": "193.168.0.3/28"
    },
    "AR_3": {
        "Gig0/0/0": "192.168.0.1/25",
        "Gig0/0/1": "10.0.2.1/27",
        "Se0/2/0": "173.16.0.6/30"
    },
    "AR_HUB": {
        "Fa0/0": "193.168.0.1/28",
        "Se0/0/0": "173.16.0.1/30",
        "Se0/0/1": "173.16.0.5/30"
    },

    "ASw2": {
        "Fa0/1": "",
        "Fa4/1": "",
        "Vlan1": "172.16.16.2/26"
    },
    "ASw11": {
        "Fa4/1": "",
        "Vlan1": "10.0.0.2/23"
    },
    "ASw12": {
        "Gig6/1": "",
        "Vlan1": "172.16.0.2/20"
    },
    "ASw31": {
        "Fa0/1": "",
        "Vlan1": "192.168.0.2/25"
    },
    "ASw32": {
        "Fa0/1": "",
        "Vlan1": "10.0.2.2/27"
    },
    "AC1": {
        "Gig1/0/1": "",
        "Gig1/0/2": "",
        "Gig1/0/3": "",
        "Vlan1": "193.168.0.14/28"
    }
}

links = (
    (
        ("AR_1", "Fa1/0"),
        ("ASw11", "Vlan1")
    ),
    (
        ("AR_1", "Gig0/1/0"),
        ("ASw12", "Vlan1")
    ),
    (
        ("AR_1", "Se0/3/0"),
        ("AR_HUB", "Se0/0/0")
    ),
    (
        ("AR_1", "Fa0/0"),
        ("AC1", "Vlan1")
    ),
    (
        ("AR_2", "Gig0/0"),
        ("ASw2", "Vlan1")
    ),
    (
        ("AR_2", "Gig0/1"),
        ("AC1", "Vlan1")
    ),
    (
        ("AR_3", "Se0/2/0"),
        ("AR_HUB", "Se0/0/1")
    ),
    (
        ("AR_3", "Gig0/0/0"),
        ("ASw31", "Vlan1")
    ),
    (
        ("AR_3", "Gig0/0/1"),
        ("ASw32", "Vlan1")
    ),
    (
        ("AR_HUB", "Fa0/0"),
        ("AC1", "Vlan1")
    )
)


@ command()
def test():
    for link in links:
        start_ip = IPv4Interface(initial_db[link[0][0]][link[0][1]])
        end_ip = IPv4Interface(initial_db[link[1][0]][link[1][1]])

        start_info = f'{style(link[0][0], fg="cyan")} ({link[0][1]})'
        end_info = f'{style(link[1][0], fg="cyan")} ({link[1][1]})'

        checkmark = style("✓", fg="green") if end_ip.ip in start_ip.network else style("✗", fg="red")

        msg = f'{start_info} - {end_info} {checkmark}'
        print(msg)


cli.add_command(test)

if __name__ == '__main__':
    cli()
