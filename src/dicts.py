from AzeibarjanWarBOT.utils.strings import *


dealer_resources = {
    "centur": ["shahid_blood"],
    "melihor": ["shahid_blood"],
    "nokturn": ["shahid_blood"],
}


item_haracteristics = {
    "damage": waepon_info_list[5],
    "health": waepon_info_list[6],
    "protect": hero_information_title[3],
    "critical": waepon_info_list[7],
    "dodge": hero_information_title[-1],
    "need_lvl": waepon_info_list[9],
    "need_power": waepon_info_list[10],
    "need_force": waepon_info_list[11],
    "need_intuition": hero_information_title[9],
    "need_dexterity": hero_information_title[8]
}

# Если нужно торговцу добавить предмет который в таблице ресурсов
resources_chield_types = ["scroll"]

item_buttons = {
    "sword": dealer_weapon_button_list[0],
    "axe": dealer_weapon_button_list[1],
    "dagger": dealer_weapon_button_list[2],
    "helmet": dealer_protect_button_list[0],
    "armor": dealer_protect_button_list[1],
    "boots": dealer_protect_button_list[4],
    "shield": dealer_protect_button_list[2],
    "gloves": dealer_protect_button_list[3],
    "ring": dealer_product_button_list[1],
    "necklace": dealer_product_button_list[0],
    "accessory": dealer_protect_button_list[5]
}

course_variants = {
    start_choose_course[0]: "white_sheep",
    start_choose_course[1]: "black_sheep",
    start_choose_course[2]: "shirvansha",

}

# ------
querry_variants = {
    data_help_answers_text[0]: "opponents",
    data_help_answers_text[1]: "items",
    data_help_answers_text[2]: "resources",
    data_help_answers_text[3]: "tricks",
    data_help_answers_text[4]: "users",
    check_clan_users_button[1]: "clan_users",
    search_clan[1]: "clans"
}

names_inline_array_types = {
    "opponents": "name",
    "items": "title",
    "resources": "title",
    "tricks": "title",
    "users": "nickname",
    "clan_users": "id"
}
# ------


transitions_v2 = {
    "baki": transitions_names[4],
    "river": transitions_names[1],
    "wasteland": transitions_names[0],
    "house_in_the_forest": transitions_names[2],
    "karabah": transitions_names[3],
    "hotbed_of_resistance": transitions_names[5],
    "cursed_lands": transitions_names[6],
    "zealot_camp": transitions_names[7],
    "gandja": transitions_names[8],
    "urt": transitions_names[9],
    "gala": transitions_names[10],
    "scala": transitions_names[11],
    "coliseum": transitions_names[12]
}


async def get_transitions(locations_l) -> list[str]:
    return [transitions_v2[location_name] for location_name in locations_l]



equip_types = ["sword", "axe", "dagger", "helmet", "armor", "boots", "shield", "gloves", "ring", "necklace", "accessory"]

coupon_shop_values = {
    "c_regeneration": ["regen_7", "regen_3", "regen_1"],
    "c_other": ["scroll_reset", "reset_course", "reset_nickname"],
    "c_gold": ["openbag_3", "openbag_2", "openbag_1"],
    "c_keys": ["nft_key"],
    "c_premium": ["prem_7", "prem_15", "prem_30"],
    "c_xp": ["potion_xp_2", "potion_xp_3", "potion_xp_4"]
}


bags_result = {
    1: 100,
    2: 250,
    3: 600
}


block_variants = {
    0: [5, 9],
    1: [5, 6],
    2: [6, 7],
    3: [7, 8],
    4: [8, 9]
}

clan_winners_positions = {
    "baki": 0,
    "karabah": 1,
    "gandja": 2
}


clan_war_rewards = {
    1: {"nft_key": 3, "regen_3": 2, "shahid_blood": 8, "gold": 300},
    2: {"nft_key": 2, "regen_3": 1, "shahid_blood": 5, "gold": 200},
    3: {"nft_key": 1, "shahid_blood": 3, "gold": 3150}
}

box_open_cost_value = {"siravi_box": 1, "epic_box": 2, "legendary_box": 3}

box_additional_loot = {
    "siravi_box": [("openbag_1",), ("scroll_reset",), ("reset_nickname",), ("reset_course",), ("regen_1",),
                   ("nft_key 2",)],
    "epic_box": [("openbag_2",), ("scroll_reset",), ("reset_nickname",), ("reset_course",), ("regen_1",),
                 ("nft_key 5",)],
    "legendary_box": [("openbag_3",), ("scroll_reset",), ("reset_nickname",), ("reset_course",), ("regen_1 2",),
                      ("nft_key 8",)]}


trainers_trick_list = {"ael": ["without_feelings", "soul_helper", "handy_tool", "hit_warrior"],
                       "aidzen": ["brave_fist", "dragons_hit", "head_butt", "lightning_strike", "chapalah", "sharingan"],
                       "urahara": ["deflection", "gashgaldah", "shahids_hit", "berserks_hit"]}

blacksmits_types = ["kuchiki_sword", "kuchiki_axe", "kuchiki_dagger", "kuchiki_helmet", "kuchiki_armor", "kuchiki_boots", "kuchiki_shield", "kuchiki_gloves", "kuchiki_ring", "kuchiki_necklace",
                    "tessai_sword", "tessai_axe", "tessai_dagger", "tessai_helmet", "tessai_armor", "tessai_boots", "tessai_shield", "tessai_gloves", "tessai_ring", "tessai_necklace"]



