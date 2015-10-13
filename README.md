# Under development
* Please see guidelines below to get current version to work locally

# Getting Started
1. All files in predict_best_team/bestteam/getdata
2. For all file have to change database name and user and have the necessary table in your database with the schema represented by player_dict (or just remove this code and write to csv)
3. PointsAgainst.py
    * This reads the data here: http://games.espn.go.com/ffl/pointsagainst
    * Only one argument: season
4. PreviousSeason.py (I used this to pull 2014 averages)
    * This reads the data here: http://games.espn.go.com/ffl/leaders?seasonTotals=true&seasonId=2014&startIndex=0
    * Two arguments: season and number of pages to pull
5. Projections.py
    * This reads the data here: http://games.espn.go.com/ffl/tools/projections
    * Three arguments: season, week, and number of pages
6. WeeklyData.py
    * This reads the data here: http://games.espn.go.com/ffl/leaders?
    * Three arguments: season, week, and number of pages
