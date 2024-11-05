import requests
import time
from bs4 import BeautifulSoup

# Pushover setup
pushover_user_key = "unss4wsbqep1kk21ncgg2vzu6xfzo8"
pushover_api_token = "ahfs4dnm35h218c51j658s4iqhc2zy"

# Target courses with CRNs and course names
target_courses = [
    {"crn": "50744", "course": "CSCE 465"},
    {"crn": "54814", "course": "CSCE 402"},
    {"crn": "19179", "course": "CSCE 445"},
    {"crn": "37077", "course": "CSCE 482 (Thomas)"},
    {"crn": "40163", "course": "CSCE 482 (Lightfoot)"},
]

def send_pushover_notification(message):
    """Send a notification to Pushover with the provided message."""
    payload = {
        "token": pushover_api_token,
        "user": pushover_user_key,
        "message": message,
        "priority": 2,  # Set as a critical alert
        "retry": 30,    # Retry every 30 seconds
        "expire": 300,  # Expire after 5 minutes
        "sound": "siren"  # Set the sound to "siren" for critical alert
    }
    requests.post("https://api.pushover.net/1/messages.json", data=payload)

def check_seat_availability():
    """Check each course for seat availability and only send a notification if any course has open seats."""
    message = "Course Seat Availability:\n"
    alert_needed = False  # Only send an alert if any course has open seats

    for course in target_courses:
        crn = course["crn"]
        course_name = course["course"]
        url = f"https://compass-ssb.tamu.edu/pls/PROD/bwykschd.p_disp_detail_sched?term_in=202511&crn_in={crn}"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", class_="datadisplaytable")
            
            if table:
                # Find the last <td> in the row containing seat data
                rows = table.find_all("tr")
                if rows and len(rows) > 1:
                    seat_info_cells = rows[1].find_all("td")
                    if seat_info_cells:
                        remaining_seats = int(seat_info_cells[-1].text.strip())
                        message += f"{course_name}: {remaining_seats} seat(s) remaining\n"
                        
                        # If any course has >0 seats, mark alert as needed
                        if remaining_seats > 0:
                            alert_needed = True
                    else:
                        message += f"{course_name}: Seat data not found\n"
                else:
                    message += f"{course_name}: Seat data row not found\n"
            else:
                message += f"{course_name}: Seat availability table not found\n"
        else:
            message += f"{course_name}: Failed to retrieve data (status code {response.status_code})\n"

    # Print the message regardless of seat availability
    print(message)

    # Send notification only if there's at least one course with open seats
    if alert_needed:
        send_pushover_notification(message)

while True:
    check_seat_availability()
    time.sleep(25) 
