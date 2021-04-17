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


from discord.ext import commands
import discord

from dataclasses import dataclass, field
import random
import asyncio


@dataclass
class Player:
    user: discord.User
    hand: list = field(default_factory=list)


@dataclass
class GameTracker:
    # type: str
    players: list = field(default_factory=list)
    kick_list: list = field(default_factory=list)
    deck = None
    s_channel: discord.TextChannel = None
    h_channels: list = field(default_factory=list)
    reversed: bool = False
    current_turn: int = -1
    settings: dict = field(default_factory=dict)
    skipping: bool = False


@dataclass
class Card:
    color: str
    number: str
    value: int


# Number emoji dictionaries used for the lobby system
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
    "wild": "<:red_wild:832339513988481024>",
    "plus4": "<:red_plus4:832498256700637224>",
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
    "wild": "<:blue_wild:832339514063323167>",
    "plus4": "<:blue_plus4:832498256399171615>",
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
    "wild": "<:green_wild:832339513639829517>",
    "plus4": "<:green_plus4:832498256822665236>",
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
    "wild": "<:yellow_wild:832339513791479870>",
    "plus4": "<:yellow_plus4:832498256563011586>",
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
                # games[id] = GameTracker([], [], [], None, [], False, -1)
                games[id] = GameTracker()
                break
        # Otherwise get the id for a new lobby
        if id == None:
            id = len(games)
            # games.append(GameTracker([], [], [], None, [], False, -1))
            games.append(GameTracker())

        games[id].settings = {
            "decktype": "single",
            "bluffing": True,
        }

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
        games[id].players.append(Player(ctx.author))

        # Lobby Embed
        embed = discord.Embed(
            title="**Ichi Game Lobby**",
            description=await self.player_list(games[id].players),
            color=discord.Color(0xFFFF00),
        )
        embed.set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
        embed.set_footer(
            text="✅ Join.\n🆗 Everybody's in.\n🔨 Kick.\n🔀 Shuffle players.\n⚙️ Settings.\n🛑 Close."
        )

        lobby_message = await ctx.send(embed=embed)
        await lobby_message.add_reaction("✅")
        await lobby_message.add_reaction("🆗")
        await lobby_message.add_reaction("🔨")
        await lobby_message.add_reaction("🔀")
        await lobby_message.add_reaction("⚙️")
        await lobby_message.add_reaction("🛑")

        # Listen for people reacting to join the lobby
        def check(reaction, user):
            return (
                str(reaction.emoji) == "✅"
                or (
                    user == ctx.author
                    and str(reaction.emoji) in ["🆗", "🛑", "🔨", "🔀", "⚙️"]
                )
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
                    joinable = True
                    for player in games[id].players:
                        if player.user == user:
                            joinable = False
                    
                    if joinable:
                        games[id].players.append(Player(user))
                        embed.description = await self.player_list(games[id].players)
                        await lobby_message.edit(embed=embed)

                # If the lobby is full
                elif (
                    reaction.emoji == "✅"
                    and len(games[id].players) == 8
                    and user != ctx.author
                ):
                    await error(ctx, "Sorry, this lobby is full!")

                # If everyone is in
                elif reaction.emoji == "🆗":
                    if len(games[id].players) >= 2:
                        await error(ctx, "Starting the game!")
                        await lobby_message.delete()
                        waiting = False
                        await self.start_game(ctx, id)
                    else:
                        await error(ctx, "You can't play a game by yourself!")

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
                    await error(
                        ctx,
                        "You can't kick yourself, wait for someone to join before you try that",
                    )

                elif reaction.emoji == "⚙️":
                    await self.settings_gui(ctx, id)

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
            descript = (
                descript + f"\n{num_emoji[n]} {games[id].players[n].user.mention}"
            )

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
                offender = games[id].players[emoji_num[reaction.emoji]].user
                # Add the user to the kick list
                games[id].kick_list.append(offender)
                # Remove the user from the lobby
                games[id].players.pop(emoji_num[reaction.emoji])
                # Close the GUI
                await error(ctx, f"Kicking {offender.mention}...", kick_message)
                return offender
            elif reaction.emoji == "🛑":
                await error(ctx, "Closing kick menu...", kick_message)
                return None

        except asyncio.TimeoutError:
            await error(
                ctx,
                "Host took to long to kick a user, closing the menu...",
                kick_message,
            )
            return None

    async def settings_gui(self, ctx, id):
        embed = discord.Embed(title="**Settings Menu**", description="Loading...")
        settings_message = await ctx.send(embed=embed)

        setting = True
        while setting:
            deck = None
            if games[id].settings["decktype"] == "single":
                deck = "Single"
            elif games[id].settings["decktype"] == "double":
                deck = "Double"
            elif games[id].settings["decktype"] == "probability":
                deck = "Probability"

            bluffing = None
            if games[id].settings["bluffing"]:
                bluffing = "On"
            else:
                bluffing = "Off"

            embed.description = f"""<:back:831717987979493436> Deck Type: {deck}
            <:action_plus4:831629944055398431> Bluffing: {bluffing}"""
            await settings_message.edit(embed=embed)

            await settings_message.add_reaction("<:back:831717987979493436>")
            await settings_message.add_reaction("<:action_plus4:831629944055398431>")
            await settings_message.add_reaction("🛑")

            def settings_check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji)
                    in [
                        "<:back:831717987979493436>",
                        "<:action_plus4:831629944055398431>",
                        "🛑",
                    ]
                ) and reaction.message == settings_message

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60, check=settings_check
                )
                if reaction.emoji == "🛑":
                    await settings_message.delete()
                    setting = False

                elif reaction.emoji.name == "back":
                    deck_embed = discord.Embed(
                        title="**Deck Settings**",
                        description="""Which deck would you like the play with?

                        1️⃣: Single deck
                        2️⃣: Double deck""",
                        # ♾️: Probability Deck""",
                    )
                    deck_message = await ctx.send(embed=deck_embed)

                    await deck_message.add_reaction("1️⃣")
                    await deck_message.add_reaction("2️⃣")
                    # await deck_message.add_reaction("♾️")
                    await deck_message.add_reaction("🛑")

                    def deck_check(reaction, user):
                        return (
                            user == ctx.author
                            # and str(reaction.emoji) in ["1️⃣", "2️⃣", "♾️", "🛑"]
                            and str(reaction.emoji) in ["1️⃣", "2️⃣", "🛑"]
                        ) and reaction.message == deck_message

                    try:
                        reaction, user = await self.bot.wait_for(
                            "reaction_add", timeout=60, check=deck_check
                        )

                        if reaction.emoji == "1️⃣":
                            games[id].settings["decktype"] = "single"
                        elif reaction.emoji == "2️⃣":
                            games[id].settings["decktype"] = "double"
                        # elif reaction.emoji == "♾️":
                        #     games[id].settings["decktype"] = "probability"
                        elif reaction.emoji == "🛑":
                            pass
                        
                        await deck_message.delete()

                    except asyncio.TimeoutError:
                        await error(
                            ctx,
                            "Host took to long to change the settings, closing the menu...",
                            deck_message,
                        )

                elif reaction.emoji.name == "action_plus4":
                    bluff_embed = discord.Embed(
                        title="**Deck Settings**",
                        description="Should bluffing be enabled?",
                    )
                    bluff_message = await ctx.send(embed=bluff_embed)

                    await bluff_message.add_reaction("<:YAY:824942140999598151>")
                    await bluff_message.add_reaction("<:NAY:824942147992158218>")
                    await bluff_message.add_reaction("🛑")

                    def bluff_check(reaction, user):
                        return (
                            user == ctx.author
                            and str(reaction.emoji)
                            in [
                                "<:YAY:824942140999598151>",
                                "<:NAY:824942147992158218>",
                                "♾️",
                                "🛑",
                            ]
                        ) and reaction.message == bluff_message

                    try:
                        reaction, user = await self.bot.wait_for(
                            "reaction_add", timeout=60, check=bluff_check
                        )

                        if reaction.emoji.name == "YAY":
                            games[id].settings["bluffing"] = True
                        elif reaction.emoji.name == "NAY":
                            games[id].settings["bluffing"] = False
                        elif reaction.emoji == "🛑":
                            pass
                        
                        await bluff_message.delete()

                    except asyncio.TimeoutError:
                        await error(
                            ctx,
                            "Host took to long to change the settings, closing the menu...",
                            bluff_message,
                        )

            except asyncio.TimeoutError:
                await error(
                    ctx,
                    "Host took to long to change the settings, closing the menu...",
                    settings_message,
                )
                setting = False

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

    # ==============================#
    #                              #
    #    Actually play the game    #
    #                              #
    # ==============================#

    async def start_game(self, ctx, id):

        # START CHANNEL, PERM, AND MESSAGE SETUP

        cleanup = []
        # Create the category for the game
        overwrites = {
            avo_cult.default_role: discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            ),
            self.bot.user: discord.PermissionOverwrite(send_messages=True),
        }
        game_category = await avo_cult.create_category(
            f"Ichi Game (ID: {id})", overwrites=overwrites, position=0
        )
        cleanup.append(game_category)

        # Create a status channel for everyone
        games[id].s_channel = await game_category.create_text_channel(
            "status", overwrites=overwrites
        )
        cleanup.append(games[id].s_channel)
        await ctx.send(f"Everyone head to {games[id].s_channel.mention}!!!")

        # Create a hand channel for each player
        for player in games[id].players:
            overwrites = {
                avo_cult.default_role: discord.PermissionOverwrite(read_messages=False),
                self.bot.user: discord.PermissionOverwrite(read_messages=True),
                player.user: discord.PermissionOverwrite(read_messages=True),
            }
            player_channel = await game_category.create_text_channel(
                "your-hand", overwrites=overwrites
            )
            games[id].h_channels.append(player_channel)
            await player_channel.send(
                f"{player.user.mention} This is your personal channel for this ichi game."
            )
        cleanup = cleanup + games[id].h_channels

        # Create the GUI for #status and #your-hand
        current_action = "The game will begin in 10 seconds..."

        status_embed = discord.Embed(
            title="Ichi Status",
            description=current_action,
            color=discord.Color(0xFFFF00),
        )
        status_embed.set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
        status_message = await games[id].s_channel.send(embed=status_embed)

        player_messages = []
        player_embeds = []
        for n in range(
            len(games[id].players)
        ):  # N is the index of the player who's hand is being built
            player_embeds.append(
                discord.Embed(
                    title="Your Hand",
                    description=current_action,
                    color=discord.Color(0xFFFF00),
                )
            )
            player_embeds[n].set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
            player_messages.append(
                await games[id].h_channels[n].send(embed=player_embeds[n])
            )

        await asyncio.sleep(10)

        # FINISH CHANNEL, PERM, AND MESSAGE SETUP

        # START PRELIMINARY GAME STUFF

        # Initialize the deck and embed
        current_action = "Grabbing a deck..."
        await update_status(
            status_message,
            status_embed,
            player_messages,
            player_embeds,
            current_action,
        )

        games[id].deck = Deck(games[id].settings["decktype"])
        await games[id].deck.initialize()

        # Shuffle the deck, update the message because why not
        current_action = "Shuffling the deck..."
        await update_status(
            status_message,
            status_embed,
            player_messages,
            player_embeds,
            current_action,
        )

        await games[id].deck.shuffle()

        # Deal the cards, update the message because why not
        current_action = "Dealing cards..."
        await update_status(
            status_message,
            status_embed,
            player_messages,
            player_embeds,
            current_action,
        )

        for player in games[id].players:
            for n in range(7):
                card = await games[id].deck.draw()
                player.hand.append(card)
                # for player in games[id].players:

        # FINISH PRELIMINARY GAME STUFF

        # games[id].current_turn = 0  # The index of the player who's turn it is
        # games[id].reversed = False

        # Check the first card for an action
        card = None
        checking_deck = True
        while checking_deck:
            top_of_deck = games[id].deck.cards[0]
            if top_of_deck.number == "plus4":
                games[id].deck.cards.pop(0)
                games[id].deck.cards.append(top_of_deck)
                continue
            card = top_of_deck
            checking_deck = False

        if card.number == "wild":
            color_message = await post(
                id=id,
                title="Action",
                description="is picking a new color",
                current_turn=await next_player_index(id),
                type=0,
                private_description="are picking a new color.\nReact with a color.",
            )
            await color_message.add_reaction("<:red_wild:832339513988481024>")
            await color_message.add_reaction("<:blue_wild:832339514063323167>")
            await color_message.add_reaction("<:green_wild:832339513639829517>")
            await color_message.add_reaction("<:yellow_wild:832339513791479870>")

            async def check(reaction, user):
                return user == games[id].players[await next_player_index(id)].user and str(
                    reaction.emoji
                ) in [
                    "<:red_wild:832339513988481024>",
                    "<:blue_wild:832339514063323167>",
                    "<:green_wild:832339513639829517>",
                    "<:yellow_wild:832339513791479870>",
                ]

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=await check
                )
                if reaction.emoji.name == "red_wild":
                    card.color = "red"
                elif reaction.emoji.name == "blue_wild":
                    card.color = "blue"
                elif reaction.emoji.name == "green_wild":
                    card.color = "green"
                elif reaction.emoji.name == "yellow_wild":
                    card.color = "yellow"

            except asyncio.TimeoutError:
                card.color = "red"

            games[id].deck.cards.pop(0)
            games[id].deck.cards.insert(0, card)

            await post(
                id=id,
                title="Action",
                description=f"picked {card.color}. {await get_emoji(card)}",
                current_turn=next_player_index(id),
                type=0,
            )

            games[id].current_turn = 0

        if card.number == "plus2":
            await post(
                id=id,
                title="Action",
                description=f"The first card was a +2.",
                no_name=True,
                type=1,
            )
            await self.draw(id, await next_player_index(id), True)
            await self.draw(id, await next_player_index(id), True)
            games[id].current_turn = 1

        if card.number == "reverse":
            if not (len(games[id].players) == 2):
                games[id].reversed = not games[id].reversed
                await post(
                    id=id,
                    title="Action",
                    description="The first card was a reverse.",
                    no_name=True,
                    type=1,
                )
            else:
                await post(
                    id=id,
                    title="Action",
                    description=f"The first card was a reverse. But there's only two players.\nSkipped {games[id].players[await next_player_index(id)].user.display_name}'s turn",
                    no_name=True,
                    type=1,
                )
                games[id].current_turn = 1

        if card.number == "skip":
            await post(
                id=id,
                title="Action",
                description=f"The first card was a skip. Skipped {games[id].players[await next_player_index(id)].user.display_name}'s turn",
                no_name=True,
                type=1,
            )
            games[id].current_turn = 1

        while True:
            current_action = (
                f"{games[id].players[games[id].current_turn].user.display_name}'s turn"
            )
            top_of_deck = games[id].deck.cards[0]
            top_of_deck_display = f"Top of deck: {await get_emoji(top_of_deck)}"

            await hand_display(
                status_embed,
                games[id].players,
                games[id].reversed,
                public=games[id].h_channels,
            )
            # Make and send the embeds that go in each "your-hand" channel
            for n in range(
                len(games[id].players)
            ):  # N is the index of the player who's hand is being built
                await hand_display(
                    player_embeds[n],
                    games[id].players,
                    games[id].reversed,
                    shown_player=n,
                )

            await update_status(
                status_message,
                status_embed,
                player_messages,
                player_embeds,
                current_action + "\n" + top_of_deck_display,
            )

            # Get playable cards from the player who's turn it is
            turn_notif = (
                await games[id]
                .h_channels[games[id].current_turn]
                .send(
                    f"{games[id].players[games[id].current_turn].user.mention} it's your turn."
                )
            )
            playable_cards = []
            playable_emojis = []
            for card in games[id].players[games[id].current_turn].hand:
                if (
                    card.color == "action"
                    or top_of_deck.color == "action"
                    or card.color == top_of_deck.color
                    or card.number == top_of_deck.number
                ):
                    playable_cards.append(card)
                    playable_emojis.append(await get_emoji(card))

            # Automatically draw a card and end the turn if there are no playable cards and if it's playable, ask if they want to play it
            if playable_cards == []:
                await self.draw(id, games[id].current_turn, False, top_of_deck)

            # Otherwise let the player play a card
            else:
                # React with the playable cards to the Your Hand embed 832339513639829516
                await player_messages[games[id].current_turn].add_reaction(
                    "<:draw:832339513639829516>"
                )
                for emoji in playable_emojis:
                    await player_messages[games[id].current_turn].add_reaction(emoji)

                def check(reaction, user):
                    return user == games[id].players[
                        games[id].current_turn
                    ].user and str(reaction.emoji) in playable_emojis + [
                        "<:draw:832339513639829516>"
                    ]

                try:
                    # Wait for the reaction
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=60.0, check=check
                    )
                    if reaction.emoji.name == "draw":
                        await self.draw(id, games[id].current_turn, False, top_of_deck)
                    else:
                        # Remove the selected card from the hand
                        card, hand = await pop_card(
                            reaction.emoji.name,
                            games[id].players[games[id].current_turn].hand,
                        )
                        games[id].players[games[id].current_turn].hand = hand
                        # Play the card
                        await self.play_card(id, card, games[id].current_turn)

                except asyncio.TimeoutError:
                    # card, hand = await pop_card(playable_emojis[0], games[id].players[games[id].current_turn].hand)
                    # TODO: Draw a card
                    await self.draw(id, games[id].current_turn, False, top_of_deck)

            # Check if someone just won
            # print(games[id].players[current_turn].hand)
            if games[id].players[games[id].current_turn].hand == []:
                current_action = f"{games[id].players[games[id].current_turn].user.display_name} has won!"
                break

            # Increment current_turn
            # if games[id].deck.cards[0].number in ["skip", "plus2", "plus4"]:
            #     games[id].current_turn = await next_player_index(id)
            #     games[id].current_turn = await next_player_index(id)
            # elif games[id].deck.cards[0].number == "reverse" and (
            #     len(games[id].players) == 2
            # ):
            if games[id].skipping:
                games[id].current_turn = await next_player_index(id)
                games[id].current_turn = await next_player_index(id)
                games[id].skipping = False
            else:
                games[id].current_turn = await next_player_index(id)

            # Delete old messages
            await turn_notif.delete()
            status_embed.clear_fields()
            await status_message.delete()
            player_embeds = []
            for msg in player_messages:
                await msg.delete()
            player_messages = []

            # Make new messages
            status_embed = discord.Embed(
                title="Ichi Status",
                description="Loading..",
                color=discord.Color(0xFFFF00),
            )
            status_embed.set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
            status_message = await games[id].s_channel.send(embed=status_embed)

            for n in range(
                len(games[id].players)
            ):  # N is the index of the player who's hand is being built
                player_embeds.append(
                    discord.Embed(
                        title="Your Hand",
                        description="Loading...",
                        color=discord.Color(0xFFFF00),
                    )
                )
                player_embeds[n].set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
                player_messages.append(
                    await games[id].h_channels[n].send(embed=player_embeds[n])
                )

        # Notes because this is starting to get out of hand:
        #
        # games[id].s_channel is #status
        # status_embed is the embed that gets sent in status
        # status_message is the message containing the embed
        #
        # games[id].h_channels are the #your-hand channels
        # player_embeds are the embeds that get sent into the #your-hand channels
        # player_messages are the messages containing the messsages
        #
        # current_turn is the index of who's turn it is
        # reversed is whether or not the direction of play is reversed
        # top_of_deck is the card that's on the top of the deck
        # top_of_deck_display is a string which contains the the emoji for the card that's on the top of the deck
        # current action should display who's turn it is or what's going on if there's a hold up.

        # Clean up the channels when we're done and post results
        embed = discord.Embed(
            title="Results",
            description=f"{current_action}",
            color=discord.Color(0xFFFF00),
        )
        embed.set_thumbnail(url="https://i.imgur.com/iRPiwm3.png")
        await hand_display(
            embed, games[id].players, games[id].reversed, shown_player=-1
        )
        await ctx.send(embed=embed)
        for n in cleanup:
            await n.delete()

    async def draw(
        self,
        id: int,
        current_turn: int,
        action: bool,
        top_of_deck: Card = None,
    ):
        card = await games[id].deck.draw()

        # If the card the player pulled is playable
        if not action and (
            card.color == "action"
            or top_of_deck.color == "action"
            or card.color == top_of_deck.color
            or card.number == top_of_deck.number
        ):
            drew_message = await post(
                id=id,
                title="Draw",
                description="drew a card. <:back:831717987979493436>",
                current_turn=current_turn,
                type=0,
                private_description=f"drew a card. {await get_emoji(card)}\n\n<:play:832339513925042186> Play the card.\n<:keep:832339513786761257> Keep the card.",
            )
            await drew_message.add_reaction("<:play:832339513925042186>")
            await drew_message.add_reaction("<:keep:832339513786761257>")

            def check(reaction, user):
                return user == games[id].players[current_turn].user and str(
                    reaction.emoji
                ) in [
                    "<:play:832339513925042186>",
                    "<:keep:832339513786761257>",
                ]

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
                # If the player can play, play the card and send the message
                if reaction.emoji.name == "play":
                    # Add the card to the deck
                    await games[id].deck.add(card)
                    await self.play_card(id, card, current_turn)

                # If the player reacts with keep
                else:
                    games[id].players[current_turn].hand.append(card)

            except asyncio.TimeoutError:
                games[id].players[current_turn].hand.append(card)

        else:
            await post(
                id=id,
                title="Draw",
                description="drew a card. <:back:831717987979493436>",
                current_turn=current_turn,
                type=0,
                private_description=f"drew a card. {await get_emoji(card)}",
            )
            games[id].players[current_turn].hand.append(card)

    # Play a card
    # Presense of current_turn indicates that this is a normal circumstance and that post isn't handled elsewhere
    async def play_card(self, id: int, card, current_turn: int = None):

        if current_turn != None:
            await post(
                id=id,
                title="Play",
                description=f"played a card. {await get_emoji(card)}",
                current_turn=current_turn,
                type=0,
            )

        if card.number == "reverse":
            if not (len(games[id].players) == 2):
                games[id].reversed = not games[id].reversed
                await post(
                    id=id,
                    title="Action",
                    description="played a reverse.",
                    current_turn=current_turn,
                    type=0,
                )
            else:
                games[id].skipping = True
                await post(
                    id=id,
                    title="Action",
                    description=f"skipped {games[id].players[await next_player_index(id)].user.display_name}'s turn",
                    current_turn=current_turn,
                    type=0,
                )

        if card.number == "skip":
            games[id].skipping = True
            await post(
                id=id,
                title="Action",
                description=f"skipped {games[id].players[await next_player_index(id)].user.display_name}'s turn",
                current_turn=current_turn,
                type=0,
            )

        if card.number == "plus2":
            games[id].skipping = True
            await self.draw(id, await next_player_index(id), True)
            await self.draw(id, await next_player_index(id), True)

        if card.number == "wild":
            color_message = await post(
                id=id,
                title="Action",
                description="is picking a new color",
                current_turn=current_turn,
                type=0,
                private_description="are picking a new color.\nReact with a color.",
            )
            await color_message.add_reaction("<:red_wild:832339513988481024>")
            await color_message.add_reaction("<:blue_wild:832339514063323167>")
            await color_message.add_reaction("<:green_wild:832339513639829517>")
            await color_message.add_reaction("<:yellow_wild:832339513791479870>")

            def check(reaction, user):
                return user == games[id].players[current_turn].user and str(
                    reaction.emoji
                ) in [
                    "<:red_wild:832339513988481024>",
                    "<:blue_wild:832339514063323167>",
                    "<:green_wild:832339513639829517>",
                    "<:yellow_wild:832339513791479870>",
                ]

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
                if reaction.emoji.name == "red_wild":
                    card.color = "red"
                elif reaction.emoji.name == "blue_wild":
                    card.color = "blue"
                elif reaction.emoji.name == "green_wild":
                    card.color = "green"
                elif reaction.emoji.name == "yellow_wild":
                    card.color = "yellow"

            except asyncio.TimeoutError:
                card.color = "red"

            await post(
                id=id,
                title="Action",
                description=f"picked {card.color}. {await get_emoji(card)}",
                current_turn=current_turn,
                type=0,
            )

        if card.number == "plus4":
            color_message = await post(
                id=id,
                title="Action",
                description="is picking a new color",
                current_turn=current_turn,
                type=0,
                private_description="are picking a new color.\nReact with a color.",
            )
            await color_message.add_reaction("<:red_plus4:832498256700637224>")
            await color_message.add_reaction("<:blue_plus4:832498256399171615>")
            await color_message.add_reaction("<:green_plus4:832498256822665236>")
            await color_message.add_reaction("<:yellow_plus4:832498256563011586>")

            def check(reaction, user):
                return user == games[id].players[current_turn].user and str(
                    reaction.emoji
                ) in [
                    "<:red_plus4:832498256700637224>",
                    "<:blue_plus4:832498256399171615>",
                    "<:green_plus4:832498256822665236>",
                    "<:yellow_plus4:832498256563011586>",
                ]

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
                if reaction.emoji.name == "red_plus4":
                    card.color = "red"
                elif reaction.emoji.name == "blue_plus4":
                    card.color = "blue"
                elif reaction.emoji.name == "green_plus4":
                    card.color = "green"
                elif reaction.emoji.name == "yellow_plus4":
                    card.color = "yellow"

            except asyncio.TimeoutError:
                card.color = "red"

            await post(
                id=id,
                title="Action",
                description=f"picked {card.color}. {await get_emoji(card)}",
                current_turn=current_turn,
                type=0,
            )

            if games[id].settings["bluffing"]:
                bluff_message = await post(
                    id=id,
                    title="Bluff",
                    description=f"Do you want to challenge {games[id].players[current_turn].user.display_name}'s bluff?",
                    current_turn=await next_player_index(id),
                    type=2,
                    no_name=True,
                )

                await bluff_message.add_reaction("<:YAY:824942140999598151>")
                await bluff_message.add_reaction("<:NAY:824942147992158218>")

                def check(reaction, user):
                    return (
                        reaction.message == bluff_message
                        and not user.bot
                        and str(reaction.emoji)
                        in ["<:YAY:824942140999598151>", "<:NAY:824942147992158218>"]
                    )

                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=20.0, check=check
                    )

                    if reaction.emoji.name == "YAY":
                        hand_message = await post(
                            id=id,
                            title="Bluff",
                            description=f"""
                            {games[id].players[current_turn].user.display_name} is showing you his hand\n
                            {await hand_builder(games[id].players[current_turn].hand, False)}
                            """,
                            current_turn=await next_player_index(id),
                            type=2,
                            no_name=True,
                        )
                        await asyncio.sleep(3)
                        await hand_message.delete()

                        bluffing = None
                        for card in games[id].players[current_turn].hand:
                            if card.color == games[id].deck.cards[0].color:
                                if games[id].deck.cards[0].color != "action":
                                    bluffing = True

                        if bluffing:
                            await post(
                                id=id,
                                title="Action",
                                description=f"challendged {games[id].players[current_turn].user.display_name}'s bluff and succeed!",
                                current_turn=await next_player_index(id),
                                type=0,
                            )
                            for n in range(4):
                                await self.draw(id, current_turn, True)
                        else:
                            games[id].skipping = True
                            await post(
                                id=id,
                                title="Action",
                                description=f"challendged {games[id].players[current_turn].user.display_name}'s bluff and failed...",
                                current_turn=await next_player_index(id),
                                type=0,
                            )
                            for n in range(6):
                                await self.draw(id, await next_player_index(id), True)

                    else:
                        games[id].skipping = True
                        for n in range(4):
                            await self.draw(id, await next_player_index(id), True)

                except asyncio.TimeoutError:
                    games[id].skipping = True
                    for n in range(4):
                        await self.draw(id, await next_player_index(id), True)
            else:
                games[id].skipping = True
                for n in range(4):
                    await self.draw(id, await next_player_index(id), True)

        # Add the card to the deck
        await games[id].deck.add(card)


async def next_player_index(id, backwards: bool = False):
    if not backwards:
        if not games[id].reversed:
            if games[id].current_turn + 1 == len(games[id].players):
                return 0
            else:
                return games[id].current_turn + 1
        else:
            if games[id].current_turn - 1 == -1:
                return len(games[id].players) - 1
            else:
                return games[id].current_turn - 1
    else:
        if games[id].reversed:
            if games[id].current_turn + 1 == len(games[id].players):
                return 0
            else:
                return games[id].current_turn + 1
        else:
            if games[id].current_turn - 1 == -1:
                return len(games[id].players) - 1
            else:
                return games[id].current_turn - 1


# After an something happens, post a message in #status and the #your-hand channels
async def post(
    id: int,
    title: str,
    description: str,
    type: int,
    current_turn: int = None,
    no_name: bool = False,
    private_description: str = None,
):
    thumbnail = None
    if no_name:
        name = ""
        thumbnail = "https://i.imgur.com/iRPiwm3.png"
    else:
        name = games[id].players[current_turn].user.display_name + " "
        thumbnail = games[id].players[current_turn].user.avatar_url
    embed = discord.Embed(title=title, description=f"{name}{description}")
    embed.set_thumbnail(url=thumbnail)

    # Send to every hand channel and a unique to current_hand
    if type == 0:
        await games[id].s_channel.send(embed=embed)

        for channel in games[id].h_channels:
            # Exclude the current player's channel in order to send them a personalized message
            if channel == games[id].h_channels[current_turn]:
                pass
            else:
                await channel.send(embed=embed)

        # Send the message to the player's hand channel
        name = "You"
        if private_description != None:
            description = private_description
        embed = discord.Embed(title=title, description=f"{name} {description}")
        embed.set_thumbnail(url=games[id].players[current_turn].user.avatar_url)
        return await games[id].h_channels[current_turn].send(embed=embed)

    # Same for every channel
    elif type == 1:
        await games[id].s_channel.send(embed=embed)

        for channel in games[id].h_channels:
            await channel.send(embed=embed)

    # Only send to a specific user
    elif type == 2:
        for channel in games[id].h_channels:
            if channel == games[id].h_channels[current_turn]:
                return await channel.send(embed=embed)
            else:
                pass


# Find a the card in a hand from given an emoji. Remove the card from that hand and return both the card and the new hand
async def pop_card(emoji, hand):
    color, number = emoji.split("_")
    for n in range(len(hand)):
        if hand[n].color == color and hand[n].number == number:
            card = hand[n]
            hand.pop(n)
            return card, hand


async def get_emoji(card):
    return emoji_colors[card.color][card.number]


# Builds the fields for embeds that displays player's cards.
# Idk why I'm doing this to myself but public is a list and not a bool. The presence of public means that the message is being built of the #status channel.
# You're supposed to pass the hand_channel list so that the embed can contain mentions to each hand channel, for mobile player accessability.
async def hand_display(
    embed: discord.Embed,
    players: list,
    reversed: bool,
    shown_player: int = None,
    public: list = None,
):
    for n in range(
        len(players)
    ):  # N is the index of the player who's hand is being build
        arrow_emoji = ""
        if not reversed:
            arrow_emoji = "<a:down:831684356832624672>"
        else:
            arrow_emoji = "<a:up:831684512655867905>"

        if public != None:
            embed.add_field(
                name=f"{arrow_emoji} {players[n].user.display_name} ({len(players[n].hand)} Cards)",
                value=await hand_builder(players[n].hand, True),
                inline=False,
            )
        elif n == shown_player or shown_player == -1:
            embed.add_field(
                name=f"{arrow_emoji} {players[n].user.display_name} ({len(players[n].hand)} Cards)",
                value=await hand_builder(players[n].hand, False),
                inline=False,
            )
        else:
            embed.add_field(
                name=f"{arrow_emoji} {players[n].user.display_name} ({len(players[n].hand)} Cards)",
                value=await hand_builder(players[n].hand, True),
                inline=False,
            )


# Builds the actual string containing card emotes#
# Hidden = true will display card backs as apposed to card faces
async def hand_builder(hand: list, hidden: bool):
    hand_string = ""
    if hand == []:
        return "Winner"
    elif hidden:
        for card in hand:
            if len(hand_string + "<:back:831717987979493436>") >= 1021:
                hand_string = hand_string + "..."
                break
            else:
                hand_string = hand_string + "<:back:831717987979493436>"
    else:
        hand.sort(key=sort_key)
        for card in hand:
            if len(hand_string + emoji_colors[card.color][card.number]) >= 1021:
                hand_string = hand_string + "..."
                break
            else:
                hand_string = hand_string + emoji_colors[card.color][card.number]
    return hand_string


# Sort key for hand_builder
def sort_key(card):
    return card.value


# Updates the status message on status and your-hand embeds, pass this after everything else as this will also edit the messages, updating the fields
async def update_status(
    s_message: discord.Message,
    s_embed: discord.Embed,
    p_messages: list,
    p_embeds: list,
    message: str,
):
    s_embed.description = message
    await s_message.edit(embed=s_embed)
    for n in range(len(p_embeds)):
        p_embeds[n].description = message
        await p_messages[n].edit(embed=p_embeds[n])

    # ===============#
    #               #
    #   Utilities   #
    #               #
    # ===============#


# Send an error message that deletes itself
async def error(ctx, message, status_message: discord.Message = None):
    if status_message != None:
        await status_message.delete()
    error = await ctx.send(message)
    await asyncio.sleep(3)
    await error.delete()


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
        if self.type == "single":
            await populate(self.cards)
        elif self.type == "double":
            await populate(self.cards)
            await populate(self.cards)
        elif self.type == "probability":
            await populate(self.cards)
            self.cards.insert(0, self.draw())

    async def shuffle(self):
        random.shuffle(self.cards)

    async def draw(self):
        if self.type == "probability":
            return self.cards[random.randint(1, 107)]
        else:
            card = self.cards.pop()
            if card.number == "wild":
                card.color = "action"
            if card.number == "plus4":
                card.color = "action"
            return card

    async def add(self, card):
        if self.type == "probability":
            self.cards[0] = card
        else:
            random.shuffle(self.cards)
            self.cards.insert(0, card)


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
            value -= 9
        value += 9
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
            value -= 3
        value += 3

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