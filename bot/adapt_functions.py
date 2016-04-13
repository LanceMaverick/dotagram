import json
import sys
import logging
from adapt.entity_tagger import EntityTagger
from adapt.tools.text.tokenizer import EnglishTokenizer
from adapt.tools.text.trie import Trie
from adapt.intent import IntentBuilder
from adapt.parser import Parser
from adapt.engine import IntentDeterminationEngine

tokenizer = EnglishTokenizer()
trie = Trie()
tagger = EntityTagger(trie, tokenizer)
parser = Parser(tokenizer, tagger)

#uses the mycroft AI intent parser for some simple ...intent parsing
def skyAdapt():
    engine = IntentDeterminationEngine()

#dota vocabulary

    dota_keywords = [ 'dota', 'dotes', 'dote']
    
    for dk in dota_keywords:
        engine.register_entity(dk, "DotaKeyword")


    happening_keywords = [
            'happening',
            'anyone up for',
            'when is',
            'what time',
            'tonight',
            'this evening?',
            'anyone about for',
            'around',
            'want to',
            'fancy some',
            'playing some',
            'anyone playing'
            ]
    for hk in happening_keywords:
        engine.register_entity(hk, "HappeningKeyword")

    
    dota_query_intent = IntentBuilder("DotaIntent")\
        .require("DotaKeyword")\
        .require("HappeningKeyword")\
        .build()
    
    stack_intent_words = [
            'stack',
            'stacked'
            ]
    for sik in stack_intent_words:
        engine.register_entity(hk, "StackKeyword")
        

    stack_optionals = [
            'are we',
            'do we have a',
            'how many',
            'who\'s playing'
            ]
            
    for osk in stack_optionals:
        engine.register_entity(hk, "StackOptionalKeyword")

    stack_intent = IntentBuilder("StackIntent")\
        .require("StackKeyword")\
        .optionally("StackOptionalKeyword")\
        .build()
    
            
    engine.register_regex_entity("at (?P<Time>.*)")     
    
    new_dota_intent = IntentBuilder("NewDotaIntent")\
        .require("DotaKeyword")\
        .require("Time")\
        .build()
    
    engine.register_intent_parser(dota_query_intent)
    engine.register_intent_parser(stack_intent)
    engine.register_intent_parser(new_dota_intent)
    

    return engine


def intentChecker(engine, confidence_cut, text):
    intents = []
    for intent in engine.determine_intent(text):
        if intent and intent.get('confidence') > confidence_cut:
            intents.append(intent)    
        elif intent and intent.get('confidence') > 0:
            print 'triggered with low confidence:\n',intent.get('confidence'), text
    
        return intents

