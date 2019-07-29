# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:57:34 2018

@author: mjdg
"""

import math

class LootEntry:
    def __init__(self, name, meta, weight, minCount=1, maxCount=1):
        self.name = name
        self.meta = meta
        self.weight = weight
        self.minCount = minCount
        self.maxCount = maxCount
        
    def __str__(self):
        text = """ {"data": {"name" : """ + "\"" + self.name + "\""
        if self.meta:
            text = text + """, "meta" : """ + str(self.meta)
        if self.minCount != 1 or self.maxCount != 1:
            text = text + """, "min" : """ + str(self.minCount) + """, "max" : """ + str(self.maxCount)
        text = text + """}, "weight" : """ + str(self.weight) + """ } """
        return text

class LootList:
    def __init__(self):
        self.entries = []
        
    def add(self, entry):
        self.entries.append(entry)
        
    def merge(self, sub):
        self.entries.extend(sub.entries)
        
    def normaliseWeight(self, weight, doCeil=False):
        if len(self.entries) == 0: return
        currentTotal = sum([e.weight for e in self.entries])
        rescale = weight / currentTotal
        for e in self.entries:
            e.weight *= rescale
            if doCeil:
                e.weight = int(math.ceil(e.weight))
                


import pandas as pd

spellProps = pd.read_csv('spellProps.txt', names=['Spell','Tier','Element','Continuous'], sep=' ')

with open('spellReg.txt') as f:
    spells = f.readlines()
spellToId = { x.rstrip() : i for (i,x) in enumerate(spells) }

tiers = ['BASIC', 'APPRENTICE', 'ADVANCED', 'MASTER']

def getSpellIdSubset(elements, tier, allowContinuous):
    ret = []
    for index, spell in spellProps.iterrows():
        if (spell['Tier'] == tier and (allowContinuous or not spell['Continuous']) and (spell['Element'] in elements)):
          ret.append(spellToId[spell['Spell']])
    return ret

def makeSpellThingList(elements, tierPerc, spellBookOrScroll):
    ret = LootList()
    for index, tier in enumerate(tiers):
        if tierPerc[index] > 0:
            spellIds = getSpellIdSubset(elements, tier, spellBookOrScroll == "spell_book")
            lootList = LootList()
            for i in spellIds:
                lootList.add(LootEntry("ebwizardry:" + spellBookOrScroll, i, 1))
            lootList.normaliseWeight(tierPerc[index])
            ret.merge(lootList)
    return ret
    

# {"data" : {"name" : "ebwizardry:smoke_bomb", "meta" : x}, "weight" : 4},

# For default loot tables the weights are as follows: 
# and other weights as follows:
#
# novice_wands 3 - equal weight selection from:
#   ebwizardry:magic_wand
#   ebwizardry:basic_fire_wand
#   ebwizardry:basic_ice_wand
#   ebwizardry:basic_lightning_wand
#   ebwizardry:basic_necromancy_wand
#   ebwizardry:basic_earth_wand
#   ebwizardry:basic_sorcery_wand
#   ebwizardry:basic_healing_wand
# wizard_armour 6 - equal weight selection from:
#   ebwizardry:wizard_hat
#   ebwizardry:wizard_hat_fire
#   ebwizardry:wizard_hat_ice
#   ebwizardry:wizard_hat_lightning
#   ebwizardry:wizard_hat_necromancy
#   ebwizardry:wizard_hat_earth
#   ebwizardry:wizard_hat_sorcery
#   ebwizardry:wizard_hat_healing
#   ebwizardry:wizard_robe
#   ebwizardry:wizard_robe_fire
#   ebwizardry:wizard_robe_lightning
#   ebwizardry:wizard_robe_necromancy
#   ebwizardry:wizard_robe_earth
#   ebwizardry:wizard_robe_sorcery
#   ebwizardry:wizard_robe_healing
#   ebwizardry:wizard_leggings
#   ebwizardry:wizard_leggings_fire
#   ebwizardry:wizard_leggings_ice
#   ebwizardry:wizard_leggings_lightning
#   ebwizardry:wizard_leggings_necromancy
#   ebwizardry:wizard_leggings_earth
#   ebwizardry:wizard_leggings_sorcery
#   ebwizardry:wizard_leggings_healing
#   ebwizardry:wizard_boots
#   ebwizardry:wizard_boots_fire
#   ebwizardry:wizard_boots_ice
#   ebwizardry:wizard_boots_lightning
#   ebwizardry:wizard_boots_necromancy
#   ebwizardry:wizard_boots_earth
#   ebwizardry:wizard_boots_sorcery
#   ebwizardry:wizard_boots_healing
# arcane_tomes 6
#   (ebwizardry:arcane_tome, apprentice-advanced-master is meta 1-2-3 with weight 3-2-1)
# wand_upgrades 2 - equal weight selection from:
#   ebwizardry:condenser_upgrade
#   ebwizardry:siphon_upgrade
#   ebwizardry:storage_upgrade
#   ebwizardry:range_upgrade
#   ebwizardry:duration_upgrade
#   ebwizardry:cooldown_upgrade
#   ebwizardry:blast_upgrade
#   ebwizardry:attunement_upgrade
# identification_scroll 3
# smoke_bomb 4
# poison_bomb 4
# firebomb 4
# magic_crystal(x1-4) 5
# armour_upgrade 1
# spell_book 20
# scroll 10

armour_types = ["hat", "robe", "leggings", "boots"]
wand_upgrade_types = ["condenser", "siphon", "storage", "range", "duration", "cooldown", "blast", "attunement"]

# Relative weights for Tiers should be: Basic (Novice) 60%, Apprentice 25%, Advanced 10%, Master 5%
# We stratify by levels 1-4 and choose per-level weight so that the overall percentages would
# be reached assuming equal numbers of samples on each level. This doesn't have a unique solution,
# but I'm arbitrarily using this:
level_tierPerc = [[100.0,  0.0,  0.0,  0.0],           # level 1 is all basic
                  [60.0,  40.0,  0.0,  0.0],
                  [50.0,  30.0, 20.0,  0.0],
                  [40.0,  30.0, 20.0, 20.0]];          # level 4 has 40% basic, 30% apprentice etc.

# For arcane tomes the standard weights are 3-2-1 so I simply place them with equal weight
# but limited to levels as for spells (Apprentice 2,3,4; Advanced 3,4; Master 4)

def getThemeLevelLists(elements):
    finalLists = []
    for level in [1,2,3,4]:
        entries = []
        numElements = len(elements)
        # novice wands
        wands = LootList()
        wands.add(LootEntry("ebwizardry:magic_wand", [], 1))
        for e in elements:
            if e != "MAGIC":
                wands.add(LootEntry("ebwizardry:basic_" + e.lower() + "_wand", [], 1))
        wands.normaliseWeight(3.0)
        # wizard armour
        armour = LootList()
        for a in armour_types:
            armour.add(LootEntry("ebwizardry:wizard_" + a, [], 1))
            for e in elements:
                if e != "MAGIC":
                    armour.add(LootEntry("ebwizardry:wizard_" + a + "_" + e.lower(), [], 1))
        armour.normaliseWeight(6.0)
        # arcane tomes
        tomes = LootList()
        for m in range(1, level):
            tomes.add(LootEntry("ebwizardry:arcane_tome", m, 1))
        tomes.normaliseWeight(6.0)
        # wand upgrades
        wand_upgrades = LootList()
        for w in wand_upgrade_types:
            wand_upgrades.add(LootEntry("ebwizardry:" + w + "_upgrade", [], 1))
        wand_upgrades.normaliseWeight(2.0)
        # spell books
        spell_books = makeSpellThingList(elements, level_tierPerc[level-1], "spell_book")
        spell_books.normaliseWeight(20.0)
        # spell scrolls
        spell_scrolls = makeSpellThingList(elements, level_tierPerc[level-1], "scroll")
        spell_scrolls.normaliseWeight(10.0)
        
        # Join and add individual items:
        loot = LootList()
        loot.merge(wands)
        loot.merge(armour)
        loot.merge(tomes)
        loot.merge(wand_upgrades)
        loot.merge(spell_books)
        loot.merge(spell_scrolls)
        loot.add(LootEntry("ebwizardry:identification_scroll", [], 3))
        loot.add(LootEntry("ebwizardry:smoke_bomb", [], 3))
        loot.add(LootEntry("ebwizardry:poison_bomb", [], 3))
        loot.add(LootEntry("ebwizardry:firebomb", [], 3))
        loot.add(LootEntry("ebwizardry:armour_upgrade", [], 3))
        loot.add(LootEntry("ebwizardry:magic_crystal", [], 5, 1, 4))
        
        # print
        print "===============" + name + " LEVEL " + str(level) + " ==================="
        for e in loot.entries:
            print e
        
        # convert weights to integers, using quantisation of 1/1000
        loot.normaliseWeight(1000, True)
        finalLists.append(loot)
    return finalLists

# I am going to map dungeon themes to Elements like this:
themes = {
    "desert_tomb": ["NECROMANCY", "FIRE"],               # in SANDY
    "ice_tomb": ["NECROMANCY", "ICE"],                   # in SNOWY
    "mountain_top": ["LIGHTNING", "ICE"],                # in MOUNTAIN, HILLS
    "forest_temple": ["HEALING", "EARTH"],               # in FOREST
    "volcano_lair": ["FIRE", "EARTH"],                   # in MOUNTAIN
    "sorceror_tower": ["LIGHTNING", "SORCERY"],          # in MESA
    "witch_lair": ["HEALING", "SORCERY"]                 # in SWAMP
}


# For each theme create lists for each level and write to file
for name, elements in themes.iteritems():
    lists = getThemeLevelLists(elements)
    with open('ebw_loot_' + name + ".json", "w") as f:
        f.write("""
        {
	"name" : """ + "\"" + name + """:ebw_loot",
	"loot_rules" : [ """)
        for i in range(0, 4):
            f.write("""{
            "level" : """ + str(i+1) + """,
            "loot" : [""")
            f.write(",\n            ".join([str(e) for e in lists[i].entries]))
            f.write("""],
			"each" : true,
			"quantity" : 1
		}""") 
            if i < 3: f.write(",\n")  
        f.write("""]
		}""")

