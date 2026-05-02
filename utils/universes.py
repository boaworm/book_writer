from models.book_config import Universe

KNOWN_UNIVERSES: dict[str, tuple[str, str]] = {
    # key: (canonical display name, world context for the prompt)
    "middle earth": (
        "Middle Earth",
        "Tolkien's legendarium. A world of immense age and deep history — Elvish lore, "
        "ancient kingdoms, and the long struggle between light and shadow. Key elements: "
        "the Valar and Maiar, the races of Elves, Dwarves, Men, Hobbits, and Orcs; "
        "realms such as Gondor, Rohan, the Shire, and Rivendell; the corrupting power "
        "of the One Ring; the Istari wizards. Magic is rare, subtle, and ancient. "
        "Tone: mythic, elegiac, hopeful against great darkness.",
    ),
    "star wars": (
        "Star Wars",
        "A galaxy-spanning space opera. Key elements: the Force (light side and dark side), "
        "the Jedi Order and the Sith, starships and hyperspace travel, droids, alien species, "
        "and the political tension between the Republic/Rebellion and the Empire/First Order. "
        "Technology is lived-in and worn. The Force is mystical but grounded. "
        "Tone: heroic adventure with mythic underpinnings.",
    ),
    "the belgariad": (
        "The Belgariad",
        "David Eddings' world of Mallorea and the West. A world shaped by the conflict "
        "between two prophecies and the gods who champion them. Key elements: Sorcerers "
        "called Disciples, the Orb of Aldur, politically distinct kingdoms each with a "
        "strong cultural identity (Cherek, Algaria, Tolnedra, Nyissa, etc.), the dark god "
        "Torak, and the quest to fulfil the Prophecy of Light. Tone: epic quest with warmth, "
        "humour, and deep character bonds.",
    ),
    "westeros": (
        "Westeros",
        "George R.R. Martin's world of the Seven Kingdoms. Key elements: noble houses "
        "competing for the Iron Throne, the Wall and the threat beyond it, dragons, the "
        "Red Priests and their fire magic, faceless assassins, and a history soaked in "
        "betrayal. Winter is always coming. No character is safe. Magic is returning after "
        "a long absence. Tone: morally complex, politically brutal, grounded and visceral.",
    ),
    "discworld": (
        "Discworld",
        "Terry Pratchett's flat world carried on four elephants standing on a giant turtle. "
        "Key elements: Ankh-Morpork (a vast, corrupt, vibrant city), the Wizards of Unseen "
        "University, the Witches, Death (who speaks IN CAPITALS), the City Watch, and magic "
        "that works but is regarded with suspicion. The world satirises fantasy tropes and "
        "human nature simultaneously. Tone: comic, satirical, deeply humanist.",
    ),
    "dune": (
        "Dune",
        "Frank Herbert's far-future universe. Key elements: the desert planet Arrakis, the "
        "only source of the Spice Mélange (which enables space travel and prescience); the "
        "Great Houses and the Imperium; the Bene Gesserit sisterhood; the Fremen desert "
        "people and their ecological religion; Mentats and Navigators; the Butlerian Jihad's "
        "prohibition on thinking machines. Tone: political, philosophical, ecological.",
    ),
    "wizarding world": (
        "The Wizarding World",
        "J.K. Rowling's world of hidden magic alongside the Muggle world. Key elements: "
        "Hogwarts School of Witchcraft and Wizardry, wand-based magic with incantations, "
        "the Ministry of Magic, Diagon Alley, Hogsmeade, magical creatures, the divide "
        "between pure-blood ideology and Muggle-born witches and wizards. "
        "Tone: school adventure with darkness growing underneath.",
    ),
    "forgotten realms": (
        "Forgotten Realms",
        "The primary D&D campaign setting. Key elements: the continent of Faerûn with its "
        "iconic cities (Waterdeep, Baldur's Gate, Neverwinter, Calimshan); the Weave of "
        "magic; gods who walk among mortals; the Underdark beneath the surface world; "
        "classic D&D races (elves, dwarves, halflings, tieflings, drow). "
        "Tone: high fantasy with adventure, dungeon-delving, and moral stakes.",
    ),
    "medieval england": (
        "Medieval England",
        "Historical setting: England approximately 1000–1485 CE. Key elements: feudal "
        "hierarchy (king, lords, knights, serfs), the Catholic Church's pervasive influence, "
        "castles and walled towns, the Crusades as backdrop, the Black Death, the Hundred "
        "Years' War, chivalric codes, and a largely agrarian economy. No magic unless "
        "the story introduces it. Tone: grounded, historically textured.",
    ),
    "victorian london": (
        "Victorian London",
        "London approximately 1837–1901. Key elements: the industrial revolution and its "
        "class divisions, fog and gaslight, the British Empire at its height, Scotland Yard, "
        "penny dreadfuls and serialised fiction, the emergence of science and scepticism "
        "challenging religion, social reform movements, and the stark divide between "
        "wealth and poverty. Tone: atmospheric, socially conscious.",
    ),
    "ancient rome": (
        "Ancient Rome",
        "The Roman world from Republic to Empire (roughly 500 BCE – 500 CE). Key elements: "
        "the Senate and political intrigue, Roman legions and military discipline, slavery, "
        "the gods of the Roman pantheon, gladiatorial combat, the provinces and borders, "
        "Latin as the language of power. Tone: epic, political, morally complex.",
    ),
    "feudal japan": (
        "Feudal Japan",
        "Japan approximately 1185–1868 CE (Kamakura to Edo periods). Key elements: "
        "the Samurai class and Bushido code, the Shogunate, rival daimyo, ninja, ronin, "
        "Zen Buddhism and Shintoism, the rigid social hierarchy, beautiful and austere "
        "aesthetics, and the tension between honour and survival. "
        "Tone: precise, honourable, quietly tragic.",
    ),
    "wild west": (
        "The American West",
        "The United States frontier, approximately 1865–1900. Key elements: cattle drives "
        "and ranches, frontier towns with saloons and sheriffs, outlaws and bounty hunters, "
        "the railroad expanding west, conflict with and displacement of Native peoples, "
        "gold rushes, Manifest Destiny ideology, and the mythology of the lone gunslinger. "
        "Tone: dusty, moral, mythic in its own way.",
    ),
    "world war ii": (
        "World War II",
        "Global conflict 1939–1945. Key elements: the European and Pacific theatres, "
        "the Nazi occupation of Europe, the Holocaust, resistance movements, the Allied "
        "powers (Britain, USA, USSR, France), the experience of soldiers and civilians "
        "alike, rationing and the home front, D-Day, the fall of Berlin, and the atomic "
        "bomb. Tone: high stakes, human cost at the forefront.",
    ),
    "golden age of piracy": (
        "The Golden Age of Piracy",
        "Caribbean and Atlantic seas, approximately 1650–1730. Key elements: merchant "
        "ships and naval vessels, pirate codes and democratic ship governance, port towns "
        "like Tortuga and Nassau, the Spanish Main and its treasure galleons, Letters of "
        "Marque, the Royal Navy in pursuit, tropical islands, and the romance and brutal "
        "reality of life at sea. Tone: swashbuckling, morally grey, high adventure.",
    ),
    "ancient greece": (
        "Ancient Greece",
        "Greece approximately 800–300 BCE. Key elements: the city-states (Athens, Sparta, "
        "Corinth), the Olympian gods who intervene in mortal affairs, heroes and their quests, "
        "the Persian Wars and Macedonian expansion, philosophy and theatre, slavery, democracy "
        "in its infancy, and the Mediterranean sea as a highway. Tone: heroic, philosophical, "
        "fatalistic.",
    ),
}

_ALIASES: dict[str, str] = {
    "lotr": "middle earth",
    "lord of the rings": "middle earth",
    "tolkien": "middle earth",
    "a song of ice and fire": "westeros",
    "game of thrones": "westeros",
    "harry potter": "wizarding world",
    "hogwarts": "wizarding world",
    "pirates of the caribbean": "golden age of piracy",
    "pirates": "golden age of piracy",
    "wwii": "world war ii",
    "world war 2": "world war ii",
    "ww2": "world war ii",
    "d&d": "forgotten realms",
    "dungeons and dragons": "forgotten realms",
    "faerûn": "forgotten realms",
    "faerun": "forgotten realms",
    "belgariad": "the belgariad",
    "eddings": "the belgariad",
    "japan": "feudal japan",
    "samurai": "feudal japan",
    "rome": "ancient rome",
    "roman": "ancient rome",
    "greece": "ancient greece",
    "greek": "ancient greece",
    "victorian": "victorian london",
    "western": "wild west",
    "cowboy": "wild west",
}


def _lookup(name: str) -> tuple[str, str] | None:
    key = name.lower().strip()
    if key in _ALIASES:
        key = _ALIASES[key]
    if key in KNOWN_UNIVERSES:
        return KNOWN_UNIVERSES[key]
    for k, v in KNOWN_UNIVERSES.items():
        if k in key or key in k:
            return v
    return None


def resolve_universe(universe: Universe) -> str:
    match = _lookup(universe.name)

    lines: list[str] = []
    if match:
        display, context = match
        lines.append(f"Universe: This story is set in {display}. {context}")
        if universe.description:
            lines.append(f"Additional context: {universe.description}")
        lines.append(
            "Maintain consistency with this universe's established lore, geography, "
            "tone, and rules. Do not contradict canon unless the story explicitly diverges."
        )
    else:
        lines.append(f"Universe: This story is set in {universe.name}.")
        if universe.description:
            lines.append(universe.description)
        else:
            lines.append(
                "Maintain a consistent world — geography, rules, culture, and tone should "
                "remain coherent across all chapters."
            )

    return " ".join(lines)
