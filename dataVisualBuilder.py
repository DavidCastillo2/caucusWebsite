import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time as time
from db import 
matplotlib inline
plt.style.use('ggplot')


def createGraph():
    # acceptable colors
    colors = ['green', 'yellow', 'pink', 'brown']

    # get database
    db = get_db()
    cursor = db.cursor()

    # get data from candidates table
    names = []
    votes = []
    for row in cursor.execute('SELECT * FROM candidate'):
        canName = row['name']
        canVotes = row['numVotes']
        names.append(canName)
        votes.append(canVotes)

    # make matplot graph
    x = np.arange(len(names))
    width = 0.35

    # configure bargraph settings
    fig, ax = plt.subplots()
    rects = ax.bar(x, votes, width, label="Candidates", color=colors)

    # configure graph labels
    ax.set_ylabel('Votes')
    ax.set_title('Votes per Candidate')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylim(ymin=0)


    # populate the rectangles with correct information
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height), 
                    xy=(rect.get_x() + rect.get_width()/2, height),
                    xytext=(0,3), # 3 points verticle offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # tie it all together and save as an image
    fig.tight_layout()
    #plt.show() # Shows created graph, comment out when runnning server side
    # create unique name to avoid cache problems
    filename = "static/images/graph" + str(time.time()) + '.png'
    plt.savefig(filename)
    return filename

