import requests
import csv
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

class Entry(object):
    def __init__(self, fn, tn, ti, aot, tr, tv, ts, aom, ai, mt, mi, jd, m, rs, p, b, l, d, g, o):
        self.Forum_Name = fn
        self.Thread_Name = tn
        self.Thread_ID = ti
        self.Author_of_Thread = aot
        self.Thread_Replies = tr
        self.Thread_Views = tv
        self.Time_Stamp = ts
        self.Author_of_Message = aom
        self.Author_ID = ai
        self.Message_Text = mt
        self.Message_ID = mi
        self.Joined_Date = jd
        self.Messages = m
        self.Reaction_Score = rs
        self.Points = p
        self.Birthday = b
        self.Location = l
        self.Driving = d
        self.Gender = g
        self.Occupation = o


class Entries(object):
    def __init__(self):
        self.EntryList = []

    def addEntry(self, e):
        self.EntryList.append(e)




def processThread(link, threadNum, employee_writer):
    print(link)
    response = session.get(
        link, verify=True)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Initializing the variables
    fn = ""
    tn = ""
    ti = ""
    aot = ""
    tr = ""
    tv = ""
    ts = ""
    aom = ""
    ai = ""
    mt = ""
    mi = ""
    jd = ""
    m = ""
    rs = ""
    p = ""
    b = ""
    l = ""
    d = ""
    g = ""
    o = ""

    ThreadEntryList = Entries()
    AuthorMap = {}
    MessageCount = 1
    authorId = 1
    # This is the Forum Name
    forum_name = soup.find(
        class_='p-body-header')

    forum_name = "Advice"
    # if forum_name is not None:
    #   forum_name = forum_name.text

    # This will be Thread Title
    thread_title = soup.find(
        class_='p-title')

    thread_title = thread_title.find('h1').text

    # This is the thread_id
    # To be done
    thread_id = threadNum

    # This is the thread author
    thread_author = soup.find(
        class_='p-description')
    thread_author = thread_author.find('a').text
    # Now we go through all the messages and print the data we already have for all of them
    listofMessages = soup.findAll(
        class_='message message--post js-post js-inlineModContainer')

    # print(listofMessages[0])

    for i in range(listofMessages.__len__()):
        fn = forum_name
        tn = thread_title
        ti = thread_id
        aot = thread_author

        timestamp = listofMessages[i].find('time')['title']
        ts = timestamp

        author_of_message = listofMessages[i].find("a").find('img')
        aom = author_of_message
        if author_of_message is not None:
            author_of_message = author_of_message['alt']
            aom = author_of_message

        if author_of_message in AuthorMap:
            ai = AuthorMap[author_of_message]
        else:
            AuthorMap[author_of_message] = authorId
            ai = authorId
            authorId += 1

        messageClass = listofMessages[i].find(
            class_='bbWrapper')

        wrapperText = messageClass.text

        message_text = wrapperText
        mt = message_text

        mi = MessageCount
        MessageCount += 1

        userProfile = listofMessages[i].find("a")

        memberLink = "https://uberpeople.net/" + userProfile['href']

        member_response = session.get(
            memberLink, verify=True)

        member_soup = BeautifulSoup(member_response.text, 'html.parser')

        # print(member_soup)

        member_header = member_soup.find(
            class_='memberHeader')

        if member_header is not None:

            member_stats = member_header.find(
                class_='memberHeader-stats')

            member_blurbs = member_header.findAll(
                class_='memberHeader-blurb')

            # print(member_blurbs)

            join_date = member_blurbs[1].find('dd').text
            jd = join_date

            titles = member_stats.findAll('dd')

            numMessages = titles[0].text.strip()
            m = numMessages

            reaction_score = titles[1].text.strip()
            rs = reaction_score

            points = titles[2].text.strip()
            p = points

            # Driving
            aboutLink = memberLink + "/about"
            about_response = session.get(
                aboutLink, verify=True)

            about_soup = BeautifulSoup(about_response.text, 'html.parser')

            AttributeMap = {'Location': "", 'Driving': "", 'Gender': "", 'Occupation': "", 'Birthday': ""}
            dgo = about_soup.findAll('dl')
            for tag in dgo:
                value = tag.find('dd').text.strip()
                titleKey = tag.find('dt').text.strip()
                AttributeMap[titleKey] = value

            l = AttributeMap['Location']
            d = AttributeMap['Driving']
            g = AttributeMap['Gender']
            o = AttributeMap['Occupation']
            b = AttributeMap['Birthday']

            AttributeMap['Location'] = ""
            AttributeMap['Driving'] = ""
            AttributeMap['Gender'] = ""
            AttributeMap['Occupation'] = ""
            AttributeMap['Birthday'] = ""
        else:
            jd = "Private"
            m = "Private"
            rs = "Private"
            p = "Private"
            l = "Private"
            d = "Private"
            g = "Private"
            o = "Private"
            b = "Private"

        entry = Entry(fn, tn, ti, aot, tr, tv, ts, aom, ai, mt, mi, jd, m, rs, p, b, l, d, g, o)
        ThreadEntryList.addEntry(entry)

    for e in ThreadEntryList.EntryList:
        employee_writer.writerow(
                [e.Forum_Name, e.Thread_Name, e.Thread_ID, e.Author_of_Thread, e.Time_Stamp, e.Author_of_Message,
                 e.Author_ID,
                 e.Message_Text, e.Message_ID, e.Joined_Date,
                 e.Messages, e.Reaction_Score, e.Points, e.Birthday, e.Location, e.Driving,
                 e.Gender, e.Occupation])


def processPage(pageLink, employee_writer):
    allAdviceThreadsRequest = session.get(
        pageLink, verify=True)

    AdviceSoup = BeautifulSoup(allAdviceThreadsRequest.text, 'html.parser')
    allAdviceThreads = AdviceSoup.findAll(
        class_='structItem-cell structItem-cell--main')

    allLinks = []

    for thread in allAdviceThreads:
        title = thread.find(
            class_='structItem-title')

        minor = thread.find(
            class_='structItem-minor')

        jumps = minor.find(
            class_='structItem-pageJump')

        link = title.find('a')['href']
        totalString = 'https://www.uberpeople.net' + link

        allLinks.append(totalString)

        if jumps is not None:
            j = jumps.findAll('a')
            if j is not None:
                for sec in j:
                    totalLink = 'https://www.uberpeople.net' + sec['href']
                    allLinks.append(totalLink)

    # This will process the link base
    threadNum = 1
    for link in allLinks:
        print("Thread " + str(threadNum) + " of " + str(allLinks.__len__()))
        processThread(link, threadNum, employee_writer)
        threadNum += 1


def main():


    with open('employee_file.csv', mode='a', encoding="utf-8", newline='') as employee_file:
        employee_writer = csv.writer(
            employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(
            ['Forum_Name', 'Thread_Name', 'Thread_ID', 'Author_Of_Thread', 'Time_Stamp', 'Author_of_Message',
             'Author_ID', 'Message_Text', 'Message_ID', 'Joined_Date',
             'Messages', 'Reaction_Score', 'Points', 'Birthday', 'Location', 'Driving',
             'Gender', 'Occupation'])
        for i in range(50):
            print("Page " + str(i + 1))
            pageLink = "https://uberpeople.net/forums/Tips/" + "page-" + str(i + 1)
            processPage(pageLink, employee_writer)


main()
