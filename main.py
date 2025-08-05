from cmd import Cmd
import csv
import argparse
from pathlib import Path
import random 
import json
import math

def ingest(sheet):
    chars = {}
    with open(str(sheet), "r") as file:
        data = json.load(file)
        for row in data:
            newEntity = Character()
            newEntity.name = row["Name"]
            newEntity.hp = row["HP"]
            newEntity.sp = row["SP"]
            for weapon in row["weapons"]:
                newWeapon = Weapon()
                newWeapon.name = weapon[0]
                newWeapon.dieCount = int(weapon[1][0].strip()[0])
                newEntity.weapons.append(newWeapon)

            newEntity.challenge_score = row["challenge_score"]
            newEntity.attributes = row["attributes"]
            newEntity.melee_skills = row["melee_skills"]
            newEntity.ranged_skills = row["ranged_skills"]
            chars[row["Name"]] = newEntity 
    return chars

class Character:
    def __init__(self):
        self.name = 0
        self.hp = 0
        self.sp = 0
        self.weapons = []
        self.is_alive = True
        self.challenge_score = None
        self.attributes = None
        self.melee_skills = None
        self.ranged_skills = None
        self.notes = ""


    def describe(self):
        return {"HP":self.hp, "SP": self.sp, 
            "weapons": [weapon.describe() for weapon in self.weapons], 
            "challenge_score": self.challenge_score, "attributes": self.attributes, 
            "melee_skills": self.melee_skills, "ranged_skills": self.ranged_skills}
    
    def damage(self, dmg, dmg_type):
        print(dmg)
        if dmg_type == "melee":
            self.hp = self.hp - (dmg - (self.sp //2))
            if self.sp > 0:
                self.sp -= 1
        if dmg_type == "direct":
            self.hp - self.hp - dmg
        else:
            # encompases ranged & autofire
            self.hp = self.hp - (dmg - self.sp)
            if self.sp > 0:
                self.sp -= 1
        if self.hp <= 0:
            self.is_alive = False
            self.hp = 0

        

    def heal(self, hp):
        self.hp += hp

    def armor_recover(self, sp):
        self.sp += sp

    def roll_initiative(self):
        if self.attributes != None:
            return random.randrange(1,10) + self.attributes["R"]
        else:
            # Intuiting Reflex from challenge_score. 
            return random.randrange(1,10) + math.floor((self.challenge_score * 0.6))

    
class Weapon:
    def __init__(self):
        self.name = None
        self.dieCount = None


    def describe(self):
        return {self.name: str(self.dieCount) + "d6"}

    def autoroll(self):
        if not self.dieCount:
            return None
        ret = 0
        for i in range(self.dieCount):
            ret += random.randrange(1,6)
        return ret

class cmdprompt(Cmd):

    prompt = '> '
    intro = "Welcome to the Cyberpunk Red DM Helper!"

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    sheet =  Path(args.path)
    if not sheet.exists():
        print("Error: Path to character sheet not recognized")
        raise SystemExit(1)

    chars = ingest(sheet)
    charKeys = list(chars.keys())
    charKeysLen = len(charKeys)
    initiativeQueue = {}
    combatReady = False
    commandHistory = []
    turn = 0

    def do_exit(self, inp):
        print("Bye")
        return True

    def set_init(self, cmds):
        # TODO - implement stronger error handling to prevent total crashout 
        print(cmds)
        if len(cmds) > 3:
            print("Error - unrecognized command structure.")
        elif cmds[1] not in self.charKeys:
            print("Error - unrecognized character name.")
        else:
            self.initiativeQueue[cmds[1]] =  int(cmds[2])
            
            if len(self.initiativeQueue) == self.charKeysLen:
                print("All initiatives have been set!")
                initQSorted = {k:v for k,v in sorted(self.initiativeQueue.items(), key=lambda item: item[1], reverse = True)}
                for k,v in initQSorted.items():
                    initQSorted[k] = [self.chars[k], initQSorted[k]]
                self.combatReady = True
                self.charKeys = list(initQSorted.keys())
                return initQSorted
                
            else: 
                return self.initiativeQueue

    def table_show(self):
        if not self.combatReady:
            print("Warning - not all initiatives have been set!\n"
                "This is an incomlete list of your battle order.\n"
                "Please set all character's initiatives to get a proper reading.")
            print(self.initiativeQueue)
        else:
            # forcing correct order of charKeys
             # charKeys = list(self.initiativeQueue.keys())
            i = 0
            print("==================================")
            print(" Char, Init, HP, SP, Weapons")
            for k, v in self.initiativeQueue.items():
                if v[0].hp > 0:
                    if i == self.turn:
                        print("* ", k, v[1], v[0].hp, v[0].sp, [weapon.describe() for weapon in v[0].weapons])
                    else:
                        print("  ", k, v[1], v[0].hp, v[0].sp, [weapon.describe() for weapon in v[0].weapons])
                i += 1
            print("==================================")
            print("It is ", self.charKeys[self.turn], "'s turn")
            print(self.initiativeQueue[self.charKeys[self.turn]][0].describe())
    
    def turn_pass(self):
        if self.turn == self.charKeysLen -1 :
                self.turn = 0
        else:
            self.charKeys = list(self.initiativeQueue.keys())
            if self.initiativeQueue[self.charKeys[self.turn]][0].hp < 0:
                self.turn_pass()
            self.turn += 1
        self.table_show()

    
    def eval_hit(self, subject, cmds):
        # expected structure - attack <target> <attacker roll> <defender roll>
        target_obj = self.initiativeQueue[cmds[1]][0]
        subject_obj = self.initiativeQueue[subject][0]
        target_obj = self.initiativeQueue[cmds[1]][0]
        attack = int(cmds[2])
        defense = int(cmds[3])
        print(attack > defense)
        return True if attack > defense else False


    def deal_damage(self, cmds):
        target, dmg_type, dmg = cmds[1], cmds[2], int(cmds[3])
        #is_ranged = True if cmds[2] == 'ranged' else False
        self.initiativeQueue[target][0].damage(dmg, dmg_type)
        return 

    def default(self, inp):
        cmds = inp.split(' ')
        print(cmds)
        #print(initiativeQueue)
        if cmds[0] == "display":
            self.table_show()
        if cmds[0] == "init":
            self.initiativeQueue = self.set_init(cmds)
            if self.combatReady:
                # charKeys = list(self.initiativeQueue.keys())
                self.table_show()

        if cmds[0] == "attack":
            if not self.combatReady:
                print("Error - not all initiatives have been set!"
                    "Give all characters an initiative value before proceeding.")
            else:
                # charKeys = list(self.initiativeQueue.keys())
                #print(cmds, charKeys[self.turn])
                if cmds[1] not in self.charKeys:
                    print("Error - target", cmds[0], " not found")
                elif cmds[1] == self.charKeys[self.turn]:
                    print("Error - this command would be a self-inflicted damage roll.")
                else:
                    if self.eval_hit(self.charKeys[self.turn], cmds):
                        print("The attack hits! Roll the appropriate count of D6s and run\n",
                            "damage ", cmds[1], " <type [ranged/melee/autofire/direct] <damage>")
                    else:
                        print("The attack did not hit.")

        if cmds[0] == "damage":
            # charKeys = list(self.initiativeQueue.keys())
            if cmds[1] == self.charKeys[self.turn]:
                print("Error - this command would apply self-inflicted damage.")
            else:
                self.deal_damage(cmds)
                print(cmds[3], "points of damage applied to ", cmds[1], "\n",
                    "Current HP is ", self.initiativeQueue[cmds[1]][0].hp)

        if cmds[0] == "pass":
            self.turn_pass()

        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)







if __name__ == '__main__':  
    cmdprompt().cmdloop()
