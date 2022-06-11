from requests_html import HTMLSession
import pandas as pd

s = HTMLSession()

def get_data(url):
	r = s.get(url)
	data = []
	cont = r.html.find('div.by_year')
	for item in cont:
		try:
			ti = item.find('h3', first=True).text.replace('The Nobel Prize in ', '')
			au = item.find('p', first=True).text.split('“')[-2].strip()
			para = item.find('p', first=True).text.split('“')[-1].replace('”', '')
			data.append([ti, au, para])
		except:
			pass

	return data

def save_data(data):
	df = pd.DataFrame(data, columns=['Departments', 'Authors', 'Inventions'])
	df.to_csv('nobel1.csv')


def main():
	url = 'https://www.nobelprize.org/prizes/lists/all-nobel-prizes/'
	save_data(get_data(url))


if __name__ == '__main__':
	main()