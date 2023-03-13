import aiomysql
import asyncio

async def execute(config, query):
    pool = await aiomysql.create_pool(host=config['db_host'],user=config['db_user'],password=config['db_pass'],db=config['db_dbname'],port=config['db_port'])
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            r = await cur.fetchall()
    return r

async def alt_execute(config, query):
    alt_pool = await aiomysql.create_pool(host=config['alt_db_host'],user=config['alt_db_user'],password=config['alt_db_pass'],db=config['alt_db_dbname'],port=config['alt_db_port'])
    async with alt_pool.acquire() as conn2:
        async with conn2.cursor() as cur2:
            await cur2.execute(query)
            r2 = await cur2.fetchall()
    return r2

async def get_oldest_mon_date(config, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select min(last_modified) from {table};"
    elif config['db_scan_schema'] == "rdm":
        query = f"select from_unixtime(min(first_seen_timestamp)) from {table};"   
    if use_alt_table:
        oldest_mon_date = await alt_execute(config, query)
    else:
        oldest_mon_date = await execute(config, query)
    for var in oldest_mon_date:
        oldest_mon_date = var[0]

    return oldest_mon_date

async def get_shiny_count(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
        shiny_table = config['alt_shiny_table']
    else:
        table = 'pokemon'
        shiny_table = 'trs_stats_detect_mon_raw'
    if config['db_scan_schema'] == "mad":
        query = f"select count({table}.pokemon_id) from {table} join {shiny_table} stats on stats.encounter_id = {table}.encounter_id where stats.is_shiny=1 and {table}.pokemon_id={mon_id} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00')"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(pokemon_id) from {table} where shiny = 1 AND pokemon_id = {mon_id} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    if use_alt_table:
        shiny_count = await alt_execute(config, query)
    else:
        shiny_count = await execute(config, query)
    for var in shiny_count:
        shiny_count = var[0]

    return shiny_count
    
async def get_shiny_total(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where pokemon_id={mon_id} and disappear_time > utc_timestamp() - INTERVAL 8 WEEK and individual_attack is not null AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00')"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT count(pokemon_id) from {table} WHERE pokemon_id = {mon_id} and atk_iv is not null AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) and first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    if use_alt_table:
        shiny_total = await alt_execute(config, query)
    else:
        shiny_total = await execute(config, query)
    for var in shiny_total:
        shiny_total = var[0]

    return shiny_total

async def get_scan_numbers(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) as scanned, ifnull(SUM(individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15), 0) AS iv100, ifnull(SUM(individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0), 0) AS iv0, ifnull(SUM(individual_attack + individual_defense + individual_stamina >= 41), 0) AS iv90 from {table} where pokemon_id = {mon_id} and individual_attack IS NOT NULL AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00') AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) as scanned, ifnull(SUM(iv = 100), 0) AS iv100, ifnull(SUM(iv = 0), 0) AS iv0, ifnull(SUM(iv > 90), 0) AS iv90 from {table} where pokemon_id = {mon_id} and iv IS NOT NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    if use_alt_table:
        hundo_count = await alt_execute(config, query)
    else:
        hundo_count = await execute(config, query)

    return hundo_count

async def get_big_numbers(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id), ifnull(sum(pokemon_id = {mon_id}), 0), ifnull(sum(weather_boosted_condition > 0 and pokemon_id = {mon_id}), 0), min(disappear_time) from {table} WHERE disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00') AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id), ifnull(sum(pokemon_id = {mon_id}), 0), ifnull(sum(weather > 0 and pokemon_id = {mon_id}), 0), FROM_UNIXTIME(min(first_seen_timestamp)) from {table} WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    if use_alt_table:
        big_numbers = await alt_execute(config, query)
    else:
        big_numbers = await execute(config, query)

    return big_numbers

async def get_active_raids(config, area, level_list, tz_offset, ex=False):
    levels = "("
    for level in level_list:
        levels = f"{levels}{level},"
    levels = levels[:-1]
    levels = f"{levels})"
    where_ex = ""
    if config['db_scan_schema'] == "mad":
        if ex:
            where_ex = "AND is_ex_raid_eligible = 1"
        query = f"SELECT gym.gym_id, Unix_timestamp(Convert_tz(start, '+00:00', '{tz_offset}')) AS starts, Unix_timestamp(Convert_tz(end, '+00:00', '{tz_offset}')) AS ends, latitude, longitude, pokemon_id, move_1, move_2, name, is_ex_raid_eligible, level, url, raid.form FROM gym LEFT JOIN gymdetails ON gym.gym_id = gymdetails.gym_id LEFT JOIN raid ON gym.gym_id = raid.gym_id WHERE name IS NOT NULL {where_ex} AND end > UTC_TIMESTAMP() AND level IN {levels} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) ORDER BY end;"
    elif config['db_scan_schema'] == "rdm":
        if ex:
            where_ex = "AND ex_raid_eligible = 1"
        query = f"SELECT id, (UNIX_TIMESTAMP(CONVERT_TZ((FROM_UNIXTIME(raid_battle_timestamp)), '+00:00', '{tz_offset}'))) AS starts, (UNIX_TIMESTAMP(CONVERT_TZ((FROM_UNIXTIME(raid_end_timestamp)), '+00:00', '{tz_offset}'))) AS ends, lat, lon, raid_pokemon_id, raid_pokemon_move_1, raid_pokemon_move_2, name, ex_raid_eligible, raid_level, url, raid_pokemon_form FROM gym WHERE name IS NOT NULL {where_ex} AND raid_end_timestamp > UNIX_TIMESTAMP() AND raid_level in {levels} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) ORDER BY raid_end_timestamp;"
    raids = await execute(config, query)

    return raids

async def get_active_quests(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select quest_reward, quest_task, latitude, longitude, name, pokestop_id from trs_quest left join pokestop on trs_quest.GUID = pokestop.pokestop_id WHERE quest_timestamp > UNIX_TIMESTAMP(CURDATE()) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) ORDER BY quest_item_id ASC, quest_pokemon_id ASC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"select quest_rewards, quest_template, lat, lon, name, id from pokestop WHERE quest_type IS NOT NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) ORDER BY quest_item_id ASC, quest_pokemon_id ASC, name;"
    active_quests = await execute(config, query)

    return active_quests

async def get_gym_stats(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(gym.gym_id), IFNULL(SUM(team_id = 0), 0), IFNULL(SUM(team_id = 1), 0), IFNULL(SUM(team_id=2), 0), IFNULL(SUM(team_id=3), 0), IFNULL(SUM(is_ex_raid_eligible = 1), 0), IFNULL(SUM(end >= utc_timestamp()), 0) from gym left join raid on gym.gym_id = raid.gym_id where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id), IFNULL(SUM(team_id = 0), 0), IFNULL(SUM(team_id = 1), 0), IFNULL(SUM(team_id=2), 0), IFNULL(SUM(team_id=3), 0), IFNULL(SUM(ex_raid_eligible = 1), 0), IFNULL(SUM(raid_end_timestamp > UNIX_TIMESTAMP()), 0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    gym_stats = await execute(config, query)

    return gym_stats

async def statboard_mon_active(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} WHERE expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_mon_active = await alt_execute(config, query)
    else:
        statboard_mon_active = await execute(config, query)

    return statboard_mon_active

async def statboard_mon_today(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} WHERE CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_mon_today = await alt_execute(config, query)
    else:
        statboard_mon_today = await execute(config, query)

    return statboard_mon_today

async def statboard_hundos_active(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} WHERE iv = 100 AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_hundos_active = await alt_execute(config, query)
    else:
        statboard_hundos_active = await execute(config, query)

    return statboard_hundos_active

async def statboard_hundos_today(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} where iv = 100 AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_hundos_today = await alt_execute(config, query)
    else:
        statboard_hundos_today = await execute(config, query)

    return statboard_hundos_today

async def statboard_iv0_active(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} WHERE iv = 0 AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_iv0_active = await alt_execute(config, query)
    else:
        statboard_iv0_active = await execute(config, query)

    return statboard_iv0_active

async def statboard_iv0_today(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} where iv = 0 AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_iv0_today = await alt_execute(config, query)
    else:
        statboard_iv0_today = await execute(config, query)

    return statboard_iv0_today

async def statboard_scanned_active(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack is not NULL and disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} WHERE iv is not NULL AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_scanned_active = await alt_execute(config, query)
    else:
        statboard_scanned_active = await execute(config, query)

    return statboard_scanned_active

async def statboard_scanned_today(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokemon_id) from {table} where individual_attack is not NULL AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from {table} where iv is not NULL AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_scanned_today = await alt_execute(config, query)
    else:
        statboard_scanned_today = await execute(config, query)

    return statboard_scanned_today

async def statboard_total_iv_active(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select ifnull(sum((individual_attack + individual_defense + individual_stamina)/45*100),0) from {table} where individual_attack is not NULL and disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select ifnull(sum(iv),0) from {table} WHERE iv is not NULL AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_total_iv_active = await alt_execute(config, query)
    else:
        statboard_total_iv_active = await execute(config, query)

    return statboard_total_iv_active

async def statboard_total_iv_today(config, area, use_alt_table=False):
    if use_alt_table:
        table = config['alt_pokemon_table']
    else:
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query = f"select ifnull(sum((individual_attack + individual_defense + individual_stamina)/45*100),0) from {table} where individual_attack is not NULL AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select ifnull(sum(iv),0) from {table} where iv is not NULL AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    if use_alt_table:
        statboard_total_iv_today = await alt_execute(config, query)
    else:
        statboard_total_iv_today = await execute(config, query)

    return statboard_total_iv_today

async def statboard_gym_amount(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(gym_id) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_gym_amount = await execute(config, query)

    return statboard_gym_amount

async def statboard_gym_teams(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select ifnull(sum(team_id = 0),0), ifnull(sum(team_id = 1),0), ifnull(sum(team_id=2),0), ifnull(sum(team_id=3),0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select ifnull(sum(team_id = 0),0), ifnull(sum(team_id = 1),0), ifnull(sum(team_id=2),0), ifnull(sum(team_id=3),0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_gym_teams = await execute(config, query)

    return statboard_gym_teams

async def statboard_raid_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0), ifnull(sum(level = 6),0) from gym left join raid on gym.gym_id = raid.gym_id where end >= utc_timestamp() and start <= utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id), ifnull(sum(raid_level = 1), 0), ifnull(sum(raid_level = 2),0), ifnull(sum(raid_level = 3),0), ifnull(sum(raid_level = 4),0), ifnull(sum(raid_level = 5),0), ifnull(sum(raid_level = 6),0) from gym where raid_battle_timestamp < UNIX_TIMESTAMP() AND raid_end_timestamp >= UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_raid_active = await execute(config, query)

    return statboard_raid_active

async def statboard_egg_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0), ifnull(sum(level = 6),0) from gym left join raid on gym.gym_id = raid.gym_id where start > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id), ifnull(sum(raid_level = 1), 0), ifnull(sum(raid_level = 2),0), ifnull(sum(raid_level = 3),0), ifnull(sum(raid_level = 4),0), ifnull(sum(raid_level = 5),0), ifnull(sum(raid_level = 6),0) from gym WHERE raid_battle_timestamp >= UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_egg_active = await execute(config, query)

    return statboard_egg_active

async def statboard_stop_amount(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokestop_id) from pokestop where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from pokestop where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_stop_amount = await execute(config, query)

    return statboard_stop_amount

async def statboard_lure_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokestop_id), ifnull(sum(active_fort_modifier = 501), 0), ifnull(sum(active_fort_modifier = 502), 0), ifnull(sum(active_fort_modifier = 503), 0), ifnull(sum(active_fort_modifier = 504), 0), ifnull(sum(active_fort_modifier = 505), 0) from pokestop where lure_expiration > UTC_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id), ifnull(sum(lure_id = 501), 0), ifnull(sum(lure_id = 502), 0), ifnull(sum(lure_id = 503), 0), ifnull(sum(lure_id = 504), 0), ifnull(sum(lure_id = 505), 0) from pokestop where lure_expire_timestamp is not NULL and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_lure_active = await execute(config, query)

    return statboard_lure_active

async def statboard_grunt_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokestop_id) from pokestop, pokestop_incident where pokestop.pokestop_id = pokestop_incident.pokestop_id AND pokestop_incident.incident_expiration > UTC_TIMESTAMP() AND pokestop_incident.character_display NOT IN (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(incident.pokestop_id) from incident, pokestop where pokestop.id = incident.pokestop_id AND incident.character not in (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(pokestop.lat, pokestop.lon));"
    statboard_grunt_active = await execute(config, query)

    return statboard_grunt_active

async def statboard_leader_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(pokestop_id) from pokestop, pokestop_incident where pokestop.pokestop_id = pokestop_incident.pokestop_id AND pokestop_incident.incident_expiration > UTC_TIMESTAMP() AND pokestop_incident.character_display >= 41 AND incident_grunt_type <= 44 and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(incident.pokestop_id) from incident, pokestop where pokestop.id = incident.pokestop_id AND incident.character in (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(pokestop.lat, pokestop.lon));"
    statboard_leader_active = await execute(config, query)

    return statboard_leader_active

async def statboard_quest_active(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"select count(GUID) from pokestop left join trs_quest on pokestop.pokestop_id = trs_quest.GUID where quest_timestamp > UNIX_TIMESTAMP(CURDATE()) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude));"
    elif config['db_scan_schema'] == "rdm":
        query = f"select count(id) from pokestop where quest_type is not null and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon));"
    statboard_quest_active = await execute(config, query)

    return statboard_quest_active
    
async def get_data(config, area, mon_id):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 1 AND trs_quest.GUID = pokestop.pokestop_id AND quest_pokemon_id = {mon_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_item_amount DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT quest_rewards, quest_template, lat, lon, name, id FROM pokestop WHERE quest_pokemon_id = {mon_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY quest_pokemon_id ASC, name;"
    quests = await execute(config, query)
    
    return quests

async def get_alt_data(config, area, mon_id):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 2 AND trs_quest.GUID = pokestop.pokestop_id AND quest_pokemon_id = {mon_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_item_amount DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT alternative_quest_rewards, alternative_quest_template, lat, lon, name, id FROM pokestop WHERE alternative_quest_pokemon_id = {mon_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY alternative_quest_pokemon_id ASC, name;"
    quests2 = await execute(config, query)
    
    return quests2

async def get_dataitem(config, area, item_id):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 1 AND trs_quest.GUID = pokestop.pokestop_id AND quest_item_id = {item_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_item_amount DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT quest_rewards, quest_template, lat, lon, name, id FROM pokestop WHERE quest_item_id = {item_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY quest_reward_amount DESC, name;"
    quests = await execute(config, query)
    
    return quests

async def get_alt_dataitem(config, area, item_id):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 2 AND trs_quest.GUID = pokestop.pokestop_id AND quest_item_id = {item_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_item_amount DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT alternative_quest_rewards, alternative_quest_template, lat, lon, name, id FROM pokestop WHERE alternative_quest_item_id = {item_id} AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY alternative_quest_reward_amount DESC, name;"
    quests2 = await execute(config, query)
    
    return quests2
    
async def get_datamega(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 1 AND trs_quest.GUID = pokestop.pokestop_id AND quest_reward_type = 12 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_pokemon_id ASC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT quest_rewards, quest_template, lat, lon, name, id FROM pokestop WHERE quest_reward_type = 12 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY quest_pokemon_id ASC, name;"
    quests = await execute(config, query)
    
    return quests
    
async def get_alt_datamega(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT quest_reward, quest_template, latitude, longitude, pokestop.name, pokestop.pokestop_id FROM trs_quest, pokestop WHERE layer = 2 AND trs_quest.GUID = pokestop.pokestop_id AND quest_reward_type = 12 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY quest_pokemon_id ASC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT alternative_quest_rewards, alternative_quest_template, lat, lon, name, id FROM pokestop WHERE alternative_quest_reward_type = 12 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY alternative_quest_pokemon_id ASC, name;"
    quests2 = await execute(config, query)
    
    return quests2
    
async def get_datastar(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT trs_quest.quest_stardust, trs_quest.quest_template, pokestop.latitude, pokestop.longitude, pokestop.name, pokestop.pokestop_id FROM pokestop, trs_quest WHERE pokestop.pokestop_id = trs_quest.GUID AND trs_quest.layer = 1 AND trs_quest.quest_reward_type = 3 AND trs_quest.quest_stardust >= 999 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND trs_quest.quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY trs_quest.quest_stardust DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT quest_reward_amount, quest_template, lat, lon, name, id FROM pokestop WHERE quest_reward_type = 3 AND quest_reward_amount >= 999 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY quest_reward_amount DESC, name;"
    quests = await execute(config, query)
    
    return quests
    
async def get_alt_datastar(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT trs_quest.quest_stardust, trs_quest.quest_template, pokestop.latitude, pokestop.longitude, pokestop.name, pokestop.pokestop_id FROM pokestop, trs_quest WHERE pokestop.pokestop_id = trs_quest.GUID AND trs_quest.layer = 2 AND trs_quest.quest_reward_type = 3 AND trs_quest.quest_stardust >= 999 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) AND trs_quest.quest_timestamp >= UNIX_TIMESTAMP()-86400 ORDER BY trs_quest.quest_stardust DESC, name;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT alternative_quest_reward_amount, alternative_quest_template, lat, lon, name, id FROM pokestop WHERE alternative_quest_reward_type = 3 AND alternative_quest_reward_amount >= 999 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) AND updated >= UNIX_TIMESTAMP()-86400 ORDER BY alternative_quest_reward_amount DESC, name;"
    quests2 = await execute(config, query)
    
    return quests2
    
async def get_datak(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT pokestop.latitude, pokestop.longitude, pokestop.name, pokestop.pokestop_id, pokestop_incident.incident_expiration FROM pokestop, pokestop_incident WHERE pokestop.pokestop_id = pokestop_incident.pokestop_id AND pokestop_incident.incident_display_type =8 AND pokestop_incident.incident_expiration >= UNIX_TIMESTAMP()+300 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) ORDER BY pokestop_incident.incident_expiration DESC;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT pokestop.lat, pokestop.lon, pokestop.name, pokestop.id, incident.expiration FROM pokestop, incident WHERE pokestop.id = incident.pokestop_id AND incident.display_type =8 AND incident.expiration >= UNIX_TIMESTAMP()+300 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) ORDER BY incident.expiration DESC;"
    quests = await execute(config, query)
    
    return quests

async def get_datacoin(config, area):
    if config['db_scan_schema'] == "mad":
        query = f"SELECT pokestop.latitude, pokestop.longitude, pokestop.name, pokestop.pokestop_id, pokestop_incident.incident_expiration FROM pokestop, pokestop_incident WHERE pokestop.pokestop_id = pokestop_incident.pokestop_id AND pokestop_incident.incident_display_type =7 AND pokestop_incident.incident_expiration >= UNIX_TIMESTAMP()+300 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(latitude,longitude)) ORDER BY pokestop_incident.incident_expiration DESC;"
    elif config['db_scan_schema'] == "rdm":
        query = f"SELECT pokestop.lat, pokestop.lon, pokestop.name, pokestop.id, incident.expiration FROM pokestop, incident WHERE pokestop.id = incident.pokestop_id AND incident.display_type =7 AND incident.expiration >= UNIX_TIMESTAMP()+300 AND ST_Contains(ST_GeomFromText('POLYGON(({area}))'), POINT(lat,lon)) ORDER BY incident.expiration DESC;"
    quests = await execute(config, query)
    
    return quests