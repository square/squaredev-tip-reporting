
# Tip reporting sample app

* [Overview](#overview)
* [Setup](#setup)
* [Project organization](#project-organization)
* [Application flow](#application-flow)

# Overview

This sample web application integrates the Square [Payments API](https://developer.squareup.com/reference/square/bookings-api), [Team API](https://developer.squareup.com/reference/square/team-api), [Orders API](https://developer.squareup.com/reference/square/orders-api) and [Labor API](https://developer.squareup.com/reference/square/labor-api). It showcases some of their functionality, including:
 
* Listing payments by a date range.
* Fetching a set of team members by ID.
* Listing team member wages.
* Fetching orders and related customers by order ID.

In addition to using the Payments API, the application demonstrates how to integrate the Payments API with the following Square APIs:

* Calling the [Team API](https://developer.squareup.com/reference/square/team-api) to search for team members by location ID.
* Calling the [Labor API](https://developer.squareup.com/reference/square/customers-api) to list shifts by location and a date range.
* Calling the [Locations API](https://developer.squareup.com/reference/square/locations-api) to get information about the seller's business location used throughout the application.

The sample shows you how you can report on tip earnings for employees by combining data from team and labor APIs.  

## Setup

### Set up the application

You need an `.env` file in your root directory to provide credentials. You can copy the content in the `.env.example` file provided in the project and use it as a template.

In the file:
1.  Set `ENVIRONMENT` to `development` (for testing).
1.  Replace the placeholder texts of `SQUARE_SANDBOX_ACCESS_TOKEN` with your access token for the chosen environment.

    You can find your Square credentials in the Square Developer Dashboard. For more information, see [Getting Started](https://developer.squareup.com/docs/get-started#step-2-create-an-application).

    **IMPORTANT:** You can use your own credentials to test the sample application. If you plan to make a version of this sample application available to other users, you must use the Square [OAuth API](https://developer.squareup.com/docs/oauth-api/overview) to safely manage access to Square accounts.


1. Copy the file `.env.example` into a new file called `.env`. Set the value of the Square Access Token for the sandbox account you want to seed data into. 
 
    `SQUARE_SANDBOX_ACCESS_TOKEN=yourSandboxAccessToken`

1. In your terminal change into the `backend` directory
    ```bash
    $ cd backend
    ```

1. Ensure that you have a python virtual environment installed and activated. If not, run the following commands from a terminal prompt.
 
    `$ python3 -m venv ./venv`
    
    `$ . ./venv/bin/activate`
    
    `$ pip3 install -r requirements.txt`
 
1. Add tip report test data to your sandbox environment by running the following commands from a terminal prompt.
 
    `$ python seed-data.py --seed`

**IMPORTANT:** This script when finished will produce a file called `output.json`. This file contains all the information of created data into the Square account. You can use this if you wish to find certain IDs and query them via the [API explorer](https://developer.squareup.com/explorer/square) or your own scripts you may have.
 
1. Start the Python server:

   `$ python -m flask run`
1. Open a new terminal and navigate to the `frontend` directory:

   `$ cd ../frontend`
1. Open a terminal and run the following command to install the sample application's dependencies:

   `$ npm install`
1. Start the node server that serves the application client page by running the following command:
 
   `$ npm start`
 
1. Type `localhost:3000` in your browser to start the application. Then select a location on the first page.

## Project organization

This application, as an React project, is organized as follows:

* The `.env` file. The application provides the `.env.example` file in the project's root folder for you to copy as a template, save it as `.env`, and provide your credentials in the saved `.env` file.
* The `frontend/` folder contains the React app code and resources for the client web page.
* The `backend/` folder contains the resources and code for the flask service that provides the endpoints called by the client to get the Square account data that feeds the client web.

### Frontend
* The `public/` folder. Static files that are used in the final output of React build process.  
* The `src/` folder. Provides all of the client application logic and styling. 
* The `src/components` folder. Includes the client logic for page components such as tables, headings, and navigation.

### Backend
* The `backend/` folder. Provides the logic and resource files that define the flask service. The `seed-data.py` file is the script that adds test data to your Square sandbox account. `app.py` contains the declarations and logic for the endpoints which fetch Square account data and return results to the client.

## Application flow

In general, React is a web application framework for JavaScript extension. It supports provisioning a user interface for the application to interact with the user by rendering HTML pages. A user action corresponds to an HTTP or HTTPS request passed to the backend through a specific route.  

Specifically, when the sample application is running, it can perform the following interactive tasks:  

* [**Select location**](#select-location)
* [**Select team to report on**](#select-team-members-to-report-on)
* [**Run the tip report**](#run-the-tip-report)
* [**See individual team member closed orders**](#see-individual-team-member-closed-orders)

User interaction in the form of select controls rely on getting selection values from endpoints in the backend of the application. Button actions call other endpoints on the backend that 

With the application's backend running, the user opens the application's home page (such as `http://localhost:3000` for the locally hosted application) to start the application flow. 

### Select location

`App.tsx` fetches a response from the `/locations` endpoint defined in the backend service.
The [_/locations route handler](backend/app.py#L23) calls the [`ListLocations`](https://developer.squareup.com/reference/square/locations/list-locations) endpoint of the Locations API to retrieve all of the seller's locations, as represented by [`Location`](https://developer.squareup.com/reference/square/objects/Location) objects.

It then opens the [locations](frontend/src/App.tsx#86) selector that presents a list of locations for the user to select one.

### Select team members to report on

`App.tsx` fetches a response from the `/team` endpoint defined in the backend service. This route handler retrieves all active team members and presents them for the user to choose. The [_/team route handler](backend/app.py#L31) calls the [`SearchTeamMembers`](https://developer.squareup.com/reference/square/team/search-team-members) endpoint of the Teams API to retrieve all of the seller's team members for the selected location.

### Run the tip report

`App.tsx` presents a Run Report button whose click event handler posts report parameters to the [_/tip-report](backend/app.py#L64) endpoint defined in the backend service. This route handler generates the tipping report and returns an object that is shown in the `report-table` component.

### See individual team member closed orders

`report-table.tsx` presents a Details Report button whose click event handler posts report parameters to the [_/team-member-details](backend/app.py#L80) endpoint defined in the backend service. This route handler generates the details of the selected team member's activity during the reporting period. The activity details are returned and shown in a modal..

# Useful Links

* [Python SDK Page](https://developer.squareup.com/docs/sdks/python)
* [Payments API Overview](https://developer.squareup.com/docs/payments-refunds)
* [Payments API Reference](https://developer.squareup.com/reference/square/payments-api)
* [Team API Overview](https://developer.squareup.com/docs/team/overview)
* [Team API Reference](https://developer.squareup.com/reference/square/team-api)
* [Labor API Overview](https://developer.squareup.com/docs/labor-api/what-it-does)
* [Labor API Reference](https://developer.squareup.com/reference/square/labor-api)

