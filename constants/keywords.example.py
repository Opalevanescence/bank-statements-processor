from enum import Enum

# --------------------------------------------------------------------
# Keywords
# --------------------------------------------------------------------

# CHARITY
NON_PROFIT_KEYWORDS = [
    "Planned Parenthood",
]

POLITICS_KEYWORDS = [
    "Democrat", 
]

ARTS_KEYWORDS = [
    "patreon", 
]

# FOOD
GROCERY_KEYWORDS = [
    "grocery",
    "aldi",
    "tesco",
    "sainsbury",
    "waitrose",
    "marks&spencer",
    "atif",
    "lidl",
    "MISSING BEAN",
    "MILLE FEUILLE OXFORD",
    "CO-OPERATIVE FOOD",
    "PAK HALAL ERDEM FOOD CE OXFORD",
    "JGS Meat & Grocery Oxford",
    "THE LARDER OXFORD",
    "WILD HONEY LOVE OXFORD OX4",
    "M&S SIMPLY FOOD",
    "THE ISIS FARMHOUSE",
    "ICELAND",
    "KOREA FOODS CO SP10 OXFORD",
    "Al Amin Oxford",
    "EXCHANGE EDICOLA SOUVEN ROMA",
    "DAVID JOHN OXFORD",
    "asda store",
    "Grocery",
    "MS Markets",
    "BUTCHERS",
    "THE OXFORD WINE COMPAN",
    "Jericho Cheese Company",
    "KHALIFA SUPERSTORE"
]

RESTAURANT_KEYWORDS = [
	"The Rusty Bicycle",
    "KFC",
    "KEBAB",
    "McDonald's",
    "McDonalds",
    "Burger King",
    "Pizza",
	"Bistro",
	"THE BRIDGE BAR",
	"THE MAD HATTER OXFORD",
	"Blenheim - Orangery Woodstock",
	"NANDOS OXFORD OXFORD",
	"Vaults and Garden Oxford",
	"GREENE KING",
	"Ramen Korner Oxford",
	"The Big Society Oxford",
	"GAILS",
	"Quod Bar & Restaurant",
	"PRET A MANGER",
	"THE ALTERNATIVE TUCK",
	"RISTORANTE",
	"BISTROT",
	"GELATERIA",
	"burger",
	"THE BOAT HOUSE CAFE",
	"Old Bank Hotel",
	"CREPES LTD",
	"Restaurant",
	"BRUNCH",
]
CAFE_KEYWORDS = [
	"NERO",
]
SNACKS_KEYWORDS = [
	"COFFEE",
	"BUFFET",
]
SNACKS_TRAVEL_KEYWORDS = [
    "Starbucks",
    "DUTY-FREE",
    "AEROPUERTO",
	"AEROPORTO",
]

# FUN
BRIDESMAID_KEYWORDS = ["bridesmaid"]
CLOTHES_KEYWORDS = [
	"UNIQLO",
    "ZARA",
    "H&M",
    "MANGO",
    "NIKE",
    "ADIDAS",
	"Foot Locker",
	"OXFORD TAILORING",
	"HOBBS LTD",
	"ANTHROPOLOGIE",
	"NEXT RETAIL LTD",
	"JOHN LEWIS",
]
ENTERTAINMENT_KEYWORDS = [
	"BLACKWELL'S",
	"WATERSTONES",
	"ODEON",
]
SUBSCRIPTION_KEYWORDS = ["SPOTIFY", "NETFLIX", "Kindle",]
WEDDING_KEYWORDS = ["wedding"]
FUN_OTHER_KEYWORDS = ["SP HOYLES OF OXFORD"]


# HEALTH
DOCTOR_KEYWORDS = ["Sutter Health", "NHS"]
PHARMACY_KEYWORDS = [
	"Boots", 
]
EYES=["SPECSVRS"]
PT_KEYWORDS = ["Physicaal Therapy"]
MASSAGE_KEYWORDS = ["MASSAGE"]
GYM_KEYWORDS = ["Iffley Road Fitness"]
HEALTH_OTHER_KEYWORDS = ["CYCLE KING"]
HAIR = ["VERSUS OXFORD"]

# HOME
CLEANING_KEYWORDS = ["ROBERT DYAS"]
KITCHEN_KEYWORDS = [
    "CRATE&BARREL", 
    "IKEA", 
    "TK MAXX",
    "T K MAXX",
]
REPAIR = ["TIMPSON LIMITED OXON"]
OTHER_HOME_KEYWORDS = [
	"WH Smith", 
	"R99RT8S15 LONDON",
	"T74JN4YH5 LONDON"
]

# PRESENT
FRIEND_KEYWORDS = ["SOCTOPUS"]
FAMILY_KEYWORDS = [
	"Pierre Marcolini", 
    "POST OFFICE COUNTER OXFORD",
    "POST OFFICE SELF SERVE",
    "BABYLON",
]

# RENT
RENTAL_KEYWORDS = ["PENNY & SINCLAIR"]
UTILITIES_KEYWORDS = ["PNET"]
TAX_KEYWORDS = ["oxford city council",]

# TRAVEL
CAR_RENTAL_KEYWORDS = [
    "HERTZ",
    "AVIS",
    "ENTERPRISE",
    "EUROPCAR",
    "BUDGET",
    "Sixt"
]
HOTEL_KEYWORDS = [
    "HOTEL ALHAMBRA PALACE GRANADA",
    "AIRBNB",
    "PREMIER INN WIGAN",
    "SEYCHELLES",
]
PLANE_KEYWORDS = [
	"ALASKA AIR",
    "AIR FRANCE",
    "BRITISH AIRWAYS",
    "BRITISH A",
    "EASYJET",
    "IBERIA"
    "KLM",
    "RYANAIR",
    "TAP AIR PORTUGAL"
    "TAP PORTUGAL",
    "IBERIA",
]
TAXI_KEYWORDS = ["Uber", "CCSCabCard", "TAXI", "London Taxi"]
TRAIN_KEYWORDS = ["GWR", "Flytoget", "Eurostar", "Trenitalia"]
PHONE_PLAN = ["HOLAFLY.COM"]

# LOCAL TRAVEL
BUS_KEYWORDS = [
    "OXFORD BUS COMPANY", 
    "STAGECOACH BUS",
    "Redline Buses",
]
CAR_KEYWORDS = ["FASTRAK", "CA DMV",]
TRAIN_COMMUTE_KEYWORDS = [
  "GWR",
  "Alpha Cars",
  "Kai cheong",
  "MUHAMMAD ABDUL",
]
TUBE_KEYWORDS = ["TFL", "Metro", "STIB"]
VOI_KEYWORDS = ["voi"]

# Miscellaneous
MISC_KEYWORDS = [
	"AMEX EPAYMENT",
	"HSBC BANK PLC",
]


# --------------------------------------------------------------------
# Sub Categories
# --------------------------------------------------------------------

class CharitySubCategory (Enum):
    """Enum for charity sub categories."""
    NON_PROFIT = "non-profit"
    POLITICS = "politics"
    ARTS = "arts"

class FoodSubCategory (Enum):
	"""Enum for food sub categories."""
	GROCERY = "grocery"
	RESTAURANT = "restaurant"
	CAFE = "cafe"
	SNACKS = "snacks"
	SNACKS_TRAVEL = "travel snacks"
	
class FunSubCategory (Enum):
    """Enum for fun sub categories."""
    ENTERTAINMENT = "entertainment"
    CLOTHES = "clothes"
    WEDDING = "wedding"
    BRIDESMAID = "bridesmaid"
    SUBSCRIPTION = "subscription"
    FUN_OTHER = "other fun"

class HealthSubCategory (Enum):
    """Enum for health sub categories."""
    DOCTOR = "doctor"
    PHARMACY = "pharmacy"
    EYES = "eyes"
    PT = "physical therapy"
    MASSAGE = "massage"
    GYM = "gym"
    HEALTH_OTHER = "other health"
    HAIR = "hair"

class HomeSubCategory (Enum):
	"""Enum for home sub categories."""
	CLEANING = "cleaning"
	KITCHEN = "kitchen"
	REPAIR = "repair"
	OTHER = "other home"

class PresentSubCategory (Enum):
	"""Enum for present sub categories."""
	FRIEND = "friend"
	FAMILY = "family"
	
class RentSubCategory (Enum):
    """Enum for rent sub categories."""
    RENT = "rent"
    UTILITIES = "utilities"
    TAX = "tax"

class TravelSubCategory (Enum):
	"""Enum for travel sub categories."""
	# BOAT = "boat"
	CAR = "rental car"
	HOTEL = "hotel"
	PLANE = "plane"
	TAXI = "taxi"
	TRAIN = "train"
	PHONE = "phone plan"

class LocalTravelSubCategory (Enum):
	"""Enum for local travel sub categories."""
	BUS = "bus"
	CAR = "car"
	TRAIN_COMMUTE = "commuter train"
	TUBE = "tube"
	VOI = "voi"

class MiscSubCategory (Enum):
    """Enum for miscellaneous sub categories."""
    UNKNOWN = "unknown" 

# --------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------

class CategoryName (Enum):
	"""Enum for transaction categories."""
	CHARITY = "charity"
	FOOD = "food"
	FUN = "fun"
	HEALTH = "health"
	HOME = "home"
	MISC = "miscellaneous"
	PRESENT = "present"
	RENT = "rent"
	TRAVEL = "travel"
	TRAVEL_LOCAL = "local travel"


# --------------------------------------------------------------------
# Map Everything to Categories
# --------------------------------------------------------------------
# todo: improve by implementing pydantic and type can be any of the above enums
# or this could be a Class with three properties
def create_keywords_map_obj (
		category: CategoryName, sub_category: str, keywords: list[str]
) -> dict:
	"""Create a dictionary for category keywords."""
	return {
        "category": category,
        "sub_category": sub_category,
        "keywords": keywords,
	}

KEYWORD_CATEGORY_MAPS = [
    create_keywords_map_obj(CategoryName.CHARITY, CharitySubCategory.NON_PROFIT, NON_PROFIT_KEYWORDS),
    create_keywords_map_obj(CategoryName.CHARITY, CharitySubCategory.POLITICS, POLITICS_KEYWORDS),
    create_keywords_map_obj(CategoryName.CHARITY, CharitySubCategory.ARTS, ARTS_KEYWORDS),
    create_keywords_map_obj(CategoryName.FOOD, FoodSubCategory.GROCERY, GROCERY_KEYWORDS),
    create_keywords_map_obj(CategoryName.FOOD, FoodSubCategory.RESTAURANT, RESTAURANT_KEYWORDS),
    create_keywords_map_obj(CategoryName.FOOD, FoodSubCategory.SNACKS, SNACKS_KEYWORDS),
    create_keywords_map_obj(CategoryName.FOOD, FoodSubCategory.CAFE, CAFE_KEYWORDS),
    create_keywords_map_obj(CategoryName.FOOD, FoodSubCategory.SNACKS_TRAVEL, SNACKS_TRAVEL_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.ENTERTAINMENT, ENTERTAINMENT_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.CLOTHES, CLOTHES_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.WEDDING, WEDDING_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.BRIDESMAID, BRIDESMAID_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.SUBSCRIPTION, SUBSCRIPTION_KEYWORDS),
    create_keywords_map_obj(CategoryName.FUN, FunSubCategory.FUN_OTHER, FUN_OTHER_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.DOCTOR, DOCTOR_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.PHARMACY, PHARMACY_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.EYES, EYES),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.PT, PT_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.MASSAGE, MASSAGE_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.GYM, GYM_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.HEALTH_OTHER, HEALTH_OTHER_KEYWORDS),
    create_keywords_map_obj(CategoryName.HEALTH, HealthSubCategory.HAIR, HAIR),
    create_keywords_map_obj(CategoryName.HOME, HomeSubCategory.REPAIR, REPAIR),
    create_keywords_map_obj(CategoryName.HOME, HomeSubCategory.CLEANING, CLEANING_KEYWORDS),
    create_keywords_map_obj(CategoryName.HOME, HomeSubCategory.KITCHEN, KITCHEN_KEYWORDS),
    create_keywords_map_obj(CategoryName.HOME, HomeSubCategory.OTHER, OTHER_HOME_KEYWORDS),
    create_keywords_map_obj(CategoryName.PRESENT, PresentSubCategory.FRIEND, FRIEND_KEYWORDS),
    create_keywords_map_obj(CategoryName.PRESENT, PresentSubCategory.FAMILY, FAMILY_KEYWORDS),
    create_keywords_map_obj(CategoryName.RENT, RentSubCategory.RENT, RENTAL_KEYWORDS),
    create_keywords_map_obj(CategoryName.RENT, RentSubCategory.UTILITIES, UTILITIES_KEYWORDS),
    create_keywords_map_obj(CategoryName.RENT, RentSubCategory.TAX, TAX_KEYWORDS),
    # create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.BOAT, BOAT_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.CAR, CAR_RENTAL_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.HOTEL, HOTEL_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.PLANE, PLANE_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.TAXI, TAXI_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.TRAIN, TRAIN_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL, TravelSubCategory.PHONE, PHONE_PLAN),
    create_keywords_map_obj(CategoryName.TRAVEL_LOCAL, LocalTravelSubCategory.BUS, BUS_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL_LOCAL, LocalTravelSubCategory.CAR, CAR_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL_LOCAL, LocalTravelSubCategory.TRAIN_COMMUTE, TRAIN_COMMUTE_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL_LOCAL, LocalTravelSubCategory.TUBE, TUBE_KEYWORDS),
    create_keywords_map_obj(CategoryName.TRAVEL_LOCAL, LocalTravelSubCategory.VOI, VOI_KEYWORDS),
    create_keywords_map_obj(CategoryName.MISC, MiscSubCategory.UNKNOWN, MISC_KEYWORDS),
]
