import requests
import sqlite3
import pyquery
import sys
import time

db = sqlite3.connect('gelbooru.db')

def log(text):
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	message = '{} | {}\n'.format(timestamp, text)
	
	with open('log.txt', 'a') as log:
		log.write(message)
	print(message, end='')

def post(no):
	url = 'http://gelbooru.com/index.php?page=post&s=view&id={}'.format(no)
	r = requests.get(url)
	r.raise_for_status()

	html = r.text
	dom = pyquery.PyQuery(html)
	
	# Check for deleted posts. Fetch those elements, and before anything else,
	# check if they are None: if so, the post has been deleted.
	tags = dom('textarea#tags').text()
	url = dom('img#image').attr('src') or dom('source').attr('src')

	if url is None:
		log('post #{} has been deleted'.format(no))
		return None
	else:
		# Process those only if the post actually exists.
		thumb_url = dom('a[href^="http://iqdb.org/?url="]').attr('href').split('=')[1]
		blob = requests.get(url).content
		thumb = requests.get(thumb_url).content

	log('fetched post #{}'.format(no))
	return {
		'no': no,
		'tags': tags,
		'url': url, # images / videos
		'thumb': thumb,
		'blob': blob,
	}

def store(post):
	db.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)',
		(post['no'], post['tags'], post['url'], post['thumb'], post['blob']))
	db.commit()
	log('stored post #{}'.format(post['no']))

start = int(sys.argv[1])
end = 3200000
for no in range(start, end):
	p = post(no)
	if p is None:
		continue
	else:
		store(p)
	time.sleep(0.5) # try not to get b& :^)
