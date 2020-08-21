import discord
import asyncio

cancel_phrases = ["stop", "cancel"]

class NoInput(Exception):
    pass

def make_list_from_string(var, number=True):
    var = var.split(",")
    for i, v in enumerate(var):
        if number:
            var[i] = int(v)
        else:
            var[i] = v.lower().strip()
    return var

async def wait_for_text_to_match(ctx, to_match, timeout=60):
    def check(m):
        return (m.content.lower() == to_match.lower() and m.author == ctx.author and m.channel == ctx.channel) or (m.content.lower() in cancel_phrases)
    try:
        confirm = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    except:
        await ctx.send("Aborting.")
        raise NoInput
    content = confirm.content

    if content in cancel_phrases:
        await ctx.send("Aborting.")
        return False

    await confirm.delete()
    return True

async def wait_for_text(ctx, timeout=60):
    def check(m):
        return (m.author == ctx.author and m.channel == ctx.channel)
    try:
        confirm = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    except:
        await ctx.send("Aborting.")
        raise NoInput
    content = confirm.content
    await confirm.delete()

    if content in cancel_phrases:
        await ctx.send("Aborting.")
        raise NoInput

    return content

async def do_dialog(ctx, message, text, matched, wait_text, make_list=False, number=False, og_var=None):
    async def dialog(text):
        message.embeds[0].description = text
        await message.edit(embed=message.embeds[0])
        try:
            var = await wait_for_text(ctx, timeout=120)
        except NoInput:
            await message.delete()
            raise NoInput
        return var

    if og_var is not None:
        var = og_var
    else:
        try:
            var = await dialog(text)
        except NoInput:
            raise NoInput

    if make_list:
        def make_var_list(var):
            try:
                var = make_list_from_string(var, number)
                to_match = matched
            except:
                to_match = [""]
            return var, to_match

        var, to_match = make_var_list(var)
        while [v for v in var if not v in to_match]:
            try:
                var = await dialog(
                    wait_text.format(var=var)
                )
                var, to_match = make_var_list(var)
            except NoInput:
                raise NoInput

    else:
        def convert_var(var):
            try:
                if number:
                    var = int(var)
                else:
                    var = var.lower()
                to_match = matched
            except:
                to_match = [""]
            return var, to_match
        
        var, to_match = convert_var(var)
        while var not in to_match:
            try:
                var = await dialog(
                    wait_text.format(var=var)
                )
                var, to_match = convert_var(var)
            except NoInput:
                raise NoInput
    return var

