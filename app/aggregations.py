def total_repositories(db):
    pipeline = [
        { "$count": "total_repositories" }
    ]
    return list(db.github_repos.aggregate(pipeline))

def repositories_by_license(db):
    pipeline = [
        { "$group": { "_id": "$license", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } }
    ]
    return list(db.github_repos.aggregate(pipeline))

def activity_metrics(db):
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_forks": { "$sum": "$forks_count" },
                "total_stargazers": { "$sum": "$stargazers_count" },
                "total_watchers": { "$sum": "$watchers_count" }
            }
        }
    ]
    return list(db.github_repos.aggregate(pipeline))

def top_keywords_from_descriptions(db):
    pipeline = [
        { "$unwind": "$keywords_from_description" },
        { "$group": { "_id": "$keywords_from_description", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 10 }
    ]
    return list(db.github_repos.aggregate(pipeline))

def top_keywords_from_readmes(db):
    pipeline = [
        { "$unwind": "$keywords_from_readme" },
        { "$group": { "_id": "$keywords_from_readme", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 10 }
    ]
    return list(db.github_repos.aggregate(pipeline))
