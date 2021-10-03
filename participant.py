import signal
import sqlite3

from click import argument, command, confirm, echo, group, prompt, secho, style

con = sqlite3.connect('participants.db')
cur = con.cursor()


def sigint_handler(signum, frame):
    secho("\nEjecución finalizada", fg="yellow")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


def create_table():
    cur.execute("""CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni INTEGER UNIQUE,
    first_name VARCHAR(255),
    middle_name VARCHAR(255),
    paternal_surname VARCHAR(255),
    maternal_surname VARCHAR(255),
    age INTEGER
    )""")
    con.commit()


create_table()


@group()
def cli():
    pass


@command()
def fill():
    try:
        cur.execute("""INSERT INTO participants (dni, first_name, middle_name, paternal_surname, maternal_surname, age) VALUES
        (12345676, "MONICA","FABIOLA","GARCIA","SARAVIA", 18),
        (12345677, "WILFREDO","","HUANCOLLO","QUISPE", 19),
        (12345678, "JOHNNIE","JESUS","MALCA","MALCA", 20),
        (12345679, "SERGIO","IVAN","PEÑA","ESPINO", 21),
        (12345680, "JOHAN","HANS","QUINTOS","ROJAS", 22)
        """)
        con.commit()
        secho("Llenado correctamente", fg="green")
    except sqlite3.Error as e:
        if e.args[0] == "UNIQUE constraint failed: participants.dni":
            secho("Los datos ya existen", fg="red")
        else:
            secho(e, fb="red")


@command()
def create():
    echo(f'Para cancelar el proceso presione {style("CTRL + C", fg="yellow")}')

    new_participant = {}

    while True:
        new_participant["dni"] = prompt(style("DNI", fg="cyan"), type=int)

        if confirm('El DNI no se podrá actualizar. ¿Desea continuar?', default=True):
            if bool(cur.execute("SELECT * FROM participants WHERE dni=:dni", new_participant).fetchone()):
                secho("El DNI ya existe", fg="red")
            else:
                break

    new_participant["first_name"] = prompt(style("Primer nombre", fg="cyan"))
    new_participant["middle_name"] = prompt(style("Segundo nombre", fg="cyan"))
    new_participant["paternal_surname"] = prompt(style("Apellido paterno", fg="cyan"))
    new_participant["maternal_surname"] = prompt(style("Apellio materno", fg="cyan"))
    new_participant["age"] = prompt(style("Edad", fg="cyan"), type=int)

    try:
        cur.execute("""INSERT INTO participants (dni, first_name, middle_name, paternal_surname, maternal_surname, age) VALUES
        (:dni, :first_name, :middle_name, :paternal_surname, :maternal_surname, :age)""", new_participant)
        con.commit()
        secho("Creado correctamente.", fg="green")
    except sqlite3.Error as e:
        secho(e, fg="red")


@command()
@argument("dni", type=int)
def read(dni):
    try:
        participant = cur.execute("SELECT * FROM participants WHERE dni=:dni", {"dni": dni}).fetchone()
        if bool(participant):
            echo(style("ID: ", fg="cyan") + str(participant[0]))
            echo(style("DNI: ", fg="cyan") + str(participant[1]))
            echo(style("Nombres: ", fg="cyan") + participant[2] + " " + participant[3])
            echo(style("Apellidos: ", fg="cyan") + participant[4] + " " + participant[5])
            echo(style("Edad: ", fg="cyan") + str(participant[6]))
            secho("Leído correctamente.", fg="green")
        else:
            secho("No hay coincidencias", fg="red")
    except sqlite3.Error as e:
        secho(e, fg="red")


@command()
@argument("dni", type=int)
def update(dni):
    participant = cur.execute("SELECT * FROM participants WHERE dni=:dni", {"dni": dni}).fetchone()
    if bool(participant):
        echo(f'Para cancelar el proceso presione {style("CTRL + C", fg="yellow")}')

        updated_data = {}
        updated_data["dni"] = dni
        updated_data["first_name"] = prompt(style("Primer nombre", fg="cyan"), default=participant[2])
        updated_data["middle_name"] = prompt(style("Segundo nombre", fg="cyan"), default=participant[3])
        updated_data["paternal_surname"] = prompt(style("Apellido paterno", fg="cyan"), default=participant[4])
        updated_data["maternal_surname"] = prompt(style("Apellio materno", fg="cyan"), default=participant[5])
        updated_data["age"] = prompt(style("Edad", fg="cyan"), type=int,  default=participant[6])

        try:
            cur.execute("""UPDATE participants
            SET first_name=:first_name,
            middle_name=:middle_name,
            paternal_surname=:paternal_surname,
            maternal_surname=:maternal_surname,
            age=:age
            WHERE dni=:dni""", updated_data)
            con.commit()
            secho("Actualizado correctamente.", fg="green")
        except sqlite3.Error as e:
            secho(e, fg="red")
    else:
        secho("No hay coincidencias", fg="red")


@command()
@argument("dni", type=int)
def delete(dni):
    participant = cur.execute("SELECT * FROM participants WHERE dni=:dni", {"dni": dni}).fetchone()
    if bool(participant):
        if confirm('El registro no se podrá recuperar. ¿Desea continuar?', default=True):
            try:
                cur.execute("DELETE FROM participants WHERE dni=:dni", {"dni": dni})
                con.commit()
                secho("Eliminado correctamente.", fg="green")
            except sqlite3.Error as e:
                secho(e, fg="red")
    else:
        secho("No hay coincidencias", fg="red")


@command()
def generate():
    participants = cur.execute("SELECT * FROM participants").fetchall()

    for participant in participants:
        first_name = style(participant[2].capitalize() * 4, fg="cyan")
        middle_name = participant[3].capitalize() * 3
        paternal_surname = style(participant[4].capitalize() * 2, fg="cyan")
        maternal_surname = participant[5].capitalize()

        echo(f'{first_name} {middle_name} {paternal_surname} {maternal_surname}')


cli.add_command(fill)
cli.add_command(create)
cli.add_command(read)
cli.add_command(update)
cli.add_command(delete)
cli.add_command(generate)

if __name__ == '__main__':
    cli()
    con.close()
