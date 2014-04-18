#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 
import sys, webbrowser
from hn import HN

def utf8_convert(original):
	workOn = original.replace(u"â€™", "'")
	workOn = workOn.replace(u"â€“", "-")
	workOn = workOn.replace(u"â€œ", '"')
	workOn = workOn.replace(u"â€", '"')
	workOn = workOn.replace(u'â„ƒ', "C")
	workOn = workOn.replace(u'â€™', "'")
	workOn = workOn.replace(u'\u2014', " ")
	return workOn

hn = HN()
if len(sys.argv) == 1:
	print "Not enough arguments. Exiting. Try using: "+sys.argv[0]+" help"
	sys.exit(1)

if sys.argv[1].lower() in ("help", "h", "?"):
	print "[*] Usage: "+sys.argv[0]+" <commands>"
	print "[*] Commands: "
	print "[*] help/h/? = show help"
	print "[*] top/t <amount> = view top stories. Additional argument: sort (points/name/rank), default is by rank."
	print "[*] comment/cm <index> <amount> = view top comments from a story. Additional argument: firstlevel (f/all), default is all."
	print "[*] open/o <index> = open the story in a web browser."

elif sys.argv[1].lower() in ("top", "t"):
	if len(sys.argv) < 3:
		print "[!] Invalid amount of arguments! Exiting."
		sys.exit(1)
	if not sys.argv[2].isdigit():
		print "[!] Amount of stories shown needs to be a number! Exiting."
		sys.exit(1)

	top_iter = hn.get_stories(limit=int(sys.argv[2]))
	stories = list(top_iter)[:int(sys.argv[2])]
	for index, story in enumerate(stories):
		story.index = index
	if len(sys.argv) <= 3:
		sys.argv.append('rank')
	sort_type = sys.argv[3].lower()
	if not (sort_type in ("points", "name", "rank")):
		print "[!] Invalid sorting argument - defaulting to rank."
		sort_type = "rank"

	if sort_type == "rank":
		pass
	elif sort_type == "points":
		tuples, newstories = [], []
		for index, story in enumerate(stories):
			tuples.append((story.points, index))
		for points, index in sorted(tuples, reverse=True):
			newstories.append(stories[index])
		stories = newstories
	elif sort_type == "name":
		tuples, newstories = [], []
		for index, story in enumerate(stories):
			tuples.append((utf8_convert(story.title), index))
		for title, index in sorted(tuples):
			newstories.append(stories[index])
		stories = newstories
	for story in stories:
		try:
			print '|{0}| - [{1}] "{2}" by {3}'.format(story.index, story.points, utf8_convert(story.title), story.submitter)
		except UnicodeEncodeError:
			print "[!] Error loading story by {0} with {1} points due to UnicodeEncodeError. Story's index is {2}".format(story.submitter, story.points, story.index)

elif sys.argv[1].lower() in ("comment", "cm"):
	sort_toplvl = False
	if len(sys.argv) < 4:
		print "[!] Invalid amount of arguments! Exiting."
		sys.exit(1)
	if len(sys.argv) > 4:
		if sys.argv[4].lower() in ("f", "all"):
			sort_toplvl = {'f':True, 'all':False}[sys.argv[4].lower()]
		else:
			print "[!] Invalid firstlevel argument - defaulting to all."
			sort_toplvl = False
	if not (sys.argv[2].isdigit() and sys.argv[3].isdigit()):
		print "[!] Both arguments need to be digits! Exiting."
		sys.exit(1)
	if int(sys.argv[3]) <= 0:
		print "[!] Amount of comments need to be above 0! Exiting."
		sys.exit(1)
	top_iter = hn.get_stories(limit=(int(sys.argv[2])+2))
	stories = list(top_iter)[:int(sys.argv[2])+2]
	story_comments = stories[int(sys.argv[2])]
	story_comments = story_comments.get_comments()
	counter, comment_counter, actual_comments = int(sys.argv[3]), 0, 0
	while True:
		comment = story_comments[comment_counter]
		if not ((sort_toplvl) and (utf8_convert(comment.level != 0))):
			try:
				print u"{3}{0}, {1}: {2}".format(utf8_convert(comment.user), utf8_convert(comment.time_ago), utf8_convert(comment.body), utf8_convert('\t'*comment.level))
			except UnicodeEncodeError:
				print "{0}[!] Error loading comment by {1} {2} due to UnicodeEncodeError. Comment's level is {3}.".format('\t'*comment.level, comment.user, comment.time_ago, comment.level)
			print ('\t'*comment.level)+("*"*50)
			actual_comments += 1
		comment_counter += 1
		if (actual_comments >= counter) or (comment_counter >= (len(story_comments)-1)):
			break
elif sys.argv[1].lower() in ("open", "o"):
	if len(sys.argv) < 3:
		print "[!] Invalid amount of arguments! Exiting."
		sys.exit(1)
	if not sys.argv[2].isdigit():
		print "[!] Index argument need to be digit! Exiting."
		sys.exit(1)
	top_iter = hn.get_stories(limit=(int(sys.argv[2])+2))
	stories = list(top_iter)[:int(sys.argv[2])+2]
	story = stories[int(sys.argv[2])]
	story_url = story.link
	if story_url:
		webbrowser.open(story_url, new=2)
		print "[*] Opened link directing to {0}, titled {1} posted by {2} {3}.".format(story_url, utf8_convert(story.title), story.submitter, story.published_time)
	else:
		print "[*] The specified link is a self-post! The developer doesn't know how to read self posts, so it will be opened in browser for you."
		webbrowser.open(story.comments_link, new=2)
