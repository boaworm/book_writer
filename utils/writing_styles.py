KNOWN_STYLES: dict[str, str] = {
    "jrr tolkien": (
        "epic and mythic; rich invented lore, languages, and history; formal prose "
        "with archaic cadence; deeply descriptive world-building that makes the world "
        "feel ancient and real; heroic themes of eucatastrophe and hope"
    ),
    "ernest hemingway": (
        "iceberg theory — what is left unsaid carries as much weight as what is written; "
        "short declarative sentences; subtext-heavy dialogue; stoic restraint; "
        "the wound is always present but never named"
    ),
    "george rr martin": (
        "morally complex characters with no plot armour; close-third POV that shifts "
        "between characters; detailed political intrigue and power dynamics; visceral "
        "and grounded — magic is rare and costly; consequences are real"
    ),
    "cormac mccarthy": (
        "sparse or absent punctuation; long, flowing sentences with biblical cadence; "
        "brutal and lyrical simultaneously; landscape treated as a moral force; "
        "violence rendered plainly without judgment"
    ),
    "terry pratchett": (
        "satirical wit and comic timing; genuine humanist warmth beneath every joke; "
        "characters who surprise you with depth; the absurd used to expose the true; "
        "never cruel — always on the side of people"
    ),
    "ursula k le guin": (
        "anthropological depth and philosophical weight; precise, elegant prose with "
        "no wasted words; explores power, gender, and belonging without preaching; "
        "the alien made deeply familiar"
    ),
    "stephen king": (
        "strong colloquial voice with deep interiority; slow-burn dread built from "
        "mundane detail; characters defined by their ordinary humanity before the "
        "extraordinary arrives; American vernacular, self-aware"
    ),
    "jane austen": (
        "sharp irony and free indirect discourse; social observation with wit; "
        "elegant period dialogue where every exchange is a negotiation; romantic "
        "stakes grounded entirely in social consequence"
    ),
    "philip k dick": (
        "paranoid and philosophical; questions of identity, memory, and reality woven "
        "into pulpy pacing; ordinary men trapped in systems they cannot understand; "
        "the uncanny treated as bureaucratic fact"
    ),
    "neil gaiman": (
        "mythic storytelling with modern accessibility; dark fairy-tale atmosphere "
        "where the fantastic is treated as matter-of-fact; warm, intimate narrative "
        "voice; ancient stories wearing contemporary clothes"
    ),
    "fyodor dostoevsky": (
        "intense psychological depth; characters who philosophise through suffering "
        "and action; cramped, urgent urban settings; ideas dramatised through "
        "extreme emotional states; redemption earned through pain"
    ),
    "gabriel garcia marquez": (
        "magical realism where the impossible is rendered ordinary; multi-generational "
        "sweep with a fatalistic undertone; dense sensory prose; love and death treated "
        "with equal gravity and beauty"
    ),
    "franz kafka": (
        "bureaucratic surrealism; alienation rendered with deadpan precision; the "
        "protagonist accepts the absurd without question; institutional logic taken "
        "to nightmarish extremes; no resolution, only process"
    ),
    "virginia woolf": (
        "stream of consciousness; interior life privileged over external event; "
        "lyrical, impressionistic prose; time experienced subjectively; "
        "consciousness as the true setting of the story"
    ),
}


def resolve_writing_style(name: str) -> str:
    """Return a prompt fragment for the given author name."""
    key = name.lower().strip()

    if key in KNOWN_STYLES:
        return f"Writing style: Emulate the prose of {name} — {KNOWN_STYLES[key]}."

    for known_key, desc in KNOWN_STYLES.items():
        if key in known_key or known_key.split()[-1] in key:
            return f"Writing style: Emulate the prose of {name} — {desc}."

    return (
        f"Writing style: Emulate the prose style of {name}. "
        "Capture their characteristic voice, sentence rhythm, narrative perspective, "
        "and the emotional register they are known for."
    )
