# SNAPCITY
### A multi-page web application that allows users to create an account, access multiple workouts (depending on the muscle group chosen) & leave interactive feedback under said workouts for other users to see. Built using Python, with data scraped from https://wger.de/en/software/api


#### App Features Include:
* The ability to create an account, allowing the user to:
    * Keep track of their current weight and goal weight (showcased only on their private account).
    * Delete their account if they so choose.
    
* User can choose between 11 muscle groups that each show:
    * A photo of the muscle that has been chosen.
    * A list of specific workouts to target that specific area.
    
* User can choose a workout from the list, openning up specifics:
    * A description on how to do the workout.
    * Some contain different variations depending on how the exercise is executed.
    * A list of the equipment needed to perform the exercise.
    * The comments/feedback other users have left under that exercise (if any)
    * The option to leave a new comment/feedback under each workout.
    
![Image of SNAPCITY site](/static/images/snapcity.png?raw=true "App Photo")
    
    
#### Resources Used:
* WGER API: https://wger.de/en/software/api

#### Technology Used:
* Python
* JavaScript
* HTML
* Bootstrap
* CSS
* Jinja2
* Django
* WTForms
