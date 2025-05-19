import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.all()
bot = commands.Bot('!', intents=intents)

@bot.event
async def on_ready():
    print('Bot inicializado com sucesso!')

@bot.event
async def on_member_join(membro: discord.Member):
    canal = bot.get_channel(1373337367741464637)  # Substitua pelo ID do seu canal de boas-vindas

    embed = discord.Embed(
        title='🌌 | UM NOVO DESBRAVADOR DE CÓDIGOS CHEGOU!',
        description=f'Bem-vindo(a) {membro.mention} ao nosso ecossistema de caos criativo!',
        color=0x00ff00
    )

    embed.add_field(
        name='📜 Regra de Ouro',
        value='*\'Commit sem teste é pecado capital\'*',
        inline=False
    )

    embed.add_field(
        name='Canais Importantes',
        value='• <#ajuda>: Transformamos erros em aprendizado\n'
              '• <#geral>: Compartilhamos dores e memes\n'
              '• <#projetos>: Construímos o futuro (com bugs inclusos)',
        inline=False
    )

    embed.set_footer(text='Que seu código seja limpo e seus bugs raros. Boa jornada, dev! 🚀💻')

    await canal.send(embed=embed)

@bot.command()
async def info(ctx: commands.Context):
    embed = discord.Embed(
        title='ℹ️ Informações do Bot',
        description='Este bot foi criado para fins educacionais, como parte de uma pesquisa desenvolvida por alguns alunos do 2º ano do curso de Informática para Internet (2025.1) do IFPI - Campus Paulistana.',
        color=0x0099ff
    )

    embed.add_field(
        name='Criador',
        value='Marcos V. Sousa',
        inline=True
    )

    embed.add_field(
        name='Versão',
        value='1.0.1',
        inline=True
    )

    embed.add_field(
        name='Colaboradores',
        value='Pedro Lucas G. de Sousa \nTayla Maria de S. Gomes \nElissandra P. Rodriges \nMaria Clara de S. Medrado',  # Substitua pelos nomes reais
        inline=False
    )

    embed.add_field(
        name='Repositório',
        value='https://github.com/Mark09092009/Projeto_BotGeugrinho',
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='ajuda')
async def help_command(ctx: commands.Context):
    embed = discord.Embed(
        title='📌 Ajuda do Bot - Comandos Disponíveis',
        description='Lista completa de comandos e funcionalidades',
        color=0x0099ff
    )

    embed.add_field(
        name='!ajuda',
        value='Mostra esta mensagem com todos os comandos',
        inline=False
    )

    embed.add_field(
        name='!info',
        value='Mostra informações sobre o bot',
        inline=False
    )

    embed.add_field(
        name='!ping',
        value='Testa a latência do bot (responde com Pong!)',
        inline=False
    )

    embed.add_field(
        name='Resposta Automática',
        value='Quando alguém digitar \'aff apaga\', o bot responde \'Isah certeza!!\'',
        inline=False
    )

    embed.add_field(
        name='Boas-vindas',
        value='Mensagem automática quando novos membros entram no servidor',
        inline=False
    )

    await ctx.send(embed=embed)

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    if (msg.content.lower() == 'aff apaga') or ('aff apaga' in msg.content.lower()):
        embed = discord.Embed(
            description='Isah certeza!!',
            color=0xff0000
        )
        await msg.channel.send(embed=embed)

    await bot.process_commands(msg)

@bot.command()
async def ping(ctx: commands.Context):
    embed = discord.Embed(
        title='🏓 Pong!',
        description=f'Latência: {round(bot.latency * 1000)}ms',
        color=0x00ff00
    )
    await ctx.send(embed=embed)

my_secret = os.environ['DISCORD_TOKEN']
keep_alive()
bot.run(my_secret)
