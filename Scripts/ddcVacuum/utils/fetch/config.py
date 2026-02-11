"""
Configuration for Google Sheets data fetching

Defines sheet IDs and output directories
"""

# Google Sheets document ID
SHEET_ID = "1tfa3mEwTWLrPUEw2p9aRKWUH37quVgpkyVisB6E1DZU"

# Sheet names mapped to their GID (tab identifier)
SHEETS = {
    "WeaponPerks": "1703329297",
    "SeasonWeaponPerks": "1175376862",
    "WeaponMods": "296976005",
    "IntrinsicTraits": "1368736324",
    "OriginTraits": "1050893845",
    "ArmorSets": "1916736284",
    "ArmorMods": "923125516",
    "ArtifactPerks": "828585521",

    "ArcVerbs": "41303738",
    #"ArcFragments": "1886162144",
    "ArcSubclass": "1622235249",

    "SolarVerbs": "993506142",
    #"SolarFragments": "514016694",
    "SolarSubclass": "1265947024",

    "VoidVerbs": "1094405333",
    #"VoidFragments": "199206387",
    "VoidSubclass": "214908620",

    "StasisVerbs": "258124247",
    #"StasisFragments": "1910636551",
    "StasisSubclass": "306610633",

    "StrandVerbs": "976476629",
    #"StrandFragments": "143366149",
    "StrandSubclass": "593125843",

    "PrismaticVerbs": "1280102267",
    "PrismaticFragments": "184315295",

    "ExoticWeapons": "1301197513",
}

# Output directory for exported JSON files
OUTPUT_DIR = "data"