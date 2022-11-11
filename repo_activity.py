#!/usr/bin/python

import sys
import argparse
import requests as req

parser = argparse.ArgumentParser(description = "Analyze repository activity...", add_help=True)
parser.add_argument('-p', '--package', type=str, help="package name")
parser.add_argument('-r', '--registry', type=str, help="registry")
parser.add_argument('-a', '--owner', type=str, help="owner")
args = parser.parse_args()

if len(sys.argv) < 5:
	print("More arguments required!")

	
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

def get_github_info(package, registry):
	languages = {"PyPI":"Python","NPM":"JavaScript","Ruby":"Ruby"}
	url = 'https://api.github.com/search/repositories?l=%s&q=%s&sort=stars'%(languages[registry],package)
	try:
		res = req.get(url)
		if res.status_code == 200:
			response_dict = res.json()
			print("Toal repositories:", response_dict['total_count'])
			repo_dicts = response_dict['items']
			print("Repositories returned:", len(repo_dicts))
			print("\nSelected information about first repository:")
			print("----------------GitHub-----------------")
			#for repo_dict in repo_dicts:
				#getRepositoryInfomation(repo_dict)
			getRepositoryInfomation(repo_dicts[0])
						
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		print("[ERROR]: Repositories Requests Error!")

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
			for val in data["info"]["project_urls"].values():
				if "github" in val:
					link = val
					print("Github Link: %s"%link)
					flag = True
					break
			# Author's name
			author = data["info"]["author"]
			print("Author's name:",author)
			# Number of downloads
			daily_downloads = data["info"]["downloads"]["last_day"]
			weekly_downloads = data["info"]["downloads"]["last_week"]
			monthly_downloads = data["info"]["downloads"]["last_month"]
			print("Number of downloads in the last day:",daily_downloads)
			print("Number of downloads in the last week:",weekly_downloads)
			print("Number of downloads in the last month:",monthly_downloads)
			# Official Docs
			docs = data["info"]["docs_url"]
			print("Docs Url:", docs)
			# Releases
			releases = data["releases"]
			print("Releases:", releases)
			
			return link, author, flag
					
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
			print("Homepage Url:", docs)
			# Release [TBD]
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)	
	
	except:
		print("[ERROR]: RubyGEMs Info Requests Error!")
	

def get_author_info(author):
	url = "https://api.github.com/users/%s" % author
	try:
		res = req.get(url)
		if res.status_code == 200:
			res = res.json()
			print("\n----------------Author-----------------\n")
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
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		print("[ERROR]: Author Info Requests Error!")

if __name__ == '__main__':
	package = args.package
	registry = args.registry
	owner = args.owner
	if package and registry == 'PyPI':
		link, author, flag = get_PyPI_info(package)
	if package and registry == 'Ruby':
		get_Ruby_info(package)
	if package and registry:
		get_github_info(package, registry)
	if owner:
		get_author_info(owner)
	
