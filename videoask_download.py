import requests
import subprocess
import json
from random import randint
import time
import sys

# config
download_location_prefix = "" # leave blank to download to current directory. Must have a trailing slash	

# calls the VideoAsk API to download all of the videos for a given question
# skips audio answers for now
# TODO: also handle audio answers
def downloadQuestion(questionID, questionNumber, token):
	print(f'requesting data for question {questionID}')

	result = subprocess.run([
		'curl', '--location', '-g', '--request', 'GET', f'https://api.videoask.com/questions/{questionID}/answers', '--header', f'Authorization: Bearer {token}'
		], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

	print(result.stderr)
	# print(result.stdout)

	if ("error" in result.stdout):
		print ("skipping because of an error")
		return

	questionDict = json.loads(result.stdout)


	# loop through answers to this question
	counter = 1
	for item in questionDict['results']:

		# if we don't know their name, we need a unique placeholder to avoid overwriting
		if ('contact_name' in item):
			name = item['contact_name']
		else:
			name = str(randint(1000, 9999)) 

		# skip if it isn't a media answer
		if ('media_url' in item):
			if (item['media_type'] == "video"):

				print(f'Downloading {name}')

				# download the file
				r = requests.get(item['media_url'], allow_redirects=True) 
				# save it to disk
				open(f'{download_location_prefix}{name}_{questionID}_{counter}.mp4', 'wb').write(r.content)

		counter += 1
		time.sleep(0.3) # avoid tripping the rate limiter


if __name__ == "__main__":

	print(len(sys.argv))
	if (len(sys.argv) != 3):
		print("Error: you need to pass in two args: the form ID, and the API token.")
		quit()

	# Note: these tokens expire every 15 minutes, so you pretty much always have to refresh it
	form_id = sys.argv[1]
	token = sys.argv[2]

	print("retrieving the form data")
	# grab the form
	form = subprocess.run([
		'curl', '--location', '-g', '--request', 'GET', f'https://api.videoask.com/forms/{form_id}', '--header', f'Authorization: Bearer {token}'
		], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

	print(form.stderr)
	# print(form)
	formDict = json.loads(form.stdout)

	# loop through the questions in the form
	questionNumber = 1
	for question in formDict['questions']:
		print ("question " + question['question_id'])

		# call downloadQuestion with this question
		downloadQuestion(question['question_id'], questionNumber, token)
		questionNumber += 1
		time.sleep(0.3) # avoid tripping the rate limiter

