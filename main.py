import PythonTelegramWraper.bot as bot
import config
import random as rdm
import copy

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext.filters import Filters
from telegram.ext import CallbackQueryHandler

startMessage="Welcome,\nType /newgroup _<name>_ for a new game.\nTo join an existing game type /join _<name>_.\nAfter creating a game you can start it by typing /begin   "
notLeaderMessage="You are not leader of a group yet.\nType /start for help"

def start(update, context):
    bot.sendMessage(bot.chatID(update), startMessage)


def newgroup(update, context):
    grpName = update.message.text.split()[1]
    bot.modifyUser(bot.chatID(update), [
                   grpName, [bot.chatID(update)], {"chat_state": 0}])
    context.bot.sendMessage(bot.chatID(
        update), "New group '"+grpName+"' has been created")


def join(update, context):
    grpName = update.message.text.split()[1]

    for u in bot.getUserDataOriginal().values():
        if u[0] == grpName:
            u[1].append(bot.chatID(update))
            bot.modifyUser(u[1][0], u)
            context.bot.sendMessage(bot.chatID(update), "Joined group")
            break


def begin(update, context):
    usrData = bot.user(bot.chatID(update))

    if usrData is None:
        context.bot.sendMessage(bot.chatID(
            update), notLeaderMessage)
        return
    reply_markup = ReplyKeyboardMarkup([["3", "4"], ["5", "6"], ["7", "8"]])
    bot.sendMessage(bot.chatID(update),
                    "How many players are you? (1-8)", rpl_markup=reply_markup)

    usrData[2]["chat_state"] = 1
    bot.modifyUser(bot.chatID(update), usrData)


def delgroup(update, context):
    bot.removeUser(bot.chatID(update))


def locations(update, context):
    locationMsg = "<b> 📍 Orte: </b>\n"
    for idx, loc in enumerate(config.areas):
        locationMsg += str(idx+1)+": "+loc[0]+"\n"
    bot.sendMessage(bot.chatID(update), locationMsg, isHTML=True)


def default(update, context):
    usrData = bot.user(bot.chatID(update))

    if usrData is not None:

        chatState = usrData[2]["chat_state"]

        if chatState == 1:
            try:
                numberInput = update.message.text
                try:
                    numberInput = int(numberInput)
                except:
                    print("Not a number")
                if numberInput > 8 or numberInput < 1:
                    bot.sendMessage(bot.chatID(update),
                                    "Choose between 1 and 8", isHTML=True)
                    return
                usrData[2]["player"] = numberInput
                usrData[2]["chat_state"] = 2
                bot.modifyUser(bot.chatID(update), usrData)

                cats = []
                cats.append(["None"])
                for i in range(0, len(config.areas)):
                    button = config.areas[i][8]["category"]
                    if button is not None:
                        cats.append([button])

                reply_markup = ReplyKeyboardMarkup(cats)
                context.bot.send_message(chat_id=bot.chatID(update),
                                         text="What category you want to play?",
                                         reply_markup=reply_markup)

            except Exception as e:
                print("a")
                bot.sendMessage(bot.chatID(update), str(e))

        elif chatState == 2:
            try:
                #areaIdx = rdm.randint(0, len(config.areas)-1)
                areaIn = update.message.text
                possibleAreas = []

                if areaIn == "None":
                    areaIn = None
                for idx, val in enumerate(config.areas):
                    category = val[8]['category']

                    if category == areaIn:
                        possibleAreas.append(idx)

                reply_markup = ReplyKeyboardRemove()
                context.bot.send_message(chat_id=bot.chatID(
                    update), text="Started game", reply_markup=reply_markup)

                playerInStore = len(usrData[1])
                playerInMessage = int(usrData[2]["player"])
                playerNotRegistered = playerInMessage-playerInStore
                playerNotOnPhone = playerInStore-1
                playerOnPhone = playerNotRegistered+1

                areaIdx = rdm.randint(0, len(possibleAreas)-1)

                area = possibleAreas[areaIdx]
                area = config.areas[area]
                areaIdx = possibleAreas[areaIdx]
                jobs = []
                jobIdx = list(range(1, len(area)-1))
                rdm.shuffle(jobIdx)

                if playerOnPhone < 2:
                    for i in range(0, playerInMessage-1):
                        jobs.append(
                            "<b> 📍 Ort: </b>\n   "+str(area[0])+"\n\n<b>💼 Beruf:</b>\n   "+area[jobIdx.pop(0)])

                    jobs.append("<b> 📍 Ort: </b>\n   "+"<i>Unbekannt</i>" +
                                "\n\n<b>💼 Beruf:</b>\n   🕵️ Spion")
                    rdm.shuffle(jobs)

                    for idx, val in enumerate(usrData[1]):

                        bot.sendMessage(val, jobs[idx], isHTML=True)
                else:
                    rdm.shuffle(jobIdx)
                    for i in range(0, 7-playerInMessage+1):
                        jobIdx.pop(0)

                    jobIdx.append("!")
                    rdm.shuffle(jobIdx)

                    jobIdxPhone = []
                    jobIdxOther = []

                    for i in range(0, playerOnPhone):
                        jobIdxPhone.append(jobIdx[0])
                        jobIdx.pop(0)

                    for i in range(0, playerNotOnPhone):
                        jobIdxOther.append(jobIdx[0])
                        jobIdx.pop(0)

                    for i, chatID in enumerate(usrData[1]):
                        if i == 0:
                            continue
                        idx = jobIdxOther[i-1]
                        if idx == "!":
                            bot.sendMessage(chatID, "<b> 📍 Ort: </b>\n   "+"<i>Unbekannt</i>" +
                                            "\n\n<b>💼 Beruf:</b>\n   🕵️ Spion", isHTML=True)
                        else:
                            bot.sendMessage(chatID, "<b> 📍 Ort: </b>\n   "+"<i>" +
                                            area[0]+"</i>"+"\n\n<b>💼 Beruf:</b>\n   "+area[idx], isHTML=True)

                    callback = ""

                    for i in jobIdxPhone:
                        callback += str(areaIdx)+","+str(i)+"#X#"

                    callback += str(bot.chatID(update))

                    button_list = [
                        InlineKeyboardButton("Next", callback_data=callback)
                    ]

                    reply_markup = InlineKeyboardMarkup(
                        bot.build_menu(button_list, n_cols=1))
                    context.bot.send_message(bot.chatID(
                        update), "Weiter geben", reply_markup=reply_markup)

                chatState = usrData[2]["chat_state"] = 0
                bot.modifyUser(bot.chatID(update), usrData)
            except Exception as e:
                print(e)


def menu_actions(update, context):

    try:
        bot.getBot().delete_message(chat_id=update.effective_chat.id,
                                    message_id=update.effective_message.message_id)
    except Exception as e:
        print(e)

    inp = str(update.callback_query.data).split("#")

    chat = inp[len(inp)-1]

    nextData = inp[0]
    inp.pop(0)

    next = ""
    for a in inp:
        next += a+"#"
    next = next[:len(next)-1]

    if nextData == 'X':
        button_list = [InlineKeyboardButton("Next", callback_data=next)]
        reply_markup = InlineKeyboardMarkup(
            bot.build_menu(button_list, n_cols=1))
        bot.sendMessage(str(chat), "Give the phone to the next player",
                        isHTML=True, rpl_markup=reply_markup)
        return

    reply_markup = None

    if len(inp) > 1:
        loc = nextData.split(",")[0]
        job = nextData.split(",")[1]

        reply_markup = None

        if len(inp) > 2:
            button_list = [InlineKeyboardButton("Next", callback_data=next)]
            reply_markup = InlineKeyboardMarkup(
                bot.build_menu(button_list, n_cols=1))

        if job == "!":
            bot.sendMessage(str(chat), "<b> 📍 Ort: </b>\n   "+"<i>Unbekannt</i>" +
                            "\n\n<b>💼 Beruf:</b>\n   🕵️ Spion", isHTML=True, rpl_markup=reply_markup)
        else:
            bot.sendMessage(str(chat), "<b> 📍 Ort: </b>\n   "+"<i>"+str(config.areas[int(loc)][0])+"</i>"+"\n\n<b>💼 Beruf:</b>\n   "+str(
                config.areas[int(loc)][int(job)]), isHTML=True, rpl_markup=reply_markup)


def buttonTest(update, context):
    try:
        print("dd")
    except Exception as e:
        print(e)


bot.addBotCommand("start", start)
bot.addBotCommand("newgroup", newgroup)
bot.addBotCommand("join", join)
bot.addBotCommand("begin", begin)
bot.addBotCommand("delgroup", delgroup)
bot.addBotCommand("locations", locations)
bot.addBotCommand("t", buttonTest)
bot.addBotMessage(Filters.all, default)
bot.botBackend.dispatcher.add_handler(CallbackQueryHandler(menu_actions))

bot.startBot()
