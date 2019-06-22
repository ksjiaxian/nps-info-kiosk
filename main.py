from flask import Flask, request, render_template
import requests
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def search_output():
    #pull the park data from the API
    park_name = request.form['park']
    state_name = request.form['state'].upper()
    designation = request.form['designation']
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
                
        #park code of the returned park
        parkCode = parksdata['data'][idx]['parkCode']
        
        #get the image data
        imageURL = "<img src=" + parksdata['data'][idx]['images'][int(random.uniform(0, 1) * 
                                 len(parksdata['data'][idx]['images']))]['url'] + ">"
                                             
        #extract the contents of the visitor center data
        visitorresponse = requests.get("https://developer.nps.gov/api/v1/visitorcenters?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "stateCode": state_name,
                                "fields": "operatingHours",
                                "parkCode": parkCode,
                                "sort":"fullName"})
        vcdata = visitorresponse.json()
        
        vcString = ""
        numOfVisitorCenters = len(vcdata['data'])
        if numOfVisitorCenters < 1:
            vcString = "<p>There are no visitor centers to display.</p>"
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
                    
        #extract the camp grounds data
        cgresponse = requests.get("https://developer.nps.gov/api/v1/campgrounds?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode})
        cgdata = cgresponse.json()
        cgString = ""
        numOfCampgrounds = len(cgdata['data'])
        if numOfCampgrounds < 1:
            cgString = "<p>There are no campgrounds to display.</p>"
        else: 
            for i in range(numOfCampgrounds):
                cgDetails = cgdata['data'][i]
                cgString += ("<h4>" + cgDetails['name'] + "</h4>"
                        "<p>" + cgDetails['description'] + "</p>"
                        )
                    
        #extract the articles data
        artresponse = requests.get("https://developer.nps.gov/api/v1/articles?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode,
                                "fields":"listingDescription"})
        artdata = artresponse.json()
        artString = ""
        numOfArticles = len(artdata['data'])
        if numOfArticles < 1:
            artString = "<p>There are no articles to display.</p>"
        else: 
            for i in range(numOfArticles):
                artDetails = artdata['data'][i]
                artString += ("<h4>"
                              "<a href =" + artDetails['url'] + ">" + artDetails['title'] + "</a>"
                              "</h4><p>"+ artDetails['listingdescription'] + "</p>")
                    
        #extract the events data
        evresponse = requests.get("https://developer.nps.gov/api/v1/events?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode})
        evdata = evresponse.json()
        evString = ""
        numOfEvents = len(evdata['data'])
        if numOfEvents < 1:
            evString = "<p>There are no events to display.</p>"
        else: 
            for i in range(numOfEvents):
                evDetails = evdata['data'][i]
                evString += ("<h4>" + evDetails['title'] + "</h4>" + evDetails['description']
                            )
                    
        #extract the news data
        newresponse = requests.get("https://developer.nps.gov/api/v1/newsreleases?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode})
        newdata = newresponse.json()
        newString = ""
        numOfNews = len(newdata['data'])
        if numOfNews < 1:
            newString = "<p>There are no news articles to display.</p>"
        else: 
            for i in range(numOfNews):
                newDetails = newdata['data'][i]
                newString += ("<h4>"
                              "<a href =" + newDetails['url'] + ">" + newDetails['title'] + "</a>"
                              "</h4><p>"+ newDetails['abstract'] + "</p>")
                    
        #extract the alerts data
        alresponse = requests.get("https://developer.nps.gov/api/v1/alerts?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode})
        aldata = alresponse.json()
        alString = ""
        numOfAlerts = len(aldata['data'])
        if numOfAlerts < 1:
            alString = "<p>There are no alerts to display.</p>"
        else: 
            for i in range(numOfAlerts):
                alDetails = aldata['data'][i]
                alString += ("<h4>"
                              "<a href =" + alDetails['url'] + ">" + alDetails['category'].upper()+
                              ": " + alDetails['title'] + "</a>"
                              "</h4><p>"+ alDetails['description'] + "</p>")
                    
        #extract the places data
        plresponse = requests.get("https://developer.nps.gov/api/v1/places?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode,
                                "fields":"listingImage"})
        pldata = plresponse.json()
        plString = ""
        numOfPlaces = len(pldata['data'])
        if numOfPlaces < 1:
            plString = "<p>There are no places to display.</p>"
        else: 
            for i in range(numOfPlaces):
                plDetails = pldata['data'][i]
                plString += ("<div class = \"img_tile\"><h4>" + plDetails['title'] +
                              "</h4><br><a href =" + plDetails['url'] + "><img src = " + 
                              plDetails['listingimage']['url'] + "></a>"
                              "<p>"+ plDetails['listingdescription'] + "</p></div>")
            plString += "<p style=\"clear: both;\">"
            
        #extract the people data
        peresponse = requests.get("https://developer.nps.gov/api/v1/people?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode,
                                "fields":"listingImage"})
        pedata = peresponse.json()
        peString = ""
        numOfPeople = len(pedata['data'])
        if numOfPeople < 1:
            peString = "<p>There are no people to display.</p>"
        else: 
            for i in range(numOfPeople):
                peDetails = pedata['data'][i]
                peString += ("<div class = \"img_tile\"><h4>" + peDetails['title'] +
                              "</h4><br><a href =" + peDetails['url'] + "><img src = " + 
                              peDetails['listingimage']['url'] + "></a>"
                              "<p>"+ peDetails['listingdescription'] + "</p></div>")
            peString += "<p style=\"clear: both;\">"
            
        #extract the lessons data
        lesresponse = requests.get("https://developer.nps.gov/api/v1/lessonplans?",
                        params={"api_key":"ytQsdNZsdNhfq788BHTHgUJ7IsW1qFNw0A3ALCfC",
                                "parkCode": parkCode,
                                "sort":"gradelevel"})
        lesdata = lesresponse.json()
        lesString = ""
        numOfLessons = len(lesdata['data'])
        if numOfLessons < 1:
            lesString = "<p>There are no lessons to display.</p>"
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
                               description = str(parksdata['data'][idx]['description']), 
                               title = str(parksdata['data'][idx]['fullName']),
                               imageURL = imageURL,
                               npsurl = "<a href=" + str(parksdata['data'][idx]['url']) + ">Learn More</a>",
                               visitor = vcString,
                               campground = cgString,
                               articles = artString,
                               events = evString,
                               news = newString,
                               alerts = alString,
                               places = plString,
                               people = peString,
                               lessons = lesString
                               )
    except:
        return render_template("search_error.html")

if __name__ == '__main__':
    app.run(debug=False)
