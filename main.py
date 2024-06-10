# Overview: This program takes in user input, and analyzes CTA ridership data based on user command.
# Data is fetched and analyzed using SQL Queries and Python. Some data is displayed using matplotlib.

import sqlite3
import matplotlib.pyplot as plt

##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    #get number of stations
    dbCursor = dbConn.cursor()
    print("General Statistics:")
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone();
    print("  # of stations:", f"{row[0]:,}")
    #get number of stops
    dbCursor.execute("Select count(*) From Stops")
    rowStops = dbCursor.fetchone();
    print("  # of stops:", f"{rowStops[0]:,}")
    #get number of ride entries
    dbCursor.execute("Select count(*) From Ridership")
    rowR_entries = dbCursor.fetchone();
    print("  # of ride entries:", f"{rowR_entries[0]:,}")
    #get date range
    dbCursor.execute("Select MIN(DATE(Ride_Date)) AS start_date, MAX(DATE(Ride_Date)) AS end_date from Ridership")
    rowD_entries = dbCursor.fetchone();
    print(f"  date range: {rowD_entries[0]} - {rowD_entries[1]}")
    #get total ridership
    dbCursor.execute("Select SUM(Num_Riders) From Ridership")
    rowT_riders = dbCursor.fetchone();
    print("  Total ridership:", f"{rowT_riders[0]:,}")
    print()

##################################################################  
#
# handle menu options
# Given user input call appropiate functions
#
def handler(user_input, dbConn):
  if user_input == 1:
    option1(dbConn)
  elif user_input == 2:  
    option2(dbConn)
  elif user_input == 3:
    option3(dbConn)
  elif user_input == 4:
    option4(dbConn)
  elif user_input == 5:
    option5(dbConn)
  elif user_input == 6:
    option6(dbConn)
  elif user_input == 7:
    option7(dbConn)
  elif user_input == 8:
    option8(dbConn)
  elif user_input == 9:
    option9(dbConn)
  else:
    print("**Error, unknown command, try again...")

##################################################################  
#
# handle option 1
def option1(dbConn):
   #find stations that match the user input
    dbCursor = dbConn.cursor()
    print()
    user_input = input("Enter partial station name (wildcards _ and %): ")
    dbCursor.execute("""Select Station_ID, Station_Name 
                        From Stations 
                        Where Station_Name Like ? 
                        Order By Station_Name Asc;""", [user_input])
    stations = dbCursor.fetchall()
    #were stations found? 
    if len(stations) == 0:
        print("**No stations found...")
        return  
    #if found print stations
    for stations in stations:
        print(f"{stations[0]} : {stations[1]}")

##################################################################  
#
# handle option 2
def option2(dbConn):
    #given station name from user
    dbCursor = dbConn.cursor()
    print()
    user_input = input("Enter the name of the station you would like to analyze: ")
    #find the number of riders on weekdays
    dbCursor.execute("""Select Sum(Num_Riders) 
                        From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                        Where Stations.Station_Name = ? AND Ridership.Type_of_Day = 'W'""", [user_input])
    weekDays = dbCursor.fetchone();
    #find the number of riders on Saturdays
    dbCursor.execute("""Select Sum(Num_Riders) 
                        From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                        Where Stations.Station_Name = ? AND Ridership.Type_of_Day = 'A'""", [user_input])
    saturday = dbCursor.fetchone();
    #find the number of riders on Sundays and holidays
    dbCursor.execute("""Select Sum(Num_Riders) 
                        From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                        Where Stations.Station_Name = ? AND Ridership.Type_of_Day = 'U'""", [user_input])
    sundays_holidays = dbCursor.fetchone();
    #find the total number of riders for specified station
    dbCursor.execute("""Select Sum(Num_Riders) 
                        From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                        Where Stations.Station_Name = ?;""", [user_input])
    total = dbCursor.fetchone();
    #check weekday data was found
    if weekDays is None or weekDays[0] is None:
        print("**No data found...")
        return
    #calculate percentages for weekdays, Saturdays, Sundays/holidays
    wPercentage = weekDays[0] / total[0] * 100 if (weekDays and total and total[0] != 0) else 0
    sPercentage = saturday[0] / total[0] * 100 if (saturday and total and total[0] != 0) else 0
    s_hPercentage = sundays_holidays[0] / total[0] * 100 if (sundays_holidays and total and total[0] != 0) else 0
    #display ridership info for given station
    print(f"Percentage of ridership for the {user_input} station: ")
    print(" Weekday ridership:", f"{weekDays[0]:,}", f"({wPercentage:.2f}%)")
    print(" Saturday ridership:", f"{saturday[0]:,}", f"({sPercentage:.2f}%)")
    print(" Sunday/holiday ridership:", f"{sundays_holidays[0]:,}", f"({s_hPercentage:.2f}%)")
    print(" Total ridership: ", f"{total[0]:,}")

##################################################################  
#
# handle option 3
def option3(dbConn):
    #get weekday ridership for each station
    dbCursor = dbConn.cursor()
    dbCursor.execute("""Select Stations.Station_Name, Sum(Ridership.Num_Riders) As WeekdayRidership 
                        From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                        Where Ridership.Type_of_Day = 'W' 
                        Group By Stations.Station_Name 
                        Order By WeekdayRidership Desc;""")
    weekDayRiders = dbCursor.fetchall()
    #get total weekday ridership for all stations combined
    dbCursor.execute("Select Sum(Num_Riders) From Ridership Where Type_of_Day = 'W';")
    riderTotal = dbCursor.fetchone()
    #display weekday ridership data per station including percentages
    print("Ridership on Weekdays for Each Station")
    for station in weekDayRiders:
        print(f"{station[0]} : {station[1]:,} ({station[1]/riderTotal[0]*100:.2f}%)")

##################################################################  
#
# handle option 4
def option4(dbConn):
    #user will input a line color
    dbCursor = dbConn.cursor()
    print()
    user_input = input("Enter a line color (e.g. Red or Yellow): ")
    #get that line color
    dbCursor.execute("""Select Color 
                        From Lines 
                        Where LOWER(Color) = LOWER(?);""",[user_input])
    colorCheck = dbCursor.fetchone()
    #make sure line color exists
    if colorCheck is None or colorCheck[0] is None:
        print("**No such line...")
        return
    #user will input a direction
    direction = input("Enter a direction (N/S/W/E): ")
    #get stops given line color and direction
    dbCursor.execute("""Select Stop_Name, Direction, ADA 
                        From Stops Join StopDetails On Stops.Stop_ID = StopDetails.Stop_ID 
                        Join Lines On StopDetails.Line_ID = Lines.Line_ID 
                        Where Lines.Color = ? AND LOWER(Stops.Direction) = LOWER(?) 
                        Order By Stop_Name Asc;""", [colorCheck[0], direction])
    result_stops = dbCursor.fetchall()
    #if there are no stops given that direction
    if len(result_stops) == 0:
        print("**That line does not run in the direction chosen...")
        return
    #check for handicap accessible and display stops, direction, and accessibility
    for stop in result_stops:
        ADA = "handicap accessible" if stop[2] == 1 else "not handicap accessible"
        print(f"{stop[0]} : direction = {stop[1]} ({ADA})")

##################################################################  
#
# handle option 5
def option5(dbConn):
  #get total number of stops
  dbCursor = dbConn.cursor()
  dbCursor.execute("Select Count(Stop_ID) From Stops;")
  totalStops = dbCursor.fetchone()
  #get number of stops by color and seperate by direction
  dbCursor.execute("""Select Lines.Color, Stops.Direction, Count(Stops.Stop_ID) 
                      From Stops Join StopDetails On Stops.Stop_ID = StopDetails.Stop_ID 
                      Join Lines On StopDetails.Line_ID = Lines.Line_ID  
                      Group By Color, Direction 
                      Order By Color Asc, Direction Asc;""")
  allStops = dbCursor.fetchall()
  #display stats and calculate percentages
  print("Number of Stops For Each Color By Direction")
  for stop in allStops:
    print(f"{stop[0]} going {stop[1]} : {stop[2]} ({(stop[2] / totalStops[0] * 100):.2f}%)")

##################################################################  
#
# handle option 6
def option6(dbConn):
  #get user input for station name 
  dbCursor = dbConn.cursor()
  print()
  user_input = input("Enter a station name (wildcards _ and %): ")
  #get specified station 
  dbCursor.execute("""Select Station_Name 
                      From Stations 
                      Where Station_Name Like ?;""", [user_input])
  stations = dbCursor.fetchall()
  #check if stations were found
  if len(stations) == 0:
    print("**No station found...")
    return
  #were multiple stations we found? 
  if len(stations) > 1:
    print("**Multiple stations found...")
    return
  #if only one station was found -> store in name var.
  name = stations[0][0]
  #get total ridership for that station per year
  dbCursor.execute("""Select strftime('%Y', Ride_Date) As Year, Sum(Num_Riders) 
                      From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? 
                      Group By Year Order By Year""", [name])
  results = dbCursor.fetchall()
  #display station yearly ridership info
  print(f"Yearly Ridership at {name}")
  for row in results:
    print(f"{row[0]} : {row[1]:,}")
  print()
  plot = input("Plot? (y/n)")
  #ask user if they want a plot, if yes store data
  if plot == "y":
    years, ridership = [],[]
    for row in results:
      years.append(row[0])
      ridership.append(row[1])
    #plot data
    plt.figure(figsize = (9,9))
    plt.plot(years, ridership)
    plt.title(f"Yearly Ridership at {name}")
    plt.xlabel("Year")
    plt.ylabel("Number of Riders")
    plt.show()

##################################################################  
#
# handle option 7
def option7(dbConn):
  #get user input for station name
  dbCursor = dbConn.cursor()
  print()
  user_input = input("Enter a station name (wildcards _ and %): ")
  #get stations
  dbCursor.execute("Select Station_Name From Stations Where Station_Name Like ?;", [user_input])
  station = dbCursor.fetchall()
  #if no stations were found
  if len(station) == 0:
    print("**No station found...")
    return
  #if there were multiple stations found
  if len(station) > 1:
    print("**Multiple stations found...")
    return
  #if only one station was found -> store in name var.
  name = station[0][0]
  #safety check
  if name is None:
    return
  #user inputs a year
  year = input("Enter a year: ")
  #get monthly ridership for that station within specified year
  dbCursor.execute("""Select strftime('%m/%Y', Ride_Date) as Monthly, Sum(Num_Riders) 
                      From Ridership Join Stations On Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                      Group By Monthly 
                      Order By Monthly;""", [name, year])
  result = dbCursor.fetchall()
  #display monthly ridership for that year
  print(f"Monthly Ridership at {name} for {year}")
  for row in result:
    print(f"{row[0]} : {row[1]:,}")
  #ask user if they want a plot, if yes store data
  plot = input("Plot? (y/n) ")
  if plot == "y":
    months, ridership = [],[]
    for row in result:
      months.append(row[0].split("/")[0])
      ridership.append(row[1])
    #plot that data
    plt.figure(figsize = (9,9))
    plt.plot(months, ridership)
    plt.title(f"Monthly Ridership at {name} ({year})")
    plt.xlabel("Month")
    plt.ylabel("Number of Riders")
    plt.show()

##################################################################  
#
# handle option 8
def option8(dbConn):
  #user inputs a year
  dbCursor = dbConn.cursor()
  print()
  year = input("Year to compare against? ")
  print()
  #user inputs first station to be compared
  user_input = input("Enter station 1 (wildcards _ and %): ")
  #get that station
  dbCursor.execute("""Select Station_Name 
                      From Stations 
                      Where Station_Name Like ?;""", [user_input])
  station1 = dbCursor.fetchall()
  #if station wasn't found
  if len(station1) == 0:
    print("**No station found...")
    return
  #if there are multiple stations
  if len(station1) > 1:
    print("**Multiple stations found...")
    return
  #if first station was found -> store that first station in name1 var.
  name1 = station1[0][0]
  print()
  #user inputs second station to be compared
  user_input2 = input("Enter station 2 (wildcards _ and %): ")
  #get that station
  dbCursor.execute("""Select Station_Name 
                      From Stations 
                      Where Station_Name Like ?;""", [user_input2])
  station2 = dbCursor.fetchall()
  #if station wasn't found
  if len(station2) == 0:
    print("**No station found...")
    return
  #if there are multiple stations
  if len(station2) > 1:
    print("**Multiple stations found...")
    return
  #if second station was found -> store that first station in name2 var.
  name2 = station2[0][0]
  #get first 5 days ridership for FIRST STATION, station ID, and total ridership, given specified year
  dbCursor.execute("""Select strftime('%Y-%m-%d', Ride_Date) As Year, Ridership.Station_ID, Ridership.Num_Riders 
                      From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                      Group By Year 
                      Order By Year Limit 5;""", [name1, year])
  results = dbCursor.fetchall()
  #display first 5 days ridership FIRST STATION
  print(f"Station 1: {results[0][1]} {name1}")
  for r in results:
    print(f"{r[0]} {r[2]}")
  #get last 5 days ridership for FIRST STATION, station ID, and total ridership, given specified year
  dbCursor.execute("""Select strftime('%Y-%m-%d', Ride_Date) As Year, Ridership.Station_ID, Ridership.Num_Riders 
                        From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                        Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                        Group By Year 
                        Order By Year Desc Limit 5;""", [name1, year])
  results1 = dbCursor.fetchall()
  #display last 5 days ridership FIRST STATION
  results1.reverse()
  for r in results1:
    print(f"{r[0]} {r[2]}")
  #get first 5 days ridership for SECOND STATION, station ID, and total ridership, given specified year
  dbCursor.execute("""Select strftime('%Y-%m-%d', Ride_Date) As Year, Ridership.Station_ID, Ridership.Num_Riders 
                        From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                        Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                        Group By Year 
                        Order By Year Limit 5;""", [name2, year])
  results2 = dbCursor.fetchall()
  #display first 5 days ridership for SECOND STATION
  print(f"Station 2: {results2[0][1]} {name2}")
  for r in results2:
    print(f"{r[0]} {r[2]}")
  #get last 5 days ridership for SECOND STATION, station ID, and total ridership, given specified year
  dbCursor.execute("""Select strftime('%Y-%m-%d', Ride_Date) As Year, Ridership.Station_ID, Ridership.Num_Riders 
                      From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                      Group By Year 
                      Order By Year Desc Limit 5;""", [name2, year])
  results3 = dbCursor.fetchall()
  #display last 5 days ridership for SECOND STATION
  results3.reverse()
  for r in results3:
    print(f"{r[0]} {r[2]}")
  #get total number of riders for STATION ONE entire year
  dbCursor.execute("""Select Ridership.Num_Riders 
                      From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                      Group By Ride_Date 
                      Order By Ride_Date Asc;""", [name1, year])
  firstResult = dbCursor.fetchall()
  #get total number of riders for STATION TWO entire year
  dbCursor.execute("""Select Ridership.Num_Riders 
                      From Ridership Join Stations on Ridership.Station_ID = Stations.Station_ID 
                      Where Station_Name Like ? And strftime('%Y', Ride_Date) = ? 
                      Group By Ride_Date 
                      Order By Ride_Date Asc;""", [name2, year])
  secondResult = dbCursor.fetchall()
  #store data for BOTH stations and initialize counter
  counter = 1
  x = []
  y1 = []
  y2 = []
  for i in range(len(firstResult)):
    x.append(counter)
    y1.append(firstResult[i][0])
    y2.append(secondResult[i][0])
    counter+=1
  #ask user if they want a plot if yes -> store data
  print()
  plot = input("Plot? (y/n) ")
  if plot == "y":
    day, ridership = [],[]
    #plot data
    plt.figure(figsize = (9,9))
    plt.legend([name1,name2])
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.title(f"Ridership each Day of ({year})")
    plt.xlabel("Day")
    plt.ylabel("Number of Riders")
    plt.show()


##################################################################  
#
# handle option 9
def option9(dbConn):
  #get user input latitude value
  print()
  user_input = input("Enter a latitude: ")
  #is latitude within range?
  if float(user_input) > 43 or float(user_input) < 40:
    print("**Latitude entered is out of bounds...")
    return
  #if yes continue and get user input longitude value
  user_input2 = input("Enter a longitude: ")
  #is longitude within range?
  if float(user_input2) < -88 or float(user_input2) > -87:
    print("**Longitude entered is out of bounds...")
    return
  #formulas for latitude with user inputs
  left_lim_latitude = round(float(user_input) - 1 / 69, 3)
  right_lim_latitude = round(float(user_input) + 1 /69, 3)
  #formulas for longitide with user inputs
  left_lim_long = round(float(user_input2) - 1 / 51, 3)
  right_lim_long = round(float(user_input2) + 1 / 51, 3)
  #get station name, latitude, and longitude coordinates
  dbCursor = dbConn.cursor()  
  dbCursor.execute(f"""Select Station_Name, Latitude, Longitude 
                        From Stops Join Stations on Stops.Station_ID = Stations.Station_ID 
                        Where Latitude Between {left_lim_latitude} And {right_lim_latitude} And Longitude Between {left_lim_long} And {right_lim_long} 
                        Group By Latitude, Longitude 
                        Order By Stations.Station_Name, Stop_ID Asc;""")
  result = dbCursor.fetchall()
  #safety check
  if len(result) == 0: 
    print("**No stations found...")
    return
  #store data for plotting
  stationNames = []
  x = []
  y = []
  for r in result:
    stationNames.append(r[0])
    x.append(r[2])
    y.append(r[1])
  #display stations within a mile
  print()
  print("List of Stations Within a Mile")
  for i in range(len(result)):
    print(f"{stationNames[i]} : ({x[i]}, {y[i]})")
  #ask user if they want a plot if yes -> load image and plot
  print()
  plot = input("Plot? (y/n) ")
  if plot == "y":
    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # area covered by
    plt.imshow(image, extent=xydims)
    plt.title("Stations Near You")
    plt.plot(x, y)
    #overlay data on top of image
    for row in result:
      plt.annotate(row[0], (row[2], row[1]))

    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()

##################################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()
#connect to database
dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')
#call function to print statistics
print_stats(dbConn)
#display menu and take user input for menu commands 1-9
while True:
    print()
    user_input = input("Please enter a command (1-9, x to exit): ")
    if user_input.isdigit():
        user_input = int(user_input)
        if  1 <= user_input <= 9:
            handler(user_input, dbConn)
        else:
           print("**Error, unknown command, try again...")
           print() 
    elif user_input.lower() == 'x':
        break
    else:
        print("**Error, unknown command, try again...")
        print() 
#
# done
#
