from flask import Flask, request, redirect, url_for, render_template
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
import requests
import json
from twilio.rest import Client
from os import environ


# Twilio Account Information
# PUT IN ENV VAR BEFORE YOU DEPLOY!!
# Your Account SID from twilio.com/console
account_sid = environ.get('TWILIO_ACCOUNT_SID')
# Your Auth Token from twilio.com/console
auth_token  = environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

# create an instance of Flask
app = Flask(__name__)

BASE_URL = 'https://pokeapi.co'

# This function that takes a single parameter (the request url)
# and creates a python representation of the json data
def query_pokeapi(resourse_uri):
    url = '{0}{1}'.format(BASE_URL, resourse_uri)
    response = requests.get(url)

    if response.status_code == 200:
        return json.loads(response.text)
    return None

# Renders the home page for this application
@app.route("/")
def home():
    return "Hello, Pokedex!"

@app.route("/sms", methods=['GET', 'POST'])
def incoming_message():
    twiml = MessagingResponse()

    # Get the body of the inbound SMS message from Twilio and
    # - remove any unnecessary white space from both ends
    # - convert to lower case
    body = request.values.get('Body', None).lower().strip().replace(" ", "")

    # PokeApi URLs
    pokemon_url = '/api/v2/pokemon/{0}/'.format(body)
    desciption_url = '/api/v2/pokemon-species/{0}'.format(body)

    # query_pokeapi returns data in json form based on user's request (message body)
    pokemon = query_pokeapi(pokemon_url)
    description = query_pokeapi(desciption_url)

    # In case the user texts something that is not a pokemon name
    if pokemon == None:
        msg = twiml.message("Something went wrong! Try 'Charmander' or 'Mew'.")
        return str(twiml)

    elif pokemon:
        # The image of the request Pokemon
        sprite_uri = pokemon['sprites']['front_default']
        image = sprite_uri

        # The Pokedex description of the request Pokemon
        for i in description['flavor_text_entries']:
            if i["language"]["name"] == "en":
                message_dex = i["flavor_text"]
                break

        frm = request.values.get("FROM", "")
        # We know it is a UK phone number, and we want to send back
        # the standard SMS instead of MMS
        if "+44" in frm:
            twiml.message('{0} {1}'.format(message_dex, image))
            return str(twiml)

        # Otherwise send back mms
        msg = twiml.message(message_dex)

        # Add image
        msg.media(image)

        # WHERE DO THESE GO??
        # image = '{0}{1}'.formate(BASE_URL, sprite)
        # message = '{0}, {1}'.format(pokemon['name'], description)

        return str(twiml)


# print(pokemon["name"])
# print(description["name"] + " belongs to " + description["generation"]["name"])
# print("and is a " + description["habitat"]["name"] + " pokemon")
# print(sprite_uri)

if __name__ == "__main__":
    app.run(debug=True)
