import random

user_words = {"hello", "house", "beach", "word"}
songs = {
    0: list(set("i know that the spades are the swords of a soldier. there are so many words in here!".split(" "))),
    1: list(set("this is another song with the coolest word in it".split(" "))),
}
recommendations = [1]


def main_handler():
    rec_length = len(recommendations)
    if rec_length == 0:
        raise RuntimeError("no recommendations")

    index = 0

    found = False
    suggested_word = None
    suggested_song = None

    while not found and index < rec_length:
        song_index = recommendations[index]
        index += 1
        song_words = set(songs[song_index])
        print(song_words)

        common_words = song_words & user_words

        if len(common_words) > 0:
            suggested_word = random.choice(list(common_words))
            suggested_song = song_index
            found = True

    if not found:
        raise RuntimeError("Not found any common words")

    return suggested_song, suggested_word


def lambda_handler(event, context):
    pass
