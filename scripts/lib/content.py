# Order within each category puts the most surprising fact last (#5 = "saved the best for last").
# *word word* marks the highlighted keyword. Illustration is an emoji or a special drawn key.
CATS = [
    dict(slug="animals", name="ANIMALS", hook="5 ANIMAL FACTS", icon="🐾",
         g1=(18, 105, 48), g2=(150, 210, 60), accent=(255, 220, 40), float=["🐾", "🐾", "🍃"], key=0,
         facts=[
            ("🐙", "An octopus has *three hearts*", "And its blood is blue, thanks to copper.", "🤯😲👀", "o"),
            ("🦦", "Sea otters *hold hands* while sleeping", "So they don't drift apart in the water.", "🥹💕🦦", "grin"),
            ("🦩", "Flamingos are born *grey*", "They turn pink from pigments in their food.", "😲🎨👀", "o"),
            ("🐨", "Koala fingerprints look *almost human*", "So similar, they could confuse crime scene investigators.", "🕵️🤯👀", "jaw"),
            ("💩", "Wombats poop *cubes*", "Their intestines shape it into little blocks.", "🤯😂🧊", "jaw"),
         ]),
    dict(slug="space", name="SPACE", hook="5 SPACE FACTS", icon="🚀",
         g1=(8, 10, 48), g2=(92, 40, 145), accent=(60, 230, 255), float=["🪐", "⭐", "🌙"], key=1,
         facts=[
            ("☀️", "Sunlight takes *8 minutes* to reach us", "You always see the Sun as it was 8 minutes ago.", "😲⏱️👀", "o"),
            ("🌍", "*1.3 million* Earths could fit inside the Sun", "The Sun holds 99.8% of the solar system's mass.", "🤯🌞😲", "jaw"),
            ("👣", "Moon footprints can last *millions of years*", "There's no wind or rain to wipe them away.", "😲🌕👀", "o"),
            ("PLANET", "A day on Venus is *longer than its year*", "One spin takes 243 Earth days. One orbit takes 225.", "🤯🪐😵", "jaw"),
            ("🌟", "A teaspoon of neutron star weighs *a billion tons*", "Its matter is packed tighter than anything on Earth.", "🤯💥😱", "jaw"),
         ]),
    dict(slug="history", name="HISTORY", hook="5 HISTORY FACTS", icon="📜",
         g1=(105, 66, 32), g2=(214, 168, 78), accent=(170, 20, 35), float=["📜", "📜", "🏛️"], key=2,
         facts=[
            ("🎖️", "Napoleon *wasn't short*", "He was about 5'7\" (170 cm), average for his time.", "😲📏👀", "o"),
            ("⏱️", "The shortest war lasted *under 45 minutes*", "Britain vs. Zanzibar, 1896.", "😂⚔️🤯", "grin"),
            ("🎓", "Oxford is *older* than the Aztec Empire", "Teaching began by 1096. Tenochtitlan was founded in 1325.", "🤯🏛️😲", "jaw"),
            ("🏺", "Cleopatra lived closer to the *Moon landing*", "...than to the building of the Great Pyramid.", "🤯🚀😲", "jaw"),
            ("🦣", "Mammoths were alive when the *pyramids* were built", "A small group survived on an Arctic island until about 4,000 years ago.", "🤯🦣😱", "jaw"),
         ]),
    dict(slug="human_body", name="HUMAN BODY", hook="5 HUMAN BODY FACTS", icon="🧠",
         g1=(236, 96, 84), g2=(246, 122, 172), accent=(255, 255, 255), float=["CELL", "CELL", "CELL"], key=3,
         facts=[
            ("📏", "You're *1 cm taller* in the morning", "Your spine's discs stretch back out while you sleep.", "😲📏👀", "o"),
            ("🪶", "You *can't tickle* yourself", "Your brain predicts the touch, so it's no surprise.", "😂🪶🤔", "grin"),
            ("🫀", "Your heart beats *100,000 times* a day", "That's over 35 million beats a year.", "😲💓👀", "o"),
            ("🧪", "Your stomach gets a *new lining* every few days", "So its own acid doesn't digest it.", "🤯🧪😲", "jaw"),
            ("🦴", "Babies have about *300 bones*", "Many fuse together. Adults have just 206.", "🤯👶😱", "jaw"),
         ]),
    dict(slug="food", name="FOOD", hook="5 FOOD FACTS", icon="🍔",
         g1=(236, 104, 18), g2=(255, 172, 62), accent=(90, 240, 180), float=["🍎", "🍋", "🍓"], key=4,
         facts=[
            ("🥜", "Peanuts *aren't nuts*", "They're legumes, like peas and beans.", "😲🥜👀", "o"),
            ("🍎", "Apples *float* in water", "They're about 25% air.", "😲💧🍎", "o"),
            ("🥕", "Carrots used to be *purple*", "Orange carrots became popular in the 1600s.", "🤯🥕💜", "jaw"),
            ("🍯", "Honey *never spoils*", "Edible honey has been found in ancient Egyptian tombs.", "😲🍯👀", "jaw"),
            ("🍌", "Bananas are *berries*. Strawberries aren't!", "It's all about how the fruit grows from the flower.", "🤯🍌🍓", "jaw"),
         ]),
]
