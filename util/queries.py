import aiomysql
import asyncio
async def connect_alt_db(config):
    alt_mydb = await aiomysql.connect(
        host=config['alt_db_host'],
        user=config['alt_db_user'],
        password=config['alt_db_pass'],
        db=config['alt_db_dbname'],
        port=config['alt_db_port'],
        autocommit=True)

    alt_cursor = await alt_mydb.cursor()
    return alt_cursor

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

async def get_oldest_mon_date(config, use_alt_table=False):
    if use_alt_table:
        cursor_oldest_mon_date = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_oldest_mon_date = await connect_db(config)
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query_oldest_mon_date = f"select min(last_modified) from {table}"
    elif config['db_scan_schema'] == "rdm":
        query_oldest_mon_date = f"select from_unixtime(min(first_seen_timestamp)) from {table}"
    await cursor_oldest_mon_date.execute(query_oldest_mon_date)
    oldest_mon_date = await cursor_oldest_mon_date.fetchall()
    for var in oldest_mon_date:
        oldest_mon_date = var[0]

    await cursor_oldest_mon_date.close()
    return oldest_mon_date

async def get_shiny_count(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        cursor_shiny_count = await connect_alt_db(config)
        table = config['alt_pokemon_table']
        shiny_table = config['alt_shiny_table']
    else:
        cursor_shiny_count = await connect_db(config)
        table = 'pokemon'
        shiny_table = 'trs_stats_detect_raw'
    if config['db_scan_schema'] == "mad":
        query_shiny_count = f"select count({table}.pokemon_id) from {table} join {shiny_table} stats on cast(stats.type_id as unsigned int) = {table}.encounter_id where stats.is_shiny=1 and {table}.pokemon_id={mon_id} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00')"
    elif config['db_scan_schema'] == "rdm":
        query_shiny_count = f"select count(pokemon_id) from {table} where shiny = 1 AND pokemon_id = {mon_id} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    await cursor_shiny_count.execute(query_shiny_count)
    shiny_count = await cursor_shiny_count.fetchall()
    for var in shiny_count:
        shiny_count = var[0]

    await cursor_shiny_count.close()
    return shiny_count
    
async def get_shiny_total(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        cursor_shiny_total = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_shiny_total = await connect_db(config)
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query_total_shiny_count = f"select count(pokemon_id) from {table} where pokemon_id={mon_id} and disappear_time > utc_timestamp() - INTERVAL 8 WEEK and individual_attack is not null AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00')"
    elif config['db_scan_schema'] == "rdm":
        query_total_shiny_count = f"SELECT count(pokemon_id) from {table} WHERE pokemon_id = {mon_id} and atk_iv is not null AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) and first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    await cursor_shiny_total.execute(query_total_shiny_count)
    shiny_total = await cursor_shiny_total.fetchall()
    for var in shiny_total:
        shiny_total = var[0]

    await cursor_shiny_total.close()
    return shiny_total

async def get_scan_numbers(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        cursor_scan_numbers = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_scan_numbers = await connect_db(config)
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query_hundo_count = f"select count(pokemon_id) as scanned, ifnull(SUM(individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15), 0) AS iv100, ifnull(SUM(individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0), 0) AS iv0, ifnull(SUM(individual_attack + individual_defense + individual_stamina >= 41), 0) AS iv90 from {table} where pokemon_id = {mon_id} and individual_attack IS NOT NULL AND disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00') AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))"
    elif config['db_scan_schema'] == "rdm":
        query_hundo_count = f"select count(id) as scanned, ifnull(SUM(iv = 100), 0) AS iv100, ifnull(SUM(iv = 0), 0) AS iv0, ifnull(SUM(iv > 90), 0) AS iv90 from {table} where pokemon_id = {mon_id} and iv IS NOT NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    await cursor_scan_numbers.execute(query_hundo_count)
    hundo_count = await cursor_scan_numbers.fetchall()

    await cursor_scan_numbers.close()
    return hundo_count

async def get_big_numbers(mon_id, area, starttime, endtime, config, use_alt_table=False):
    if use_alt_table:
        cursor_big_numbers = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_big_numbers = await connect_db(config)
        table = 'pokemon'
    if config['db_scan_schema'] == "mad":
        query_big_count = f"select count(pokemon_id), ifnull(sum(pokemon_id = {mon_id}), 0), ifnull(sum(weather_boosted_condition > 0 and pokemon_id = {mon_id}), 0), min(disappear_time) from {table} WHERE disappear_time > convert_tz('{starttime}', '{config['timezone']}', '+00:00') AND disappear_time < convert_tz('{endtime}', '{config['timezone']}', '+00:00') AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))"
    elif config['db_scan_schema'] == "rdm":
        query_big_count = f"select count(id), ifnull(sum(pokemon_id = {mon_id}), 0), ifnull(sum(weather > 0 and pokemon_id = {mon_id}), 0), FROM_UNIXTIME(min(first_seen_timestamp)) from {table} WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) AND first_seen_timestamp > UNIX_TIMESTAMP(convert_tz('{starttime}', '{config['timezone']}', '+00:00')) AND first_seen_timestamp < UNIX_TIMESTAMP(convert_tz('{endtime}', '{config['timezone']}', '+00:00'))"
    await cursor_big_numbers.execute(query_big_count)
    big_numbers = await cursor_big_numbers.fetchall()

    await cursor_big_numbers.close()
    return big_numbers

async def get_active_raids(config, area, level_list, tz_offset, ex=False):
    levels = "("
    for level in level_list:
        levels = f"{levels}{level},"
    levels = levels[:-1]
    levels = f"{levels})"

    where_ex = ""

    cursor_raids = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        if ex:
            where_ex = "AND is_ex_raid_eligible = 1"
        await cursor_raids.execute(f"SELECT gym.gym_id, Unix_timestamp(Convert_tz(start, '+00:00', '{tz_offset}')) AS starts, Unix_timestamp(Convert_tz(end, '+00:00', '{tz_offset}')) AS ends, latitude, longitude, pokemon_id, move_1, move_2, name, is_ex_raid_eligible, level, url, raid.form FROM gym LEFT JOIN gymdetails ON gym.gym_id = gymdetails.gym_id LEFT JOIN raid ON gym.gym_id = raid.gym_id WHERE name IS NOT NULL {where_ex} AND end > UTC_TIMESTAMP() AND level IN {levels} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) ORDER BY end;")
    elif config['db_scan_schema'] == "rdm":
        if ex:
            where_ex = "AND ex_raid_eligible = 1"
        await cursor_raids.execute(f"SELECT id, (UNIX_TIMESTAMP(CONVERT_TZ((FROM_UNIXTIME(raid_battle_timestamp)), '+00:00', '{tz_offset}'))) AS starts, (UNIX_TIMESTAMP(CONVERT_TZ((FROM_UNIXTIME(raid_end_timestamp)), '+00:00', '{tz_offset}'))) AS ends, lat, lon, raid_pokemon_id, raid_pokemon_move_1, raid_pokemon_move_2, name, ex_raid_eligible, raid_level, url, raid_pokemon_form FROM gym WHERE name IS NOT NULL {where_ex} AND raid_end_timestamp > UNIX_TIMESTAMP() AND raid_level in {levels} AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) ORDER BY raid_end_timestamp; ")
    raids = await cursor_raids.fetchall()

    await cursor_raids.close()
    return raids

async def get_active_quests(config, area):
    cursor_active_quests = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_active_quests.execute(f"select quest_reward, quest_task, latitude, longitude, name, pokestop_id from trs_quest left join pokestop on trs_quest.GUID = pokestop.pokestop_id WHERE quest_timestamp > UNIX_TIMESTAMP(CURDATE()) AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)) ORDER BY quest_item_id ASC, quest_pokemon_id ASC, name;")
    elif config['db_scan_schema'] == "rdm":
        await cursor_active_quests.execute(f"select quest_rewards, quest_template, lat, lon, name, id from pokestop WHERE quest_type IS NOT NULL AND ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)) ORDER BY quest_item_id ASC, quest_pokemon_id ASC, name;")
    quests = await cursor_active_quests.fetchall()

    await cursor_active_quests.close()
    return quests

async def get_gym_stats(config, area):
    cursor_gym_stats = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_gym_stats.execute(f"select count(gym.gym_id), IFNULL(SUM(team_id = 0), 0), IFNULL(SUM(team_id = 1), 0), IFNULL(SUM(team_id=2), 0), IFNULL(SUM(team_id=3), 0), IFNULL(SUM(is_ex_raid_eligible = 1), 0), IFNULL(SUM(end >= utc_timestamp()), 0) from gym left join raid on gym.gym_id = raid.gym_id where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_gym_stats.execute(f"select count(id), IFNULL(SUM(team_id = 0), 0), IFNULL(SUM(team_id = 1), 0), IFNULL(SUM(team_id=2), 0), IFNULL(SUM(team_id=3), 0), IFNULL(SUM(ex_raid_eligible = 1), 0), IFNULL(SUM(raid_end_timestamp > UNIX_TIMESTAMP()), 0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    gym_stats = await cursor_gym_stats.fetchall()

    await cursor_gym_stats.close()
    return gym_stats

async def statboard_mon_active(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_mon_active = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_mon_active = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_mon_active.execute(f"select count(pokemon_id) from {table} where disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_mon_active.execute(f"select count(id) from {table} WHERE expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_mon_active = await cursor_statboard_mon_active.fetchall()

    await cursor_statboard_mon_active.close()
    return statboard_mon_active

async def statboard_mon_today(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_mon_today = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_mon_today = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_mon_today.execute(f"select count(pokemon_id) from {table} where CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_mon_today.execute(f"select count(id) from {table} WHERE CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_mon_today = await cursor_statboard_mon_today.fetchall()

    await cursor_statboard_mon_today.close()
    return statboard_mon_today

async def statboard_hundos_active(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_hundos_active = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_hundos_active = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_hundos_active.execute(f"select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_hundos_active.execute(f"select count(id) from {table} WHERE iv = 100 AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_hundos_active = await cursor_statboard_hundos_active.fetchall()

    await cursor_statboard_hundos_active.close()
    return statboard_hundos_active

async def statboard_hundos_today(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_hundos_today = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_hundos_today = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_hundos_today.execute(f"select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_hundos_today.execute(f"select count(id) from {table} where iv = 100 AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_hundos_today = await cursor_statboard_hundos_today.fetchall()

    await cursor_statboard_hundos_today.close()
    return statboard_hundos_today

async def statboard_iv0_active(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_iv0_active = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_iv0_active = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_iv0_active.execute(f"select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_iv0_active.execute(f"select count(id) from {table} WHERE iv = 0 AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_iv0_active = await cursor_statboard_iv0_active.fetchall()

    await cursor_statboard_iv0_active.close()
    return statboard_iv0_active

async def statboard_iv0_today(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_iv0_today = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_iv0_today = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_iv0_today.execute(f"select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_iv0_today.execute(f"select count(id) from {table} where iv = 0 AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_iv0_today = await cursor_statboard_iv0_today.fetchall()

    await cursor_statboard_iv0_today.close()
    return statboard_iv0_today

async def statboard_scanned_active(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_scanned_active = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_scanned_active = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_scanned_active.execute(f"select count(pokemon_id) from {table} where individual_attack is not NULL and disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_scanned_active.execute(f"select count(id) from {table} WHERE iv is not NULL AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_scanned_active = await cursor_statboard_scanned_active.fetchall()

    await cursor_statboard_scanned_active.close()
    return statboard_scanned_active

async def statboard_scanned_today(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_scanned_today = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_scanned_today = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_scanned_today.execute(f"select count(pokemon_id) from {table} where individual_attack is not NULL AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_scanned_today.execute(f"select count(id) from {table} where iv is not NULL AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_scanned_today = await cursor_statboard_scanned_today.fetchall()

    await cursor_statboard_scanned_today.close()
    return statboard_scanned_today

async def statboard_total_iv_active(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_total_iv_active = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_total_iv_active = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_total_iv_active.execute(f"select ifnull(sum((individual_attack + individual_defense + individual_stamina)/45*100),0) from {table} where individual_attack is not NULL and disappear_time > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_total_iv_active.execute(f"select ifnull(sum(iv),0) from {table} WHERE iv is not NULL AND expire_timestamp > UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_total_iv_active = await cursor_statboard_total_iv_active.fetchall()

    await cursor_statboard_total_iv_active.close()
    return statboard_total_iv_active

async def statboard_total_iv_today(config, area, use_alt_table=False):
    if use_alt_table:
        cursor_statboard_total_iv_today = await connect_alt_db(config)
        table = config['alt_pokemon_table']
    else:
        cursor_statboard_total_iv_today = await connect_db(config)
        table = 'pokemon'

    if config['db_scan_schema'] == "mad":
        await cursor_statboard_total_iv_today.execute(f"select ifnull(sum((individual_attack + individual_defense + individual_stamina)/45*100),0) from {table} where individual_attack is not NULL AND CONVERT_TZ({table}.disappear_time,'+00:00','{config['timezone']}') > curdate() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_total_iv_today.execute(f"select ifnull(sum(iv),0) from {table} where iv is not NULL AND CONVERT_TZ(from_unixtime(first_seen_timestamp),'+00:00','{config['timezone']}') > CURDATE() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_total_iv_today = await cursor_statboard_total_iv_today.fetchall()

    await cursor_statboard_total_iv_today.close()
    return statboard_total_iv_today

async def statboard_gym_amount(config, area):
    cursor_statboard_gym_amount = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_gym_amount.execute(f"select count(gym_id) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_gym_amount.execute(f"select count(id) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_gym_amount = await cursor_statboard_gym_amount.fetchall()

    await cursor_statboard_gym_amount.close()
    return statboard_gym_amount

async def statboard_gym_teams(config, area):
    cursor_statboard_gym_teams = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_gym_teams.execute(f"select ifnull(sum(team_id = 0),0), ifnull(sum(team_id = 1),0), ifnull(sum(team_id=2),0), ifnull(sum(team_id=3),0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_gym_teams.execute(f"select ifnull(sum(team_id = 0),0), ifnull(sum(team_id = 1),0), ifnull(sum(team_id=2),0), ifnull(sum(team_id=3),0) from gym where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_gym_teams = await cursor_statboard_gym_teams.fetchall()

    await cursor_statboard_gym_teams.close()
    return statboard_gym_teams

async def statboard_raid_active(config, area):
    cursor_statboard_raid_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_raid_active.execute(f"select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0) from gym left join raid on gym.gym_id = raid.gym_id where end >= utc_timestamp() and start <= utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_raid_active.execute(f"select count(id), ifnull(sum(raid_level = 1), 0), ifnull(sum(raid_level = 2),0), ifnull(sum(raid_level = 3),0), ifnull(sum(raid_level = 4),0), ifnull(sum(raid_level = 5),0) from gym where raid_battle_timestamp < UNIX_TIMESTAMP() AND raid_end_timestamp >= UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_raid_active = await cursor_statboard_raid_active.fetchall()

    await cursor_statboard_raid_active.close()
    return statboard_raid_active

async def statboard_egg_active(config, area):
    cursor_statboard_egg_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_egg_active.execute(f"select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0) from gym left join raid on gym.gym_id = raid.gym_id where start > utc_timestamp() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_egg_active.execute(f"select count(id), ifnull(sum(raid_level = 1), 0), ifnull(sum(raid_level = 2),0), ifnull(sum(raid_level = 3),0), ifnull(sum(raid_level = 4),0), ifnull(sum(raid_level = 5),0) from gym WHERE raid_battle_timestamp >= UNIX_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_egg_active = await cursor_statboard_egg_active.fetchall()

    await cursor_statboard_egg_active.close()
    return statboard_egg_active

async def statboard_stop_amount(config, area):
    cursor_statboard_stop_amount = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_stop_amount.execute(f"select count(pokestop_id) from pokestop where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_stop_amount.execute(f"select count(id) from pokestop where ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_stop_amount = await cursor_statboard_stop_amount.fetchall()

    await cursor_statboard_stop_amount.close()
    return statboard_stop_amount

async def statboard_lure_active(config, area):
    cursor_statboard_lure_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_lure_active.execute(f"select count(pokestop_id), ifnull(sum(active_fort_modifier = 501), 0), ifnull(sum(active_fort_modifier = 502), 0), ifnull(sum(active_fort_modifier = 503), 0), ifnull(sum(active_fort_modifier = 504), 0) from pokestop where lure_expiration > UTC_TIMESTAMP() and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_lure_active.execute(f"select count(id), ifnull(sum(lure_id = 501), 0), ifnull(sum(lure_id = 502), 0), ifnull(sum(lure_id = 503), 0), ifnull(sum(lure_id = 504), 0) from pokestop where lure_expire_timestamp is not NULL and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_lure_active = await cursor_statboard_lure_active.fetchall()

    await cursor_statboard_lure_active.close()
    return statboard_lure_active

async def statboard_grunt_active(config, area):
    cursor_statboard_grunt_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_grunt_active.execute(f"select count(pokestop_id) from pokestop where incident_expiration > UTC_TIMESTAMP() AND incident_grunt_type NOT IN (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_grunt_active.execute(f"select count(id) from pokestop where grunt_type not in (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_grunt_active = await cursor_statboard_grunt_active.fetchall()

    await cursor_statboard_grunt_active.close()
    return statboard_grunt_active

async def statboard_leader_active(config, area):
    cursor_statboard_leader_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_leader_active.execute(f"select count(pokestop_id) from pokestop where incident_expiration > UTC_TIMESTAMP() AND incident_grunt_type >= 41 AND incident_grunt_type <= 44 and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_leader_active.execute(f"select count(id) from pokestop where grunt_type in (41,42,43,44) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_leader_active = await cursor_statboard_leader_active.fetchall()

    await cursor_statboard_leader_active.close()
    return statboard_leader_active

async def statboard_quest_active(config, area):
    cursor_statboard_quest_active = await connect_db(config)
    if config['db_scan_schema'] == "mad":
        await cursor_statboard_quest_active.execute(f"select count(GUID) from pokestop left join trs_quest on pokestop.pokestop_id = trs_quest.GUID where quest_timestamp > UNIX_TIMESTAMP(CURDATE()) and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))")
    elif config['db_scan_schema'] == "rdm":
        await cursor_statboard_quest_active.execute(f"select count(id) from pokestop where quest_type is not null and ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))")
    statboard_quest_active = await cursor_statboard_quest_active.fetchall()

    await cursor_statboard_quest_active.close()
    return statboard_quest_active
