cogs = [
    #    "dp.cogs.usercommands",
        "dp.cogs.admincommands",
        "dp.cogs.boardloop",
    #    "dp.cogs.channelloop"
    ]

def start_cogs(bot):
    for extension in cogs:
        bot.load_extension(extension)