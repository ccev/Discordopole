import json
from dp.utils.commands.generic import NoInput, do_dialog, wait_for_text, make_list_from_string

def get_raidboard_dict(bot):
    return {
        "channel_id": "",
        "message_id": "",
        "title": bot.locale["raids"],
        "area": "",
        "wait": 2,
        "levels": [
            5
        ],
        "ex": False,
        "static_map": False
    }

def parse_string(s):
    c = s
    if s.lower() == "true":
        c = True
    elif s.lower() == "false":
        c = False
    
    try:
        c = int(s)
    except:
        pass

    if isinstance(s, str):
        try:
            s = make_list_from_string(s)
            if not [v for v in s if not v in [1,2,3,4,5]]:
                c = s
        except:
            pass

    return c

def get_areas(bot):
    return "- " + "\n- ".join([a["name"] for a in bot.geofences])

def get_area_list(bot):
    return [a["name"].lower() for a in bot.geofences]

async def raid_board(ctx, message):
    board = get_raidboard_dict(ctx.bot)
    board["channel_id"] = ctx.channel.id
    board["message_id"] = message.id

    message.embeds[0].title = "Let's create a Raid Board"
    try:
        area_name = await do_dialog(
            ctx, message,
            "**Please choose one of these areas:**\n" + get_areas(ctx.bot),
            get_area_list(ctx.bot),
            "Sorry, `{var}` is not known. Use one of the following areas instead:\n" + get_areas(ctx.bot)
        )
    except NoInput:
        raise NoInput

    try:
        levels = await do_dialog(
            ctx, message,
            "Perfect. What Raid levels should the board show?\nYou can use multiple by seperating them with a `,`.",
            [1, 2, 3, 4, 5],
            "Sorry, `{var}` does not work. The level has to be between 1 and 5.",
            True, True
        )
    except NoInput:
        raise NoInput

    board["area"] = area_name
    board["levels"] = levels

    text = ""
    done = False
    done_text = "Done. Below you can see your current settings.\n- To change a setting, you can say `(key) (value)` - e.g. `title Level 5 Raid Board`\n- If you're done, say `Done`\n\n```{board}```"
    embed = message.embeds[0]
    async def write_succes(board, extra=""):
        embed.description = extra + done_text.format(board=json.dumps(board, indent=4))
        await message.edit(embed=embed)
    await write_succes(board)

    while not done:
        try:
            text = await wait_for_text(ctx, timeout=150)
        except NoInput:
            raise NoInput
        
        k = text.split(" ")[0]
        if k in board.keys():
            s = text.replace(f"{k} ", "")
            c = parse_string(s)
            board[k] = c
            await write_succes(board)
        elif text.lower() in ["finished", "done"]:
            done = True
        else:
            await write_succes(board, f"Sorry, `{k}` is no correct key.\n\n")
        
    ctx.bot.boards['raids'].append(board)

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(ctx.bot.boards, indent=4))

    embed.description = f"Finished. You'll see this message being filled in soon.\n\n```{json.dumps(board, indent=4)}```"
    await message.edit(embed=embed)

async def egg_board(ctx, message):
    pass

async def quest_board(ctx, message):
    pass

async def stat_board(ctx, message):
    pass