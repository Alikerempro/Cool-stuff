import requests
import discord
from datetime import datetime, timedelta
import pytz

def get_weather(city, state, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{city},{state}",
        "appid": api_key,
        "units": "imperial",
        "cnt": 9
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if the API request was successful
    if response.status_code == 200:
        # Extract and format the weather information
        weather_info = []
        offset = get_timezone_offset(data)

        for forecast in data['list']:
            date_time_str = forecast['dt_txt']
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            date_time = date_time + timedelta(seconds=offset)
            date_time = pytz.utc.localize(date_time).astimezone(pytz.timezone('US/Eastern'))
            date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")

            temperature = forecast['main']['temp']
            weather_description = forecast['weather'][0]['description']
            weather_info.append(f"{date_time}: {temperature}°F, {weather_description}")

        return weather_info
    else:
        return f"Error: {data['message']}"

def get_timezone_offset(data):
    if 'timezone_offset' in data:
        return data['timezone_offset']
    elif 'timezone' in data['city']:
        return -14400  # Offset for US/Eastern timezone (UTC-4:00)
    else:
        return 0
#insert your api keys here
api_key = ''
bot_token = ''

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"logged in as {client.user}")
#discord commands
@client.event
async def on_message(message):
  
    if message.author == client.user:
        return
#command to call the bot
    if message.content.startswith("!weather"):
        #records state
        await message.channel.send("Enter the state: ")

        def check_state(m):
            return m.author == message.author and m.channel == message.channel

        state_msg = await client.wait_for("message", check=check_state, timeout=60)
        state = state_msg.content
        #records city
        await message.channel.send("Enter the city: ")

        def check_city(m):
            return m.author == message.author and m.channel == message.channel

        city_msg = await client.wait_for("message", check=check_city, timeout=60)
        city = city_msg.content
        #calls get_weather function
        weather_info = get_weather(city, state, api_key)
        #sends weather information for the next 24 hours.
        if isinstance(weather_info, str):
            await message.channel.send(weather_info)
        else:
            await message.channel.send("\n".join(weather_info))

client.run(bot_token)
