# Nowe przedmioty katalogu globalnego

Chcę zrobić te tematy:  
1. Wygenerować przykładowe zestawy (np. wersja budżetowa i medium),
2. Uzupełnić globalny katalog o brakujące przedmioty (które będą w example sets),
3. Powiązać istniejące example sets z catalogue.

Chcę tylko realne przedmioty, polecane. Powinny mieć w miarę możliwości markę, nazwę, model, url strony producenta, kolor, orientacyjną cenę w USD lub PLN, wagę.

## New catalogue items
```jsonc
[
  {
    "id": "NEW0001",
    "name": "Mil-Tec Emergency Thermal Blanket (foil)",
    "category": "shelter",
    "brand": "Mil-Tec",
    "model": "Thermal Blanket",
    "description": "Lekka folia ratunkowa / koc termoizolacyjny – przydatna do ochrony przed wychłodzeniem lub jako awaryjne schronienie.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 50.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0002",
    "name": "CNOC Vecto Collapsible Water Bottle 1L",
    "category": "water",
    "brand": "CNOC",
    "model": "Vecto 1L",
    "description": "Składana, lekka butelka na wodę – dobra do noszenia przefiltrowanej wody lub transportu wody pitnej.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 40.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0003",
    "name": "Aquamira Water Purification Tablets (30 tabs)",
    "category": "water",
    "brand": "Aquamira",
    "model": "Water Treatment Tablets",
    "description": "Tabletki do chemicznego uzdatniania wody – backup lub alternatywa do filtra.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 30.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0004",
    "name": "GSI Outdoors Stainless Steel Cup 700 ml",
    "category": "other",
    "brand": "GSI Outdoors",
    "model": "Stainless Steel Cup 700 ml",
    "description": "Metalowy kubek / menażka – do gotowania wody lub posiłków w terenie.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 150.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0005",
    "name": "UCO Stormproof Matches – 25 szt.",
    "category": "fire",
    "brand": "UCO",
    "model": "Stormproof Matches",
    "description": "Wodoodporne, wiatroszczelne zapałki – dobre zabezpieczenie awaryjne dla ognia.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 25.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0006",
    "name": "Compact Duct Tape (10 m roll)",
    "category": "tools",
    "brand": "Generic",
    "model": "10m Duct Tape",
    "description": "Uniwersalna taśma naprawcza – przydatna do napraw, improwizacji, uszczelniania, zabezpieczeń.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 100.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0007",
    "name": "Metal Spork (Titanium / Stainless)",
    "category": "tools",
    "brand": "Generic",
    "model": "Folding Spork",
    "description": "Składana łyżko-widelec – lekki element do jedzenia / gotowania w terenie.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 25.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0008",
    "name": "Emergency Poncho (nylon / waterproof)",
    "category": "shelter",
    "brand": "Generic",
    "model": "Emergency Poncho",
    "description": "Lekki wodoodporny poncho – zabezpieczenie przed deszczem / wilgocią, może służyć jako prowizoryczne schronienie.",
    "price_tier": "low",
    "quality": "medium",
    "weight": 120.0,
    "weight_unit": "g"
  },
  {
    "id": "NEW0009",
    "name": "Olight i3T EOS 2",
    "category": "light",
    "brand": "Olight",
    "model": "i3T 2 EOS",
    "color": "Black",
    "price": 25,
    "price_currency": "USD",
    "weight": 40,
    "weight_unit": "g",
    "url": "https://www.olightstore.com/i3t-eos",
    "description": "Mała, niezawodna latarka EDC na jedną baterię AAA (180 lm, momentary tail switch)."
  },
  {
    "id": "NEW0010",
    "name": "Light My Fire Swedish FireSteel 2.0",
    "category": "fire",
    "brand": "Light My Fire",
    "model": "Swedish FireSteel 2.0",
    "price": 15,
    "price_currency": "USD",
    "weight": 50,
    "weight_unit": "g",
    "url": "https://lightmyfire.com/products/swedish-firesteel",
    "description": "Klasyczne ferro rod — iskry 3000°C, bardzo niezawodne w warunkach terenowych."
  },
  {
    "id": "NEW0011",
    "name": "Victorinox Huntsman",
    "category": "tools",
    "brand": "Victorinox",
    "model": "Huntsman",
    "color": "Red",
    "price": 45,
    "price_currency": "USD",
    "weight": 97,
    "weight_unit": "g",
    "url": "https://www.victorinox.com/global/en/products/Swiss-Army-Knives/Medium-Pocket-Knives/Huntsman/p/1.3713",
    "description": "Klasyczny scyzoryk z piłką, nożyczkami i ostrzem — świetny do EDC i outdoor."
  },
  {
    "id": "NEW0012",
    "name": "Ferrocerium Rod 8 mm",
    "category": "fire",
    "brand": "Generic",
    "model": "Ferro Rod 8mm",
    "price": 8,
    "price_currency": "USD",
    "weight": 35,
    "weight_unit": "g",
    "url": "https://www.amazon.com",
    "description": "Standardowy ferro rod 8 mm — lekka alternatywa do większych prętów."
  },
  {
    "id": "NEW0013",
    "name": "Rite in the Rain All-Weather Notepad 3x5",
    "category": "other",
    "brand": "Rite in the Rain",
    "model": "3x5 Top-Spiral",
    "color": "Yellow",
    "price": 6,
    "price_currency": "USD",
    "weight": 70,
    "weight_unit": "g",
    "url": "https://riteintherain.com/products/top-spiral-notepad-3x5",
    "description": "Notes wodoodporny — działa w deszczu, śniegu, błocie; klasyk w survivalu."
  },
  {
    "id": "NEW0014",
    "name": "Sharpie Permanent Marker (Fine Tip)",
    "category": "other",
    "brand": "Sharpie",
    "model": "Fine Black",
    "color": "Black",
    "price": 2,
    "price_currency": "USD",
    "weight": 9,
    "weight_unit": "g",
    "url": "https://www.sharpie.com",
    "description": "Marker permanentny — podpisywanie, notatki awaryjne, oznaczanie sprzętu."
  },
  {
    "id": "NEW0015",
    "name": "Fenix E01 V2.0",
    "category": "light",
    "brand": "Fenix",
    "model": "E01 V2.0",
    "price": 20,
    "price_currency": "USD",
    "color": "Black",
    "weight": 13,
    "weight_unit": "g",
    "url": "https://www.fenixlighting.com/product/e01-v2-flashlight/",
    "description": "Ultra-lekka latarka AAA, idealna jako backup."
  }
]
```

## Example sets

### Budget EDC Survival Kit

```jsonc
{
  "id": "SET_EDC_BUDGET_01",
  "name": "Budget EDC Survival Kit",
  "items": [
    { "item_id": "NEW0009", "qty": 1 },   // Olight i3T EOS 2
    { "item_id": "NEW0010", "qty": 1 },   // Light My Fire FireSteel 2.0
    { "item_id": "NEW0013", "qty": 1 },   // Rite in the Rain Notepad 3x5
    { "item_id": "NEW0014", "qty": 1 },   // Sharpie Fine Tip
    { "item_id": "NEW0006", "qty": 1 },   // Compact Duct Tape (10m)
    { "item_id": "NEW0007", "qty": 1 },   // Metal Spork
    { "item_id": "NEW0002", "qty": 1 },   // CNOC Vecto 1L
    { "item_id": "NEW0005", "qty": 1 },   // UCO Stormproof Matches
    { "item_id": "NEW0015", "qty": 1 }    // Fenix E01 V2.0 (backup light)
  ]
}
```

### Medium EDC / Urban Survival Kit

```jsonc
{
  "id": "SET_EDC_MEDIUM_01",
  "name": "Medium EDC / Urban Survival Kit",
  "items": [
    { "item_id": "NEW0009", "qty": 1 },   // Olight i3T EOS 2
    { "item_id": "NEW0011", "qty": 1 },   // Victorinox Huntsman
    { "item_id": "NEW0010", "qty": 1 },   // Swedish FireSteel 2.0
    { "item_id": "NEW0013", "qty": 1 },   // Rite in the Rain Notepad
    { "item_id": "NEW0014", "qty": 1 },   // Sharpie
    { "item_id": "NEW0006", "qty": 1 },   // Compact Duct Tape
    { "item_id": "NEW0002", "qty": 1 },   // CNOC Vecto Bottle
    { "item_id": "NEW0001", "qty": 1 },   // Mil-Tec Emergency Blanket
    { "item_id": "NEW0012", "qty": 1 },   // Ferro Rod 8mm
    { "item_id": "NEW0004", "qty": 1 },   // GSI Stainless Cup 700 ml
    { "item_id": "FA001", "qty": 1 }      // Basic Mini First Aid Kit (zakładam że masz w katalogu)
  ]
}
```
