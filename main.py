from flask import Flask, request, render_template, redirect, url_for, make_response
import requests
import random
import string

app = Flask(__name__)

#this dictionary helps track and separate users' history
history = {}

@app.route('/')
def home():
    resp = make_response(render_template("index.html"))
    #generate a random cookie
    resp.set_cookie('session_id', ''.join(random.choices(string.ascii_uppercase + 
                                                         string.digits, k=10)))
    return resp

def search(park_name, state_name, designation):
    parksresponse = requests.get("https://developer.nps.gov/api/v1/parks?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "stateCode": state_name,
                                "q": park_name + " " + designation,
                                "fields": "images",
                                "sort": "fullName"})
    parksdata = parksresponse.json()
    
    #if the above query returns no result, try again dropping the designation
    if len(parksdata['data']) < 1:
        parksresponse = requests.get("https://developer.nps.gov/api/v1/parks?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "stateCode": state_name,
                                "q": park_name,
                                "fields": "images",
                                "sort": "fullName"})
        parksdata = parksresponse.json()
        
    #again, if the above query returns no result, try again dropping the state code
    if len(parksdata['data']) < 1:
        parksresponse = requests.get("https://developer.nps.gov/api/v1/parks?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "q": park_name,
                                "fields": "images",
                                "sort": "fullName"})
        parksdata = parksresponse.json()   
    
    try:
        #see which index is the searched park
        idx = 0
        for i in range(len(parksdata['data'])):
            if park_name.lower() in parksdata['data'][i]['fullName'].lower():
                idx = i
                
        resp = make_response(redirect(url_for('title')))
        
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        global history
        history[cookie] = {'parkCode': parksdata['data'][idx]['parkCode'],
                            'parkTitle': str(parksdata['data'][idx]['fullName']),
                            'npsurl': str(parksdata['data'][idx]['url'])}
        
        resp.set_cookie('session_id', cookie)
            
        return resp
    
    except:
        return render_template("search_error.html")

@app.route('/', methods=['POST'])
def search_output():
    if request.form['park'] == "" and request.form['state'] == "" and request.form['designation'] == "":
        return render_template("index.html")
    else:
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
    
    
@app.route('/title', methods=['GET', 'POST'])
def title():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        
        #extract the park data
        parkresponse = requests.get("https://developer.nps.gov/api/v1/parks?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "fields": "images",
                                "parkCode": history[cookie]['parkCode']})
        parksdata = parkresponse.json()
        
        #get the image data
        imageURL = "<img src=" + parksdata['data'][0]['images'][int(random.uniform(0, 1) * 
                                 len(parksdata['data'][0]['images']))]['url'] + ">"
        
        return render_template("search_success.html", 
                               description ="<p id = \"description\">" +
                                            str(parksdata['data'][0]['description']) + "</p>", 
                               title = history[cookie]['parkTitle'],
                               imageURL = imageURL,
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>"
                               )
    
   

@app.route('/visitorcenters', methods=['GET', 'POST'])
def visitor_centers():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        
        #extract the contents of the visitor center data
        visitorresponse = requests.get("https://developer.nps.gov/api/v1/visitorcenters?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "fields": "operatingHours",
                                "parkCode": history[cookie]['parkCode'],
                                "sort":"fullName"})
        vcdata = visitorresponse.json()
        
        vcString = "<h3>Visitor Center and Museum Information:</h3>"
        numOfVisitorCenters = len(vcdata['data'])
        if numOfVisitorCenters < 1:
            vcString += "<p>There are no visitor centers to display.</p>"
        else:
            for i in range(numOfVisitorCenters):
                vcDetails = vcdata['data'][i]
                vcString += ("<h4>" + vcDetails['name'] + "</h4>"
                        "<p>" + vcDetails['description'] + "</p>"
                        )
                if 'operatingHours' in vcDetails:
                    vcString += ("<h5>Operating Hours</h5><ul>"
                        "<li>Monday: " + vcDetails['operatingHours'][0]['standardHours']['monday'] + "</li>"
                        "<li>Tuesday: " + vcDetails['operatingHours'][0]['standardHours']['tuesday'] + "</li>"
                        "<li>Wednesday: " + vcDetails['operatingHours'][0]['standardHours']['wednesday'] + "</li>"
                        "<li>Thursday: " + vcDetails['operatingHours'][0]['standardHours']['thursday'] + "</li>"
                        "<li>Friday: " + vcDetails['operatingHours'][0]['standardHours']['friday'] + "</li>"
                        "<li>Saturday: " + vcDetails['operatingHours'][0]['standardHours']['saturday'] + "</li>"
                        "<li>Sunday: " + vcDetails['operatingHours'][0]['standardHours']['sunday'] + "</li>"
                        "</ul>"
                        )
                if 'directionsInfo' in vcDetails and len(vcDetails['directionsInfo']) > 0:
                    vcString +=("<h5>Travel Directions</h5>"
                            "<p>" + vcDetails['directionsInfo'] + "</p>"
                            )
        
        return render_template("search_success.html", 
                               visitor = vcString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>"
                               )
                    
@app.route('/campgrounds', methods=['GET', 'POST'])
def camp_grounds():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        
        #extract the campgrounds data
        cgresponse = requests.get("https://developer.nps.gov/api/v1/campgrounds?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode']})
        cgdata = cgresponse.json()
        cgString = "<h3>Campground Information:</h3>"
        numOfCampgrounds = len(cgdata['data'])
        if numOfCampgrounds < 1:
            cgString += "<p>There are no campgrounds to display.</p>"
        else: 
            for i in range(numOfCampgrounds):
                cgDetails = cgdata['data'][i]
                cgString += ("<h4>" + cgDetails['name'] + "</h4>"
                        "<p>" + cgDetails['description'] + "</p>"
                        )
        
        return render_template("search_success.html", 
                               campgrounds = cgString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>"
                               )
    
@app.route('/articles', methods=['GET', 'POST'])
def articles():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the articles data
        artresponse = requests.get("https://developer.nps.gov/api/v1/articles?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode'],
                                "fields":"listingDescription"})
        artdata = artresponse.json()
        artString = "<h3>Related Articles:</h3>"
        numOfArticles = len(artdata['data'])
        if numOfArticles < 1:
            artString += "<p>There are no articles to display.</p>"
        else: 
            for i in range(numOfArticles):
                artDetails = artdata['data'][i]
                artString += ("<h4>"
                              "<a href =" + artDetails['url'] + ">" + artDetails['title'] + "</a>"
                              "</h4><p>"+ artDetails['listingdescription'] + "</p>")
                
        return render_template("search_success.html", 
                               articles = artString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>")
    
@app.route('/events', methods=['GET', 'POST'])
def events():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the events data
        evresponse = requests.get("https://developer.nps.gov/api/v1/events?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode']})
        evdata = evresponse.json()
        evString = "<h3>Events:</h3>"
        numOfEvents = len(evdata['data'])
        if numOfEvents < 1:
            evString += "<p>There are no events to display.</p>"
        else: 
            for i in range(numOfEvents):
                evDetails = evdata['data'][i]
                evString += ("<h4>" + evDetails['title'] + "</h4>" + evDetails['description']
                            )
                
        return render_template("search_success.html", 
                               events = evString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>"
                               )
    
@app.route('/news', methods=['GET', 'POST'])
def news():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the news data
        newresponse = requests.get("https://developer.nps.gov/api/v1/newsreleases?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode']})
        newdata = newresponse.json()
        newString = "<h3>News:</h3>"
        numOfNews = len(newdata['data'])
        if numOfNews < 1:
            newString += "<p>There are no news articles to display.</p>"
        else: 
            for i in range(numOfNews):
                newDetails = newdata['data'][i]
                newString += ("<h4>"
                              "<a href =" + newDetails['url'] + ">" + newDetails['title'] + "</a>"
                              "</h4><p>"+ newDetails['abstract'] + "</p>")
        
        return render_template("search_success.html", 
                               news = newString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>")    
    
@app.route('/alerts', methods=['GET', 'POST'])
def alerts():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the alerts data
        alresponse = requests.get("https://developer.nps.gov/api/v1/alerts?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode']})
        aldata = alresponse.json()
        alString = "<h3>Alerts:</h3>"
        numOfAlerts = len(aldata['data'])
        if numOfAlerts < 1:
            alString += "<p>There are no alerts to display.</p>"
        else: 
            for i in range(numOfAlerts):
                alDetails = aldata['data'][i]
                alString += ("<h4>"
                              "<a href =" + alDetails['url'] + ">" + alDetails['category'].upper()+
                              ": " + alDetails['title'] + "</a>"
                              "</h4><p>"+ alDetails['description'] + "</p>") 
                
        return render_template("search_success.html", 
                               alerts = alString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>")     
    
@app.route('/places', methods=['GET', 'POST'])
def places():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the places data
        plresponse = requests.get("https://developer.nps.gov/api/v1/places?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode'],
                                "fields":"listingImage"})
        pldata = plresponse.json()
        plString = "<h3>Places:</h3>"
        numOfPlaces = len(pldata['data'])
        if numOfPlaces < 1:
            plString += "<p>There are no places to display.</p>"
        else: 
            for i in range(numOfPlaces):
                plDetails = pldata['data'][i]
                plString += ("<div class = \"img_tile\"><h4>" + plDetails['title'] +
                              "</h4><br><a href =" + plDetails['url'] + "><img src = " + 
                              plDetails['listingimage']['url'] + "></a>"
                              "<p>"+ plDetails['listingdescription'] + "</p></div>")
            plString += "<p style=\"clear: both;\">" 
            
        return render_template("search_success.html", 
                               places = plString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>")    
    
@app.route('/people', methods=['GET', 'POST'])
def people():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the people data
        peresponse = requests.get("https://developer.nps.gov/api/v1/people?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode'],
                                "fields":"listingImage"})
        pedata = peresponse.json()
        peString = "<h3>People:</h3>"
        numOfPeople = len(pedata['data'])
        if numOfPeople < 1:
            peString += "<p>There are no people to display.</p>"
        else: 
            for i in range(numOfPeople):
                peDetails = pedata['data'][i]
                peString += ("<div class = \"img_tile\"><h4>" + peDetails['title'] +
                              "</h4><br><a href =" + peDetails['url'] + "><img src = " + 
                              peDetails['listingimage']['url'] + "></a>"
                              "<p>"+ peDetails['listingdescription'] + "</p></div>")
            peString += "<p style=\"clear: both;\">"
            
        return render_template("search_success.html", 
                               people = peString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>") 
    
@app.route('/lessons', methods=['GET', 'POST'])
def lessons():
    if (request.method == "POST" and not (request.form['park'] == "" and 
        request.form['state'] == "" and request.form['designation'] == "")):
        #pull the park data from the API
        park_name = request.form['park']
        state_name = request.form['state'].upper()
        designation = request.form['designation']
        
        return search(park_name, state_name, designation)
        
    else:
        cookie = ""
        if 'session_id' in request.cookies:
            cookie = request.cookies.get('session_id')
        else:
            #go back to the homepage and get a cookie
            return redirect(url_for('home'))
        
        #extract the lessons data
        lesresponse = requests.get("https://developer.nps.gov/api/v1/lessonplans?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": history[cookie]['parkCode'],
                                "sort":"gradelevel"})
        lesdata = lesresponse.json()
        lesString = "<h3>Lessons:</h3>"
        numOfLessons = len(lesdata['data'])
        if numOfLessons < 1:
            lesString += "<p>There are no lessons to display.</p>"
        else: 
            grade = lesdata['data'][0]['gradelevel']
            lesString += "<h4>" + grade + "</h4>"
            for i in range(numOfLessons):
                lesDetails = lesdata['data'][i]
                if not lesDetails['gradelevel'] == grade:
                    grade = lesDetails['gradelevel']
                    lesString += "<h4>" + grade + "</h4>"
                lesString += ("<a href =" + lesDetails['url'] + "><p>" + lesDetails['title'] + 
                              "</a> - "+ lesDetails['questionobjective'] + "</p>")
            
        return render_template("search_success.html", 
                               lessons = lesString, 
                               title = history[cookie]['parkTitle'],
                               npsurl = "<a href=" + history[cookie]['npsurl'] + ">Learn More</a>") 
                    
    
if __name__ == '__main__':
    app.run(debug=False)
