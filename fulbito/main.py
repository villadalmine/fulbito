import click
import os
import requests
import sys
import json

BASE_URL = 'http://apiclient.resultados-futbol.com/scripts/api/api.php?key='


def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data


TEAM_DATA = load_json("teams.json")["teams"]
TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}
LEAGUE_ARGENTINA = load_json("leagues.json")["Argentina"]
LEAGUE_CHILE = load_json("leagues.json")["Chile"]

def get_input_key():
    """Input API key and validate"""
    click.secho("No API key found!", fg="yellow", bold=True)
    click.secho("Please visit {0} and get an API token.".format(BASE_URL),
                fg="yellow", bold=True)
    while True:
        confkey = click.prompt(click.style("Enter API key",
                                           fg="yellow", bold=True))
        if len(confkey) == 32:  # 32 chars
            try:
                int(confkey, 16)  # hexadecimal
            except ValueError:
                click.secho("Invalid API key", fg="red", bold=True)
            else:
                break
        else:
            click.secho("Invalid API key", fg="red", bold=True)
    return confkey

def load_config_key():
    """Load API key from config file, write if needed"""
    global api_token
    try:
        api_token = os.environ['FULBITO_CLI_API_TOKEN']
    except KeyError:
        home = os.path.expanduser("~")
        config = os.path.join(home, ".fulbito.ini")
        if not os.path.exists(config):
            with open(config, "w") as cfile:
                key = get_input_key()
                cfile.write(key)
        else:
            with open(config, "r") as cfile:
                key = cfile.read()
        if key:
            api_token = key
        else:
            os.remove(config)  # remove 0-byte file
            click.secho('No API Token detected. '
                        'Please visit {0} and get an API Token, '
                        'which will be used by Soccer CLI '
                        'to get access to the data.'
                        .format(BASE_URL), fg="red", bold=True)
            sys.exit(1)
    return api_token

def _get(url):
    """Handles api.football-data.org requests"""
    req = requests.get(BASE_URL+api_token+url, headers=headers)

    if req.status_code == requests.codes.ok:
        return req

    if req.status_code == requests.codes.bad:
        raise APIErrorException('Invalid request. Check parameters.')

    if req.status_code == requests.codes.forbidden:
        raise APIErrorException('This resource is restricted')

    if req.status_code == requests.codes.not_found:
        raise APIErrorException('This resource does not exist. Check parameters')

    if req.status_code == requests.codes.too_many_requests:
        raise APIErrorException('You have exceeded your allowed requests per minute/day')

    click.secho(req, fg="green")
    #resp = json.loads(u.read().decode('utf-8'))
    #for num in range(1,23):
       # a=resp["table"][num]["team"]
       # b=resp["table"][num]["pos"]
       # if a == "Villa Dálmine":
       	#    click.secho(a + " Posicion:" + b, fg="green")

def get_team_position(team):
    """Queries the API and gets the standings for a particular league"""
    team_id=_get_team_id(team)
    team_lg=_get_team_league(team)
    click.secho("No position availble for team." + str(team_id) + str(team_lg),
                    fg="red", bold=True)


def map_team_id(code):
    """Take in team ID, read JSON file to map ID to name"""
    for team in TEAM_DATA:
        if team["code"] == code:
            click.secho(team["name"], fg="green")
            break
    else:
        click.secho("No team found for this code", fg="red", bold=True)

def _get_team_id(code):
    """Get team id from json"""
    for team in TEAM_DATA:
        if team["code"] == code:
            return team["id"]
            break
    else:
        return null


def _get_team_league(code):
    """Get team id from json"""
    for team in TEAM_DATA:
        if team["code"] == code:
            return team["league"]["id"]
            break
    else:
        return null


def list_team_codes():
    """List team names in alphabetical order of team ID, per league."""
    # Sort teams by league, then alphabetical by code
    cleanlist = sorted(TEAM_DATA, key=lambda k: (k["league"]["name"], k["code"]))
    # Get league names
    leaguenames = sorted(list(set([team["league"]["name"] for team in cleanlist])))
    for league in leaguenames:
        teams = [team for team in cleanlist if team["league"]["name"] == league]
        click.secho(league, fg="green", bold=True)
        for team in teams:
            if team["code"] != "null":
                click.secho(u"{0}: {1}".format(team["code"], team["name"]), fg="yellow")
        click.secho("")

@click.command()
@click.option('--posi', is_flag=True,
              help="Shows position for a particular team.")
@click.option('--apikey', default=load_config_key,
              help="API key to use.")
@click.option('--list', 'listcodes', is_flag=True,
              help="List all valid team code/team name pairs.")
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()),
              help=("Choose a particular team's fixtures."))
@click.option('--lookup', is_flag=True,
              help="Get full team name from team code when used with --team command.")

def main(listcodes, lookup, team, posi, apikey):
    """
    - PD: Primera Division
    - SD: Segunda Division
    """
    global headers
    headers = {'X-Auth-Token': apikey}

    try:
        if listcodes:
            list_team_codes()
            return


        if team:
            if lookup:
                map_team_id(team)
                return
            else:
                get_team_position(team)
                return

    except IncorrectParametersException as e:
        click.secho(e.message, fg="red", bold=True)

if __name__ == '__main__':
    main()
