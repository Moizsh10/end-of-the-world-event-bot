import threading
import praw
import time

subreddits = ['BotsAndCSS']
flair_list = ["13", "14", "15", "16", "17", "18", "19", "OLD"]
eventText = "The event has started! This post will update about whether or not the subreddit is in \"Lockdown\" or  \"Explore\" modes!!! Happy hunting everyone!!!!"
postID = "kagqlj"
commentRecord = set()
position = 0
numInfections = 0
numCures = 0

# Phrase that activates the bot
keyphrase = "!dapper"
infectPhrase = "!bite"
curePhrase = "!cure"

# Opens the commentRecord file and adds all the ids to the Set
with open("commentRecord.txt", encoding="Latin-1") as file:
    fileLst = file.readlines()
    for line in fileLst:
        commentRecord.add(line.rstrip())


def main():
    # reddit API login
    reddit = praw.Reddit("bot1")
    reddit.validate_on_submit = True

    # This var is a subreddit that the bot is going to be active on
    currentSub = reddit.subreddit(subreddits[position])

    # Loop to run program and switch between Lockdown and Explore
    while True:
        # Activates lockdown
        lockdownOn = True
        lockdown(reddit)
        time.sleep(60)
        # Activates the explore Thread
        lockdownOn = False
        explore(currentSub, reddit, lockdownOn)
        time.sleep(40)


def botReply(comment):
    """Makes sure comment hasn't been previously replied to"""
    # print(f"Already Replied to comment {comment.id}")
    if keyphrase in comment.body:
        try:
            # Adds comment's ID to the record file to avoid repeated replies
            with open("commentRecord.txt", "a") as file:
                file.write(f"{comment.id}\n")
                # print(f"Added a new comment ID: {comment.id}")

            # Updates the commentRecord Set
            with open("commentRecord.txt", encoding="Latin-1") as file:
                fileLst = file.readlines()
                for line in fileLst:
                    commentRecord.add(line.rstrip())
                print(f"{commentRecord}")

            # Replies to the comment
            comment.reply(f"You're looking pretty dapper yourself {comment.author}!")
            print("Replied to user!\n")
        except:
            print("Invoked too frequently")
    return


def infect(subreddit, comment, commentParent):
    """Method that infects a user if the requirements of game are met"""
    global numInfections
    authFlair = comment.author_flair_text
    # Makes it so only "infected" users can use !infect
    if authFlair.lower() == "infected":
        try:
            # Adds comment's ID to the record file to avoid repeated replies
            with open("commentRecord.txt", "a") as file:
                file.write(f"{commentParent.id}\n")
                print(f"Added a new comment ID: {commentParent.id}")

            # Updates the commentRecord Set
            with open("commentRecord.txt", encoding="Latin-1") as file:
                fileLst = file.readlines()
                for line in fileLst:
                    commentRecord.add(line.rstrip())
                print(f"{commentRecord}")

            # Changes flair of user that is targeted to the 'infected' flair
            currentAuthor = commentParent.author
            subreddit.flair.set(currentAuthor, css_class="infected")
            print("Changed user flair!\n")
            numInfections = readScore(1)
            numInfections += 1
            recordScore(numInfections, 1)
        except:
            print("Invoked too frequently")
    else:
        print(f"Attacker {comment.id} can't use this command")
    return


def cure(subreddit, comment, commentParent):
    """Method that cures a user if the requirements of game are met"""
    global numCures
    authFlair = comment.author_flair_text
    # Makes it so only "cured" users can use !cure
    if authFlair.lower() == "cured":
        try:
            # Adds comment's ID to the record file to avoid repeated replies
            with open("commentRecord.txt", "a") as file:
                file.write(f"{commentParent.id}\n")
                print(f"Added a new comment ID: {commentParent.id}")

            # Updates the commentRecord Set
            with open("commentRecord.txt", encoding="Latin-1") as file:
                fileLst = file.readlines()
                for line in fileLst:
                    commentRecord.add(line.rstrip())
                print(f"{commentRecord}")

            # Changes flair of user that is targeted to the 'cured' flair
            currentAuthor = commentParent.author
            subreddit.flair.set(currentAuthor, css_class="cured")
            print("Changed user flair!\n")
            numCures = readScore(3)
            numCures += 1
            recordScore(numCures, 3)
        except:
            print("Invoked too frequently")
    else:
        print("Attacker can't use this command")
    return


def changeFlair(comment, subreddit):
    """Checks for key phrases. If phrase is found, it passes to the infect and cure methods"""
    parentComment = comment.parent()

    # Starts process to cure target
    if curePhrase in comment.body:
        if checkFlairs(comment, parentComment):
            try:
                # Cures the target
                cure(subreddit, comment, parentComment)
            except:
                print("Invoked too frequently")
        else:
            # Adds comment's ID to the record file to avoid repeated replies
            with open("commentRecord.txt", "a") as file:
                file.write(f"{parentComment.id}\n")
                print(f"Added a new comment ID: {parentComment.id}")

            # Updates the commentRecord Set
            with open("commentRecord.txt", encoding="Latin-1") as file:
                fileLst = file.readlines()
                for line in fileLst:
                    commentRecord.add(line.rstrip())
                print(f"{commentRecord}")
            print("Error: Same Flair\n")
    # Starts process to infect target
    elif infectPhrase in comment.body:
        if checkFlairs(comment, parentComment):
            try:
                # Infects the target
                infect(subreddit, comment, parentComment)
            except:
                print("Invoked too frequently")
        else:
            # Adds comment's ID to the record file to avoid repeated replies
            with open("commentRecord.txt", "a") as file:
                file.write(f"{parentComment.id}\n")
                print(f"Added a new comment ID: {parentComment.id}")

            # Updates the commentRecord Set
            with open("commentRecord.txt", encoding="Latin-1") as file:
                fileLst = file.readlines()
                for line in fileLst:
                    commentRecord.add(line.rstrip())
                print(f"{commentRecord}")
            print("Error: Same Flair\n")
    return


def checkFlairs(comment, commentParent):
    """Makes sure that users have the appropriate flair to target another user"""
    proceed = False
    targetFlair = commentParent.author_flair_text
    attackerFlair = comment.author_flair_text

    if (targetFlair.lower() == "infected") and (attackerFlair.lower() == "cured"):
        proceed = True
    elif (targetFlair.lower() == "cured") and (attackerFlair.lower() == "infected"):
        proceed = True
    elif (targetFlair.lower() in flair_list) and (attackerFlair.lower() == "cured"):
        proceed = True
    elif (targetFlair.lower() in flair_list) and (attackerFlair.lower() == "infected"):
        proceed = True
    elif (targetFlair.lower() == "infected") and (attackerFlair.lower() == "infected"):
        print("User cannot change their target")
        proceed = False
    elif (targetFlair.lower() == "cured") and (attackerFlair.lower() == "cured"):
        print("User cannot change their target")
        proceed = False
    else:
        proceed = True

    return proceed


def lockdown(redditVar):
    """Puts game/subreddit into "Lockdown." Requires specific post ID"""
    global postID
    global eventText

    currentPost = redditVar.submission(id=postID)
    currentPost.edit(eventText + "\n\nStatus: Lockdown currently active!!!")
    print(f"Lockdown status updated!")


def explore(currentSubreddit, redditVar, status):
    """Puts game/subreddit into "Explore." Requires specific post ID. Gameplay only active during this period"""
    global postID
    global eventText

    currentPost = redditVar.submission(id=postID)
    currentPost.edit(eventText + "\n\nStatus: Explore period currently active!!!")
    print(f"Explore status updated!")

    if not status:
        # Starts a thread to run the game while the main program is sleeping
        gameThread = threading.Thread(target=runGame, args=[currentSubreddit])
        gameThread.start()
        print("Starting Thread")


def readScore(fileLine):
    """Reads score from the score file. Requires the file line you are reading the specific score from"""
    with open("scoreRecord.txt", encoding="Latin-1") as currentfile:
        fileList = currentfile.readlines()
        for i, myLine in enumerate(fileList):
            if i == fileLine:
                score = int(myLine.rstrip())
            else:
                pass
    print(f"Score: {score}")
    return score


def recordScore(score, fileLine):
    """Records the current score to the score file. Requires the file line you are recording the specific score to"""
    with open('scoreRecord.txt', 'r') as currentfile:
        # Read a list of lines into data
        data = currentfile.readlines()

    data[fileLine] = str(score) + "\n"

    with open('scoreRecord.txt', 'w') as currentfile:
        currentfile.writelines(data)

    print("Changed score")


# def post():
#     """Method that makes a post to subreddits"""
#     global subreddits
#     global position
#
#     currentSub = reddit.subreddit(subreddits[position])
#     currentSub.submit(title, selftext="Bismillah. Hello World!")
#
#     print("Successfully posted!")
#     return

def runGame(currentSubreddit):
    """Runs game on the assigned subreddit."""
    for newComment in currentSubreddit.stream.comments():
        changeFlair(newComment, currentSubreddit)
        print(f"Infection Count: {numInfections}")
        print(f"Cure Count: {numCures}")


if __name__ == "__main__":
    main()
