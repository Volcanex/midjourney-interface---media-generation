The image_bot_gui is probably the only file useful to anyone else. It's quite handy to use when working with mid-journey, it's essentially a fake api. 

I think it goes against the terms of service actually.

The template.env file should be filled in with the details you have and then saved as a .env file.

The image_bot_gui file uses the following two 'bots', the prompting bot is actually just your computer running a selenium controlled chrome instance and interacting with the discord chat.

Discord bot:

DISCORD_TOKEN: The token for your Discord bot, you should add this to the server that you want to work in. 
IMG_GEN_BOT_ID: The user id of that discord bot.
TEXT_CHANNEL_NAME: The name of the text channel in which the bot will send messages.

Prompting bot:

DISCORD_EMAIL: The email address associated with your Discord account.
DISCORD_PASSWORD: The password for your Discord account.
DISCORD_CHANNEL_LINK: The link to the Discord channel you want to interact with.

I'm using this for personal reasons, code is provided as is. I don't mind *trying* to help. Good luck!

