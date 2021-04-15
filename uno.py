"""
Settings:
    Deck:
        Single Deck
        Double Deck
        Probability Deck
    Extra Rules:
        Draw to match
        Jump in
        0-7
        Stacking:
            Classic (Stacking doesn't work with Jump In)
            Enhanced (Stacking works with Jump In)
        Bluffing
"""


"""
Order of events:
    Open a lobby
    Ask to chose between public and private
        Public: Add a reaction to the lobby message
        Private: Ask the user to ping the people they want to invite
        Maybe: ID system
    Lobby owner functions:
        Remove people
        Everybody's in
    Start game
"""

from discord.ext import commands
import discord

from dataclasses import dataclass
import random
import asyncio


@dataclass
class Player:
    user: discord.User
    hand: list


@dataclass
class GameTracker:
    # type: str
    players: list
    kick_list: list
    deck: list

num_emoji = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
}


emoji_num = {value: key for key, value in num_emoji.items()}

# Card dictionaries used for retrieveing a card's emoji
red_emojis = {
    "0": "<:red_0:831629943908597762>",
    "1": "<:red_1:831629944202723359>",
    "2": "<:red_2:831629944153047101>",
    "3": "<:red_3:831629944169300010>",
    "4": "<:red_4:831629944198529035>",
    "5": "<:red_5:831629944290541599>",
    "6": "<:red_6:831629943947001921>",
    "7": "<:red_7:831629944290541600>",
    "8": "<:red_8:831629944198529036>",
    "9": "<:red_9:831629943879761965>",
    "skip": "<:red_skip:831641162552049734>",
    "reverse": "<:red_reverse:831629944265506906>",
    "plus2": "<:red_plus2:831629944223694849>",
}
blue_emojis = {
    "0": "<:blue_0:831629943947001917>",
    "1": "<:blue_1:831629943879761964>",
    "2": "<:blue_2:831629944249122906>",
    "3": "<:blue_3:831629944153047100>",
    "4": "<:blue_4:831629943879761962>",
    "5": "<:blue_5:831629943908597761>",
    "6": "<:blue_6:831629943867441203>",
    "7": "<:blue_7:831629944198135880>",
    "8": "<:blue_8:831629944135090256>",
    "9": "<:blue_9:831629943787225109>",
    "skip": "<:blue_skip:831641162590453770>",
    "reverse": "<:blue_reverse:831629943996678175>",
    "plus2": "<:blue_plus2:831629943879761963>",
}
green_emojis = {
    "0": "<:green_0:831629944239947847>",
    "1": "<:green_1:831629944198529034>",
    "2": "<:green_2:831629943905189919>",
    "3": "<:green_3:831629944198397982>",
    "4": "<:green_4:831629944303517775>",
    "5": "<:green_5:831629943867441204>",
    "6": "<:green_6:831629944215044162>",
    "7": "<:green_7:831629944223301702>",
    "8": "<:green_8:831629944223694848>",
    "9": "<:green_9:831629944286347265>",
    "skip": "<:green_skip:831641162565419028>",
    "reverse": "<:green_reverse:831629943947001918>",
    "plus2": "<:green_plus2:831629944266031155>",
}
yellow_emojis = {
    "0": "<:yellow_0:831636590609956914>",
    "1": "<:yellow_1:831636590606417940>",
    "2": "<:yellow_2:831636590584397895>",
    "3": "<:yellow_3:831636590602354718>",
    "4": "<:yellow_4:831636590300233819>",
    "5": "<:yellow_5:831636590492123137>",
    "6": "<:yellow_6:831636590584397896>",
    "7": "<:yellow_7:831636590602354719>",
    "8": "<:yellow_8:831636590626996235>",
    "9": "<:yellow_9:831636590471807039>",
    "skip": "<:yellow_skip:831641162456367135>",
    "reverse": "<:yellow_reverse:831636590598029312>",
    "plus2": "<:yellow_plus2:831636590622933033>",
}
action_emojis = {
    "wild": "<:action_wild:831665137806868511>",
    "plus4": "<:action_plus4:831629944055398431>",
}

emoji_colors = {
    "red": red_emojis,
    "blue": blue_emojis,
    "green": green_emojis,
    "yellow": yellow_emojis,
    "action": action_emojis,
}


games = []

avo_cult = None

class Uno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global avo_cult
        avo_cult = self.bot.get_guild(556972632977965107)

    # Main game command
    @commands.command()
    async def ichi(self, ctx):

        # ===================#
        #                    #
        #   Lobby System     #
        #                    #
        # ===================#

        id = None
        # Look over the list of lobbies for a None lobby
        for n in range(len(games)):
            # If there's a None lobby, make the id the index of that lobby
            if games[n] == None:
                id = n
                games[id] = (GameTracker([], []))
                break
        # Otherwise get the id for a new lobby
        if id == None:
            id = len(games)
            games.append(GameTracker([], [], []))


        await self.public_lobby(ctx, id)

        # # Setup Embed --- Will need to be rewritten if it gets reimplemented
        # embed = discord.Embed(
        #     title="**Ichi Game Setup**",
        #     description="Do you want the game to be:\n\n:unlock:: **Public** (Anyone can join)\n:lock:: **Private** (Invite Only)",
        #     color=discord.Color(0xFFFF00),
        # )
        # embed.set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
        # embed.set_author(name="")
        # setup_message = await ctx.send(embed=embed)
        # await setup_message.add_reaction("🔓")
        # await setup_message.add_reaction("🔒")

        # # Listen for which type the user wants the lobby to be
        # def check(reaction, user):
        #     return user == ctx.author and str(reaction.emoji) in ["🔓", "🔒"]

        # try:
        #     reaction, user = await self.bot.wait_for(
        #         "reaction_add", timeout=30, check=check
        #     )
        #     if reaction.emoji == "🔓":
        #         self.lobby.type = "Public"
        #         await setup_message.delete()
        #         await self.public_lobby(ctx)

        #     elif reaction.emoji == "🔒":
        #         self.lobby.type = "Private"
        #         await setup_message.delete()

        # except asyncio.TimeoutError:
        #     await self.lobby_close(ctx, "User took to long to complete the setup, closing the lobby...", setup_message)
        #     return

        # elif self.lobby != None:
        #     await self.error(ctx, "Sorry, there can only be one ichi game at once right now...")

    # A lobby that anyone can join
    async def public_lobby(self, ctx, id):
        # Add the user starting the lobby to players
        games[id].players.append(Player(ctx.author, []))

        # Lobby Embed
        embed = discord.Embed(
            title="**Ichi Game Lobby**",
            description=await self.player_list(games[id].players),
            color=discord.Color(0xFFFF00),
        )
        embed.set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
        embed.set_footer(text="✅ Join.\n🆗 Everybody's in.\n🔨 Kick.\n🔀 Shuffle players.\n🛑 Close.")

        lobby_message = await ctx.send(embed=embed)
        await lobby_message.add_reaction("✅")
        await lobby_message.add_reaction("🆗")
        await lobby_message.add_reaction("🔨")
        await lobby_message.add_reaction("🔀")
        await lobby_message.add_reaction("🛑")

        # Listen for people reacting to join the lobby
        def check(reaction, user):
            return (
                str(reaction.emoji) == "✅"
                or (user == ctx.author and str(reaction.emoji) in ["🆗", "🛑", "🔨", "🔀"])
            ) and reaction.message == lobby_message

        waiting = True
        while waiting:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=600, check=check
                )
                if (
                    reaction.emoji == "✅"
                    and len(games[id].players) != 8
                    and user != ctx.author
                    and not user in (games[id].players + games[id].kick_list)
                ):
                    games[id].players.append(Player(user, []))
                    embed.description = await self.player_list(games[id].players)
                    await lobby_message.edit(embed=embed)

                # If the lobby is full
                elif (
                    reaction.emoji == "✅"
                    and len(games[id].players) == 8
                    and user != ctx.author
                ):
                    await self.error(ctx, "Sorry, this lobby is full!")

                # If everyone is in
                elif reaction.emoji == "🆗":
                    await self.error(ctx, "Starting the game!")
                    await lobby_message.delete()
                    waiting = False
                    # TODO: Actually start the game
                    await self.start_game(ctx, id)

                elif reaction.emoji == "🔀":
                    random.shuffle(games[id].players)
                    embed.description = await self.player_list(games[id].players)
                    await lobby_message.edit(embed=embed)

                # If kick a user
                elif reaction.emoji == "🔨" and len(games[id].players) >= 2:
                    offender = await self.kick_gui(ctx, id)
                    if offender != None:
                        embed.description = await self.player_list(games[id].players)
                        await lobby_message.edit(embed=embed)

                elif reaction.emoji == "🔨" and len(games[id].players) == 1:
                    await self.error(
                        ctx,
                        "You can't kick yourself, wait for someone to join before you try that",
                    )

                # If close the lobby
                elif reaction.emoji == "🛑":
                    await self.lobby_close(
                        ctx,
                        "Host canceled the game, closing the lobby...",
                        lobby_message,
                        id,
                    )
                    return

            except asyncio.TimeoutError:
                await self.lobby_close(
                    ctx,
                    "Host took to long to start the game, closing the lobby...",
                    lobby_message,
                    id,
                )
                return

    async def kick_gui(self, ctx, id):
        descript = "Who would you like to kick:"
        for n in range(1, len(games[id].players)):
            descript = descript + f"\n{num_emoji[n]} {games[id].players[n].user.mention}"

        embed = discord.Embed(title="**Kick Menu**", description=descript)

        kick_message = await ctx.send(embed=embed)
        for n in range(1, len(games[id].players)):
            await kick_message.add_reaction(num_emoji[n])
        await kick_message.add_reaction("🛑")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in (list(num_emoji.values()) + ["🛑"])
            ) and reaction.message == kick_message

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=60, check=check
            )
            if reaction.emoji in list(num_emoji.values()):
                offender = games[id].players[emoji_num[reaction.emoji]]
                # Add the user to the kick list
                games[id].kick_list.append(offender)
                # Remove the user from the lobby
                games[id].players.pop(emoji_num[reaction.emoji])
                # Close the GUI
                await self.error(ctx, f"Kicking {offender.mention}...", kick_message)
                return offender
            elif reaction.emoji == "🛑":
                await self.error(ctx, "Closing kick menu...", kick_message)
                return None

        except asyncio.TimeoutError:
            await self.error(
                ctx,
                "Host took to long to kick a user, closing the menu...",
                kick_message,
            )
            return None

    async def player_list(self, players):
        player_list = f"**Players**: `{len(players)}/8`"
        for n in players:
            player_list = player_list + f"\n{n.user.mention}"
        return player_list


    # Send an error message that deletes itself and close/cleanup the lobby
    async def lobby_close(self, ctx, message, status_message, id):
        games[id] = None
        await status_message.delete()
        error = await ctx.send(message)
        await asyncio.sleep(7)
        await error.delete()

    #==============================#
    #                              #
    #    Actually play the game    #
    #                              #
    #==============================#

    async def start_game(self, ctx, id):
        
        # START CHANNEL, PERM, AND MESSAGE SETUP
        
        cleanup = []
        # Create the category for the game
        overwrites = {
            avo_cult.default_role: discord.PermissionOverwrite(read_messages=False),
            self.bot.user: discord.PermissionOverwrite(read_messages=True),
        }
        game_category = await avo_cult.create_category(f"Ichi Game (ID: {id})", overwrites=overwrites, position=0)
        cleanup.append(game_category)
        
        # Create a status channel for everyone
        for member in games[id].players:
            overwrites[member.user] = discord.PermissionOverwrite(read_messages=True)
        status_channel = await game_category.create_text_channel("status", overwrites=overwrites)
        cleanup.append(status_channel)
        await ctx.send(f"Everyone head to {status_channel.mention}!!!")
        
        # Create a hand channel for each player
        hand_channels = []
        for player in games[id].players:
            overwrites = {
                avo_cult.default_role: discord.PermissionOverwrite(read_messages=False),
                self.bot.user: discord.PermissionOverwrite(read_messages=True),
                player.user:  discord.PermissionOverwrite(read_messages=True),
            }
            player_channel = await game_category.create_text_channel("your-hand", overwrites=overwrites)
            hand_channels.append(player_channel)
            await player_channel.send(f"{player.user.mention} This is your personal channel for this ichi game.")
        cleanup = cleanup + hand_channels
        
        # Create the GUI for #status and #your-hand
        current_action = "The game will begin in 10 seconds..."
        
        status_embed = discord.Embed(title="Ichi Status", description=current_action, color=discord.Color(0xFFFF00))
        status_embed.set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
        status_message = await status_channel.send(embed=status_embed)
        
        player_messages = []
        player_embeds = []
        for n in range(len(games[id].players)): # N is the index of the player who's hand is being built
            player_embeds.append(discord.Embed(title="Your Hand", description=current_action, color=discord.Color(0xFFFF00)))
            player_embeds[n].set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
            player_messages.append(await hand_channels[n].send(embed=player_embeds[n]))
        
        await asyncio.sleep(10)
        
        # FINISH CHANNEL, PERM, AND MESSAGE SETUP

        # START PRELIMINARY GAME STUFF

        # Initialize the deck and embed
        current_action = "Grabbing a deck..."    
        await self.update_status(status_message, status_embed, status_channel, player_messages, player_embeds, current_action)

        games[id].deck = Deck("single")
        await games[id].deck.initialize()
        
        # Shuffle the deck, update the message because why not
        current_action = "Shuffling the deck..."
        await self.update_status(status_message, status_embed, status_channel, player_messages, player_embeds, current_action)

        await games[id].deck.shuffle()

        # Deal the cards, update the message because why not
        current_action = "Dealing cards..."
        await self.update_status(status_message, status_embed, status_channel, player_messages, player_embeds, current_action)
        
        for player in games[id].players:
            for n in range(7):
                card = await games[id].deck.draw()
                player.hand.append(card)
                # for player in games[id].players:

        # FINISH PRELIMINARY GAME STUFF

        current_turn = 0 # The index of the player who's turn it is
        reversed = False
        
        gaming = True
        while gaming:
            current_action = f"{games[id].players[current_turn].user.name}'s turn"
            
            top_of_deck = games[id].deck.cards[0]
            top_of_deck_display = f"Top of deck: {await self.get_emoji(top_of_deck)}"

            await self.hand_display(status_embed, games[id].players, reversed, public=hand_channels)
            # Make and send the embeds that go in each "your-hand" channel
            for n in range(len(games[id].players)): # N is the index of the player who's hand is being built
                await self.hand_display(player_embeds[n], games[id].players, reversed, shown_player=n)

            await self.update_status(status_message, status_embed, status_channel, player_messages, player_embeds, current_action + "\n" + top_of_deck_display)
        
            # Get playable cards from the player who's turn it is
            await hand_channels[current_turn].send(f"{games[id].players[current_turn].user.mention} it's your turn.")
            playable_cards = []
            playable_emojis = []
            for card in games[id].players[current_turn].hand:
                if (
                    card.color == "action"
                    or top_of_deck.color == "action"
                    or card.color == top_of_deck.color
                    or card.number == top_of_deck.number
                ):
                    playable_cards.append(card)
                    playable_emojis.append(await self.get_emoji(card))

            # Automatically draw a card and end the turn if there are no playable cards
            if playable_cards == []:
                card = await games[id].deck.draw()
                games[id].players[current_turn].hand.append(card)
                await hand_channels[current_turn].send(f"You drew a card. {await self.get_emoji(card)}")
                await status_channel.send(f"{games[id].players[current_turn].user.name} drew a card. <:back:831717987979493436>")
            # Otherwise let the player play a card
            else:
                # React with the playable cards to the Your Hand embed
                for emoji in playable_emojis:
                    await player_messages[current_turn].add_reaction(emoji)
                
                def check(reaction, user):
                    return user == games[id].players[current_turn].user and str(reaction.emoji) in playable_emojis

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    card, hand = await self.pop_card(reaction.emoji, games[id].players[current_turn].hand)
                    games[id].players[current_turn].hand = hand
                    await games[id].deck.add(card)

                except asyncio.TimeoutError:
                    # Find out what happens if time runs out, probably play a random card
                    print("Player took too long")
            
            # Increment current_turn
            if current_turn + 1 == len(games[id].players):
                current_turn = 0
            else:
                current_turn += 1
            # Delete old status messages
            status_embed.clear_fields()
            await status_message.delete()
            player_embeds = []
            for msg in player_messages:
                await msg.delete()
            player_messages = []

            status_embed = discord.Embed(title="Ichi Status", description=current_action, color=discord.Color(0xFFFF00))
            status_embed.set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
            status_message = await status_channel.send(embed=status_embed)

            for n in range(len(games[id].players)): # N is the index of the player who's hand is being built
                player_embeds.append(discord.Embed(title="Your Hand", description=current_action, color=discord.Color(0xFFFF00)))
                player_embeds[n].set_thumbnail(url="https://i.imgur.com/HA3FOW2.png")
                player_messages.append(await hand_channels[n].send(embed=player_embeds[n]))
            

        # Notes because this is starting to get out of hand:
        #
        # status_channel is #status
        # status_embed is the embed that gets sent in status
        # status_message is the message containing the embed
        #
        # hand_channels are the #your-hand channels
        # player_embeds are the embeds that get sent into the #your-hand channels
        # player_messages are the messages containing the messsages
        #
        # current_turn is the index of who's turn it is
        # reversed is whether or not the direction of play is reversed
        # top_of_deck is the card that's on the top of the deck
        # top_of_deck_display is a string which contains the the emoji for the card that's on the top of the deck
        # current action should display who's turn it is or what's going on if there's a hold up.
        
        # Clean up the channels when we're done
        await asyncio.sleep(30)
        for n in cleanup:
            await n.delete()

    
    async def pop_card(self, emoji, hand):
        color, number = emoji.name.split("_")
        for n in range(len(hand)):
            if hand[n].color == color and hand[n].number == number:
                card = hand[n]
                hand.pop(n)
                return card, hand
    
    async def get_emoji(self, card):
        return emoji_colors[card.color][card.number]
    
    # Builds the fields for embeds that displays player's cards. 
    # Idk why I'm doing this to myself but public is a list and not a bool. The presence of public means that the message is being built of the #status channel.
    # You're supposed to pass the hand_channel list so that the embed can contain mentions to each hand channel, for mobile player accessability.
    async def hand_display(self, embed: discord.Embed, players: list, reversed: bool, shown_player: int = None, public: list = None):
        for n in range(len(players)): # N is the index of the player who's hand is being build
            arrow_emoji = ""
            if not reversed:
                arrow_emoji = "<a:down:831684356832624672>"
            else:
                arrow_emoji = "<a:up:831684512655867905>"

            if public != None:
                embed.add_field(name=f"{arrow_emoji} {players[n].user.name} ({len(players[n].hand)} Cards)",value=await self.hand_builder(players[n].hand, True) + public[n].mention, inline=False)
            elif n == shown_player:
                embed.add_field(name=f"{arrow_emoji} {players[n].user.name} ({len(players[n].hand)} Cards)",value=await self.hand_builder(players[n].hand, False), inline=False)
            else:
                embed.add_field(name=f"{arrow_emoji} {players[n].user.name} ({len(players[n].hand)} Cards)",value=await self.hand_builder(players[n].hand, True), inline=False)
    
    # Builds the actual string containing card emotes#
    # Hidden = true will display card backs as apposed to card faces
    async def hand_builder(self, hand: list, hidden: bool):
        hand_string = ""
        if hidden:
            for card in hand:
                hand_string = hand_string + "<:back:831717987979493436>"
        else:
            hand.sort(key=self.sort_key)
            for card in hand:
                hand_string = hand_string + emoji_colors[card.color][card.number]
        return hand_string
    
    # Sort key for hand_builder
    def sort_key(self, card):
        return card.value

    # Updates the status message on status and your-hand embeds, pass this after everything else as this will also edit the messages, updating the fields
    async def update_status(self, s_message: discord.Message, s_embed: discord.Embed, s_channel: discord.TextChannel, p_messages: list, p_embeds: list, message: str):
        s_embed.description = message
        await s_message.edit(embed=s_embed)
        for n in range(len(p_embeds)):
            p_embeds[n].description = message + "\n" + s_channel.mention
            await p_messages[n].edit(embed=p_embeds[n])

    #===============#
    #               #
    #   Utilities   #
    #               #
    #===============#

    # Send an error message that deletes itself
    async def error(self, ctx, message, status_message: discord.Message = None):
        if status_message != None:
            await status_message.delete()
        error = await ctx.send(message)
        await asyncio.sleep(3)
        await error.delete()

    #     if arg == "grab":
    #         self.deck = Deck("Single")
    #         await self.deck.initialize()
    #         await ctx.send("You grabbed a deck of cards")
    #         self.lobby.players.append(Player(ctx.author, None, []))
    #     if arg == "shuffle":
    #         await self.deck.shuffle()
    #         await ctx.send("You shuffled the deck")
    #     if arg == "draw":
    #         card = await self.deck.draw()
    #         await ctx.send(f"You drew a... whatever this means: {card}")
    #         self.lobby.players[0].hand.append(card)
    #     if arg == "hand":
    #         await ctx.send(self.lobby.players[0].hand)


# Cards per Deck Settings
# Colors per deck
colors = 4
# Action cards per color
per_color = 2
# Numbers per color (excluding Zeros)
numbers = 9
# Wilds per deck
wilds = 4
# plus fours per deck
plus_fours = 4


@dataclass
class Card:
    color: str
    number: str
    # actionable: bool
    # action: str
    value: int


color_dict = {
    0: "red",
    1: "blue",
    2: "green",
    3: "yellow",
}


class Deck:
    def __init__(self, type):
        self.type = type
        self.cards = []

    async def initialize(self):
        if self.type == "single" or "probability":
            await populate(self.cards)
        elif self.type == "double":
            await populate(self.cards)
            await populate(self.cards)

    async def shuffle(self):
        random.shuffle(self.cards)

    async def draw(self):
        if self.type == "Probability":
            return self.cards[random.randint(0, 107)]
        else:
            card = self.cards.pop()
            return card

    async def add(self, card):
        if self.type != "Probability":
            self.cards.insert(0, card)
        else:
            pass



async def populate(cards):
    value = 0
    # Add the colored cards
    for colorN in range(colors):
        # 1 Zero per color
        cards.append(Card(color_dict[colorN], "0", value))
        value += 1
        for perColorN in range(per_color):
            # Numbered Cards
            for numberN in range(numbers):
                cards.append(Card(color_dict[colorN], str(numberN + 1), value))
                value += 1
        # Separate loop so that action cards aren't vauled higher than number cards
        for perColorN in range(per_color):
            # Reverse
            cards.append(Card(color_dict[colorN], "reverse", value))
            value += 1
            # Skips
            cards.append(Card(color_dict[colorN], "skip", value))
            value += 1
            # +2s
            cards.append(Card(color_dict[colorN], "plus2", value))
            value += 1


    # Add wild cards
    for n in range(wilds):
        cards.append(Card("action", "wild", value))
        value += 1

    # Add +4 cards
    for n in range(plus_fours):
        cards.append(Card("action", "plus4", value))
        value += 1




def setup(bot):
    bot.add_cog(Uno(bot))