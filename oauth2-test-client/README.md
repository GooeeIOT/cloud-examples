OAuth2 Docker Test Client
=========================

This is a sample app that serves as an example of how to integrate 3rd party apps using OAuth2. See the actual [Gooee Authentication documentation](https://api-docs.gooee.io/general/authentication.html) for more information. Read app.py to see what type of requests your app must make to successfully generate OAuth2 tokens.

Requirements
------------

[Docker](https://www.docker.com/get-docker) installed and setup to pull images from [Docker Hub](https://hub.docker.com/)

Usage
-----

1. Register the Application with the Gooee Auth Server by emailing <cloud-backend@gooee.com> with your application's Redirect URI. For Gooee admins, register the application at `/auth/o/applications/register` using a redirect URI `http://localhost:8080/api_callback` and Authorization Grant Type of `Authorization Code`. Copy down the Client ID and Secret for the next step.

2. Fill in the `env.list.dist` file with the correct values. Use the Client ID and Secret from the step above. Rename it to `env.list`

3. Run the client:
`docker run --name flask -p 8080:80 -v $(pwd):/app --env-file env.list -d jazzdd/alpine-flask:python3`

4. (Optional) If you need this as a public resource, try <ngrok.com>. You will need to modify `env.list` to use the Ngrok forwarding URL.

5. Visit the client page in your browser at:
`http://localhost:8080`

6. Stop the client:
`docker rm -f flask`

License
-------

This example is distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0), see the parent directory's LICENSE for more information.
