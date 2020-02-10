import aiomysql
import asyncio

async def connect_db():
    mydb = await aiomysql.connect(
        host='0.0.0.0',
        user='user',
        password='password',
        db='pogorm',
        port=3306,
        autocommit=True)

    cursor = await mydb.cursor()
    return cursor

async def get_shiny_count(mon_id):
    cursor_shiny_count = await connect_db()
    query_shiny_count = "select count(pokemon.pokemon_id) from pokemon join trs_stats_detect_raw stats on cast(stats.type_id as unsigned int) = pokemon.encounter_id where stats.is_shiny=1 and pokemon.pokemon_id={mon_id}"
    await cursor_shiny_count.execute(query_shiny_count.format(mon_id=mon_id))
    shiny_count = await cursor_shiny_count.fetchall()
    for var in shiny_count:
        shiny_count = var[0]

    await cursor_shiny_count.close()
    return shiny_count
    
async def get_shiny_total(mon_id):
    cursor_shiny_total = await connect_db()
    query_total_shiny_count = "select count(pokemon_id) from pokemon where pokemon_id={mon_id} and disappear_time > utc_timestamp() - INTERVAL 8 WEEK and individual_attack is not null"
    await cursor_shiny_total.execute(query_total_shiny_count.format(mon_id=mon_id))
    shiny_total = await cursor_shiny_total.fetchall()
    for var in shiny_total:
        shiny_total = var[0]

    await cursor_shiny_total.close()
    return shiny_total

async def get_scan_numbers(mon_id):
    cursor_scan_numbers = await connect_db()
    query_hundo_count = "select count(pokemon_id) as scanned, SUM(individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15) AS iv100, SUM(individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0) AS iv0, SUM(individual_attack + individual_defense + individual_stamina >= 41) AS iv90 from pokemon where pokemon_id = {mon_id} and individual_attack IS NOT NULL"
    await cursor_scan_numbers.execute(query_hundo_count.format(mon_id=mon_id))
    hundo_count = await cursor_scan_numbers.fetchall()

    await cursor_scan_numbers.close()
    return hundo_count

async def get_big_numbers(mon_id):
    cursor_big_numbers = await connect_db()
    query_big_count = "select count(pokemon_id), sum(pokemon_id = {mon_id}), sum(weather_boosted_condition > 0 and pokemon_id = {mon_id}) from pokemon"
    await cursor_big_numbers.execute(query_big_count.format(mon_id=mon_id))
    big_numbers = await cursor_big_numbers.fetchall()

    await cursor_big_numbers.close()
    return big_numbers