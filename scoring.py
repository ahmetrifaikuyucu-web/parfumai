# ParfumAI — Puanlama Motoru
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

from questions import QUESTIONS

NOTE_CATEGORIES = {
    "top": {
        "citrus": ["bergamot", "lemon", "orange", "grapefruit", "mandarin", "lime", "yuzu", "kumquat"],
        "green": ["green", "grass", "leaf", "galbanum", "fig_leaf", "violet_leaf", "stem", "hay_top"],
        "aqua": ["aqua", "marine", "ozone", "sea", "salt", "calone", "water", "ocean"],
        "fruity_top": ["apple", "pear", "pineapple", "tropical", "berry", "melon", "peach_top", "cassis"],
        "aldehyde": ["aldehyde", "aldehydic", "soapy", "sparkling", "champagne"],
        "spice_top": ["pepper", "pink_pepper", "black_pepper", "saffron_top", "chili"],
        "aromatic_top": ["mint", "peppermint", "eucalyptus", "anis", "basil_top", "tarragon"],
        "bergamot": ["bergamot", "bergamot_top"]
    },
    "middle": {
        "floral": ["rose", "jasmine", "ylang", "orchid", "gardenia", "freesia", "lily", "carnation", "champaca"],
        "white_floral": ["jasmine", "tuberose", "gardenia", "lily", "neroli", "orange_blossom", "stephanotis"],
        "spice_mid": ["cinnamon", "clove", "cardamom", "ginger", "nutmeg", "saffron", "coriander", "caraway"],
        "herbal": ["lavender", "sage", "rosemary", "thyme", "basil", "mint", "chamomile", "clary_sage"],
        "fruity_mid": ["peach", "apricot", "plum", "raspberry", "strawberry", "lychee", "blackberry", "cherry"],
        "powdery": ["iris", "violet", "almond", "heliotrope", "powdery", "orris", "mimosa"],
        "honey_tobacco": ["honey", "tobacco_blossom", "beeswax", "hay", "broom"],
        "woody_mid": ["cedar_mid", "sandalwood_mid", "pine_mid", "cashmeran_mid"]
    },
    "base": {
        "woody": ["cedar", "sandalwood", "pine", "woody", "cashmeran", "cypress", "juniper", "akigalawood"],
        "amber": ["amber", "ambroxan", "ambergris", "labdanum", "golden_amber", "succinic"],
        "vanilla_gourmand": ["vanilla", "tonka", "benzoin", "caramel", "praline", "cocoa", "chocolate", "sugar", "cotton_candy"],
        "musk": ["musk", "white_musk", "cashmeran_musk", "vegetal_musk", "silky_musk"],
        "leather": ["leather", "suede", "isobutyl_quinoline", "birch_tar", "styrax"],
        "oud": ["oud", "agarwood", "oudh", "laos_oud"],
        "patchouli_earthy": ["patchouli", "earthy", "soil", "moss", "oakmoss", "tree_moss"],
        "incense_tobacco": ["incense", "frankincense", "myrrh", "tobacco", "hay", "dried_fruit", "raisin"]
    }
}

class ScoringEngine:
    def __init__(self):
        self.scores = {}
        self.nota_profili = {
            "top": {},
            "middle": {},
            "base": {}
        }

    def process_answers(self, answers):
        self.scores = {}
        for q_id, option_index in answers.items():
            try:
                q_id = int(q_id)
            except (ValueError, TypeError):
                continue
            question = next((q for q in QUESTIONS if q["id"] == q_id), None)
            if not question:
                continue
            if option_index < len(question["options"]):
                option = question["options"][option_index]
                for key, value in option["scores"].items():
                    self.scores[key] = self.scores.get(key, 0) + value

        self._calculate_nota_profili()
        return self.get_summary()

    def _calculate_nota_profili(self):
        self.nota_profili = {"top": {}, "middle": {}, "base": {}}
        note_mapping = {
            "top_citrus": ("top", "citrus"), "top_bergamot": ("top", "bergamot"),
            "top_green": ("top", "green"), "top_aqua": ("top", "aqua"),
            "top_aldehyde": ("top", "aldehyde"), "top_spice_top": ("top", "spice_top"),
            "top_aromatic_top": ("top", "aromatic_top"), "top_fruity_top": ("top", "fruity_top"),
            "middle_floral": ("middle", "floral"), "middle_white_floral": ("middle", "white_floral"),
            "middle_spice_mid": ("middle", "spice_mid"), "middle_herbal": ("middle", "herbal"),
            "middle_fruity_mid": ("middle", "fruity_mid"), "middle_powdery": ("middle", "powdery"),
            "middle_woody_mid": ("middle", "woody_mid"), "middle_honey_tobacco": ("middle", "honey_tobacco"),
            "base_woody": ("base", "woody"), "base_amber": ("base", "amber"),
            "base_vanilla_gourmand": ("base", "vanilla_gourmand"), "base_musk": ("base", "musk"),
            "base_leather": ("base", "leather"), "base_oud": ("base", "oud"),
            "base_patchouli_earthy": ("base", "patchouli_earthy"), "base_incense_tobacco": ("base", "incense_tobacco"),
        }

        for key, value in self.scores.items():
            if key in note_mapping:
                category, sub_category = note_mapping[key]
                if sub_category not in self.nota_profili[category]:
                    self.nota_profili[category][sub_category] = 0
                self.nota_profili[category][sub_category] += value

        for layer in ["top", "middle", "base"]:
            all_keys = list(NOTE_CATEGORIES[layer].keys())
            has_any = any(k in self.nota_profili[layer] for k in all_keys)
            if not has_any:
                for k in all_keys[:3]:
                    self.nota_profili[layer][k] = 1

    def get_summary(self):
        top_total = sum(self.nota_profili["top"].values())
        middle_total = sum(self.nota_profili["middle"].values())
        base_total = sum(self.nota_profili["base"].values())
        grand_total = top_total + middle_total + base_total

        if grand_total == 0:
            return {
                "top_pct": 33, "middle_pct": 33, "base_pct": 34,
                "top_dominant": "citrus",
                "middle_dominant": "floral",
                "base_dominant": "musk",
                "profile_type": "Dengeli",
                "nota_detay": self.nota_profili
            }

        top_pct = round((top_total / grand_total) * 100)
        middle_pct = round((middle_total / grand_total) * 100)
        base_pct = 100 - top_pct - middle_pct

        max_pct = max(top_pct, middle_pct, base_pct)
        if max_pct >= 40:
            if max_pct == top_pct:
                profile_type = "Yaz-Kehribar (Top Note Ağırlıklı)"
            elif max_pct == base_pct:
                profile_type = "Kış-Derin (Base Note Ağırlıklı)"
            elif max_pct == middle_pct:
                profile_type = "İlkbahar-Yaz (Middle Note Ağırlıklı)"
            else:
                profile_type = "Karma Profil"
        elif top_pct >= 35:
            profile_type = "Hafif Yaz Eğilimli"
        elif base_pct >= 35:
            profile_type = "Hafif Kış Eğilimli"
        elif top_pct >= 25 and middle_pct >= 25 and base_pct >= 20:
            profile_type = "4 Mevsim Unisex (Dengeli Profil)"
        else:
            profile_type = "Karma Profil"

        return {
            "top_pct": top_pct,
            "middle_pct": middle_pct,
            "base_pct": base_pct,
            "top_dominant": self._get_dominant(self.nota_profili["top"]),
            "middle_dominant": self._get_dominant(self.nota_profili["middle"]),
            "base_dominant": self._get_dominant(self.nota_profili["base"]),
            "profile_type": profile_type,
            "nota_detay": self.nota_profili
        }

    def _get_dominant(self, category_dict):
        if not category_dict:
            return "none"
        return max(category_dict, key=category_dict.get)

    def get_note_profile_vector(self):
        summary = self.get_summary()
        return {
            "top_dominant": summary["top_dominant"],
            "middle_dominant": summary["middle_dominant"],
            "base_dominant": summary["base_dominant"],
            "top_pct": summary["top_pct"],
            "middle_pct": summary["middle_pct"],
            "base_pct": summary["base_pct"]
        }
