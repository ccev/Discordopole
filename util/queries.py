import aiomysql
import asyncio

async def connect_db(config):
    mydb = await aiomysql.connect(
        host=config['db_host'],
        user=config['db_user'],
        password=config['db_pass'],
        db=config['db_dbname'],
        port=config['db_port'],
        autocommit=True)

    cursor = await mydb.cursor()
    return cursor

async def get_shiny_count(mon_id, config):
    cursor_shiny_count = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        query_shiny_count = "select count(pokemon.pokemon_id) from pokemon join trs_stats_detect_raw stats on cast(stats.type_id as unsigned int) = pokemon.encounter_id where stats.is_shiny=1 and pokemon.pokemon_id={mon_id}"
    elif config['db_scan_schema'] == "rdm":
        query_shiny_count = "SELECT IFNULL(SUM(shiny_stats.count), 0) as count FROM pokemon_iv_stats as stats LEFT JOIN pokemon_shiny_stats as shiny_stats on stats.pokemon_id = shiny_stats.pokemon_id AND stats.date = shiny_stats.date WHERE stats.pokemon_id = {mon_id}"
    await cursor_shiny_count.execute(query_shiny_count.format(mon_id=mon_id))
    shiny_count = await cursor_shiny_count.fetchall()
    for var in shiny_count:
        shiny_count = var[0]

    await cursor_shiny_count.close()
    return shiny_count
    
async def get_shiny_total(mon_id, config):
    cursor_shiny_total = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        query_total_shiny_count = "select count(pokemon_id) from pokemon where pokemon_id={mon_id} and disappear_time > utc_timestamp() - INTERVAL 8 WEEK and individual_attack is not null"
    elif config['db_scan_schema'] == "rdm":
        query_total_shiny_count = "SELECT SUM(stats.count) as total FROM pokemon_iv_stats as stats LEFT JOIN pokemon_shiny_stats as shiny_stats on stats.pokemon_id = shiny_stats.pokemon_id AND stats.date = shiny_stats.date WHERE stats.pokemon_id = {mon_id}"
    await cursor_shiny_total.execute(query_total_shiny_count.format(mon_id=mon_id))
    shiny_total = await cursor_shiny_total.fetchall()
    for var in shiny_total:
        shiny_total = var[0]

    await cursor_shiny_total.close()
    return shiny_total

async def get_scan_numbers(mon_id, config):
    cursor_scan_numbers = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        query_hundo_count = "select count(pokemon_id) as scanned, SUM(individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15) AS iv100, SUM(individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0) AS iv0, SUM(individual_attack + individual_defense + individual_stamina >= 41) AS iv90 from pokemon where pokemon_id = {mon_id} and individual_attack IS NOT NULL"
    elif config['db_scan_schema'] == "rdm":
        query_hundo_count = "select count(id) as scanned, SUM(iv = 100) AS iv100, SUM(iv = 0) AS iv0, SUM(iv > 90) AS iv90 from pokemon where id = {mon_id} and atk_iv IS NOT NULL"
    await cursor_scan_numbers.execute(query_hundo_count.format(mon_id=mon_id))
    hundo_count = await cursor_scan_numbers.fetchall()

    await cursor_scan_numbers.close()
    return hundo_count

async def get_big_numbers(mon_id, config):
    cursor_big_numbers = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        query_big_count = "select count(pokemon_id), sum(pokemon_id = {mon_id}), sum(weather_boosted_condition > 0 and pokemon_id = {mon_id}) from pokemon"
    elif config['db_scan_schema'] == "rdm":
        query_big_count = "select count(id), sum(pokemon_id = {mon_id}), sum(weather > 0 and pokemon_id = {mon_id}) from pokemon"
    await cursor_big_numbers.execute(query_big_count.format(mon_id=mon_id))
    big_numbers = await cursor_big_numbers.fetchall()

    await cursor_big_numbers.close()
    return big_numbers

async def get_active_raids(config, area, level_list):
    levels = "("
    for level in level_list:
        levels = f"{levels}{level},"
    levels = levels[:-1]
    levels = f"{levels})"
    cursor_raids = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_raids.execute(f"SELECT Unix_timestamp(Convert_tz(start, '+00:00', @@global.time_zone)) AS starts, Unix_timestamp(Convert_tz(end, '+00:00', @@global.time_zone)) AS ends, latitude, longitude, pokemon_id, move_1, move_2, name, is_ex_raid_eligible FROM gym LEFT JOIN gymdetails ON gym.gym_id = gymdetails.gym_id LEFT JOIN raid ON gym.gym_id = raid.gym_id WHERE name IS NOT NULL AND end > UTC_TIMESTAMP() AND level IN {levels} AND pokemon_id IS NOT NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) ORDER BY end;")
    #elif config['db_scan_schema'] == "rdm":
        #query_big_count = "select count(id), sum(pokemon_id = {mon_id}), sum(weather > 0 and pokemon_id = {mon_id}) from pokemon"
    raids = await cursor_raids.fetchall()

    await cursor_raids.close()
    return raids