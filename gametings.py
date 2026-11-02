import pygame
import pandas as pd
import random
from pathlib import Path

pygame.init()
#This was a lot.... next time I will be chill about this.
# THE LOST LABYRINTH OF MARS
# Okay, now that I can move my astronaut around,
# I want to give them things to actually discover!


#MUSIC TIMMEEEe (If you don't got this please comment out everything.)
# Now I want the music to change depending on the room I'm exploring.

import os

pygame.mixer.init()

music_muted = False
current_music = None

def play_music(room_type):
    global current_music

    # Don't restart the same song unnecessarily.
    if current_music == room_type:
        return

    music_file = os.path.join(
        "generated_music",
        room_type.lower() + ".mp3"
    )

    if os.path.exists(music_file):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.4 if not music_muted else 0)
        pygame.mixer.music.play(-1)

        current_music = room_type
    else:
        print("Music not found:", music_file)


WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Lost Labyrinth of Mars")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 23)
label_font = pygame.font.SysFont("couriernew", 17, bold=True)

# Colors
MARS_RED = (174, 96, 78)
WHITE = (235, 235, 225)
BLUE = (113, 190, 215)
DARK = (44, 45, 62)
CYAN = (105, 235, 220)
PURPLE = (190, 150, 225)
GOLD = (245, 205, 120)
PANEL = (30, 35, 45)
SLOT = (53, 59, 67)

# Load my fake Martian dataset
# Using the file's location means this still works if Terminal is in another folder.
rooms = pd.read_csv(Path(__file__).parent / "mars_labyrinth_rooms.csv")
print("Loaded", len(rooms), "Martian rooms!")

# Player stats
player = pygame.Rect(385, 285, 30, 40)
player_speed = 5

# Since I eventually want to add combat, (if i have time and energy lol)
# I think I need health AND oxygen.
# Oxygen is for exploring Mars, and health is for fighting.
health = 100
oxygen = 100
crystals = 0
backpack = []

# Objects the astronaut can discover
crystal = pygame.Rect(120, 190, 25, 35)
artifact = pygame.Rect(550, 390, 30, 30)
door = pygame.Rect(650, 130, 80, 110)
crystal_collected = False
artifact_collected = False

# Text displayed after an interaction
message = "Explore Mars! Press E near an object."
message_timer = 0

# I want the doorway to actually open a story instead
# of just printing everything in the terminal.
# This tells the game whether we're exploring
# or reading a story encounter.
# Adding backpack as a third mode keeps the controls separate.
game_mode = "explore"
current_room = None
play_music("discovery")

# GAME GOAL!
# I need a reason to explore instead of collecting stuff forever.
# Get 100 crystals and an ancient artifact, then return to the doorway.
GOAL_CRYSTALS = 100
rooms_visited = 0
end_message = ""



def show_message(text):
    global message, message_timer
    message = text
    message_timer = 240


# I already have a backpack list, but I want the items inside it to actually be useful.
# Starting with oxygen tanks and medkits. Any thoughts on how to make them more interesting than just "restore 30 oxygen/health"?
def use_item(item_name):
    global oxygen, health

    if item_name not in backpack:
        # this is a good place to add a sound effect for trying to use an item you don't have.x
        show_message("You don't have a " + item_name + "!")
        return

    if item_name == "Oxygen Tank":
        oxygen = min(100, oxygen + 30)
        backpack.remove(item_name)
        show_message("Oxygen restored! Oxygen: " + str(oxygen))
    elif item_name == "Medkit":
        health = min(100, health + 30)
        backpack.remove(item_name)
        show_message("Health restored! Health: " + str(health))
    else:
        show_message("You can't use that item yet!")

        #I wish I had better ideas for the Space Key and Ancient Martian Artifact. Maybe they could unlock a secret room or give a bonus at the end of the game. For now, they just sit in the backpack as collectibles.


# I wanted the backpack to feel more like a real game UI.
# So each item gets a tiny description instead of just being a boring list.
def get_item_description(item_name):
    if item_name == "Oxygen Tank":
        return "Restores 30 oxygen."
    elif item_name == "Medkit":
        return "Restores 30 health."
    elif item_name == "Space Key":
        return "Might unlock something later..."
    elif item_name == "Ancient Martian Artifact":
        return "A strange object from the ruins."
    elif item_name == "Mysterious Martian Relic":
        return "An ancient relic with unknown purpose."
    else:
        return "Unknown item."


def reset_game():
    # Let me replay without closing the whole game window.
    global health, oxygen, crystals, backpack
    global crystal_collected, artifact_collected, game_mode, current_room
    global rooms_visited, end_message, player
    health = 100
    oxygen = 100
    crystals = 0
    backpack = []
    crystal_collected = False
    artifact_collected = False
    game_mode = "explore"
    play_music("discovery")
    current_room = None
    rooms_visited = 0
    end_message = ""
    player.topleft = (385, 285)
    show_message("New mission! Find an artifact and 100 crystals.")


def check_survival():
    # No health or oxygen means my astronaut can't continue.
    global game_mode, end_message
    if oxygen <= 0:
        game_mode = "game_over"
        end_message = "Your oxygen ran out in the labyrinth."
    elif health <= 0:
        game_mode = "game_over"
        end_message = "The dangers of Mars overwhelmed you."


def draw_wrapped(text, x, y, max_width, text_font, color, line_height=24):
    # New helper: Pygame doesn't wrap long text automatically.
    words = str(text).split()
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if text_font.size(trial)[0] > max_width and line:
            screen.blit(text_font.render(line, True, color), (x, y))
            y += line_height
            line = word
        else:
            line = trial
    if line:
        screen.blit(text_font.render(line, True, color), (x, y))


def draw_backpack():
    # BACKPACK PANEL!
    # I wanted an actual inventory screen like an RPG.
    # The items should appear inside the game, not just in my Terminal.
    # Tried the plain popup and then lots of nested rectangles.
    # Keeping this version more like a field inventory / explorer's kit.
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((12, 15, 20, 155))
    screen.blit(veil, (0, 0))
    #I feel like this is ugly, but I want the backpack to look like a real panel instead of just a rectangle.... need more time to tinker IG
    pygame.draw.rect(screen, PANEL, (88, 82, 624, 428), border_radius=8)
    pygame.draw.rect(screen, GOLD, (88, 82, 624, 428), 2, border_radius=8)
    pygame.draw.rect(screen, GOLD, (108, 105, 5, 36))
    screen.blit(font.render("FIELD PACK / 01", True, WHITE), (127, 110))
    screen.blit(label_font.render("B / ESC TO CLOSE", True, GOLD), (520, 119))
    pygame.draw.line(screen, (93, 101, 107), (110, 157), (688, 157), 1)

    screen.blit(small_font.render(f"O2 {oxygen:03d}   HP {health:03d}   CRYSTALS {crystals:03d}", True, CYAN), (119, 174))
    screen.blit(label_font.render("CONTENTS", True, GOLD), (119, 210))

    # Six visible slots. We can add scrolling later if needed. Probablt won't be needed since the game is short and I don't want to make it too complicated. and I don 't want to. 
    if not backpack:
        screen.blit(font.render("Empty. Go find something strange.", True, WHITE), (125, 270))
    else:
        for index, item in enumerate(backpack[:6]):
            item_y = 239 + index * 35
            pygame.draw.rect(screen, SLOT, (116, item_y, 572, 31), border_radius=3)
            label = "[1]" if item == "Oxygen Tank" else "[2]" if item == "Medkit" else "[ ]"
            screen.blit(label_font.render(label, True, GOLD), (128, item_y + 8))
            screen.blit(small_font.render(item, True, WHITE), (179, item_y + 6))
            description = small_font.render(get_item_description(item), True, CYAN)
            screen.blit(description, (405, item_y + 6))
        if len(backpack) > 6:
            screen.blit(small_font.render(f"+ {len(backpack) - 6} more in pack", True, GOLD), (121, 454))

    screen.blit(label_font.render("1 USE OXYGEN  /  2 USE MEDKIT", True, WHITE), (118, 474))

# Start with mysterious exploration music. so freeeee!
play_music("discovery")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Press E to interact with nearby objects
        if event.type == pygame.KEYDOWN:
            # Press M to mute or unmute my Lyria soundtrack.
            if event.key == pygame.K_m:
                music_muted = not music_muted
                pygame.mixer.music.set_volume(0 if music_muted else 0.4)
                continue
            # WIN / LOSE SCREEN
            # Press R to try again (no need to restart Python).
            if game_mode in ("won", "game_over"):
                if event.key == pygame.K_r:
                    reset_game()
                continue

            # BACKPACK MODE
            # If my backpack is open, I only want backpack controls to work.
            # That way the player doesn't accidentally interact with the world underneath it.
            if game_mode == "backpack":
                if event.key in (pygame.K_b, pygame.K_ESCAPE):
                    game_mode = "explore"
                    play_music("discovery")
                elif event.key == pygame.K_1:
                    use_item("Oxygen Tank")
                elif event.key == pygame.K_2:
                    use_item("Medkit")
                continue

            # STORY MODE
            # If I'm reading a story encounter, pressing 3 takes me back to exploring.
            if game_mode == "story":
                # lol so now I want the choices to actually do something.
                # Investigating should depend on what kind of room I found.
                # Searching should let me collect supplies. maybe I can make some supplies rarer than others.
                if event.key == pygame.K_1:
                    room_type = current_room["room_type"]
                    if room_type == "Treasure":
                        reward = int(current_room["crystal_reward"])
                        crystals += reward
                        show_message(f"You found {reward} crystals!")
                    elif room_type == "Rest":
                        amount = int(current_room["oxygen_restore"])
                        oxygen = min(100, oxygen + amount)
                        show_message(f"You restored {amount} oxygen!")
                    elif room_type == "Hazard":
                        # A tiny combat encounter: one quick hit from a guardian.
                        # Later this could become a proper turn-based fight.
                        cost = int(current_room["oxygen_cost"])
                        damage = random.randint(8, 18)
                        oxygen = max(0, oxygen - cost)
                        health = max(0, health - damage)
                        show_message(f"Martian guardian! -{damage} HP, -{cost} oxygen!")
                    elif room_type == "Discovery":
                        backpack.append("Mysterious Martian Relic")
                        show_message("You discovered an ancient relic!")
                    elif room_type == "Puzzle":
                        reward = int(current_room["crystal_reward"])
                        crystals += reward
                        show_message(f"You uncovered {reward} crystals!")
                    game_mode = "explore"
                    play_music("discovery")
                    current_room = None
                    check_survival()
                #this was hard to figure out, but I wanted the player to be able to search for supplies instead of just investigating the room. I also wanted it to be random so that the player doesn't know what they'll get. I might make some supplies rarer than others later, but for now it's just a random choice from a list.
                elif event.key == pygame.K_2:
                    # For now, I'm thinking searching gives me a random supply.
                    # Later I might make some supplies rarer than others. I don't have time lol but it would be fun!
                    supplies = ["Oxygen Tank", "Medkit", "Space Key"]
                    found_item = random.choice(supplies)
                    backpack.append(found_item)
                    show_message(f"You found: {found_item}")
                    game_mode = "explore"
                    play_music("discovery")
                    current_room = None

                elif event.key == pygame.K_3:
                    game_mode = "explore"
                    play_music("discovery")
                    current_room = None
                    show_message("You leave the room.")
                continue

            # Press B to check the backpack
            # Old experiment (Terminal-only backpack):
            # elif event.key == pygame.K_b:
            #     print("\nYOUR BACKPACK:", backpack)
            #     show_message("Backpack: " + ", ".join(backpack) if backpack else "Your backpack is empty!")
            # I want it to show up on screen instead of just in Terminal.
            if event.key == pygame.K_b:
                game_mode = "backpack"
                continue

            if event.key == pygame.K_e:
                # inflate() creates a larger interaction area
                nearby = player.inflate(45, 45)
                if nearby.colliderect(crystal) and not crystal_collected:
                    crystal_collected = True
                    crystals += 25
                    show_message("You collected 25 energy crystals!")
                elif nearby.colliderect(artifact) and not artifact_collected:
                    artifact_collected = True
                    backpack.append("Ancient Martian Artifact")
                    show_message("An ancient artifact! Added to backpack.")
                elif nearby.colliderect(door):
                    # Once I have the objective, this doorway becomes my escape!
                    has_artifact = any(
                        item in backpack
                        for item in ("Ancient Martian Artifact", "Mysterious Martian Relic")
                    )
                    if crystals >= GOAL_CRYSTALS and has_artifact:
                        game_mode = "won"
                        end_message = "You escaped with the secrets of Mars!"
                    else:
                        # Randomly select a room from my dataset
                        new_room = rooms.sample(1).iloc[0]
                        # The room's type determines its soundtrack.
                        play_music(str(new_room["room_type"]))
                        rooms_visited += 1
                        # Entering unknown rooms consumes a little oxygen.
                        oxygen = max(0, oxygen - 4)
                        check_survival()
                        if game_mode != "game_over":
                            current_room = new_room
                            game_mode = "story"
                            print("\nNEW DISCOVERY!")
                            print("Room:", new_room["room_name"])
                            print("Type:", new_room["room_type"])
                            print("Description:", new_room["description"])
                            show_message("Discovered: " + str(new_room["room_name"]))

    # DEBUGGINGNOTE:
    # I couldn't figure out why my screen was completely black.
    # Turns out I accidentally put the drawing code OUTSIDE
    # the while loop. Python indentation is no joke lol.
    #
    # Also learned that display.flip() needs to run every frame,
    # not just when the story panel is open.

    # Movement
    # I only want the astronaut to move while exploring,
    # not while reading a story encounter.
    if game_mode == "explore":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += player_speed

    # Keep the player inside the window
    player.clamp_ip(screen.get_rect())

    # Draw the background
    screen.fill(MARS_RED)

    # Draw crystal, unless collected
    if not crystal_collected:
        pygame.draw.polygon(screen, CYAN, [
            (crystal.centerx, crystal.top), (crystal.right, crystal.centery),
            (crystal.centerx, crystal.bottom), (crystal.left, crystal.centery)
        ])

    # Draw artifact, unless collected
    if not artifact_collected:
        pygame.draw.rect(screen, PURPLE, artifact, border_radius=5)
        pygame.draw.circle(screen, GOLD, artifact.center, 7)

    # Draw Martian doorway
    pygame.draw.rect(screen, DARK, door, border_radius=15)
    pygame.draw.rect(screen, PURPLE, door, 5, border_radius=15)

    # Draw astronaut
    #astronaut is tea!!!! 
    pygame.draw.rect(screen, WHITE, (player.x + 5, player.y + 15, 20, 25), border_radius=5)
    pygame.draw.circle(screen, WHITE, (player.centerx, player.y + 12), 15)
    pygame.draw.ellipse(screen, BLUE, (player.x + 4, player.y + 5, 22, 12))

    # HUD: display player information
    hud = font.render(f"Health: {health}   Oxygen: {oxygen}   Crystals: {crystals}", True, WHITE)
    screen.blit(hud, (20, 20))

    # Mission progress: make it obvious what I need to WIN.
    artifact_found = any(item in backpack for item in ("Ancient Martian Artifact", "Mysterious Martian Relic"))
    mission_text = small_font.render(
        f"ESCAPE GOAL: {crystals}/{GOAL_CRYSTALS} crystals | Relic: {'YES' if artifact_found else 'NO'} | Rooms: {rooms_visited}",
        True, GOLD
    )
    screen.blit(mission_text, (20, 85))

    # Instructions
    instructions = small_font.render(
        "WASD / Arrows: Move   E: Interact   B: Backpack   M: Music",
        True, WHITE
    )
    screen.blit(instructions, (20, 55))
    # Message panel
    if message_timer > 0:
        message_timer -= 1
        pygame.draw.rect(screen, DARK, (20, 510, 760, 65), border_radius=10)
        draw_wrapped(message, 35, 530, 725, small_font, WHITE)

    # STORY MODE!
    # I want the player to see a room description
    # and make choices without leaving the game window.
    if game_mode == "story" and current_room is not None:
        pygame.draw.rect(screen, DARK, (80, 130, 640, 340), border_radius=15)
        room_title = font.render(str(current_room["room_name"]), True, GOLD)
        screen.blit(room_title, (110, 160))
        room_type = small_font.render("Room type: " + str(current_room["room_type"]), True, CYAN)
        screen.blit(room_type, (110, 200))
        # For now, we're showing the description directly.
        # We can add automatic text wrapping next.
        draw_wrapped(current_room["description"], 110, 245, 570, small_font, WHITE)
        screen.blit(small_font.render("[1] Investigate", True, WHITE), (110, 325))
        screen.blit(small_font.render("[2] Search for supplies", True, WHITE), (110, 360))
        screen.blit(small_font.render("[3] Leave", True, WHITE), (110, 395))

    # IMPORTANT:
    # This needs to happen inside while running,
    # but OUTSIDE the story condition.
    # Otherwise the game doesn't redraw normally. (found the hard way lol)
    if game_mode == "backpack":
        draw_backpack()

    # END SCREEN? End da game mode. I want the player to see a message and their stats, then press R to restart. Or something.
    if game_mode in ("won", "game_over"):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 12, 20, 215))
        screen.blit(veil, (0, 0))
        heading = "MISSION COMPLETE" if game_mode == "won" else "MISSION FAILED"
        heading_color = GOLD if game_mode == "won" else PURPLE
        screen.blit(font.render(heading, True, heading_color), (260, 190))
        draw_wrapped(end_message, 170, 250, 480, font, WHITE, 32)
        screen.blit(small_font.render(f"Crystals: {crystals}     Rooms explored: {rooms_visited}", True, CYAN), (225, 320))
        screen.blit(font.render("PRESS R TO RESTART", True, GOLD), (265, 390))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
