#!/usr/bin/env python3
# Build food pages for the 9 missing Palawan venues + update category indexes.
import os, urllib.parse

BASE = "food/philippines"

def maps(query):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(query)

# each venue: dict
V = [
  dict(
    city="puerto-princesa", cat="bars-pubs", slug="palaweno-brewery",
    title="Palaweño Brewery",
    sub="Puerto Princesa · Craft Beer",
    body="Puerto's only craft beer microbrewery, and I really wanted to love it. Nice garden setting, friendly staff, and the beers, pricey as they are, are actually tasty. The problem is there isn't much choice, there's barely any food, and the place was practically empty when we came. Craft beer just doesn't seem to have found its market in Puerto yet, which is a shame, because with a bit more life this could be a great spot.",
    ratings=[("Beer","8/10"),("Service","7.5/10"),("Value for money","7/10"),("Atmosphere","6.5/10"),("Overall","7.5/10")],
    emoji="🍺", type="Craft Beer, Brewery", price="moderate to expensive",
    maps_q="Palaweño Brewery Puerto Princesa Palawan",
    summary="Puerto's only craft beer microbrewery, tasty if pricey beers and a nice garden, let down by little choice, barely any food and empty tables.",
  ),
  dict(
    city="puerto-princesa", cat="restaurants", slug="majo-imbiss",
    title="Majo-Imbiss",
    sub="Puerto Princesa · German",
    body="A basic German-run eatery with a bar and a nice garden. The one big reason to come is the litro bottles of Beer na Beer, dirt cheap and a great find at that price. Sadly the food really lets it down: amateurish homemade stuff that isn't even tasty, and the burgers arrived dry with cold cheese. Come for the cheap beers in the garden, and have your dinner elsewhere.",
    ratings=[("Food","5/10"),("Service","6.5/10"),("Value for money","7.5/10"),("Atmosphere","7/10"),("Overall","6/10")],
    emoji="🍽️", type="German, Bar", price="cheap",
    maps_q="Majo-Imbiss Puerto Princesa Palawan",
    summary="Cheap litro bottles of Beer na Beer in a nice garden are the draw; the food, sadly, is amateurish and best skipped.",
  ),
  dict(
    city="puerto-princesa", cat="restaurants", slug="bonas-chao-long-haus",
    title="Bona's Chao Long Haus",
    sub="Puerto Princesa · Vietnamese-Filipino",
    body="A basic place doing very tasty and cheap chaolong, the Viet-Filipino beef noodle soup that's a Palawan speciality. If you want a good, inexpensive bowl of noodle soup, this is a great option. Skip the banh mi though; it's nothing like a proper one.",
    ratings=[("Food","8/10"),("Service","7.5/10"),("Value for money","8.5/10"),("Atmosphere","6.5/10"),("Overall","8/10")],
    emoji="🍽️", type="Vietnamese-Filipino, Noodles", price="cheap",
    maps_q="Bona's Chao Long Haus Puerto Princesa Palawan",
    summary="A basic place doing very tasty, cheap chaolong; a great option for a proper bowl of noodle soup, though skip the banh mi.",
  ),
  dict(
    city="puerto-princesa", cat="restaurants", slug="kinabuchs",
    title="Kinabuchs (KGB)",
    sub="Rizal Avenue, Puerto Princesa · Filipino, Grill",
    body="KGB, as everyone calls it, is still exactly as I remembered it from 2009, a great open-air grill and one of Puerto's institutions. Good food, huge portions, and while it's obviously pricier now, it's still reasonable for what you get. The grilled tuna belly in particular was delicious. The perfect place to end a long day, or a long trip, over cold beer and something off the grill.",
    ratings=[("Food","8.5/10"),("Service","8/10"),("Value for money","7.5/10"),("Atmosphere","9/10"),("Overall","8.5/10")],
    emoji="🍽️", type="Filipino, Grill", price="moderate",
    maps_q="Kinabuchs Puerto Princesa Palawan",
    summary="Still the same Puerto institution it was in 2009, a great open-air grill with huge portions and delicious grilled tuna belly.",
  ),
  dict(
    city="el-nido", cat="bars-pubs", slug="odessa-mama",
    title="Odessa Mama",
    sub="El Nido Town · Craft Beer, Ukrainian",
    body="El Nido's only craft beer microbrewery, and a good one at that: the beers are lovely, the best in town in my opinion. It's also a Ukrainian restaurant and I do like Ukrainian food, but the prices were a bit too steep for me, so I stuck to the beer. There's a sign at the door saying Russians aren't welcome which, given the circumstances, is fair enough.",
    ratings=[("Beer","8.5/10"),("Service","7.5/10"),("Value for money","6.5/10"),("Atmosphere","7.5/10"),("Overall","8/10")],
    emoji="🍺", type="Craft Beer, Ukrainian", price="expensive",
    maps_q="Odessa Mama El Nido Palawan",
    summary="El Nido's only craft beer microbrewery, the best beers in town, plus Ukrainian food that is good if a little pricey.",
  ),
  dict(
    city="el-nido", cat="restaurants", slug="bhabahs-chaolong",
    title="Bhabah's Chaolong",
    sub="El Nido Town · Vietnamese-Filipino",
    body="Extremely basic, almost a dark hole inside, though thankfully there are a few tables outside, even if they're right by the busy, polluted road. Still, it's cheap and the Viet-Filipino noodle soup is very tasty. It also seemed to be the only chaolong place in town, so it's not like there's much choice.",
    ratings=[("Food","8/10"),("Service","7/10"),("Value for money","8/10"),("Atmosphere","5.5/10"),("Overall","7.5/10")],
    emoji="🍽️", type="Vietnamese-Filipino, Noodles", price="cheap",
    maps_q="Bhabah's Chaolong El Nido Palawan",
    summary="Extremely basic and right by the busy road, but cheap and with very tasty noodle soup, and seemingly the only chaolong in town.",
  ),
  dict(
    city="el-nido", cat="cafes", slug="blackbird-coffee",
    title="Blackbird Coffee",
    sub="El Nido Town · Café, Coffee",
    body="No million-dollar view like Hama, but when Hama is packed, which is basically always, this is a great alternative for quality coffee. Tiny but air-conditioned and friendly, and the breakfasts look great and come in massive portions.",
    ratings=[("Coffee","8/10"),("Service","8/10"),("Value for money","7.5/10"),("Atmosphere","7/10"),("Overall","8/10")],
    emoji="☕", type="Café, Coffee", price="moderate",
    maps_q="Blackbird Coffee El Nido Palawan",
    summary="No million-dollar view like Hama, but a tiny, friendly, air-conditioned spot for quality coffee and massive breakfasts.",
  ),
  dict(
    city="el-nido", cat="restaurants", slug="casa-rosa-seaview-inn",
    title="Casa Rosa Seaview Inn & Restaurant",
    sub="Taytay, Palawan · Filipino",
    body="A very quiet resort on a hill above Taytay, with beautiful views over the town and bay from the restaurant terrace. The service is slow and the food is so-so, but as a rest stop on the long ride between El Nido and Puerto Princesa it's a lovely place to pause. With more time, I'd happily have broken the trip here for a night.",
    ratings=[("Food","6/10"),("Service","5.5/10"),("Value for money","7/10"),("Atmosphere","8.5/10"),("Overall","7/10")],
    emoji="🍽️", type="Filipino", price="moderate",
    maps_q="Casa Rosa Seaview Inn Taytay Palawan",
    summary="A very quiet hilltop resort with beautiful views over Taytay bay, a lovely rest stop on the long ride even if the food is so-so.",
  ),
  dict(
    city="port-barton-san-vicente", cat="bars-pubs", slug="prince-john-resort",
    title="Prince John Resort",
    sub="Port Barton, San Vicente · Resort Bar",
    body="We only stopped for drinks, but the setting is absolutely gorgeous, easily one of the most beautiful spots around Port Barton. It's tricky to reach and was almost empty when we visited, and yes, it's on the expensive side, but for a location like this the prices are totally justified. Well worth the ride out for a drink with a view.",
    ratings=[("Service","7.5/10"),("Value for money","6.5/10"),("Atmosphere","9/10"),("Overall","8.5/10")],
    emoji="🍺", type="Resort Bar", price="expensive",
    maps_q="Prince John Resort Port Barton Palawan",
    summary="A gorgeous, hard-to-reach and rather pricey resort, almost empty when we visited, but the setting alone is worth the ride out for a drink.",
  ),
]

def page_md(v):
    # ratings table
    rows = "".join([f"| {c:<15} | {s:<6} |\n" for c,s in v["ratings"]])
    fm = (
        "---\n"
        "layout: default\n"
        "section: food\n"
        "review: true\n"
        f"title: {v['title']}\n"
        f"subtitle: {v['sub']}\n"
        "---\n\n"
    )
    body = v["body"] + "\n\n"
    ratings = (
        "## Ratings\n\n"
        "| Category        | Score  |\n"
        "| ---             | ---    |\n"
        + rows + "\n"
    )
    practical = (
        "### Practical\n\n"
        f"🗺️ **Google Maps:** [Open in Google Maps]({maps(v['maps_q'])})\n"
        f"{v['emoji']} **Type:** {v['type']}\n"
        f"💰 **Price level:** {v['price']}\n"
    )
    return fm + body + ratings + practical

created=[]
for v in V:
    d = os.path.join(BASE, v["city"], v["cat"], v["slug"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "index.md")
    with open(p,"w",encoding="utf-8") as f:
        f.write(page_md(v))
    created.append(p)

# update category indexes
from collections import defaultdict
bycat = defaultdict(list)
for v in V:
    bycat[(v["city"], v["cat"])].append(v)

def entry_block(v):
    link = f"/{BASE}/{v['city']}/{v['cat']}/{v['slug']}/"
    return (
        f"## {v['title']}\n"
        f"*{v['sub']}*\n"
        f"{v['summary']}\n"
        f"→ [Read the full review]({link})\n\n"
        "---\n\n"
    )

updated=[]
for (city,cat), vs in bycat.items():
    idx = os.path.join(BASE, city, cat, "index.md")
    content = open(idx,encoding="utf-8").read()
    blocks = "".join(entry_block(v) for v in vs)
    if "**Price level note:**" in content:
        i = content.index("**Price level note:**")
        new = content[:i] + blocks + content[i:]
    else:
        new = content.rstrip() + "\n\n" + blocks
        new = new.rstrip() + "\n"
    open(idx,"w",encoding="utf-8").write(new)
    updated.append(idx)

print("CREATED PAGES:")
for c in created: print("  ",c)
print("UPDATED INDEXES:")
for u in updated: print("  ",u)
