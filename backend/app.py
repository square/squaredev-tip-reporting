from square.client import Client
from flask_restful import Resource, Api, reqparse
from dotenv import load_dotenv
from datetime import datetime
import os
from flask import Flask, request
import requests
import time


load_dotenv()
app = Flask(__name__)

api = Api(app)

square_client = Client(
    access_token=os.environ['SQUARE_SANDBOX_ACCESS_TOKEN'],
    environment="sandbox" if os.environ['ENVIRONMENT'] == 'development'
    else "production", )


class Locations(Resource):
    def get(self):
        result = square_client.locations.list_locations()
        return [{"name": location['name'], "id": location['id']} for location in result.body['locations']]


class Team(Resource):
    def get(self):
        # Populate our Team member data
        args = request.args
        location_id = args['location_id']
        result = square_client.team.search_team_members(
            body={
                "query": {
                    "filter": {"is_owner": False, "status": "ACTIVE", "location_ids": [location_id]}
                }
            })
        return list(
            map(
                lambda team_member: {
                    "name": f"{team_member['given_name']} {team_member['family_name']}",
                    "id": team_member['id']
                },
                result.body['team_members']
            )
        )

class TipReport(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('location_id')
        parser.add_argument('team_member_ids', action='append')
        parser.add_argument('start_date')
        parser.add_argument('end_date')
        args = parser.parse_args()
        return run_tip_report(location_id=args['location_id'],
                              team_member_ids=args['team_member_ids'],
                              start_date=args['start_date'],
                              end_date=args['end_date'])

class TeamMemberDetails(Resource):
    def get(self):
        # Populate our Team member data
        order_ids = request.args.getlist('order_id')
        return fetch_graphql(order_ids)

api.add_resource(Locations, '/locations')
api.add_resource(Team, '/team')
api.add_resource(TipReport, '/tip-report')
api.add_resource(TeamMemberDetails, '/team-member-details')


def get_payment_data(location_id,
                     start_date,
                     end_date,
                     team_member_shift_dict,
                     total_hours_worked) -> dict:

    payment_data_start = time.time()
    result = square_client.payments.list_payments(
        begin_time=start_date,
        end_time=end_date,
        location_id=location_id
    )
    team_tip_pool = 0
    if result.is_success():
        # Loop through the payments and tally the total tips for the given time frame
        for payment in result.body['payments']:
            if 'tip_money' in payment and payment['status'] == 'COMPLETED':

                team_tip_pool += payment['tip_money']['amount']
                if payment['team_member_id'] in team_member_shift_dict:
                    team_member_id = payment['team_member_id']
                    team_member_shift_dict[team_member_id]['shifts'][0].setdefault(
                        'orders', []).append(payment['order_id'])

        credit_tip_to_team_member(
            team_member_shift_dict, team_tip_pool, total_hours_worked, )

    elif result.is_error():
        payment_data = dict()
        errors = []
        for error in result.errors:
            errors.append(f"{error['category']} {error['code']} {error['detail']}")
        payment_data['errors'] = errors
    print('Time to get tips', time.time() - payment_data_start)
    return team_member_shift_dict


def get_shift_length(start_time_str, end_time_str):
    # Convert strings to datetime objects
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S%z')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S%z')

    # Calculate the time difference
    shift_length = end_time - start_time

    # Extract the hour difference
    return int(shift_length.total_seconds() / 3600)


def credit_tip_to_team_member(
        team_member_shift_dict,
        team_tip_pool,
        total_hours_worked,
) -> dict:

    # number of pennies earned per hour
    pennies_per_hour = int(team_tip_pool / total_hours_worked)
    # Loop through our team members
    for key, value in team_member_shift_dict.items():
        # Loop through the team members shifts
        team_member_shift_total = 0
        for shift in value['shifts']:
            team_member_shift_total += get_shift_length(
                shift['start_at'], shift['end_at'])
            # do the tip math
            # Increment the tip for the tippable team member
        team_member_shift_dict[key]['tips'] = pennies_per_hour * \
            team_member_shift_total
        team_member_shift_dict[key]['hours_worked'] = team_member_shift_total

    return team_member_shift_dict

def get_shifts_by_date_range(
        location_id,
        start_date,
        end_date) -> dict:
    body = {
        "query": {
            "filter": {
                "location_ids": [
                    location_id
                ],
                "start": {
                    "start_at": start_date,
                    "end_at": end_date
                }
            }
        }
    }
    result = square_client.labor.search_shifts(body)
    if result.is_success():
        return result.body
    else:
        return result.errors


def get_team_member_info(
    team_member_shift_dict
) -> dict:

    team_ids = list(team_member_shift_dict.keys())
    body = {'team_members': {}}

    # Prepare body for request
    for id in team_ids:
        body['team_members'][id] = {
            'team_member': {}
        }

    # The team api doesn't have the ability to list members with a supply of ids
    # however we can bulk update without changing data to get the information we want
    team_members_result = square_client.team.bulk_update_team_members(body)

    if team_members_result.is_success():
        team_members = team_members_result.body['team_members']
        for key, _ in team_members.items():

            # return team member data
            team_member = team_members[key]['team_member']
            data = {
                "id": key,
                'given_name': team_member['given_name']
                if 'given_name' in team_member else "",
                'family_name': team_member['family_name']
                if 'family_name' in team_member else "",
                'tips': 0,
                "shifts": team_member_shift_dict[key]['shifts']
            }
            team_member_shift_dict[key] = data
    return team_member_shift_dict


def run_tip_report(
        location_id, *,
        team_member_ids,
        start_date,
        end_date) -> dict:


    tip_report_start = time.time()
    team_member_total_hours = 0
    # Get a list of all shifts that were worked during the start and end date
    shifts_by_date_range = get_shifts_by_date_range(
        location_id=location_id,
        start_date=start_date,
        end_date=end_date)

    # Team_Member_shift_dict - this dictionary is our source of information 
    # for all app logic
    # key: team member id
    # value: {shifts: []}
    team_member_shift_dict = {}
    for shift in shifts_by_date_range['shifts']:
        team_member_id = shift['team_member_id']
        # Check if the shift was for a tippable job.
        # only include them in this list if the job is tippable
        if (shift['wage']['tip_eligible'] is True):
            # Add up shift time of all team members

            team_member_total_hours += get_shift_length(
                shift['start_at'], shift['end_at'])

            # Only create the shift dictionary for selected team members in the frontend
            if (team_member_id in team_member_ids):
                team_member_shift_dict.setdefault(
                    team_member_id, {}).setdefault('shifts', []).append(shift)

    # Go and get the team member name and put it into our dictionary object
    team_member_shift_dict = get_team_member_info(team_member_shift_dict)
    print('Time to get Team Member Data: ', time.time() - tip_report_start)

    team_member_shift_dict = get_payment_data(location_id,
                                              start_date,
                                              end_date,
                                              team_member_shift_dict,
                                              total_hours_worked=team_member_total_hours)


    print('Total Time to run tip report: ', time.time() - tip_report_start)
    return team_member_shift_dict


def fetch_graphql(ids):
    # GraphQL server endpoint

    url = 'https://connect.squareupsandbox.com/public/graphql' if os.environ[
        'ENVIRONMENT'] == 'development' else 'https://connect.squareup.com/public/graphql'

    # GraphQL query
    query = '''
        query ($merchantId: ID!, $ids: [ID!]){
            orders(
                filter: {
                    merchantId: { equalToAnyOf: [$merchantId] }
                    id: { equalToAnyOf: $ids }
                }
            ) {
                nodes {
                    id
                    customer {
                        id
                        givenName
                        familyName
                    }
                    ticketName
                    location {
                        id
                    }
                    totalMoney {
                        amount
                    }
                    totalTip {
                        amount
                    }
                }
            }
        }
    '''

    # Create the request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.environ['SQUARE_SANDBOX_ACCESS_TOKEN'])
    }
    merchant_id = requests.get(
        'https://connect.squareupsandbox.com/v2/merchants/me', headers=headers).json()['merchant']['id']

    # Create the request payload
    data = {
        'query': query,
        'variables': {
            'merchantId': merchant_id,
            'ids': ids,
        }
    }
    graphql_start = time.time()
    # Send the POST request to the server
    response = requests.post(url, headers=headers, json=data)
    print('Time to get graphql', time.time() - graphql_start)
    # Parse the response as JSON
    result = response.json()
    return result['data']['orders']['nodes']
