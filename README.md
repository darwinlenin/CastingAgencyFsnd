# Casting Agency Full Stack

## Full Stack Nano - Final Project

The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies. You are an Executive Producer within the company and are creating a system to simplify and streamline your process.

## Tasks


1. Application is live and hosted in Heroku in the following url: 
https://castingagencyfsnd1.herokuapp.com/

2. All required configuration settings are included in a bash file which export: [`setup.sh`]
AUTH0_DOMAIN=zoegeop.auth0.com
API_AUDIENCE=castingagency
CLIENT_ID='CLIENT_ID_HERE'
CLIENT_SECRECT='CLIENT_SECRECT_HERE'

3. Access of roles:
Casting Director : All permissions a Casting Assistant has and Add or delete an actor from the database. Modify actors or movies
Casting Assistant : Can view actors and movies
Executive Producer : All permissions a Casting Director has and Add or delete a movie from the database