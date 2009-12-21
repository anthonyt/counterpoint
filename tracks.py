# Active tracks defined in the following dict
melodies = {
    'Soprano': [
        ('C-5', 1),
        ('B-4', 1),
        ('A-4', 1),
        ('B-4', 1),
        ('C-5', 1),
        ('D-5', 1),
        ('D-5', 1),
        ('E-5', 1),
        ('B-4', 1),
        ('C-5', 1)
    ],

    'Alto': [
        ('E-4', 1),
        ('G-4', 1),
        ('F-4', 1),
        ('G-4', 1),
        ('E-4', 1),
        ('B-4', 1),
        ('A-4', 1),
        ('A-4', 1),
        ('G-4', 1),
        ('E-4', 1)
    ],

    'Tenor': [
    ],

    'Bass': [
        ('C-3', 1),
        ('D-3', 1),
        ('F-3', 1),
        ('E-3', 1),
        ('A-3', 1),
        ('G-3', 1),
        ('F-3', 1),
        ('E-3', 1),
        ('D-3', 1),
        ('C-3', 1)
    ]
}

cantus_firmus = 'Bass' # one of 'Soprano', 'Alto', 'Tenor', 'Bass'
key = 'C' # currently only major keys supported
meter = (4, 4) # currently only 4/4 supported
species = 1 # 1, 2, or 4
author = 'Anthony Theocharis'



# alternate canti firmi and harmonies for later testing.
first_species_cf_2_alto = [
    ('C-4', 1),
    ('D-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('F-4', 1),
    ('G-4', 1),
    ('A-4', 1),
    ('G-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

first_species_cf_3_alto = [
    ('C-4', 1),
    ('G-3', 1),
    ('A-3', 1),
    ('B-3', 1),
    ('C-4', 1),
    ('D-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

first_species_cf_4_alto = [
    ('D-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('A-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('D-4', 1)
]

second_species_cf_1_alto = [
    ('C-4', 1),
    ('E-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('C-4', 1),
    ('A-4', 1),
    ('F-4', 1),
    ('G-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

second_species_harm_1_sop = [
    (None,  2), ('C-5', 2),
    ('G-4', 2), ('A-4', 2),
    ('B-4', 2), ('G-4', 2),
    ('A-4', 2), ('B-4', 2),
    ('C-5', 2), ('B-4', 2),
    ('C-5', 2), ('E-5', 2),
    ('F-5', 2), ('E-5', 2),
    ('D-5', 2), ('C-5', 2),
    ('B-4', 2), ('D-5', 2),
    ('C-5', 2), ('G-4', 2),
    ('A-4', 2), ('B-4', 2),
    ('C-5', 1)
]

# melodies = { 'Soprano': second_species_harm_1_sop, 'Alto': second_species_cf_1_alto, 'Tenor': [], 'Bass': [] }
# species = 2

