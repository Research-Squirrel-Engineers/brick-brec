# Registering https://w3id.org/brec/

1. Check that the path is free: `curl -sI https://w3id.org/brec/` should answer 404, and the folder `brec/` must not exist in https://github.com/perma-id/w3id.org.
2. Fork https://github.com/perma-id/w3id.org
3. Copy the folder `brec/` from this directory into the root of the fork (it holds `.htaccess` and `README.md`).
4. Fill in the maintainer contact in `brec/README.md`.
5. Open a pull request. Redirects work as soon as it is merged.

Check afterwards (Windows cmd, one line):

    curl -sIL -H "Accept: text/turtle" https://w3id.org/brec/ontology && curl -sIL https://w3id.org/brec/id/lego_pyramid_2
