# backend/app/rules/default_rules.py

from sqlalchemy.orm import Session
from app.models.rule import Rule


DEFAULT_RULES = [
    # ── FOOD & DINING RULES ──────────────────────────────────────────
    {
        "name": "Food delivery apps",
        "rule_type": "keyword",
        "condition": "swiggy,zomato,uber eats,dominos,pizza hut,mcdonalds,kfc,subway,burger king",
        "category_name": "Food & Dining",
        "priority": 10,
        "apply_on": "title"
    },
    {
        "name": "Restaurant keywords",
        "rule_type": "keyword",
        "condition": "restaurant,cafe,coffee,lunch,dinner,breakfast,biryani,dosa,idli",
        "category_name": "Food & Dining",
        "priority": 8,
        "apply_on": "title"
    },
    {
        "name": "Grocery stores",
        "rule_type": "keyword",
        "condition": "bigbasket,grofers,blinkit,dunzo,grocery,supermarket,zepto",
        "category_name": "Food & Dining",
        "priority": 9,
        "apply_on": "title"
    },

    # ── TRANSPORT RULES ─────────────────────────────────────────────
    {
        "name": "Ride sharing apps",
        "rule_type": "keyword",
        "condition": "uber,ola,rapido,namma yatri,indrive",
        "category_name": "Transport",
        "priority": 10,
        "apply_on": "title"
    },
    {
        "name": "Transport keywords",
        "rule_type": "keyword",
        "condition": "fuel,petrol,diesel,metro,bus,auto,rickshaw,taxi,parking,toll",
        "category_name": "Transport",
        "priority": 8,
        "apply_on": "title"
    },

    # ── SHOPPING RULES ───────────────────────────────────────────────
    {
        "name": "E-commerce platforms",
        "rule_type": "keyword",
        "condition": "amazon,flipkart,myntra,meesho,ajio,nykaa,snapdeal",
        "category_name": "Shopping",
        "priority": 10,
        "apply_on": "title"
    },
    {
        "name": "Shopping keywords",
        "rule_type": "keyword",
        "condition": "shopping,purchase,buy,order,clothes,shoes,electronics",
        "category_name": "Shopping",
        "priority": 7,
        "apply_on": "title"
    },

    # ── ENTERTAINMENT RULES ─────────────────────────────────────────
    {
        "name": "Streaming services",
        "rule_type": "keyword",
        "condition": "netflix,hotstar,amazon prime,spotify,youtube premium,apple music,jiosaavn,gaana",
        "category_name": "Entertainment",
        "priority": 10,
        "apply_on": "title"
    },
    {
        "name": "Entertainment keywords",
        "rule_type": "keyword",
        "condition": "movie,cinema,pvr,inox,multiplex,theatre,concert,game,bowling",
        "category_name": "Entertainment",
        "priority": 8,
        "apply_on": "title"
    },

    # ── HEALTH RULES ────────────────────────────────────────────────
    {
        "name": "Health & Medical",
        "rule_type": "keyword",
        "condition": "pharmacy,medical,doctor,hospital,clinic,medicine,apollo,1mg,netmeds,gym,fitness",
        "category_name": "Health",
        "priority": 9,
        "apply_on": "title"
    },

    # ── UTILITIES RULES ─────────────────────────────────────────────
    {
        "name": "Utility bills",
        "rule_type": "keyword",
        "condition": "electricity,water bill,internet,broadband,airtel,jio,vi,bsnl,recharge,mobile bill",
        "category_name": "Utilities",
        "priority": 9,
        "apply_on": "title"
    },

    # ── EDUCATION RULES ─────────────────────────────────────────────
    {
        "name": "Education & Learning",
        "rule_type": "keyword",
        "condition": "udemy,coursera,byju,unacademy,book,course,tutorial,school,college,fees",
        "category_name": "Education",
        "priority": 9,
        "apply_on": "title"
    },

    # ── TRAVEL RULES ────────────────────────────────────────────────
    {
        "name": "Travel booking",
        "rule_type": "keyword",
        "condition": "irctc,makemytrip,goibibo,yatra,ixigo,flight,hotel,booking,airbnb,oyo",
        "category_name": "Travel",
        "priority": 10,
        "apply_on": "title"
    },

    # ── AMOUNT RANGE RULES ───────────────────────────────────────────
    {
        "name": "Small purchase (under 100)",
        "rule_type": "amount_range",
        "condition": "0-99",
        "category_name": "Miscellaneous",
        "priority": 1,   # Low priority — only applies if no keyword rule matched
        "apply_on": "title"
    },
]


def seed_default_rules(db: Session) -> bool:
    """Add default rules if none exist."""
    existing = db.query(Rule).count()
    if existing == 0:
        for rule_data in DEFAULT_RULES:
            rule = Rule(**rule_data)
            db.add(rule)
        db.commit()
        print(f"✅ Seeded {len(DEFAULT_RULES)} default rules")
        return True
    return False