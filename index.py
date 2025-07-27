import os
import random
import asyncio
import discord
import requests
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl

# --------------------------- Configurações iniciais ---------------------------

load_dotenv()

TOKEN_DISCORD = os.getenv("DISCORD_TOKEN")
TOKEN_OPENROUTER = os.getenv("OPENROUTER_TOKEN")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

historico_conversas = {}

# --------------------------- Configurações YoutubeDL para música ---------------------------

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn',
    'executable': r'C:\Users\marco\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe'  # Coloque o caminho absoluto do ffmpeg no seu PC
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class FonteYTDL(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.titulo = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def de_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# --------------------------- Eventos do Bot ---------------------------

@bot.event
async def on_ready():
    print(f"Bot {bot.user} está online!")

@bot.event
async def on_member_join(membro):
    canal = bot.get_channel(1373337367741464637)  # ID do canal de boas-vindas

    if canal:
        try:
            headers = {
                "Authorization": f"Bearer {TOKEN_OPENROUTER}",
                "Content-Type": "application/json"
            }

            dados = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "Você é um bot acolhedor e criativo que dá boas-vindas a novos membros de um servidor de programação no Discord."},
                    {"role": "user", "content": "Crie uma mensagem curta, divertida e acolhedora para dar boas-vindas a um novo programador que acabou de entrar no servidor. Pode usar emojis, linguagem informal e referência a código, bugs e café."}
                ]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=dados
            )

            if response.status_code != 200:
                await canal.send(f"👋 Bem-vindo(a) {membro.mention}! (Erro ao gerar mensagem personalizada)")
                return

            mensagem_ia = response.json()["choices"][0]["message"]["content"].strip()

            embed = discord.Embed(
                title="🌌 | UM NOVO DESBRAVADOR DE CÓDIGOS CHEGOU!",
                description=f"{mensagem_ia}\n\n👤 Usuário: {membro.mention}",
                color=0x00ff00
            )
            embed.add_field(name="📜 Regra de Ouro", value="*'Commit sem teste é pecado capital'*", inline=False)
            embed.add_field(
                name="Canais Importantes",
                value="• <#ajuda>: Transformamos erros em aprendizado\n"
                    "• <#geral>: Compartilhamos dores e memes\n"
                    "• <#projetos>: Construímos o futuro (com bugs inclusos)",
                inline=False
            )
            embed.set_footer(text="Que seu código seja limpo e seus bugs raros. Boa jornada, dev! 🚀💻")

            await canal.send(embed=embed)

        except Exception as e:
            await canal.send(f"👋 Bem-vindo(a) {membro.mention}!\n❌ Erro ao gerar mensagem personalizada: {e}")

@bot.event
async def on_message(mensagem):
    if mensagem.author.bot:
        return

    if "aff apaga" in mensagem.content.lower():
        embed = discord.Embed(description="Isah certeza!!", color=0xff0000)
        await mensagem.channel.send(embed=embed)

    await bot.process_commands(mensagem)

# --------------------------- Comandos Básicos ---------------------------

@bot.command(name="ajuda")
async def comando_ajuda(ctx):
    embed = discord.Embed(
        title="📌 Ajuda do Bot - Comandos e Eventos",
        color=discord.Color.blue()
    )

    comandos1 = {
        "!ajuda": "Mostra esta mensagem com todos os comandos e eventos",
        "!info": "Mostra informações sobre o bot",
        "!ping": "Responde Pong! e a latência",
        "!chat [mensagem]": "Conversa com IA via OpenRouter",
        "!spam [canal_id] [mensagem] [quantidade]": "Envia mensagens repetidas para o canal",
        "!musica play [url ou termo]": "Toca música no canal de voz",
        "!musica stop": "Para a música e desconecta",
        "!musica skip": "Pula a música atual",
        "!musica fila": "Mostra a fila de músicas",
        "!musica proximo": "Toca a próxima música da fila",
    }

    comandos2 = {
        "!gif [termo]": "Envia um gif relacionado",
        "!gifRandom": "Envia um gif aleatório de temas variados",
        "!google [termo]": "Pesquisa no Google e envia link",
        "!agendar [data] [hora] [descrição]": "Agenda reunião",
        "!enquete [pergunta];[opções]": "Cria enquete",
        "!piada": "Conta uma piada em português",
        "!frase [tema]": "Frases e humor para animar",
        "!emoji": "Envia emoji aleatório",
        "!conta [@usuário]": "Mostra informações públicas do usuário",
        "!festa [@usuário]": "Move o usuário para o canal de festa",
        "!animar": "Envia mensagens e emojis aleatórios para animar",
    }

    eventos = {
        "on_ready": "Indica que o bot está online",
        "on_member_join": "Mensagem de boas-vindas para novos membros",
        "on_message": "Responde a mensagens específicas e processa comandos"
    }

    embed.add_field(
        name="🔧 Comandos - Parte 1",
        value="\n".join(f"**{cmd}**: {desc}" for cmd, desc in comandos1.items()),
        inline=False
    )

    embed.add_field(
        name="🔧 Comandos - Parte 2",
        value="\n".join(f"**{cmd}**: {desc}" for cmd, desc in comandos2.items()),
        inline=False
    )

    embed.add_field(
        name="⚡ Eventos Importantes",
        value="\n".join(f"**{ev}**: {desc}" for ev, desc in eventos.items()),
        inline=False
    )

    embed.set_footer(text="Use os comandos com ! na frente. Aproveite! 🚀")

    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="ℹ️ Informações do Bot",
        description="Bot educativo feito por alunos do IFPI - Campus Paulistana",
        color=0x0099ff
    )
    embed.add_field(name="Criador", value="Marcos V. Sousa", inline=True)
    embed.add_field(name="Versão", value="1.0.1", inline=True)
    embed.add_field(
        name="Colaboradores",
        value="Tayla Maria de S. Gomes\nElissandra P. Rodriges\nMaria Clara de S. Medrado",
        inline=False
    )
    embed.add_field(name="Repositório", value="https://github.com/Mark09092009/Projeto_BotGeugrinho", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: {latencia}ms")

# --------------------------- Comando Chat IA ---------------------------

@bot.command()
async def chat(ctx: commands.Context, *, mensagem):
    try:
        user_id = str(ctx.author.id)
        if user_id not in historico_conversas:
            historico_conversas[user_id] = []

        sistema_msg = {
            "role": "system",
            "content": (
                "Você é um assistente de chat útil, educado e prestativo. "
                "Responda de forma clara e objetiva às perguntas do usuário."
            )
        }

        historico_conversas[user_id].append({"role": "user", "content": mensagem})

        if len(historico_conversas[user_id]) > 10:
            historico_conversas[user_id] = historico_conversas[user_id][-10:]

        mensagens_api = [sistema_msg] + historico_conversas[user_id]

        headers = {
            "Authorization": f"Bearer {TOKEN_OPENROUTER}",
            "Content-Type": "application/json"
        }

        dados = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": mensagens_api
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=dados
        )

        if response.status_code != 200:
            await ctx.send(f"❌ Erro {response.status_code}: {response.text}")
            return

        conteudo = response.json()["choices"][0]["message"]["content"]

        historico_conversas[user_id].append({"role": "assistant", "content": conteudo})

        if len(conteudo) > 2000:
            conteudo = conteudo[:1997] + "..."

        await ctx.send(f"🤖 ChatBot: {conteudo}")

    except Exception as e:
        await ctx.send(f"❌ Ocorreu um erro: {str(e)}")

# --------------------------- Comando Spam ---------------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def spam(ctx, canal_id: int, *, args):
    try:
        partes = args.rsplit(" ", 1)
        if len(partes) != 2:
            await ctx.send("Uso incorreto! Exemplo: !spam 123456789012345678 Olá 5")
            return

        mensagem, qtd_str = partes
        quantidade = int(qtd_str)

        canal = bot.get_channel(canal_id)
        if canal is None:
            await ctx.send("Canal não encontrado.")
            return

        for _ in range(quantidade):
            await canal.send(mensagem)
            await asyncio.sleep(1)

        await ctx.send(f"✅ Enviado '{mensagem}' {quantidade} vezes para {canal.mention}")

    except Exception as e:
        await ctx.send(f"❌ Erro no comando spam: {str(e)}")

# ----------------------- Comando MÚSICA --------------------------

filas = {}  # Dicionário de filas de música por servidor

async def tocar_proxima(guild, voz):
    print(f"[DEBUG] Tentar tocar próxima na guilda {guild.id}")
    if guild.id in filas and filas[guild.id]:
        entrada = filas[guild.id].pop(0)
        print(f"[DEBUG] Tocando próxima música: {entrada['busca']}")
        try:
            player = await FonteYTDL.de_url(entrada["busca"], loop=bot.loop, stream=True)

            def after_play(error):
                if error:
                    print(f"[ERROR] Erro no after_play: {error}")
                # Chama recursivamente a próxima música
                bot.loop.create_task(tocar_proxima(guild, voz))

            voz.play(player, after=after_play)
            await entrada["canal_texto"].send(f"▶️ Tocando agora: **{player.titulo}**")
        except Exception as e:
            await entrada["canal_texto"].send(f"❌ Erro ao tocar próxima música: {e}")
    else:
        print("[DEBUG] Fila vazia, desconectando...")
        filas[guild.id] = []
        await voz.disconnect()

@bot.group(name="musica", invoke_without_command=True)
async def musica(ctx):
    await ctx.send("Use !musica play [nome ou link] para tocar música ou !musica stop para parar.")

@musica.command(name="play")
async def musica_play(ctx, *, busca):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Você precisa estar em um canal de voz para tocar música.")
        return

    canal_voz = ctx.author.voice.channel
    voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Garante que a fila existe
    if ctx.guild.id not in filas:
        filas[ctx.guild.id] = []

    print(f"[DEBUG] Fila antes da ação: {filas[ctx.guild.id]}")

    if not voz:
        try:
            voz = await canal_voz.connect()
        except Exception as e:
            await ctx.send(f"❌ Não consegui conectar ao canal de voz: {e}")
            return
    elif voz.channel != canal_voz:
        await voz.move_to(canal_voz)

    if voz.is_playing():
        filas[ctx.guild.id].append({"busca": busca, "canal_texto": ctx.channel})
        print(f"[DEBUG] Música adicionada na fila: {busca}")
        print(f"[DEBUG] Fila atualizada: {filas[ctx.guild.id]}")
        await ctx.send("🎶 Já estou tocando! Música adicionada à fila.")
    else:
        await ctx.send(f"🔎 Buscando por: {busca}...")
        try:
            player = await FonteYTDL.de_url(busca, loop=bot.loop, stream=True)

            def after_play(error):
                if error:
                    print(f"[ERROR] Erro no after_play: {error}")
                bot.loop.create_task(tocar_proxima(ctx.guild, voz))

            voz.play(player, after=after_play)
            await ctx.send(f"▶️ Tocando agora: **{player.titulo}**")
            print(f"[DEBUG] Tocando: {player.titulo}")
        except Exception as e:
            await ctx.send(f"❌ Erro ao tocar música: {e}")

@musica.command(name="skip")
async def musica_skip(ctx):
    voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voz and voz.is_playing():
        voz.stop()  # Para música atual e chama próxima (se houver)
        await ctx.send("⏭️ Música atual pulada!")
    else:
        await ctx.send("❌ Não estou tocando música agora.")


@musica.command(name="fila")
async def musica_fila(ctx):
    fila = filas.get(ctx.guild.id, [])

    if not fila:
        await ctx.send("📭 A fila está vazia.")
        return

    texto = "**🎶 Fila de reprodução:**\n"
    for i, entrada in enumerate(fila, start=1):
        texto += f"{i}. {entrada['busca']}\n"

    await ctx.send(texto)

@musica.command(name="stop")
async def musica_stop(ctx):
    voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voz and voz.is_playing():
        filas[ctx.guild.id] = []
        voz.stop()
        await voz.disconnect()
        await ctx.send("⏹️ Música parada, fila limpa e desconectado do canal de voz.")
    else:
        await ctx.send("❌ Não estou tocando música agora.")


# --------------------------- Comando GIF ---------------------------

@bot.command(name="gif")
async def comando_gif(ctx, *, termo):
    if not GIPHY_API_KEY:
        await ctx.send("❌ A chave da API do Giphy não está configurada.")
        return

    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={termo}&limit=5&rating=g"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Erro ao buscar gifs.")
                return
            data = await resp.json()
            if not data["data"]:
                await ctx.send("⚠️ Nenhum gif encontrado para esse termo.")
                return
            gif_url = random.choice(data["data"])["images"]["downsized_medium"]["url"]
            await ctx.send(gif_url)

@bot.command(name="gifRandom")
async def comando_gifaleatorio(ctx):
    temas = ["cats", "dogs", "memes", "gaming", "funny", "anime", "nature", "dance", "movie","gay", "love", "happy", "sad", "music", "art", "food", "sports", "travel", "fashion", "animals", "comics", "science", "technology", "history", "books", "photography", "quotes", "inspirational", "motivational", "life", "health", "fitness", "education", "business", "finance", "politics"]
    termo = random.choice(temas)
    await ctx.invoke(bot.get_command("gif"), termo=termo)

# --------------------------- Comando Google ---------------------------

@bot.command(name="google")
async def comando_google(ctx, *, termo):
    termo_escapado = termo.replace(' ', '+')
    url_pesquisa = f"https://www.google.com/search?q={termo_escapado}"
    await ctx.send(f"🔎 Pesquisa Google para **{termo}**:\n{url_pesquisa}")

# --------------------------- Comando Agendar ---------------------------

agendamentos = {}

@bot.command(name="agendar")
async def comando_agendar(ctx, data, hora, *, descricao):
    try:
        chave = f"{data} {hora}"
        if chave not in agendamentos:
            agendamentos[chave] = []
        agendamentos[chave].append({"descricao": descricao, "usuario": ctx.author.mention})

        await ctx.send(f"📅 Agendamento criado para {data} às {hora}:\n**{descricao}**\nUsuário: {ctx.author.mention}")

    except Exception as e:
        await ctx.send(f"❌ Erro no agendamento: {str(e)}")

# --------------------------- Comando Enquete ---------------------------

@bot.command(name="enquete")
async def comando_enquete(ctx, *, args):
    try:
        partes = args.split(";")
        if len(partes) < 2:
            await ctx.send("❌ Uso: !enquete Pergunta; Opção1; Opção2; ...")
            return

        pergunta = partes[0].strip()
        opcoes = [p.strip() for p in partes[1:]]

        if len(opcoes) > 10:
            await ctx.send("❌ Número máximo de opções: 10")
            return

        emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

        texto = f"**{pergunta}**\n\n"
        for i, opcao in enumerate(opcoes):
            texto += f"{emojis[i]} {opcao}\n"

        mensagem = await ctx.send(texto)
        for i in range(len(opcoes)):
            await mensagem.add_reaction(emojis[i])

    except Exception as e:
        await ctx.send(f"❌ Erro na enquete: {str(e)}")

# --------------------------- Comando Piada ---------------------------

@bot.command(name="piada")
async def comando_piada(ctx):
    try:
        prompt = (
            "Conte uma piada EM PORTUGUES e que faça SENTIDO EM PORTUGUES, criativa, divertida e QUE FAÇA SENTIDO. "
            "Use emoji se fizer sentido. Apenas envie a piada direto, sem explicações ou contexto."
        )

        headers = {
            "Authorization": f"Bearer {TOKEN_OPENROUTER}",
            "Content-Type": "application/json"
        }

        dados = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "Você é um contador de piadas engraçadas, leves e criativas."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=dados
        )

        if response.status_code != 200:
            await ctx.send(f"❌ Erro {response.status_code}: {response.text}")
            return

        piada = response.json()["choices"][0]["message"]["content"].strip()

        if len(piada) > 2000:
            piada = piada[:1997] + "..."

        await ctx.send(piada)

    except Exception as e:
        await ctx.send(f"❌ Erro ao gerar piada: {str(e)}")

# --------------------------- Comando Frases ---------------------------

@bot.command(name="frase")
async def comando_frases(ctx, *, tema: str):
    try:
        prompt = (
            f"Crie uma frase original, curta, criativa e divertida sobre **{tema}**. "
            "O estilo deve ser informal, inspirador e com  humor ou motivação. "
            "Use emojis se fizer sentido."
        )

        headers = {
            "Authorization": f"Bearer {TOKEN_OPENROUTER}",
            "Content-Type": "application/json"
        }

        dados = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "Você é um gerador de frases curtas e criativas."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=dados
        )

        if response.status_code != 200:
            await ctx.send(f"❌ Erro {response.status_code}: {response.text}")
            return

        frase = response.json()["choices"][0]["message"]["content"].strip()

        if len(frase) > 2000:
            frase = frase[:1997] + "..."

        await ctx.send(f"💡 {frase}")

    except Exception as e:
        await ctx.send(f"❌ Erro ao gerar frase: {str(e)}")


# --------------------------- Comando Emoji Aleatório ---------------------------

@bot.command(name="emoji")
async def comando_emoji(ctx):
    emojis = ['😀','😂','😎','🥳','🤖','🔥','💥','🌟','🎉','🚀','🌈','🍀','🎈','🤩','🦄','💫','⭐']
    await ctx.send(random.choice(emojis))

# --------------------------- Comando Conta ---------------------------

@bot.command(name="conta")
async def comando_conta(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    embed = discord.Embed(title=f"Informações de {membro}", color=0x00ff00)
    embed.add_field(name="Nome", value=membro.name, inline=True)
    embed.add_field(name="ID", value=membro.id, inline=True)
    embed.add_field(name="Conta criada em", value=membro.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.set_thumbnail(url=membro.avatar.url if membro.avatar else None)
    await ctx.send(embed=embed)

# --------------------------- Comando Festa ---------------------------

@bot.command(name="festa")
async def comando_festa(ctx, membro: discord.Member = None):
    if membro is None:
        await ctx.send("❌ Por favor, mencione o usuário que você quer mover para o canal de festa.\nExemplo: `!festa @usuario`")
        return

    nome_canal_festa = "🎉Festa"
    canal_festa = discord.utils.get(ctx.guild.voice_channels, name=nome_canal_festa)
    if not canal_festa:
        await ctx.send(f"❌ Canal de voz '{nome_canal_festa}' não encontrado.")
        return

    if not membro.voice or not membro.voice.channel:
        await ctx.send(f"❌ O usuário {membro.mention} não está em um canal de voz.")
        return

    try:
        await membro.move_to(canal_festa)
        await ctx.send(f"🎉 {membro.mention} foi movido para o canal {canal_festa.name}!")
    except Exception as e:
        await ctx.send(f"❌ Não consegui mover {membro.mention}: {e}")

# --------------------------- Comando Animar ---------------------------

@bot.command(name="animar")
async def comando_animar(ctx):
    try:
        prompt = (
            "Crie uma frase curta e divertida para animar um canal de Discord. "
            "Pode incluir emojis e gírias nerds ou geeks. "
            "A ideia é deixar o ambiente mais divertido e enérgico. "
            "Seja criativo, positivo e espontâneo!"
        )

        headers = {
            "Authorization": f"Bearer {TOKEN_OPENROUTER}",
            "Content-Type": "application/json"
        }

        dados = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "Você é um bot animador de servidores, divertido, espontâneo e criativo."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=dados
        )

        if response.status_code != 200:
            await ctx.send(f"❌ Erro {response.status_code}: {response.text}")
            return

        frase_animada = response.json()["choices"][0]["message"]["content"].strip()

        if len(frase_animada) > 2000:
            frase_animada = frase_animada[:1997] + "..."

        await ctx.send(frase_animada)

    except Exception as e:
        await ctx.send(f"❌ Erro ao gerar mensagem animada: {str(e)}")

# --------------------------- Rodar o bot ---------------------------

bot.run(TOKEN_DISCORD)
