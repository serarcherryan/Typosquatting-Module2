#!/usr/bin/python

import sys
import argparse
import requests as req
import pypistats

parser = argparse.ArgumentParser(description = "Analyze repository activity...", add_help=True)
parser.add_argument('-p', '--package', type=str, help="package name")
parser.add_argument('-r', '--registry', type=str, help="registry")
parser.add_argument('-a', '--owner', type=str, help="owner")
args = parser.parse_args()

if len(sys.argv) < 5:
	print("More arguments required!")
token = "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"
headers = {"Authorization": "token" + token}	
#headers={}
def getRepositoryInfomation(repo_dict):
	# print(repo_dict)
	# Author's Name
	print('\nName:', repo_dict['name'])
	# Owner's Name
	print('Owner:', repo_dict['owner']['login'])
	# Stars
	print('Stars:', repo_dict['stargazers_count'])
	# Repository Url
	print('Repository:', repo_dict['html_url'])
	# Created at
	print('Created:', repo_dict['created_at'])
	# Updated at
	print('Updated:', repo_dict['updated_at'])
	# Forks count
	print("Forks:", repo_dict['forks'])
	# Issues count
	print("Issues Count:", repo_dict['open_issues'])
	# Issues Urls
	print("Issues Urls:", repo_dict['issues_url'])
	if type(repo_dict['description']):
		print('Description: ', 'null')
	else:
		# Project description
		print('Description:', repo_dict['description'])
	
	return str(repo_dict['html_url']).split("github.com/")[1]

def get_github_info_by_link(link):
	rep = link.split('github.com/')[1]
	url1 = "https://api.github.com/search/repositories?q=%s"%rep
	try:
		res1 = req.get(url1, headers=headers)
		if res1.status_code == 200:
			response_dict = res1.json()
			#print("Toal repositories:", response_dict['total_count'])
			repo_dicts = response_dict['items']
			#print("Repositories returned:", len(repo_dicts))
			print("----------------GitHub [First]-----------------")
			#for repo_dict in repo_dicts:
				#getRepositoryInfomation(repo_dict)
			repository_name = getRepositoryInfomation(repo_dicts[0])
			
						
		else:
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		print("[ERROR]: Repositories Basic Info Requests Error!")

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
			print("----------------GitHub [First]-----------------")
			#for repo_dict in repo_dicts:
				#getRepositoryInfomation(repo_dict)
			repository_name = getRepositoryInfomation(repo_dicts[0])
						
		else:
			print("[ERROR]: Status Code: %d"%res1.status_code)
		
	except:
		print("[ERROR]: Repositories Basic Info Requests Error!")
		
		
def get_PyPI_info(package):
	#if flag == true, there is a github link
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
					if "github" in val:
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
			
			return link, author, maintainer, flag
					
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		print("[ERROR]: PyPI Info Requests Error!")
		
def get_Ruby_info(package):
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
			version_downloads = data["version_downloads"]
			print("Number of downloads in this version:",version_downloads)
			# Official Docs
			docs = data["documentation_uri"]
			print("Docs Url:", docs)
			# Home page
			home_page = data["homepage_uri"]
			print("Homepage Url:", home_page)
			# return maintainer's name
			if link:
				return link, link.split("github.com/")[1].split("/")[0]
			else:
				return None
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)	
	
	except:
		print("[ERROR]: RubyGEMs Info Requests Error!")
	
def get_NPM_info(package):
	url = "https://www.npmjs.com/package/%s"%package
	try:
		res = req.get(url)
		if res.status_code == 200:
			print("\n----------------Registry - NPM-----------------\n")
			data = res.content.decode('utf-8')
			# Github link
			link = data.split('repository-link">')[1].split('</span>')[0]
			print("Github Link: %s"%link)
			# Author's name  -- [Only the first one]
			author = data.split('border-radius:4%" alt="')[1].split('" title=')[0]
			print("Author's name:",author)
			# Number of downloads
			version_downloads = data.split('<p class="_9ba9a726 f4 tl flex-auto fw6 black-80 ma0 pr2 pb1">')[1].split('</p>')[0]
			print("Number of downloads in this version last week:",version_downloads)
			# Official Docs
			#docs = data["documentation_uri"]
			#print("Docs Url:", docs)
			# Home page
			home_page = data.split('<span id="homePage-link">')[1].split('</span>')[0]
			print("Homepage Url:", home_page)
			# Release [TBD]
			return link, author
			
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)	
	
	except:
		print("[ERROR]: RubyGEMs Info Requests Error!")

def get_author_info(author, maintainer, registry):
	if author:
		url_github = "https://api.github.com/users/%s" % author
	else:
		url_github = "https://api.github.com/users/%s" % maintainer
	try:https://github.com/caolan/async

		res = req.get(url_github, headers=headers)
		print("\n----------------Author: Search Github...-----------------\n")
		if res.status_code == 200:
			res = res.json()
			print("Author:", author)
			# date
			created_time = res["created_at"]
			updated_time = res["updated_at"]
			print("Creation date",created_time)
			print("Update date",updated_time)
			
			# bio
			print("\n------Author's Bio------\n")
			real_name = res["name"]
			company = res["company"]
			blog = res["blog"]
			email = res["email"]
			bio = res["bio"]
			twitter = res["twitter_username"]
			followers = res["followers"]
			repos_num = res["public_repos"]
			print("Author's real name:",real_name)
			print("Author's company:",company)
			print("Author's blog:",blog)
			print("Author's email:",email)
			print("Author's bio:",bio)
			print("Author's twitter:",twitter)
			print("Author's followers:",followers)
			print("Number of repositories:",repos_num)
		elif res.status_code == 404:
			print("No such user!")
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		print("[ERROR]: Author Info Requests Error!")
	
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
	
if __name__ == '__main__':
	package = args.package
	registry = args.registry
	owner = args.owner
	if package and registry == 'PyPI':
		link, author, maintainer, flag = get_PyPI_info(package)
	if package and registry == 'Ruby':
		link, maintainer = get_Ruby_info(package)
	if package and registry == 'NPM':
		link ,maintainer = get_NPM_info(package)
	if link and package and registry:
		print("----------Github Link Found-----------")
		get_github_info_by_link(link)
	elif package and registry:
		print("---------No Github Link----------")
		get_github_info_by_package(package, registry)
	
	get_author_info(owner, maintainer, registry)
	
