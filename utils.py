import re
import markovify
import pronouncing
from textstat.textstat import textstat


def generateMarkovChain(filename):
    corpus = ""
    with open(str(filename)) as fileObject:
        text = fileObject.read()
        for line in text.split("\n"):
            if line != "":
                if line[-1] not in "!?.;)":
                    corpus += line + ". "
    text_model = markovify.Text(corpus)
    neural_lyrics = ""
    neural_last_words = []
    while len(neural_lyrics.split("\n")) < (len(text.split("\n"))) / 2:
        neural_line = (str(text_model.make_sentence())[:-1])
        last_word = neural_line.split(" ")[-1]
        if neural_last_words.count(
                last_word) < 2:
            neural_lyrics += neural_line
            neural_lyrics += ("\n")
        neural_last_words.append(last_word)
    return neural_lyrics


def countSyllablesWord(word):
    return textstat.syllable_count(word)


def countSyllablesSentence(sentence):
    count = 0
    for word in sentence.split(" "):
        count += countSyllablesWord(word)
    return count


def most_common(listItem):
    return max(set(listItem), key=listItem.count)


def remove_duplicate_items(seq):
    dupset = set()
    dupset_add = dupset.add
    return [x for x in seq if not (x in dupset or dupset_add(x))]


def getRhymes(lyrics):
    rhyme_master_list = []
    print("Alright, building the list of all the rhymes - here are the words that have to be taken into account;")
    for letter in lyrics:
        word = re.sub(r"\W+", '', letter.split(" ")[-1]).lower()
        rhymeList = pronouncing.rhymes(word)
        rhymeList = [x.encode('UTF8') for x in rhymeList]
        rhymeListends = []
        for i in rhymeList:
            rhymeListends.append(i[-2:])
        try:
            rhymescheme = most_common(rhymeList)
        except Exception:
            rhymescheme = word[-2:]
        rhyme_master_list.append(rhymescheme)
    rhyme_master_list = remove_duplicate_items(rhyme_master_list)
    return rhyme_master_list


def determine_rhyme(sentence):
    word = re.sub(r"\W+", '', sentence.split(" ")[-1]).lower()
    rhymeslist = pronouncing.rhymes(word)
    rhymeslist = [x.encode('UTF8') for x in rhymeslist]
    rhymeslistends = []
    for i in rhymeslist:
        rhymeslistends.append(i[-2:])
    try:
        rhymescheme = most_common(rhymeslistends)
    except Exception:
        rhymescheme = word[-2:]
    return rhymescheme


def rhyme_list_generator(lyrics, songdict, all_possible_rhymes):
    for i in lyrics:
        if i != "":
            try:
                songdict.append(
                    [str(i), int(countSyllablesSentence(str(i))), all_possible_rhymes.index(determine_rhyme(i))])
            except Exception:
                print 'Nope'


def formatbar(bar, songdict, all_possible_rhymes, lyricsused, song):
    for i in songdict:
        if abs(i[1] - int(bar[0] * 20)) < 2 and i[2] == int((bar[1]) * len(all_possible_rhymes)):
            if str(i[0]) not in lyricsused and str(i[0]) not in lyrics_used_in_song(song):
                lyricsused.append(str(i[0]))


def writesong(start, net, songdict, all_possible_rhymes, lyricsused, song):
    song = [start]
    while len(song) < 100:
        song.append(net.activate(song[-1]))

    for i in range(0, 100):
        formatbar([song[i][0], song[i][1]], songdict, all_possible_rhymes, lyricsused, song)
        formatbar([song[i][2], song[i][3]], songdict, all_possible_rhymes, lyricsused, song)
    if len(lyricsused) > 3:
        return lyricsused
    else:
        return []


def lyrics_used_in_song(song):
    used = []
    for line in song:
        if line != "":
            used.append(line)
    return used



