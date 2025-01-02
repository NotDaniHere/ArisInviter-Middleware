# ArisInviter Example Frontend + Middleware

## What is this?

This is a simple flask app, easily configurable and customisable to fit your needs. Includes a simple frontend too.

## What does it do?

The middleware (flask app) connects to LoginSecurity's database (spigot plugin) and authenticates invites using the input username and password in order to invite a new player using the ArisInviter backend (the spigot plugin https://github.com/NotDaniHere/ArisInviter).

## How to run it?
**First method**
Assuming you have placed the ```app.py``` in the main folder of your spigot server, and have installed LoginSecurity, you need to run this command to start the Middleware server:
```console
flask run
```
Now to test the functionality, you need to run this following command in another terminal:
```console
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"Notch","password":"mysecret123","invite":"Steve"}' \
     http://[your-server-ip]:5000/invite
```
Assuming you have whtielist enabled on your server and have correctly inputed a whitelisted user's Username and Password, the invited should now be whitelisted on the server too.

**Second method**
Upon running the flask app as in the first method, navigate to ```http://[your-server-ip]:5000```
There, authenticate with your LoginSecurity details and invite your player.