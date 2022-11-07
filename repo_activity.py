#!/usr/bin/python

import sys
import argparse
import requests as req

parser = argparse.ArgumentParser(description = "Analyze repository activity...", add_help=True)
parser.add_argument('-p', '--package', type=str, help="package name")
parser.add_argument('-r', '--repository', type=str, help="repository")
args = parser.parse_args()

if len(sys.argv) != 5:
	print("More arguments required!")

	
def getRepositoryInfomation(repo_dict):
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

def get_github_info(package, repository):
	languages = {"PyPI":"Python","NPM":"JavaScript","RubyGem":"Ruby"}
	url = 'https://api.github.com/search/repositories?l=%s&q=%s&sort=stars'%(languages[repository],package)
	try:
		res = req.get(url)
		if res.status_code == 200:
			response_dict = res.json()
			print("Toal repositories:", response_dict['total_count'])
			repo_dicts = response_dict['items']
			print("Repositories returned:", len(repo_dicts))
			print("\nSelected information about first repository:")
			
			for repo_dict in repo_dicts:
				getRepositoryInfomation(repo_dict)
						
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
			data = res.json()
			#GitHub Link
			link = data["info"]["project_url"]
			for val in data["info"]["project_urls"].values():
				if "github" in val:
					link = val
					print("Github Link: %s"%link)
					flag = True
					break
			#Author's name
			author = data["info"]["author"]
			return link, author, flag
					
		else:
			print("[ERROR]: Status Code: %d"%res.status_code)
		
	except:
		print("[ERROR]: PyPI Info Requests Error!")

if __name__ == '__main__':
	package = args.package
	repository = args.repository
	get_github_info(package, repository)
	#link, author, flag = get_PyPI_info(package)
	
