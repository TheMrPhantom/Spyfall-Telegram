import PythonTelegramWraper.bot as bot
import config
import random as rdm

def start(update, context):
    message="Welcome,\n"
    message+="Type /newgroup for a new game"
    context.bot.sendMessage(bot.chatID(update), message)

def newgroup(update, context):
    grpName = update.message.text.split()[1]
    bot.modifyUser(bot.chatID(update), [grpName,[bot.chatID(update)]])
    context.bot.sendMessage(bot.chatID(update), "New group '"+grpName+"' has been created")

def join(update, context):
    grpName = update.message.text.split()[1]
    
    for u in bot.getUserDataOriginal().values():
        if u[0]==grpName:
            u[1].append(bot.chatID(update))
            bot.modifyUser(u[1][0], u)
            context.bot.sendMessage(bot.chatID(update), "Joined group")
            break

def begin(update, context):
    usrData=bot.user(bot.chatID(update))
    if usrData is None:
        context.bot.sendMessage(bot.chatID(update), "You are not leader of a group yet")
        return
    playerCount=len(usrData[1])
    
    areaIdx=rdm.randint(0,len(config.areas)-1)
    
    area=config.areas[areaIdx]
    
    jobs=[]
    for i in range(0,playerCount-1):
        jobs.append("<b> 📍 Ort: </b>\n   "+str(area[0])+"\n\n<b>💼 Beruf:</b>\n   "+area[i+1])
        
    jobs.append("<b> 📍 Ort: </b>\n   "+"<i>Unbekannt</i>"+"\n\n<b>💼 Beruf:</b>\n   🕵️ Spion")
    rdm.shuffle(jobs)

    for idx, val in enumerate(usrData[1]):
        bot.sendMessage(val, jobs[idx],isHTML=True)

def delgroup(update, context):
    bot.removeUser(bot.chatID(update))

bot.addBotCommand("start", start)
bot.addBotCommand("newgroup", newgroup)
bot.addBotCommand("join", join)
bot.addBotCommand("begin", begin)
bot.addBotCommand("delgroup", delgroup)

bot.startBot()