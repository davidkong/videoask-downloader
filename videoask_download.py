import requests
import subprocess
import json
from random import randint
import time

# Note: these tokens expire every 15 minutes, so you pretty much always have to refresh it

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UTkJRamhFUmpZd05VRXlRakpFUkRGRk5rSXpPRGc0T0RZMlFqWTNSamd3TURoRVFUVTROZyJ9.eyJodHRwczovL3ZpZGVvYXNrLmNvbS9sb2dpbnNfY291bnQiOjI1LCJpc3MiOiJodHRwczovL2F1dGgudmlkZW9hc2suY29tLyIsInN1YiI6ImF1dGgwfDYwNjM3YmIyM2U4ZTJhMDA3MGE3OTg0MSIsImF1ZCI6WyJodHRwczovL2FwaS52aWRlb2Fzay5jb20vIiwiaHR0cHM6Ly92aWRlb2Fzay5ldS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjI0OTE1MjM1LCJleHAiOjE2MjQ5MTYxMzUsImF6cCI6InAzTW0zOGpSaWRlaFNNTU9BOTdsVHZKMjdQQ25uR0poIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9.Cv34B0LBEEpUnpyW6NwJUVFzKLHLxTtjt_r47AXsbsWtAVhg26RM_8KKjnAfz2M6-uq-U2tXo4zGwzizGTzKZyahKD6KkqJvBmmfFeOFNv4h0bbUW7Dgx5xqo3nMAfjsMq-iNelUYUp2vG8bCKZNe9cF586uTe3EdMtd_kbtB6BQImf8GuYuKmGuFvK24bsw3xspSz8HzqHn9XPmCTFom2qmjxl2NrrxdZuTh4ll4m8ggWrWAQKst76jSs6LN4HwXJkpQgl2enT1cGHLl2MNqxNXzFpo4pxhswiKejtWA6_qajMPtQBNw7mW3lOA9G7YXuEsjLweE1GfiNVKHcd61g"
form_id = "93acb357-9b95-43db-95b0-acd47aa44a3f"


# calls the VideoAsk API to download all of the videos for a given question
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

	jsonResult = json.loads(result.stdout)

	counter = 1

	for item in jsonResult['results']:
		if ('contact_name' in item):
			name = item['contact_name']
		else:
			name = str(randint(1000, 9999))

		if ('media_url' in item):
			if (item['media_type'] == "video"):
				url = item['media_url']

				print(f'Downloading {name}')

				# download the file
				r = requests.get(url, allow_redirects=True) 
				open(f'{name}_{questionID}_{counter}.mp4', 'wb').write(r.content)

		counter += 1
		time.sleep(0.2)


if __name__ == "__main__":

	print("retrieving the form data")
	# grab the form
	form = subprocess.run([
		'curl', '--location', '-g', '--request', 'GET', f'https://api.videoask.com/forms/{form_id}', '--header', f'Authorization: Bearer {token}'
		], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

	print(form.stderr)
	# print(form)
	jsonResult = json.loads(form.stdout)

	# loop through the questions in the form
	questionNumber = 1
	for question in jsonResult['questions']:
		print ("question " + question['question_id'])

		# call downloadQuestion with this question
		downloadQuestion(question['question_id'], questionNumber, token)
		questionNumber += 1
		time.sleep(0.2)

