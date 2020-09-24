import sys
import textwrap

import click
import requests
import tabulate

import configuration


@click.group()
def cli():
    pass


@click.group()
def orders():
    pass

def get_url(url):
    config = configuration.load_config()
    jwt = config["DEFAULT"].get("jwt", None)
    if not jwt:
        print("You need to login first")

    order_req = requests.get(url, headers={"Authorization":f"Bearer {jwt}"})
    if not order_req.ok:
        print("Error in request:", order_req.text)
        sys.exit(1)

    orders = order_req.json()
    return orders

@click.command("list")
def orders_list():
    orders = get_url("https://api.aceandtate.com/api/me/orders")
    for order in orders:
        print(order["number"])
        print(f"\tStatus: {order['status']} - {order['sub_status']}")
        print(f"\tDelivery between {order['delivery_window']['min']} and {order['delivery_window']['max']}")
        print("\tItems:")
        for item in order["regular_lines"]:
            print(f"\t\tName: {item['variant']['name']}")
            print(f"\t\tColor: {item['variant']['color']}")
            prescription = item['line_item_prescription']
            print(f"\t\tPrescription: {prescription['prescription_type']}")
            table = [
                ["", "Left", "Right"],
                ["Sphere", prescription['l_sphere'], prescription['r_sphere']],
                ["Cylinder", prescription['l_cylinder'], prescription['r_cylinder']],
                ["Axis", prescription['l_axis'], prescription['r_axis']],
                ["Pupillary Distance", prescription['l_pupillary_distance'], prescription["r_pupillary_distance"]],
            ]
            print(textwrap.indent(tabulate.tabulate(table), prefix="\t\t"))

@click.command()
@click.argument("email")
@click.argument("password")
def login(email, password):
    print(f"Logging in as {email}")
    login_req = requests.post(
        "https://api.aceandtate.com/api/login",
        json={"auth": {"email": email, "password": password}},
    )
    if not login_req.ok:
        print("Error logging in:", login_req.text)
        sys.exit(1)

    print("Login successful")
    jwt = login_req.json()['jwt']
    config = configuration.load_config()
    config["DEFAULT"]["jwt"] = jwt
    configuration.save_config(config)



@click.group()
def prescriptions():
    pass

@click.command("list")
def prescriptions_list():
    prescriptions = get_url("https://api.aceandtate.com/api/me/prescriptions")
    for prescription in prescriptions:
        print(f"Prescription: {prescription['prescription_type']}")
        print(f"\tCreated at: {prescription['created_at']}")
        table = [
            ["", "Left", "Right"],
            ["Sphere", prescription['l_sphere'], prescription['r_sphere']],
            ["Cylinder", prescription['l_cylinder'], prescription['r_cylinder']],
            ["Axis", prescription['l_axis'], prescription['r_axis']],
            ["Pupillary Distance", prescription['l_pupillary_distance'], prescription["r_pupillary_distance"]],
        ]
        print(textwrap.indent(tabulate.tabulate(table), prefix="\t"))


# cli.add_command(initdb)
# cli.add_command(dropdb)
cli.add_command(login)
cli.add_command(orders)
cli.add_command(prescriptions)


orders.add_command(orders_list)

prescriptions.add_command(prescriptions_list)
if __name__ == "__main__":
    cli()
