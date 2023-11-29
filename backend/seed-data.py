#!/opt/homebrew/bin/python3

# TODO: add support for pagination
# TODO: add support for other test data (catalog, orders, etc.)

import argparse
import json
import os
import sys
import uuid
import random
from square.client import Client
from dotenv import load_dotenv
from datetime import datetime
import inquirer
from ratelimit import limits, sleep_and_retry
from faker import Faker


SEED_DATA_REFERENCE_ID = "SEED_DATA_APP"

load_dotenv()
with open('test-data.json', 'r') as test_data:
    seed_data = json.load(test_data)

seeded_customers = {}
seeded_orders = {}
seeded_team_members = {}
team_ids_for_payment = []
location_id = ""

final_print_out = {
    "payment_ids": [],
    "shift_ids": [],
    "wage_info": [],
}

# instantiate faker library
fake = Faker('en_US')

client = Client(
    access_token=os.environ['SQUARE_SANDBOX_ACCESS_TOKEN'],
    environment='sandbox',
    custom_url='https://connect.squareupsandbox.com')


def seed_team_members():
    global seed_data

    create_team_members()
    create_wages()
    create_shifts()


def create_team_members():
    global seeded_team_members
    body = {"team_members": {}}
    team_range = 12
    print("Creating {} team members".format(team_range))
    for _ in range(team_range):
        key = uuid.uuid1().hex
        body["team_members"][key] = {}
        body["team_members"][key]["team_member"] = {
            "reference_id": SEED_DATA_REFERENCE_ID,
            "status": "ACTIVE",
            "email_address": fake.email(),
            "family_name": fake.last_name(),
            "given_name": fake.first_name(),
            "phone_number": "+12533350168",
            "assigned_locations": {
                "assignment_type": "EXPLICIT_LOCATIONS",
                "location_ids": [location_id]
            }
        }

    try:
        result = client.team.bulk_create_team_members(body)
        seeded_team_members = {
            data['team_member']['id']: data['team_member']
            for _, data in result.body['team_members'].items()
        }

    except:
        oops(result.errors)

    final_print_out["team_member_ids"] = [
        key for key in seeded_team_members.keys()]
    print('Creating team members complete\n')


def create_wages():
    print('Creating {} wages'.format(len(seeded_team_members)))
    i = 0
    for key, _ in seeded_team_members.items():
        # Pick some non-tipping jobs
        body = ""
        if i % len(seeded_team_members.items()) == 0:
            body = {
                "wage_setting": {
                    "is_overtime_exempt": False,
                    "job_assignments": [seed_data['jobs']['manager']],
                    "team_member_id": key
                }
            }
        elif i % 3:
            body = {
                "wage_setting": {
                    "is_overtime_exempt": False,
                    "job_assignments": [random.choice(seed_data['jobs']['staff'])],
                    "team_member_id": key
                }
            }
        else:
            body = {
                "wage_setting": {
                    "is_overtime_exempt": False,
                    "job_assignments": random.sample(seed_data['jobs']['serving'], 2),
                    "team_member_id": key
                }
            }
            team_ids_for_payment.append(key)
        i += 1
        try:
            wage_result = client.team.update_wage_setting(
                team_member_id=key,
                body=body
            )
            seeded_team_members[key]['job_assignments'] = wage_result.body['wage_setting']['job_assignments']
            final_print_out['wage_info'].append(
                wage_result.body['wage_setting'])
        except:
            oops(wage_result.errors)
    print('Completed creating wages\n')


def create_shifts():
    time_format = "%Y-%m-%dT%H:%M:%SZ"  # RFC 3339 format

    current_datetime = datetime.now()
    current_hour = current_datetime.hour
    current_day = current_datetime.day
    current_month = current_datetime.month
    current_year = current_datetime.year

    print('Creating {} shifts'.format(len(seeded_team_members)))
    for key, _ in seeded_team_members.items():
        start_time = datetime(current_year, current_month, current_day,
                              current_hour - random.randint(0, 4), 0).strftime(time_format)
        end_time = datetime(current_year, current_month, current_day,
                            current_hour + 4, 0).strftime(time_format)
        random_job = random.choice(seeded_team_members[key]['job_assignments'])
        random_job['title'] = random_job['job_title']
        random_job['tip_eligible'] = False if random_job['job_title'] == 'Manager' else True
        body = {
            "idempotency_key": uuid.uuid1().hex,
            "shift": {
                "location_id": location_id,
                "start_at": start_time,
                "end_at": end_time,
                "wage": random_job,
                "status": "CLOSED",
                "team_member_id": key
            }
        }

        try:
            result = client.labor.create_shift(body)
            seeded_team_members[key]['shift'] = result.body['shift']
            final_print_out['shift_ids'].append(result.body['shift']['id'])
        except:
            oops(result.errors)
    print('Completed creating shifts\n')


def seed_customers():
    customer_range = 50
    print('Creating {} customers...'.format(customer_range))
    for _ in range(customer_range):
        key = uuid.uuid1().hex
        body = {
            "idempotency_key": key,
            "reference_id": SEED_DATA_REFERENCE_ID,
            "email_address": fake.email(),
            "family_name": fake.last_name(),
            "given_name": fake.first_name(),
            "phone_number": "+12533350168",
        }
        call_customer_api(body)
    final_print_out["customer_ids"] = [key for key in seeded_customers.keys()]
    print('Completed created customers\n')


@sleep_and_retry
@limits(calls=4, period=2)
def call_customer_api(body):
    try:
        result = client.customers.create_customer(body)
        seeded_customers[result.body['customer']
                         ['id']] = result.body['customer']

    except:
        oops(result.errors)


def seed_orders():
    global seed_data
    print('Creating {} orders...'.format(len(seeded_customers)))
    for _, value in seeded_customers.items():
        ticket_name_string = "Table " + \
            str(random.randrange(1, 9, 1)) + " - " + value["family_name"]
        body = {}
        body["order"] = {}
        body["idempotency_key"] = uuid.uuid1().hex
        body["order"]["line_items"] = random.sample(
            seed_data["line_items"], random.randint(1, 10))
        body["order"]["location_id"] = location_id
        body["order"]["reference_id"] = SEED_DATA_REFERENCE_ID
        body["order"]["customer_id"] = value["id"]
        body["order"]["ticket_name"] = ticket_name_string
        try:
            result = client.orders.create_order(body)
            if result.is_success():
                seeded_orders[result.body['order']
                              ['id']] = result.body['order']
            else:
                print("   Failed to created order:")

        except Exception:
            oops(result.errors)
    final_print_out["order_ids"] = [key for key in seeded_orders.keys()]
    print('Completed created orders\n')


def calculate_tip(total_money):
    # Random tip percentage between 10% and 25%
    tip_percentage = random.randint(10, 25) / 100
    tip = int(total_money * tip_percentage)  # Calculate tip amount in cents
    return tip


def seed_payments():
    print("Creating {} payments...".format(len(seeded_orders)))
    for _, value in seeded_orders.items():

        # sum up the value of each line item in our order
        total_money = sum(obj["total_money"]["amount"]
                          for obj in value["line_items"])

        # calculate a tip for the order - returns the tip in cents
        tip = calculate_tip(total_money)
        payment = {
            "source_id": "cnon:card-nonce-ok",
            "idempotency_key": uuid.uuid1().hex,
            "amount_money": {
                "amount": total_money,
                "currency": "USD"
            },
            "tip_money": {
                "amount":  tip,
                "currency": "USD"
            },
            "autocomplete": True,
            "customer_id": value["customer_id"],
            # Grab a random team member who would be the one closing a payment
            # Server or bartender..
            "team_member_id": random.choice(team_ids_for_payment),
            "reference_id": SEED_DATA_REFERENCE_ID,
            "order_id": value["id"],
            "location_id": location_id,
        }

        try:
            result = client.payments.create_payment(payment)
            if result.is_success() and result.body:
                final_print_out["payment_ids"].append(
                    result.body["payment"]["id"])
        except Exception:
            oops(result.errors)
    print('Completed creating payments\n')


def delete_orders():
    print("Deleting Orders")
    try:
        result = client.orders.search_orders(
            body={
                "location_ids": [location_id],
                "query": {
                    "filter": {
                        "state_filter": {
                            "states": [
                                "OPEN",
                            ]
                        }
                    },
                    "limit": 100
                }
            }
        )
        if result.is_success() and result.body:
            for order in result.body['orders']:
                try:
                    result_cancel = client.orders.update_order(
                        order_id=order['id'],
                        body={
                            "order": {
                                "location_id": location_id,
                                "state": "CANCELED",
                                "version": order["version"]
                            },
                            "idempotency_key": uuid.uuid1().hex
                        }
                    )
                    if not result_cancel.is_success():
                        print("failed to cancel order:", order['id'], "\n")

                except Exception:
                    oops(result_cancel.errors)
        elif result.is_success() and not result.body:
            print("No open orders\n")

        else:
            print("No open orders\n")
    except Exception:
        oops(result.errors)
    print('Completed deleting orders\n')


def delete_team_members():
    print("Deactivating team members")
    try:
        result = client.team.search_team_members(
            body={
                "query": {
                    "filter": {
                        "location_ids": [
                            location_id
                        ],
                        "status": "ACTIVE",
                        "is_owner": False
                    }
                }
            }
        )
        # This filter will allow "is_owner": False when location is "All current and future locations"
        if result.is_success():
            if 'team_members' in result.body:
                updated_action = False
                for t in result.body['team_members']:
                    try:
                        # Check for that owner who passed through the filter because of location setting
                        if t["is_owner"] == False and t["status"] == "ACTIVE":
                            result_2 = client.team.update_team_member(
                                team_member_id=t['id'],
                                body={
                                    "team_member": {
                                        "status": "INACTIVE"
                                    }
                                }
                            )
                            updated_action = True

                    except Exception:
                        oops(result_2.errors)
                if updated_action == False:
                    print("No active team members found")
            elif not result.body:
                print("No active team members found")
    except Exception:
        oops(result.errors)
    print('Completed deactivating team members\n')


def delete_customers():
    print('Deleting customers')
    try:
        result = client.customers.search_customers(
            body={"query": {"filter": {"reference_id": {"exact": SEED_DATA_REFERENCE_ID}}}})
        if result.is_success():
            if 'customers' in result.body:
                for c in result.body['customers']:
                    try:
                        result_2 = client.customers.delete_customer(c['id'])
                    except Exception:
                        oops(result_2.errors)
            else:
                print("No customers found")
    except Exception:
        oops(result.errors)
    print('Completed deleting customers\n')


def delete_shifts():
    print("Deleting shifts")
    try:
        result = client.labor.search_shifts(
            body={
                "query": {
                    "filter": {
                        "location_ids": [
                            location_id
                        ],
                        "status": "CLOSED"
                    }
                }
            }
        )
        if result.is_success() and result.body:
            try:
                for shift in result.body["shifts"]:
                    delete_result = client.labor.delete_shift(shift["id"])
            except Exception:
                oops(delete_result.errors)
        else:
            print("No shifts found")

    except Exception:
        oops(result.errors)

    print("Completed deleting shifts\n")


def oops(errors):
    print("Exception:")
    for err in errors:
        print(f"\tcategory: {err['category']}")
        print(f"\tcode: {err['code']}")
        print(f"\tdetail: {err['detail']}")
    sys.exit(1)


def clear():
    delete_customers()
    delete_orders()
    delete_team_members()
    delete_shifts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload or delete test data',
        epilog="You can specify either --seed or --clear, but not both")
    parser.add_argument('--seed', action='store_true', help='Upload test data')
    parser.add_argument('--clear', action='store_true',
                        help='Delete test data')

    args = parser.parse_args()

    # Ask the user which location they want to use
    result = client.locations.list_locations()
    location_list = []
    location_map = {}
    for location in result.body['locations']:
        label = "{} - {}".format(location['name'], location['id'])
        location_list.append(label)
        location_map[label] = location['id']
    questions = [
        inquirer.List('location',
                      message="Which location would you like use? [Use Arrow keys and Enter to Select]",
                      choices=location_list,
                      ),
    ]

    location_id = location_map[inquirer.prompt(questions)['location']]

    if args.seed and not args.clear:
        print('---Begin Seeding Data---')
        seed_team_members()
        seed_customers()
        seed_orders()
        seed_payments()
        print('---Seed Data Complete---')
        # Serializing json
        json_object = json.dumps(final_print_out, indent=4)
        # Writing to sample.json
        with open("output.json", "w") as outfile:
            outfile.write(json_object)
        print("Created IDs written to output.json")
        sys.exit()
    elif args.clear and not args.seed:
        clear()
    else:
        parser.print_usage()
