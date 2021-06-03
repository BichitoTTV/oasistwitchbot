import os
import json
import discord
import requests
import datetime

from discord.ext import tasks, commands
from twitchAPI.twitch import Twitch
from discord.utils import get

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', description="Esto es un bot de pruebas", intents=intents)

TOKEN = os.getenv('TESTINGMF_DISCORD_TOKEN')


# Autentificandonos con la API De TWITCH
client_id = "uuvhaiw9w5bnfb0sx7o5bfukist657"
client_secret = "bjky7un8zsxnc2ssity80x8nrezxam"
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID': client_id,
    'Accept': 'application/vnd.twitchtv.v5+json',
}

print('Bot Autentificado con la APP de Twitch.')

# Devuelve True si el Streamer está en directo. Falso si no.
def checkuser(user):
    try:
        userid = twitch.get_users(logins=[user])['data'][0]['id']
        url = TWITCH_STREAM_API_ENDPOINT_V5.format(userid)
        try:
            req = requests.Session().get(url, headers=API_HEADERS)
            jsondata = req.json()
            if 'stream' in jsondata:
                if jsondata['stream'] is not None:
                    return True
                else:
                    return False
        except Exception as e:
            print("Error comprobando al usuario: ", e)
            return False
    except IndexError:
        return False

# Executes when bot is started
@bot.event
async def on_ready():
    # Comprueba usuarios en directo cada 10 segundos.
    @tasks.loop(seconds=120)
    async def live_notifs_loop():
        # Abre y lee el archivo .JSON, comprueba que no está vacío.
        with open('streamers.json', 'r') as file:
            streamers = json.loads(file.read())
        if streamers is not None:
            # Introducir aqui los datos del servidor de Discord.
            guild = bot.get_guild(843540178345263154)
            channel = bot.get_channel(843540178345263156)
            for user_id, twitch_name in streamers.items():
                # Comprueba que el usuario está en directo mediante checkuser
                # True si lo está y False si no.
                status = checkuser(twitch_name)
                # Makes sure they're live
                if status is True:
                    # Comprueba si el mensaje ya  ha sido enviado.
                    async for message in channel.history(limit=200):
                        # Si lo está, para el bucle.
                        if str(twitch_name) in message.content and "esta en directo." in message.content:
                            break

                        else:
                            # Gets all the members in your guild.
                            async for member in guild.fetch_members(limit=None):
                            # Sends the live notification to the 'twitch streams' channel then breaks the loop.
                                await channel.send(
                                f":red_circle: **LIVE**\n{twitch_name} está ahora en directo en Twitch!"
                                f"\nhttps://www.twitch.tv/{twitch_name}")
                            print(f"{twitch_name} started streaming. Sending a notification.")
                            break
                # Si no están en directo:
                else:
                    # Comprueba si la notificacion fue enviada.
                     async for message in channel.history(limit=200):
                        # Si lo fue, la borra.
                        if str(twitch_name) in message.content and "está ahora en directo" in message.content:
                            await message.delete()
    # Inicia el bucle
    live_notifs_loop.start()

# Comando para añadir streamers al JSON
@bot.command(name='addtwitch', help='Añade un canal de Twitch a la lista de notificaciones.', pass_context=True)
async def add_twitch(ctx, twitch_name):
    # Abre y lee el archivo JSON
    with open('streamers.json', 'r') as file:
        streamers = json.loads(file.read())
    
    # Gets the users id that called the command.
    user_id = ctx.author.id
    # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
    streamers[user_id] = twitch_name
    
    # Añade la nueva linea al JSON.
    with open('streamers.json', 'w') as file:
        file.write(json.dumps(streamers))
    # Mensaje de confirmación
    confirmacion = discord.Embed(title=f"{ctx.guild.name}", description="Servicios del bot de Streamers de Oasis de RP", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    confirmacion.add_field(name="Confirmación de usuario añadido.", value=f"Añadido {twitch_name} por {ctx.author} a la lista de notificación.")
    confirmacion.set_thumbnail(url="https://images-ext-1.discordapp.net/external/eQYiay_XLmml_twRzutAcrS0OgVTjxAk0aQZgKcN8Zk/%3Fwidth%3D940%26height%3D683/https/media.discordapp.net/attachments/763881075629883452/773126293004484628/Marca_de_agua.png")

    await ctx.send(embed=confirmacion)
    #await ctx.send(f"Añadido {twitch_name} por {ctx.author} a la lista de notificación.")

#Comando para ver el estado del bot.
@bot.command()
async def ping(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Servicios del bot de Streamers de Oasis de RP", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.add_field(name="Estado del Bot:", value="🟢 Correcto.")
    embed.add_field(name="Estado del Servicio de Twitch:", value="🟢 Correcto.")

    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/eQYiay_XLmml_twRzutAcrS0OgVTjxAk0aQZgKcN8Zk/%3Fwidth%3D940%26height%3D683/https/media.discordapp.net/attachments/763881075629883452/773126293004484628/Marca_de_agua.png")
    print('Ping solicitado y respondido con éxito.')
    await ctx.send(embed=embed)

# Ejecutamos el bot
print('Bot Funcionando.')
bot.run('ODUwMTI3MDE1MDkyNjgyODEy.YLlMeg.p0cy5SPHaQn24XqDN1UfPIpkg7k')
