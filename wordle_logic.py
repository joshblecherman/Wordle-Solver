letters = "abcdefghijklmnopqrstuvwxyz"

class Letter:
    def __init__(self, letter, possible_indices):
        if possible_indices is None:
            possible_indices = list(range(5))
        self.letter = letter
        self.indices = possible_indices
        self.count = 1  # smallest number of self.letter in the word (cannot be > than len(self.indices))

        # True if we know that there must be exactly count # of occurrences
        # False if there must be at least count # of occurrences
        self.count_is_max = False

    def match(self, word):
        matches = []
        for index in self.indices:
            if word[index] == self.letter:
                matches.append(index)
        return matches

    def remove(self, index):
        if index not in self.indices:
            return
        self.indices.remove(index)

    def split(self, index):
        self.remove(index)
        self.count -= 1
        return Letter(self.letter, [index])

    def in_word(self):
        return len(self) > 0

    def __len__(self):  # the length is the number of positions it can occupy
        return len(self.indices)

    def __eq__(self, other):
        return self.letter == other.letter

    def __str__(self):
        return "%s: %s, %s, %s" % (self.letter, self.indices, self.count, self.count_is_max)


# all letters that have been tested are added to the letter group
# if the letter does not exist in the answer (equivalent to gray in wordle), letter.indices = []
# if the letter is in the answer but in a different spot (yellow), len(letter.indices) > 1
# if the letter is in the answer in the correct spot (green), len(letter.indices) == 1
class LetterGroup:
    def __init__(self, last_guess=None, from_colors=None):
        global letters
        letters = "abcdefghijklmnopqrstuvwxyz"
        self.letters = []  # contains Letter types

        self.known = []  # indices with known letters

        self.last_guess = ""
        if last_guess is not None:
            self.last_guess = last_guess

        if from_colors is not None:  # from_colors is of form (**5 letter long string**, **list of colors for guess**)
            self.construct_from_guess(from_colors)

    def construct_from_guess(self, from_colors):
        for index, (letter, color) in enumerate(zip(from_colors[0], from_colors[1])):
            if color == "G":
                self.add(Letter(letter, [index]))
                self.known.append(index)

        for index, (letter, color) in enumerate(zip(from_colors[0], from_colors[1])):
            if color == "Y":
                self.add(Letter(letter, [ind for ind in range(5) if ind != index and ind not in self.known]))

        for index, (letter, color) in enumerate(zip(from_colors[0], from_colors[1])):
            if color == "B":
                self.add(Letter(letter, []))

    def add(self, letter):  # letter is of type Letter
        self.letters.append(letter)

    def remove(self, letter):
        self.letters.remove(letter)

    # should be called after every update
    # will check for indices that cannot be occupied and fix them
    def fix(self):
        for letter in self.letters:
            new_indices = letter.indices[:]
            if len(letter) > 1:
                for index in self.known:
                    if index in letter.indices:
                        new_indices.remove(index)
                letter.indices = new_indices

        new_letters = []
        for letter in self.letters:
            if letter.count > 0:
                new_letters.append(letter)
        self.letters = new_letters

    def match(self, word):
        for letter in self.letters:
            does_match = letter.match(word)
            # if a gray word appears in word -> not a match
            if not letter.in_word() and letter.letter in word:
                return False

            # if a letter appears more than letter.count times and letter.count is the exact # of occurrences
            elif letter.in_word() and letter.count_is_max and len(does_match) > letter.count:
                return False

            # if a letter appears less than the required number of times
            elif letter.in_word() and len(does_match) < letter.count:
                return False

            # indices where the letter cannot be
            if len(letter) > 1:
                other_inds = [ind for ind in range(5) if ind not in letter.indices]
                matches = self.find(letter.letter)
                greens = [match for match in matches if len(match) == 1]
                for ind in other_inds:
                    if word[ind] == letter.letter:
                        cnt = 0
                        for green in greens:
                            if ind == green.indices[0]:
                                return True
                        return False
        return True

    def find(self, let):
        matches = []
        for letter in self.letters:
            if let == letter.letter:
                matches.append(letter)
        return matches

    # takes a new word group as input and updates self.letters with the new info
    def update(self, new_group):

        if len(self.letters) == 0:  # if update is called on an empty letter group, simply copy the passed LG and return
            self.letters = new_group.letters
            self.known = new_group.known
            return

        for letter in new_group.letters:
            # check for new green letters first to update self.known
            if len(letter) == 1:

                # if it is totally new, just add it
                if letter not in self.letters:
                    self.add(letter)
                    self.known.append(letter.indices[0])

                else:
                    matches = self.find(letter.letter)
                    yellows = [match for match in matches if len(match) > 1]

                    # 1. there is a yellow in matches
                    #      the green must be in one of the yellow indices, so split the yellow letter
                    if len(yellows) == 1:  # max size of yellows is 1
                        green = yellows[0].split(letter.indices[0])
                        self.add(green)
                        self.known.append(green.indices[0])

                    # 2. there is no yellow in matches
                    #      only add the letter if the index is different
                    else:
                        if letter.indices[0] not in self.known:
                            self.add(letter)
                            self.known.append(letter.indices[0])

        for letter in new_group.letters:

            # check for new gray letters
            if len(letter) == 0:  # letters not in answer
                if letter not in self.letters:  # letter not already added to self
                    self.add(letter)

            # check for yellow letters
            elif len(letter) > 1:

                if letter not in self.letters:
                    self.add(letter)

                # if the letter is in self.letters
                else:
                    matches = self.find(letter.letter)
                    yellows = [match for match in matches if len(match) > 1]
                    greens = [match for match in matches if len(match) == 1]

                    if len(greens) > 0 and len(yellows) == 0:  # there are greens and no yellows
                        if letter.count - len(matches) > 0:
                            new_letter = Letter(letter.letter, letter.indices)
                            new_letter.count = letter.count - len(matches)
                            self.add(new_letter)

                    elif len(greens) == 0 and len(yellows) == 1:  # there are no greens and a yellow
                        yellow = yellows[0]
                        new_indices = [ind for ind in yellow.indices if ind in letter.indices]
                        yellow.indices = new_indices
                        yellow.count = max(yellow.count, letter.count)
                        yellow.count_is_max = yellow.count_is_max or letter.count_is_max

                    elif len(greens) > 0 and len(yellows) == 1:  # there is at least one green and a yellow
                        yellow = yellows[0]
                        greens = [match for match in matches if len(match) == 1]
                        yellow.indices = [ind for ind in yellow.indices if ind in letter.indices]
                        if yellow.count + len(greens) < letter.count:  # we know that there must be more letters
                            yellow.count = letter.count
                        yellow.count_is_max = yellow.count_is_max or letter.count_is_max
        self.fix()

    def __str__(self):
        return "\n".join([str(letter) for letter in self.letters])


def guess(guess, answer):
    new_group = LetterGroup(guess)

    guess = [(guess[index], index) for index in range(5)]
    answer = [(answer[index], index) for index in range(5)]

    # check for greens
    greens = [let for let in guess if let in answer]
    for green in greens:
        guess.remove(green)
        answer.remove(green)
        new_group.known.append(green[1])
        new_group.add(Letter(green[0], [green[1]]))

    # check if a duplicate green was found that doesn't match anything in answer
    for letter in new_group.letters:
        if letter.letter in [let[0] for let in guess] and letter.letter not in [let[0] for let in answer]:
            letter.count_is_max = True

    # check for yellow
    guess_yellows = [let for let in guess if let[0] in [let[0] for let in answer]]
    answer_yellows = [let for let in answer if let[0] in [let[0] for let in guess]]
    for let in guess_yellows:
        guess.remove(let)
        matches = new_group.find(let[0])  # get all greens/yellows that have already been matched
        yellows = [match for match in matches if len(match) > 1]
        indices = [i for i in range(5) if i != let[1] and i not in new_group.known]

        # yellows should have a max size of 1
        if len(yellows) > 0 and let[0] in [a_yellow[0] for a_yellow in answer_yellows]:
            match = yellows[0]
            new_indices = [index for index in match.indices if index in indices]
            match.indices = new_indices
            match.count += 1

        #  check if another yellow was found that does not match anything in answer
        elif len(yellows) > 0:  # yellows should have a max size of 1
            for match in yellows:
                match.count_is_max = True
                match.indices.remove(let[1])
        else:
            new_group.add(Letter(let[0], indices))

        for a_let in answer_yellows:
            if a_let[0] == let[0]:
                answer_yellows.remove(a_let)
                break

    # add remaining grays
    for let in guess:
        absent = Letter(let[0], [])
        if absent not in new_group.letters:
            new_group.add(absent)

    return new_group


def get_guess_colors(letter_group):  # should only be used on a letter_group that has one guesses worth of data
    result = [None for _ in range(5)]
    for letter in letter_group.last_guess:
        matches = letter_group.find(letter)
        greens = [match for match in matches if len(match) == 1]
        for green in greens:
            result[green.indices[0]] = "G"  # found a green

    for letter in letter_group.last_guess:
        matches = letter_group.find(letter)
        yellows = [match for match in matches if len(match) > 1]
        for yellow in yellows:
            indices = [i for i in range(5) if i not in yellow.indices and result[i] is None]
            for index in indices:
                result[index] = "Y"   # found a yellow

    for i in range(len(result)):
        if result[i] is None:
            result[i] = "B"

    return result


def get_words(letter_group = None):
    path = "words.txt"
    with open(path) as words:
        words = words.read().splitlines()
    if not letter_group:
        return words

    else:
        return [word for word in words if letter_group.match(word)]




