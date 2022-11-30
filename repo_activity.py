#!/usr/bin/python

import sys
import argparse
import requests as req
import time
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


parser = argparse.ArgumentParser(description = "Analyze repository activity...", add_help=True)
parser.add_argument('-p', '--package', type=str, help="package name")
parser.add_argument('-r', '--registry', type=str, help="registry")
parser.add_argument('-a', '--owner', type=str, help="owner")
args = parser.parse_args()

if len(sys.argv) < 5:
	print("More arguments required!")
token = "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"
#token = "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"
headers = {"Authorization": "token" + token}
#headers={}


class Scoring:
	def __init__(self, author, registry, github):
		self.author = author
		self.registry = registry
		self.github = github
	
	""" Author """
	# Author's age
	def author_age(self):
		if not self.author:
			return 0
		updated = parse(self.author['updated'])
		created = parse(self.author['created'])
		# half year
		half_year = created + relativedelta(months = 6)
		# 2 years
		two_year = created + relativedelta(years = 2)
		
		if (updated - half_year).days < 0:
			return 0
		elif (updated - half_year).days >= 0 and (updated - two_year).days < 0:
			return 5
		else:
			return 10
	
	# Author's social media
	def author_social_media(self):
		if not self.author:
			return 0
		followers = self.author['followers']
		blog = self.author['blog']
		twitter = self.author['twitter']
		
		f_score = 0	# Max 6
		b_score = 0	# Max 3	
		t_score = 0	# Max 1
		
		if followers >= 10:
			f_score = 6
		elif followers < 10 and followers > 0:
			f_score = 3
		else:
			f_score = 0
		
		if blog:
			b_score = 3
		else:
			b_score = 0
		
		if twitter:
			t_score = 1
		else:
			t_score = 0
		
		return (f_score + b_score + t_score)
	
	# Author's achievements
	def author_achievements(self):
		if not self.author:
			return 0
	
		repos = self.author['repos']
		orgnizations = self.author['orgnizations']
		badge = self.author['badge']
		
		r_score = 0	# Max 4
		o_score = 0	# Max 3
		b_score = 0	# Max 3
		
		if repos >= 10:
			r_score = 4
		elif repos > 0 and repos < 10:
			r_score = 2
		else:
			r_score = 0
		
		if orgnizations:
			o_score = 3
		else:
			o_score = 0
			
		if badge and badge >= 2:
			b_score = 3
		elif badge and badge == 1:
			b_score = 1
		else:
			b_score = 0
		
		return (r_score + o_score + b_score)
	
	""" Github """	
	# Repo's age
	def github_repo_age(self):
		if not self.github:
			return 0
		updated = parse(self.github['updated'])
		created = parse(self.github['created'])
		# half year
		half_year = created + relativedelta(months = 6)
		# 2 years
		two_year = created + relativedelta(years = 2)
		
		if (updated - half_year).days < 0:
			return 0
		elif (updated - half_year).days > 0 and (updated - two_year).days < 0:
			return 5
		else:
			return 10
		
	# Popularity
	def github_popularity(self):
		if not self.github:
			return 0
		stars = self.github['stars']
		forks = self.github['forks']
		used_by = self.github['used_by']
		
		s_score = 0	# Max 4
		f_score = 0	# Max 4
		u_score = 0	# Max 2
		
		if stars >= 20:
			s_score = 4
		elif stars > 0 and stars < 20:
			s_score = 2
		else:
			s_score = 0
		
		if forks >= 10:
			f_score = 4
		elif forks > 0 and forks < 10:
			f_score = 2
		else:
			f_score = 0
		
		if used_by:
			u_score = 2
		else:
			u_score = 0
		
		return (s_score + f_score + u_score)
		
	# Maintenance
	def github_maintenance(self):
		if not self.github:
			return 0
		releases = self.github['releases']
		contributors = self.github['contributors']
		issues = self.github['issues']
		
		r_score = 0	# Max 4
		c_score = 0	# Max 3
		i_score = 0	# Max 3
		
		if releases >= 3:
			r_score = 4
		elif releases > 0:
			r_score = 2
		else:
			r_score = 0
		
		if contributors >= 4:
			c_score = 3
		elif contributors > 0:
			c_score = 1
		else:
			c_score = 0
		
		if issues >= 4:
			i_score = 3
		elif issues > 0:
			i_score = 1
		else:
			i_score = 0
		
		return (r_score + c_score + i_score)
		
	""" Registry """	
	# Downloads
	def registry_downloads(self):
		if not self.registry:
			return 0
		downloads = self.registry['downloads']
		reg = self.registry['registry']
		if reg == "NPM":
			downloads = int(downloads.replace(',',''))
		downloads = int(downloads)
		if reg == 'Ruby' :
			if downloads > 1000:
				return 10
			elif downloads > 500:
				return 5
			else:
				return 0
		else:
			if downloads > 100:
				return 10
			elif downloads > 50:
				return 5
			else:
				return 0
	# Total score
	def total_score(self):
		author_score = self.author_age() + self.author_social_media() + self.author_achievements()
		github_score = self.github_repo_age() + self.github_popularity() + self.github_maintenance()
		registry_score = self.registry_downloads()
		
		total_score = author_score * 0.5 + github_score * 0.4 + registry_score * 0.1
		return total_score, author_score, github_score, registry_score

def getRepositoryInfomation(repo_dict):
	# initialize the score dict
	store = {"description":repo_dict['description'], "created":repo_dict['created_at'], "updated":repo_dict['updated_at'], "stars":repo_dict['stargazers_count'], "forks":repo_dict["forks"], "issues":repo_dict['open_issues']}
	# print(repo_dict)
	if type(repo_dict['description']):
		print('Description: ', 'null')
	else:
		# Project description
		print('Description:', repo_dict['description'])
	"""Print as required"""
	print("\n--------- Age ---------\n")
	# Created at
	print('Created:', repo_dict['created_at'])
	# Updated at
	print('Updated:', repo_dict['updated_at'])
	print("\n----- Popularity ------\n")
	# Stars
	print('Stars:', repo_dict['stargazers_count'])
	# Forks count
	print("Forks:", repo_dict['forks'])
	
	# Get used by
	try:
		url1 = repo_dict['html_url']
		res1 = req.get(url1)
		if res1.status_code == 200:
			data1 = res1.content.decode('utf-8')
			# Used by
			try:
				#print(data1)
				#print(data1)
				print("hi im here")
				used_by = data1.split('<span class="px-2 text-bold text-small no-wrap">')[1].split('+ ')[1].split('\n          </span>')[0]
				#print(used_by)
				#print("This is data split"+data1.split('<span class="px-2 text-bold text-small no-wrap">')[1].split('+ ')[1].split('\n          </span>')[0])
			except:
				#print(data1)
				used_by = None
			store["used_by"] = used_by
			# Used by
			print("Used by:", used_by)
			print("\n---- Maintainance -----\n")	
		else:
			store["used_by"] = None
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		store["used_by"] = None
		print("[ERROR]: Popular Info Requests Error!")
	
	
	# Get releases
	owner_repo = str(repo_dict['html_url']).split("github.com/")[1]
	try:
		res4 = req.get("https://api.github.com/repos/%s/releases"%owner_repo)
		time.sleep(2)
		if res4.status_code == 200:
			data4 = res4.json()
			# releases
			store["releases"] =  len(data4)
			print("Releases:", len(data4))	
		else:
			store["releases"] = None
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		store["releases"] = None
		print("[ERROR]: Releases Info Requests Error!")
	
	
	# Get contributors
	try:
		res5 = req.get("https://api.github.com/repos/%s/contributors"%owner_repo)
		time.sleep(2)
		if res5.status_code == 200:
			data5 = res5.json()
			# releases
			store["contributors"] =  len(data5)
			print("Contributors:", len(data5))	
		else:
			store["contributors"] = None
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		store["contributors"] = None
		print("[ERROR]: Contributors Info Requests Error!")

	
	# Issues count
	print("Issues Count:", repo_dict['open_issues'])
	# Issues Urls
	print("Issues Urls:", repo_dict['issues_url'])
	# Get commits
	print("\n------- Commits -------\n")
	try:
		url2 = "https://api.github.com/repos/%s/stats/participation"%str(repo_dict['html_url']).split("github.com/")[1]
		url3 = "https://api.github.com/repos/%s/stats/commit_activity"%str(repo_dict['html_url']).split("github.com/")[1]
		res2 = req.get(url2,headers=headers)
		res3 = req.get(url3,headers=headers)
		time.sleep(5) # wait for the response
		if res2.status_code == 200 and res3.status_code == 200:
			data2 = res2.json()
			data3 = res3.json()

			print("Weekly commits:", data2,'\n')
			print("Yearly commits:", data3,'\n')
			store["weekly_commits"] = data2
			store["yearly_commits"] = data3
		else:
			store["weekly_commits"] = None
			store["yearly_commits"] = None
			print("[ERROR]: Status Code: %d"%res3.status_code)
		
	except:
		store["weekly_commits"] = None
		store["yearly_commits"] = None
		print("[ERROR]: Commits Info Requests Error!")
	
	
	print("\n----- Other Info ------\n")
	# Author's Name
	print('\nName:', repo_dict['name'])
	# Owner's Name
	print('Owner:', repo_dict['owner']['login'])
	# Repository Url
	print('Repository:', repo_dict['html_url'])
	
	return str(repo_dict['html_url']).split("github.com/")[1], store

def get_github_info_by_link(link):
	try:
		#rep = link.split("github.com/")[1]
		rep = link.split("github.com/")[1].split("/")[0]+"/"+link.split("github.com/")[1].split("/")[1]
		print(rep)
		url1 = "https://api.github.com/search/repositories?q=%s"%rep
	except:
		return {}
	try:
		res1 = req.get(url1, headers=headers)
		if res1.status_code == 200:
			response_dict = res1.json()
			#print("Toal repositories:", response_dict['total_count'])
			repo_dicts = response_dict['items']
			#print("Repositories returned:", len(repo_dicts))
			print("\n----------------GitHub Module-----------------")
			#for repo_dict in repo_dicts:
				#getRepositoryInfomation(repo_dict)
			repository_name, store = getRepositoryInfomation(repo_dicts[0])
			return store
						
		else:
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		print("[ERROR]: Repositories Basic Info Requests Error!")
	return {}

	# closed PRs -- First page -- minimum of 2 approved commits
	"""
	url2 = 'https://api.github.com/repos/%s/pulls?state=closed'%repository_name	
	try:
		res2 = req.get(url2, headers=headers)
		if res2.status_code == 200:
			data1 = res2.json()
			if data1:
				# enumerate PRs of the first page
				PR_flag = False
				for key1 in data1:
					approved, total = 0, 0
					#print(key)
					PR_id = key1['number']
					# get detailed PRs
					url3 = 'https://api.github.com/repos/%s/pulls/%s/reviews'%(repository_name, PR_id)
					try:
						res3 = req.get(url3, headers=headers)
						data2 = res3.json()
						if not data2:
							continue
						for key2 in data2:
							total += 1
							if key2['state'] and key2['state'] == 'APPROVED':
								approved += 1
					except:
						print("[ERROR]: Repositories detailed PRs Requests Error!")	
					#print("#%d has %d APPROVED pull requests, the total number is %d"%(PR_id, approved, total))
					if approved >= 2:
						PR_flag = True
						print("#%d has %d APPROVED pull requests, the total number is %d"%(PR_id, approved, total))	
			else:
				print("Pull Requests: 0")
			if PR_flag == False:
				print("Pull Requests: 0")
						
		else:
			print("[ERROR]: Status Code: %d"%res2.status_code)
		
	except:
		print("[ERROR]: Repositories PRs Requests Error!")
	"""
def get_github_info_by_package(package, registry):
	languages = {"PyPI":"Python","NPM":"JavaScript","Ruby":"Ruby"}
	repository_name = ""
	# basic info
	url1 = 'https://api.github.com/search/repositories?l=%s&q=%s&sort=stars'%(languages[registry],package)
	try:
		res1 = req.get(url1, headers=headers)
		if res1.status_code == 200:
			response_dict = res1.json()
			#print("Toal repositories:", response_dict['total_count'])
			repo_dicts = response_dict['items']
			#print("Repositories returned:", len(repo_dicts))
			print("\n----------------GitHub Module[may not be accurate] -----------------")
			#for repo_dict in repo_dicts:
				#getRepositoryInfomation(repo_dict)
			repository_name, store = getRepositoryInfomation(repo_dicts[0])
			return store
						
		else:
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		print("[ERROR]: Repositories Basic Info Requests Error!")
	return {}
		
def get_PyPI_info(package):
	#if flag == true, there is a github link
	store = {}
	flag = False
	url = "https://pypi.org/pypi/%s/json"%package
	try:
		res = req.get(url)
		if res.status_code == 200:
			print("\n----------------Registry - PyPI-----------------\n")
			data = res.json()
			#GitHub Link
			link = data["info"]["project_url"]
			if data["info"]["project_urls"]:
				for val in data["info"]["project_urls"].values():
					if "github" in val and val.count('/')==4:
						link = val
						print("Github Link: %s"%link)
						flag = True
						break

			# Author's name
			author = data["info"]["author"]
			print("Author's name:",author)
			# Maintainer's name
			res_temp = req.get("https://pypi.org/project/%s/"%package, headers=headers)
			maintainer = res_temp.content.decode('utf-8').split('<span class="sidebar-section__user-gravatar-text">\n')[1].split('\n')[0].strip()
			print("Maintainer's name:",maintainer)
			# Number of downloads
			downloads = req.get("https://pypistats.org/api/packages/%s/recent"%package, headers=headers).json()
			daily_downloads = downloads["data"]["last_day"]
			weekly_downloads = downloads["data"]["last_week"]
			monthly_downloads = downloads["data"]["last_month"]
			print("Number of downloads in the last day:",daily_downloads)
			print("Number of downloads in the last week:",weekly_downloads)
			print("Number of downloads in the last month:",monthly_downloads)
			# Official Docs
			docs = data["info"]["docs_url"]
			print("Docs Url:", docs)
			# Releases
			releases = data["releases"]
			release_num = 0
			if releases:
				for key in releases:
					release_num += 1
			print("Number of releases:", release_num)
			
			# store 
			store = {"registry": "PyPI", "downloads": weekly_downloads}
					
		else:
			store = {"registry": "PyPI","downloads": None}
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		store = {"registry": "PyPI","downloads": None}
		print("[ERROR]: PyPI Info Requests Error!")

	return link, author, maintainer, flag, store
		
def get_Ruby_info(package):
	store = {}
	url = "https://rubygems.org/api/v1/gems/%s.json"%package
	try:
		res = req.get(url)
		if res.status_code == 200:
			print("\n----------------Registry - RubyGEMs-----------------\n")
			data = res.json()
			# Github link
			link = data["source_code_uri"]
			print("Github Link: %s"%link)
			# Author's name
			author = data["authors"]
			print("Author's name:",author)
			# Number of downloads
			downloads = data["downloads"]
			print("Number of downloads in this version:",downloads)
			# Official Docs
			docs = data["documentation_uri"]
			print("Docs Url:", docs)
			# Home page
			home_page = data["homepage_uri"]
			print("Homepage Url:", home_page)
			
			# store 
			store = {"registry": "Ruby","downloads": downloads}
		else:
			store = {"registry": "Ruby","downloads": None}
			print("[ERROR]: Status Code: %d"%res.status_code)	
	
	except:
		store = {"registry": "Ruby" ,"downloads": None}
		print("[ERROR]: RubyGEMs Info Requests Error!")
	# return maintainer's name
	if link:
		return link, link.split("github.com/")[1].split("/")[0], store
	else:
		return None, None, store
	
def get_NPM_info(package):
	url = "https://www.npmjs.com/package/%s"%package
	store = {}
	try:
		res = req.get(url)
		if res.status_code == 200:
			print("\n----------------Registry - NPM-----------------\n")
			data = res.content.decode('utf-8')
			# Github link
			link = "https://"+data.split('repository-link">')[1].split('</span>')[0]
			print("Github Link: %s"%link)
			# Author's name  -- [Only the first one]
			author = data.split('border-radius:4%" alt="')[1].split('" title=')[0]
			print("Author's name:",author)
			# Number of downloads
			weekly_downloads = data.split('<p class="_9ba9a726 f4 tl flex-auto fw6 black-80 ma0 pr2 pb1">')[1].split('</p>')[0]
			print("Number of downloads in this version last week:",weekly_downloads)
			# Official Docs
			#docs = data["documentation_uri"]
			#print("Docs Url:", docs)
			# Home page
			home_page = "https://"+data.split('<span id="homePage-link">')[1].split('</span>')[0]
			print("Homepage Url:", home_page)
			
			# store 
			store = {"registry":"NPM", "downloads": weekly_downloads}
			
		else:
			store = {"registry":"NPM", "downloads":None}
			print("[ERROR]: Status Code: %d"%res.status_code)	
	
	except:
		store = {"registry":"NPM", "downloads":None}
		print("[ERROR]: NPM Info Requests Error!")
	
	# return maintainer's name
	return link, link.split("github.com/")[1].split("/")[0], store
	

def get_author_info(author, maintainer, registry):
	store = {}
	if author:
		url_github = "https://api.github.com/users/%s" % author
	else:
		url_github = "https://api.github.com/users/%s" % maintainer
	try:
		res = req.get(url_github, headers=headers)
		print("\n----------------Author: Search Github...-----------------\n")
		if res.status_code == 200:
			res = res.json()
			print("--------- Age ---------\n")
			real_name = res["name"]
			print("Author's real name:",real_name)
			# date
			created_time = res["created_at"]
			updated_time = res["updated_at"]
			print("Creation date",created_time)
			print("Update date",updated_time)
			
			"""test"""
			#print(author_age_check(updated_time, created_time))
			
			
			# bio
			real_name = res["name"]
			blog = res["blog"]
			email = res["email"]
			bio = res["bio"]
			twitter = res["twitter_username"]
			followers = res["followers"]
			repos_num = res["public_repos"]
			
			
			# print as required
			print("\n-----Social Media------\n")
			print("Author's blog:",blog)
			print("Author's email:",email)
			print("Author's bio:",bio)
			print("Author's twitter:",twitter)
			print("Author's followers:",followers)
			
			# activity
			print("\n--------Activity-------\n")
			company = res["company"]
			print("Author's orgnization:",company)
			print("Number of repositories:",repos_num)
			
			# store 
			store = {"created":created_time, "updated":updated_time, "blog":blog, "email":email, "bio":bio, "twitter":twitter, "followers":followers, "repos":repos_num, "company":company}
			
			# achievements
			try:
				if author:
					url_badge = "https://github.com/%s?tab=achievements"%author
				else:
					url_badge = "https://github.com/%s?tab=achievements"%maintainer
				res2 = req.get(url_badge, headers=headers)
				if res2.status_code == 200:
					data2 = res2.content.decode('utf-8')
					badge_num = data2.count('achievement-badge-card')
					print("Author's badges:", badge_num)
					# store
					store["badge"] = badge_num
				else:
					store["badge"] = None
					print("[ERROR]: Status Code: %d"%res2.status_code)
			
			except:
				store["badge"] = None
				print("[ERROR]: Author Info Requests Error!")
			
			# orginizations
			try:
				if author:
					url_org = "https://api.github.com/users/%s/orgs"%author
				else:
					url_org = "https://api.github.com/users/%s/orgs"%maintainer
				res3 = req.get(url_org, headers=headers)
				time.sleep(2)
				if res3.status_code == 200:
					data3 = res3.json()
					orgs_num = len(data3)
					print("Author's organizations:", orgs_num)
					store["orgnizations"] = orgs_num
				else:
					store["orgnizations"] = None
					print("[ERROR]: Status Code: %d"%res2.status_code)
			
			except:
				store["orgnizations"] = None
				print("[ERROR]: Orgnizations Info Requests Error!")
				
			
		elif res.status_code == 404:
			
			print("No such user!")
			return {}
		else:
			
			print("[ERROR]: Status Code: %d"%res.status_code)
			return {}
		
	except:
		
		print("[ERROR]: Author Info Requests Error!")
		return {}
	
	if registry == "PyPI":
		url_pypi = "https://pypi.org/user/%s" % maintainer
		try:
			res = req.get(url_pypi, headers=headers)
			print("\n----------------Author: Search PyPI...-----------------\n")
			if res.status_code == 200:
				""" Needs to be polished """
				print("Info Url:", url_pypi)
			elif res.status_code == 404:
				print("No such user!")
			else:
				print("[ERROR]: Status Code: %d"%res.status_code)
			
		except:
			print("[ERROR]: Author Info Requests Error!")
	
	if registry == 'NPM':
		url_npm = "https://www.npmjs.com/~%s"%maintainer
		try:
			res = req.get(url_npm, headers=headers)
			print("\n----------------Author: Search NPM...-----------------\n")
			if res.status_code == 200:
				""" Needs to be polished """
				print("Info Url:", url_npm)
			elif res.status_code == 404:
				print("No such user!")
			else:
				print("[ERROR]: Status Code: %d"%res.status_code)
			
		except:
			print("[ERROR]: Author Info Requests Error!")
	if registry == 'Ruby':
		url_ruby = "https://rubygems.org/profiles/%s"%maintainer
		try:
			res = req.get(url_ruby, headers=headers)
			print("\n----------------Author: Search RubyGEMs...-----------------\n")
			if res.status_code == 200:
				""" Needs to be polished """
				print("Info Url:", url_ruby)
			elif res.status_code == 404:
				print("No such user!")
			else:
				print("[ERROR]: Status Code: %d"%res.status_code)
			
		except:
			print("[ERROR]: Author Info Requests Error!")
	
	return store
if __name__ == '__main__':
	package = args.package
	registry = args.registry
	owner = args.owner
	if package and registry == 'PyPI':
		link, author, maintainer, flag, registry_store = get_PyPI_info(package)
	if package and registry == 'Ruby':
		link, maintainer, registry_store = get_Ruby_info(package)
		#link = "https://github.com/flyerhzm/rails_best_practices"
	if package and registry == 'NPM':
		link ,maintainer, registry_store = get_NPM_info(package)
	if link and package and registry:
		# github store
		github_store = get_github_info_by_link(link)
		print(github_store)
	elif package and registry:
		github_store = get_github_info_by_package(package, registry)
		print(github_store)
	# author store
	author_store = get_author_info(owner, maintainer, registry)
	print("Author store:", author_store)
	# print(author_store)
	# print(registry_store)
	
	obj = Scoring(author_store, registry_store, github_store)
	
	print("\n----------------- Score ------------------\n")
	total, author_score, github_score, registry_score = obj.total_score()
	
	print("Author score:", author_score)
	print("Github score:", github_score)
	print("Registry score:", registry_score)
	print("Total score:", total)
	
	
	
	
	
