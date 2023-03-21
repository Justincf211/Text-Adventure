from adventurelib import *
import time
import adventurelib

# Global variables
Money = 100
Health = 100
XP_lvl = 0
MC_lvl = 0
lvl_Cap = 100
lvl_mod = 0
damage = 1
global currentweapon

# Intro
print("""
Welcome to the Adventure Game! At any point type Help for more information.
As an avid traveler, you have decided to stop at small tavern.
""")


# Player name entry
def name():
    print("Once inside the barkeep asks your name")
    name = input()
    if name.isalpha():
        print("Welcome " + name + ".")
    else:
        print("Nah g")
        names()


def names():
    print("The Barkeep asks your name again")
    name = input()
    if name.isalpha():
        print("Welcome " + name + ".")
    else:
        print("Nah g")
        names()


name()


# Mini intro
def barKeep():
    answer = input("Hey there, looking for some food? (yes/no)")

    if answer.lower().strip() == "yes":
        print(
            "Then sit down and eat some slop.")
    elif answer.lower().strip() == "no":
        print("Then what you die in my tavern? No, take some water")
    else:
        print("I cant hear you speak up.")
        barKeep()


barKeep()

# Setting each Room
current_Room = startRoom = Room("""
    You are home.
""")

Field = startRoom.north = Room("""
    You are in a beautiful field.  
""")

startRoomSouth = startRoom.south = Room("""
    You have entered the dungeon.
""")

Shop = startRoom.east = Room("""
    You have entered the shop.
""")

Blacksmith = startRoom.west = Room("""
    You have arrived at the blacksmith.
""")

enemyRoomOne = startRoomSouth.south = Room("""
    There is an enemy in front of you. 
    There is a door to your north and south.
""")

bossRoom = enemyRoomOne.south = Room("""
    A large hulking mass stands before you.
""")

# Setting Combat Zones
startRoomSouth.can_fight = True
enemyRoomOne.can_fight = True
bossRoom.can_fight = True
startRoom.can_fight = False
Blacksmith.can_fight = False
Shop.can_fight = False
Field.can_fight = False


# Setting shop zones
Shop.can_buy = True
startRoomSouth.can_buy = False
startRoom.can_buy = False
enemyRoomOne.can_buy = False
Blacksmith.can_buy = False
Field.can_buy = False
bossRoom.can_buy = False

# Setting Healing Areas
startRoom.can_sleep = True
Shop.can_sleep = False
startRoomSouth.can_sleep = False
enemyRoomOne.can_sleep = False
Blacksmith.can_sleep = False
Field.can_sleep = False
bossRoom.can_sleep = False


# For checking how much money the player has
@when('currency')
def currency():
    print("You have $", Money)
    look()


# for checking how much health the player has
@when('hp')
def hp():
    global Health
    print("You have", Health, "health points")
    look()


# Lists
merch = ["water", "milk", "Apple"]
weapon = ["sword"]
helm = []
chest = []
legs = []
drop = ["coin"]
mob = ["zombie", "skelly", "slime", "wolf"]

# Setting items and their values

# Drops
coin = Item('coin')
coin.colour = 'gold'

# Shop Items
water = Item('Water')
water.cost = 25
water.colour = 'Blue'

milk = Item('Milk')
milk.cost = 200

Apple = Item("Apple")

# Weapons
sword = Item('sword')
sword.atk = 100

# Enemies
zombie = Item('Zombie')
zombie.atk = 5
zombie.health = 25
zombie.exp = 75

skelly = Item('Skelly')
skelly.atk = 5
skelly.health = 25
skelly.exp = 75

slime = Item('Slime')
slime.atk = 5
slime.health = 25
slime.exp = 75

wolf = Item('Wolf')
wolf.atk = 5
wolf.health = 25
wolf.exp = 75

# Setting items locations
startRoom.items = Bag({coin, sword})
Shop.items = Bag({water, milk})

# Setting Enemies locations (yes it's the same thing as above and yes I need to fix this)
startRoomSouth.items = Bag({zombie})
enemyRoomOne.items = Bag({slime})
bossRoom.items = Bag({skelly})

# Inventory System
inventory = Bag()
Room.items = Bag()
void = Bag()


@when('bag')
def show_inventory():
    print('You have:')
    if not inventory:
        print('nothing')
        return
    for item in inventory:
        print(f'* {item}')


# Tell the player where they are and whats there
@when('look')
def look():
    say(current_Room)
    if current_Room.items:
        for i in current_Room.items:
            say('A %s is here.' % i)
    else:
        say('There are no items here.')


# Movement
@when('north', direction='north')
@when('south', direction='south')
@when('east', direction='east')
@when('west', direction='west')
def go(direction):
    global current_Room
    room = current_Room.exit(direction)
    if room:
        if current_Room.can_fight == True:
            print("You can't turn your back to these monsters")
        elif room == bossRoom:
            current_Room = room
            print(f'You go {direction}.')
            look()
            endgame()
        else:
            current_Room = room
            print(f'You go {direction}.')
            look()
    else:
        print("You can not go that way")


# Picking up items:
@when("pick up ITEM")
def pick_up(item):
    obj = current_Room.items.find(item)
    if item in drop:
        obj = current_Room.items.take(item)
        inventory.add(obj)
        print(f'You take the {obj}.')
        look()
    elif item in weapon:
        obj = current_Room.items.take(item)
        inventory.add(obj)
        print(f'You obtain the {obj}.')
        look()
    elif item in merch:
        print(f'you have to pay for that')
        look()
    else:
        print(f'There is no {item} here.')
        look()


# The commends required to buy and item
def take(item):
    obj = current_Room.items.take(item)
    print(f"You grab a {item}")
    inventory.add(obj)


@when("buy ITEM")
def buy(item):
    global Money
    obj = current_Room.items.find(item)
    if item in merch:
        if Money >= obj.cost:
            obj = current_Room.items.find(item)
            Money = Money - obj.cost
            take(item)
            currency()
        elif Money < obj.cost:
            print("You're broke")
            currency()
    elif item in drop:
        print("Just pick it up")
    else:
        print(f"There is no {item} here")


# Base combat mechanics
@when('fight ITEM')
def fight(item):
    global damage
    global XP_lvl
    global Health
    global lvl_mod
    obj = current_Room.items.find(item)
    if item in mob:
        for item in void:
            print("That enemy is not here")
            look()
        else:
            current_Room.can_fight = True
            print("Slapboxing time")
            Health = Health - (obj.atk - lvl_mod)
            obj.health = obj.health - (damage + lvl_mod)
            if Health < 1:
                print(Health, "HP")
                print("Game Over")
                quit()
            elif obj.health < 1:
                XP_lvl = XP_lvl + obj.exp
                print(f"You have slain the {item}")
                print("You gained " + str(obj.exp) + " experience points")
                obj = current_Room.items.take(item)
                void.add(item)
                lvlup()
                look()
                current_Room.can_fight = False
                return current_Room.can_fight
            else:
                hp()
                print(str(obj) + " has " + str(obj.health) + " health left")
                look()
    else:
        print("What, exactly, are you trying to attack?")


# Level System (Add Level Cap)
@when('level')
def level():
    global MC_lvl
    print(f"You are level " + str(MC_lvl) + " with " + str(XP_lvl) + " XP.")


def lvlup():
    global MC_lvl
    global XP_lvl
    global lvl_mod
    if XP_lvl >= 100:
        MC_lvl = MC_lvl + 1
        XP_lvl = XP_lvl - 100
        lvl_mod = lvl_mod + 5


#boss encounter:
def endgame():
    print("The monster rears its head")
    if input() == shoot:
        print("Bang")
    elif input() == swing:
        print("Slash")
    elif input() == bash:
        print("Boom")
    else:
        print("Didn't work")

# Equiptment
@when('equip ITEM')
def equip(item):
    global currentweapon
    global damage
    obj = current_Room.items.find(item)
    if item in weapon:
        obj = inventory.find(item)
        currentweapon = obj
        damage = obj.atk
        print(f"You equip {item} to your main hand.")
        equiptment()
        look()
    else:
        print("That doesn't go there")


@when('test')
def test():
    print(void)


@when('equiptment')
def equiptment():
    global currentweapon
    print("you have a " + str(currentweapon))


# Healing
@when('sleep')
def sleep():
    global Health
    if Health <= 100 and current_Room.can_sleep == True:
        print("After a nice nap you wake up feeling refreshed")
        Health = 100
        hp()
    else:
        print("Try sleeping in your own bed")
        hp()


# A test command that lets the player know the color of an item
@when("peak at ITEM")
def peak(item):
    obj = current_Room.items.find(item)
    print(f'It is a {obj.colour} color')
    look()


# A test command that lets the player look cool
@when("sigh")
def sigh():
    print("You lean against that wall and sigh. You look so cool.")


look()
start()