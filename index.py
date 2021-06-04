import os
import json
import discord
import requests
import datetime
import time
  
from pypresence import Presence
from discord.ext import tasks, commands
from twitchAPI.twitch import Twitch
from discord.utils import get

intents = discord.Intents.all()
activity = discord.Streaming(name="OasisRP", url="https://www.twitch.tv/team/oasisrp")
bot = commands.Bot(command_prefix='$', description="Bot de Notificación de Streamings para Oasis RP.", intents=intents, activity=activity, status=discord.Status.idle)
bot.remove_command('help')
TOKEN = os.getenv('TESTINGMF_DISCORD_TOKEN')


# Autentificandonos con la API De TWITCH [NO TOCAR]
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

# Events

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

# Evento1
@bot.event
async def on_ready():
    # Comprueba usuarios en directo cada 60 segundos.
    @tasks.loop(seconds=60)
    async def live_notifs_loop():
        # Abre y lee el archivo .JSON, comprueba que no está vacío.
        with open('streamers.json', 'r') as file:
            streamers = json.loads(file.read())
        if streamers is not None:
            # Introducir aqui los datos del servidor de Discord.
            guild = bot.get_guild(843540178345263154)
            channel = bot.get_channel(850164822305407016)
            for user_id, twitch_name in streamers.items():
                # Comprueba que el usuario está en directo mediante checkuser
                # True si lo está y False si no.
                status = checkuser(twitch_name)
                # Comprueba si están en directo.
                if status is True:
                    # Comprueba si el mensaje ya  ha sido enviado.
                    async for message in channel.history(limit=200):
                        # Si lo está, para el bucle.
                        if str(twitch_name) in message.content and "esta en directo." in message.content:
                            break

                        else:
                            
                            #Cancela mandar la notificación si ya fue enviada.
                            async for message in channel.history(limit=200):
                                if str(twitch_name) in message.content and "está ahora en directo en Twitch!" in message.content:
                                    print(f"{twitch_name} sigue en directo.")
                                    break
                            else:
                            # Manda la notificación de directo.
                                await channel.send(
                                f":red_circle: **DIRECTO** {twitch_name} está ahora en directo en Twitch! "
                                f"https://www.twitch.tv/{twitch_name}")
                                print(f"{twitch_name} Notificación enviada.")
                            break
                # Si no están en directo:
                if status is False:
                    # Comprueba si la notificacion fue enviada en los ultimos 200 mensajes.
                     async for message in channel.history(limit=200):
                        # Si lo fue, la borra.
                        if str(twitch_name) in message.content and "está ahora en directo en Twitch!" in message.content:
                            await message.delete()
                            print(f"{twitch_name}: Notificación Eliminada.")
    # Inicia el bucle
    live_notifs_loop.start()

# Comando para añadir streamers al JSON
@bot.command(name='addstreamer', help='Añade un canal de Twitch a la lista de notificaciones.', pass_context=True)
async def add_streamer(ctx, twitch_name):
    # Abre y lee el archivo JSON
    with open('streamers.json', 'r') as file:
        streamers = json.loads(file.read())
    
    # Guarda el usuario que ejecutó el comando y añade el streamer.
    user_id = twitch_name
    streamers[user_id] = twitch_name
    
    # Añade la nueva linea al JSON.
    with open('streamers.json', 'w') as file:
        file.write(json.dumps(streamers, indent=5))
    # Mensaje de confirmación
    confirmacion = discord.Embed(title=f"{ctx.guild.name}", description="Servicios del bot de Streamers de Oasis de RP", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    confirmacion.add_field(name="Confirmación de usuario añadido.", value=f"Añadido {twitch_name} por {ctx.author} a la lista de notificación.")
    confirmacion.set_thumbnail(url="https://images-ext-1.discordapp.net/external/eQYiay_XLmml_twRzutAcrS0OgVTjxAk0aQZgKcN8Zk/%3Fwidth%3D940%26height%3D683/https/media.discordapp.net/attachments/763881075629883452/773126293004484628/Marca_de_agua.png")
    print (f"Añadido usuario: {twitch_name}")
    await ctx.send(embed=confirmacion)
    #await ctx.send(f"Añadido {twitch_name} por {ctx.author} a la lista de notificación.")

#Comando para ver el estado del bot.
@bot.command()
async def ping(ctx):
    count = len(open('streamers.json').readlines(  ))
    cantidadstreamers = count - 2
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Servicios del bot de Streamers de Oasis de RP", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.add_field(name="Estado del Bot:", value="🟢 Correcto.", inline=False )
    embed.add_field(name="Estado del Servicio de Twitch:", value="🟢 Correcto.", inline=False)
    embed.add_field(name="Cantidad de Streamers en Lista:", value=f"👤 {cantidadstreamers}", inline=False)

    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/eQYiay_XLmml_twRzutAcrS0OgVTjxAk0aQZgKcN8Zk/%3Fwidth%3D940%26height%3D683/https/media.discordapp.net/attachments/763881075629883452/773126293004484628/Marca_de_agua.png")
    print('Ping solicitado y respondido con éxito.')
    await ctx.send(embed=embed)

# Comando para leer el JSON en Discord.
@bot.command(pass_context = True)
async def streamerlist(ctx):
    count = len(open('streamers.json').readlines(  ))
    cantidadstreamers = count - 2
    await ctx.send(f"Lista de los {cantidadstreamers} Streamers con acceso al bot de Notificaciones solicitada por: @{ctx.author}")
    await ctx.send(file=discord.File(r'streamers.json'))
    print("Lista de Streamers enviada.")

# comando clear

@bot.command()
async def clear(ctx, amount):
    cantidad = int(amount)
    await ctx.channel.purge(limit=cantidad+1)
    await ctx.send(f"{amount} Mensajes han sido eliminados.", delete_after=5)
    print(f"{cantidad} mensajes han sido eliminados de {ctx.channel}")
        

# Comando HELP
@bot.command(pass_context=True)
async def help(ctx):
    help = discord.Embed(title="Comando de ayuda", timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    help.add_field(name="$ping", value="Muestra el estado actual del bot.", inline=False)
    help.add_field(name="$streamerlist", value="Devuelve la lista de Streamers con las Notificaciones por Bot Activadas.", inline=False)
    help.add_field(name="$addstreamer", value="Añade un streamer a la lista de Notificación.", inline=False)
    help.add_field(name="$clear", value="Elimina la cantidad de mensajes que se especifiquen a continuacion.", inline=False)
    help.add_field(name="$help", value="Muestra este mensaje.", inline=False)

    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    help.set_thumbnail(url="https://images-ext-1.discordapp.net/external/eQYiay_XLmml_twRzutAcrS0OgVTjxAk0aQZgKcN8Zk/%3Fwidth%3D940%26height%3D683/https/media.discordapp.net/attachments/763881075629883452/773126293004484628/Marca_de_agua.png")
    print(f'Comando de ayuda solicitado por {ctx.author}')
    await ctx.send(embed=help)


# Ejecutamos el bot
print('Bot Iniciado.')
bot.run('TOKEN')
