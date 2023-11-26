import re
from nltk.stem import PorterStemmer

def normalizeTag(top_tags=None, artist="", track="", n=3):
    '''
    Given a list of (tag, count) pairs for a song that can be retrieved 
    using last.fm api, normalize the tags so they are meaningful. Inspired 
    by https://archives.ismir.net/ismir2007/paper/000525.pdf, page 3.

    Input:
    1) top_tags: a list of (tag, count) tuples
    2) artist: a string representing the artist's name
    3) track: a string representing the track's name,
    the track and artist should come in pairs
    4) n: the number of "most descriptive" tags after normalization

    Output:
    A list of size n with (tag, count) pairs that are "most descriptive"
    '''
    if not top_tags:
        return []
    
    # First filter
    idx = 0 # Keep track of idx in original tags list
    filtered = []
    for tag, count in top_tags:
        if tag.lower() != artist.lower() and tag.lower() != track.lower():
            filtered.append((tag, count, idx))
        idx += 1

    # Stemming
    stemmer = PorterStemmer()
    filtered = [(re.sub(r'[^a-zA-Z0-9]', '', stemmer.stem(tag.lower())), count, idx) for tag, count, idx in filtered]
    # Remove duplicate
    unique_normalized_tags = {}
    seen_normalized_tags = set()

    for tag, count, idx in filtered:
        if tag not in seen_normalized_tags:
            unique_normalized_tags[tag] = (count, idx)
            seen_normalized_tags.add(tag)

    # Calculate the threshold for removing tags
    tag_counts = sum([tup[0] for tup in unique_normalized_tags.values()])
    threshold = tag_counts * 0.1

    # Remove tags applied to less than threshold
    normalized = {tag: tup for tag, tup in unique_normalized_tags.items() if tup[0] >= threshold}
    # Retrieve original tags from the top tags list
    norm_original = []
    for tag, (count, idx) in normalized.items():
        if len(top_tags[idx][0].title()) <= 30 and len(top_tags[idx][0].title().encode('utf-8')) <= len(top_tags[idx][0].title()):
            norm_original.append((top_tags[idx][0].title(), top_tags[idx][1]))
    
    return norm_original[:n]

def main():
    print("Hello World!")
    artist = "Lady Gaga"
    track = "Poker Face"
    tags = [("pop", 100),
            ("dance", 99),
            ("Lady Gaga", 88),
            ("electronic", 48),
            ("party", 39),
            ("female vocalists", 22),
            ("female vocalist", 15),
            ("poker face", 16),
            ("electropop", 10),
            ("sexy", 9),
            ("catchy", 7),
            ("00s", 7),
            ("2009", 5),
            ("addictive", 4),
            ("Disco", 3),
            ("love at first listen", 3)]
    filtered = normalizeTag(tags, artist, track)
    print(filtered)

    artist = "Pink Floyd"
    track = "High Hopes"
    tags = [("Progressive rock", 100),
            ("Psychedelic Rock", 60),
            ("classic rock", 59),
            ("Pink Floyd", 51),
            ("psychedelic", 15),
            ("Masterpiece", 12),
            ("beautiful", 11),
            ("art rock", 11),
            ("british", 9),
            ("memories", 3),
            ("melancholy", 5),
            ("70s", 3)]
    filtered = normalizeTag(tags, artist, track)
    print(filtered)


if __name__ == "__main__":
    main()
