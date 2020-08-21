import aiomysql
import asyncio

class Queries():
    def __init__(self, bot):
        self.bot = bot
        self.generate_queries()
        
    async def execute(self, query_string, sql_fence="", table=""):
        query = self.queries.get(query_string, query_string)
        query = query.format(area=sql_fence, timezone="+02:00", table="pokemon") #TODO TIMEZONES, EXTRA TABLES
        pool = await aiomysql.create_pool(host=self.bot.config.db_host, port=self.bot.config.db_port, user=self.bot.config.db_user, password=self.bot.config.db_pass, db=self.bot.config.db_dbname)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                r = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return r
    
    def generate_queries(self):
        if self.bot.config.db_scan_schema == "mad":
            generics = {
                "area": "" + "ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))",
                "timezone": "CONVERT_TZ({table}.{column},'+00:00','{timezone}')"
            }
            self.queries = {
                "active_raids": "SELECT gym.gym_id, Unix_timestamp(CONVERT_TZ(spawn,'+00:00','{timezone}')) AS starts, Unix_timestamp(CONVERT_TZ(end,'+00:00','{timezone}')) AS ends, latitude, longitude, ifnull(pokemon_id, 0), move_1, move_2, name, is_ex_raid_eligible, level, url, raid.form FROM gym LEFT JOIN gymdetails ON gym.gym_id = gymdetails.gym_id LEFT JOIN raid ON gym.gym_id = raid.gym_id WHERE name IS NOT NULL AND end > UTC_TIMESTAMP() AND " + generics["area"] + " ORDER BY end;",
                "active_quests": "select quest_reward, quest_task, latitude, longitude, name, pokestop_id from trs_quest left join pokestop on trs_quest.GUID = pokestop.pokestop_id WHERE quest_timestamp > UNIX_TIMESTAMP(CURDATE()) AND " + generics["area"] + " ORDER BY quest_item_id ASC, quest_pokemon_id ASC, name;"

                """
                #Stat Board
                "mon_active": "select count(pokemon_id) from {table} where disappear_time > utc_timestamp() and " + generics["area"],
                "mon_today": "select count(pokemon_id) from {table} where " + generics["timezone"].format(column="disappear_time") + " > curdate() and " + generics["area"],
                "scanned_active": "select count(pokemon_id) from {table} where individual_attack is not NULL and disappear_time > utc_timestamp() and " + generics["area"],
                "scanned_today": "select count(pokemon_id) from {table} where individual_attack is not NULL AND " + generics["timezone"].format(column="disappear_time") + " > curdate() and " + generics["area"],
                "hundos_active": "select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND disappear_time > utc_timestamp() and " + generics["area"],
                "hundos_today": "select count(pokemon_id) from {table} where individual_attack = 15 AND individual_defense = 15 AND individual_stamina = 15 AND " + generics["timezone"].format(column="disappear_time") + " > curdate() and " + generics["area"],
                "zeros_active": "select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND disappear_time > utc_timestamp() and " + generics["area"],
                "zeros_today": "select count(pokemon_id) from {table} where individual_attack = 0 AND individual_defense = 0 AND individual_stamina = 0 AND " + generics["timezone"].format(column="disappear_time") + " > curdate() and " + generics["area"],

                "gym_amount": "select count(gym_id) from gym where " + generics["area"],
                "gym_teams": "select ifnull(sum(team_id = 0),0), ifnull(sum(team_id = 1),0), ifnull(sum(team_id=2),0), ifnull(sum(team_id=3),0) from gym where " + generics["area"],

                "raid_active": "select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0) from gym left join raid on gym.gym_id = raid.gym_id where end >= utc_timestamp() and start <= utc_timestamp() and " + generics["area"],
                "egg_active": "select count(raid.gym_id) from gym left join raid on gym.gym_id = raid.gym_id where start > utc_timestamp() and " + generics["area"],
                "egg_levels_active": "select count(raid.gym_id), ifnull(sum(level = 1), 0), ifnull(sum(level = 2),0), ifnull(sum(level = 3),0), ifnull(sum(level = 4),0), ifnull(sum(level = 5),0) from gym left join raid on gym.gym_id = raid.gym_id where start > utc_timestamp() and " + generics["area"],
                
                "stop_amount": "select count(pokestop_id) from pokestop where " + generics["area"],
                "lure_active": "select count(pokestop_id), ifnull(sum(active_fort_modifier = 501), 0), ifnull(sum(active_fort_modifier = 502), 0), ifnull(sum(active_fort_modifier = 503), 0), ifnull(sum(active_fort_modifier = 504), 0) from pokestop where lure_expiration > UTC_TIMESTAMP() and " + generics["area"],
                "grunt_active": "select count(pokestop_id) from pokestop where incident_expiration > UTC_TIMESTAMP() AND incident_grunt_type NOT IN (41,42,43,44) and " + generics["area"],
                "leader_active": "select count(pokestop_id) from pokestop where incident_expiration > UTC_TIMESTAMP() AND incident_grunt_type >= 41 AND incident_grunt_type <= 44 and " + generics["area"],
                "quest_active": "select count(GUID) from pokestop left join trs_quest on pokestop.pokestop_id = trs_quest.GUID where quest_timestamp > UNIX_TIMESTAMP(CURDATE()) and " + generics["area"]
            """
            }
        elif self.bot.config.db_scan_schema == "rdm":
            generics = {
                "area": "ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))"
            }