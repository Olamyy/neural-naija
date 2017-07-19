import os
import random
import ast
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.tools.xml.networkreader import NetworkReader
from config import word_by_word, epoch, training
import click
from utils import *


def savenetwork(net, rhymelist, epoch):
    os.mkdir(str(epoch))
    r = open(str(epoch) + '/rhymelist', 'w')
    r.write(str(rhymelist))
    # n = open(str(epoch)) + '/network.xml', 'w'
    NetworkWriter.writeToFile(net, str(epoch) + "/network.xml")


def opennetwork(epoch):
    r = open(str(epoch) + '/rhymelist', 'r')
    rhymelist = ast.literal_eval(str(r.read()))
    net = NetworkReader.readFrom(str(epoch) + "/network.xml")
    return net, rhymelist


@click.command
@click.option('--word_by_word', default=word_by_word, help='# if zero, the program will write using existing lines, '
                                                    'if it is 1,a markov chain will be used towrite songs word by word.')
@click.option('--training', default=training, help='training of 0 means you just want to have it write a song - '
                                                'training of 1 will train the network on# the contents of lyrics.txt.')
@click.option('--epoch', default=epoch, help='this is the number of the folder you would '
                                             'like to load (folder contains the trained net and rhymes).')
@click.option('--filename', default=False, help='Lyrics File.')
def run(word_by_word, training, epoch, filename):
    if word_by_word == 0:
        lyrics = open(filename).read().split("\n")
    elif word_by_word == 1:
        lyrics = generateMarkovChain(filename).split("\n")
    song = []
    if training == 1:
        all_possible_rhymes = getRhymes(lyrics)
    elif training == 0:
        all_possible_rhymes = opennetwork(epoch)[1]
        rhymes_in_lyrics = getRhymes(lyrics)
        for rhyme in rhymes_in_lyrics:
            if rhyme not in all_possible_rhymes:
                all_possible_rhymes.append(rhyme)
        print(all_possible_rhymes)
    
    if training == 1:
        net = buildNetwork(4, 8, 8, 8, 8, 8, 8, 8, 8, 4, recurrent=True, hiddenclass=TanhLayer)
        t = BackpropTrainer(net, learningrate=0.05, momentum=0.5, verbose=True)
    
    if training == 0:
        songdict = []
        rhyme_list_generator(lyrics, songdict, all_possible_rhymes)
        net = opennetwork(epoch)[0]
    t = BackpropTrainer(net, learningrate=0.01, momentum=0.5, verbose=True)
        
    if training == 1:
        songdict = []
        rhyme_list_generator(lyrics, songdict, all_possible_rhymes)
        ds = SupervisedDataSet(4, 4)    
        for i in songdict[:-3]:
            if i != "" and songdict[songdict.index(i) + 1] != "" and songdict[songdict.index(i) + 2] != "" and songdict[
                        songdict.index(i) + 3] != "":
                twobars = [i[1], i[2], songdict[songdict.index(i) + 1][1], songdict[songdict.index(i) + 1][2],
                           songdict[songdict.index(i) + 2][1], songdict[songdict.index(i) + 2][2],
                           songdict[songdict.index(i) + 3][1], songdict[songdict.index(i) + 3][2]]
    
                ds.addSample((twobars[0] / float(20), int(twobars[1]) / float(len(all_possible_rhymes)),
                              twobars[2] / float(20), int(twobars[3]) / float(len(all_possible_rhymes))), (
                             twobars[4] / float(20), int(twobars[5]) / float(len(all_possible_rhymes)),
                             twobars[6] / float(20), int(twobars[7]) / float(len(all_possible_rhymes))))
        print(ds)
    
    lyricsused = []
    
    trainingcount = 0
    
    final_song = open("song.txt", "r+")
    if training == 0:
        while len(song) < len(lyrics) / 3 and len(song) < 50:
            verse = writesong([(random.choice(range(1, 20))) / 20.0,
                               (random.choice(range(1, len(all_possible_rhymes)))) / float(len(all_possible_rhymes)),
                               (random.choice(range(1, 20))) / 20.0,
                               (random.choice(range(1, len(all_possible_rhymes)))) / float(len(all_possible_rhymes))],
                              net, songdict, all_possible_rhymes, lyricsused, song)
            if len(verse) > 3:  # this number can be adjusted - usually the short verses it generates are low quality.
                for line in lyricsused:
                    final_song.write(str(line) + "\n")
    
                    # actually write the line to the song
                    song.append(line)
                final_song.write("\n...\n")
                print("Just wrote a verse to the file... - " + str(lyricsused))
                lyricsused = []
    
    if training == 1:
        while True:
            epochs_per_iteration = 100
            trainingcount += epochs_per_iteration
            t.trainOnDataset(ds, epochs_per_iteration)
            print("just wrote " + str(trainingcount) + "/" + "...")
            savenetwork(net, all_possible_rhymes, trainingcount)

if __name__ == '__main__':
    run()
