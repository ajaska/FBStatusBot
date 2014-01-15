import api
import markov_model
from chatterbotapi import ChatterBotFactory, ChatterBotType

bot, me = True, False
factory = ChatterBotFactory()

class User(object):
    def __init__(self, access_token, uid):
        self.generator = self.messageGenerator(access_token)
        self.name = api.getFirstName(access_token)
        self.uid = uniqueid

        self.last_message = 'Hi'
        self.last_turn = bot

    def generateMessage(self):
        name = "CleverBot" if bot else self.name
        message = self.generator()
        return "{name}: {message}".format(name=name, message=message)
    
    def messageGenerator(self, access_token):
        me = User.generateStatusMessageGenerator(access_token)
        bot = User.generateBotMessageGenerator()
        def generatorWrapper():
            if self.last_turn == bot:
                message = me(self.last_message)
            else:
                message = bot(self.last_message)
            self.last_message = message
            self.last_turn = not self.last_turn
            return message
        return generatorWrapper
        
    def generateStatusMessageGenerator(access_token):
        statuses = api.getAllStatuses(access_token)
        markov = markov_model.generateMarkovMap(statuses)
        raw_generator = lambda: markov_model.generateStatus(markov, statuses)
        return lambda last_message: markov_model.makeSimilarStatus(
                                                 last_message, raw_generator)
        
    def generateBotMessageGenerator():
        session = factory.create(ChatterBotType.CLEVERBOT).create_session()
        return lambda last_message: session.think(last_message)


