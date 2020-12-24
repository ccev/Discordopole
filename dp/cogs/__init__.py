def start_cogs(bot):
    cogs = [
    #    "dp.cogs.usercommands",
        "dp.cogs.admincommands",
        "dp.cogs.boardloop",
    #    "dp.cogs.channelloop"
    ]
    for extension in cogs:
        bot.load_extension(extension)