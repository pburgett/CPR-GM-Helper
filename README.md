# CPR-GM-Helper

This project is designed to help Cyberpunk Red Game Masters administer their games by keeping track of initiative turns, player & NPC statistics and resolve combat skill checks.

## Basic Usage

### Getting Started and Setting Initiatives

Invoke the program by running `python main.py examples/example.json`, where `examples/example.json` is an arbitrary path to your input json file. 

Once the program launches, have you & your players roll for NPC initiatives and Player initiatives respectively. The system tracks this with the `init` command:

```
> init Alpha 10
['init', 'Alpha', '10']
> init Bravo 13
['init', 'Bravo', '13']
> init Charlie 15
['init', 'Charlie', '15']
> init Delta 9
['init', 'Delta', '9']
All initiatives have been set!
```

After player initiatives are set, the `display` command is automatically ran. This command displays the current initiative chart with a short description of each character, and a more detailed description of the current character in the initiative chart. You can invoke this command at any point during the combat loop.

```
 Char, Init, HP, SP, Weapons
*  Charlie 15 35 7 [{'Vampyres': '1d6'}, {'rippers': '2d6'}, {'Heavy Pistol': '3d6'}]
   Bravo 13 30 7 [{'Assault Rifle': '5d6'}, {'Heavy Pistol': '3d6'}, {'Big knucks': '3d6'}]
   Alpha 10 20 3 [{'M SMG': '2d6'}, {'M Pistol': '2d6'}, {'Rippers': '2d6'}]
   Delta 9 35 11 [{'Wolvers': '3d6'}, {'Heavy Pistol': '3d6'}, {'assault rifle': '5d6'}]
==================================
It is  Charlie 's turn
{'HP': 35, 'SP': 7, 'weapons': [{'Vampyres': '1d6'}, {'rippers': '2d6'}, {'Heavy Pistol': '3d6'}], 'challenge_score': None, 'attributes': {'I': 5, 'R': 8, 'D': 6, 'T': 4, 'C': 5, 'W': 5, 'M': 7, 'B': 5, 'E': 2}, 'melee_skills': {'B': 8, 'E': 14, 'MA': 0, 'M': 13}, 'ranged_skills': {'A': 8, 'Ha': 8, 'He': 3, 'S': 8}}
```

### The Combat Loop

After setting initiatives, the combat loop for each character is to run the `attack` command to see if an attack succeeds, run the `damage` command if the attack succeeds, and then the `pass` command to end the character's turn.

The `attack` command is structured as follows: the target character, the subject's attack roll and *EITHER* the defender's evasion/brawling check *OR* the DV for the ranged attack. Difficulty charts for ranged attacks by weapon class can be found on page 173 of the Cyberpunk Red Corebook.

For example, if Charlie was to attack Bravo, using a Pistol within 6 meters, the GM would run the following:
```
> attack Bravo 17 13
The attack hits! Roll the appropriate count of D6s and run
 damage  Bravo  <type [ranged/melee/autofire/direct] <damage>
```
In this case, the last input is the DV for the melee attack as per page 173. Next, either the GM or respective player would roll *N* D6 for damage:
```
damage Bravo ranged 14
14 points of damage applied to  Bravo 
 Current HP is  23
```
Now assuming that Charlie is done with their turn, they can run `pass` to move along to the next character in the initiative chart. Next Bravo would roll for attack, pass onto Alpha, and carry down the initiative chart. 
```
> pass
==================================
 Char, Init, HP, SP, Weapons
   Charlie 15 35 7 [{'Vampyres': '1d6'}, {'rippers': '2d6'}, {'Heavy Pistol': '3d6'}]
*  Bravo 13 23 6 [{'Assault Rifle': '5d6'}, {'Heavy Pistol': '3d6'}, {'Big knucks': '3d6'}]
   Alpha 10 20 3 [{'M SMG': '2d6'}, {'M Pistol': '2d6'}, {'Rippers': '2d6'}]
   Delta 9 35 11 [{'Wolvers': '3d6'}, {'Heavy Pistol': '3d6'}, {'assault rifle': '5d6'}]
==================================
It is  Bravo 's turn
{'HP': 23, 'SP': 6, 'weapons': [{'Assault Rifle': '5d6'}, {'Heavy Pistol': '3d6'}, {'Big knucks': '3d6'}], 'challenge_score': None, 'attributes': {'I': 4, 'R': 7, 'D': 5, 'T': 4, 'C': 5, 'W': 2, 'M': 5, 'B': 4, 'E': 3}, 'melee_skills': {'B': 9, 'E': 7, 'MA': 0, 'M': 11}, 'ranged_skills': {'A': 10, 'Ha': 12, 'He': 3, 'S': 12}}
```